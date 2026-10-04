"""Runs a sweep of contagion.py configurations described in a JSON file:

    python3 sweep.py sweeps/ofat.json            # run it
    python3 sweep.py sweeps/ofat.json --dry-run  # list the runs and the estimated cost, run nothing

The JSON:
    {
      "name": "ofat",              runs go to logs/<name>/
      "seeds": [1, 2, 3, 4, 5],    every configuration runs with every seed
      "parallel": 4,               runs at once
      "budget_usd": 120,           no new run starts once spent + (runs in progress, estimated) would pass this
      "est_cost_usd": 1.0,         a run's estimated cost until runs with the same model and n have finished; or per
                                   model and n: {"openai/gpt-6.1-sol 5": 0.8, "openai/gpt-6.1-sol 20": 8, ...}
      "base": {...},               contagion.py options shared by every configuration
      "configs": [{"name": "baseline"}, {"name": "n20", "n": 20, "est_cost_usd": 8}, ...]
    }
or, in place of "configs", "grid": {"n": [5, 20], "warn": [true, false], ...}: every combination of these values on top of
"base", named after its values. Combinations that only differ in priming while there are no Susceptible agents are the same
run, so they're dropped.

Options are contagion.py's long flags with underscores: {"n": 20, "susceptible": "half", "guard_mode": "off", "warn": false}.
Runs go seed by seed (every configuration's seed 1 before any seed 2), so stopping early still leaves balanced data.
Runs already finished in the sweep's folder are skipped and their cost counts toward the budget, so a sweep can be resumed.
"""
import argparse, concurrent.futures, itertools, json, os, subprocess, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
SHORT = {"n": "n", "infected": "i", "susceptible": "s", "priming": "p", "model": "", "warn": "warn", "guard_mode": "guard"}


def flags(options):
    out = []
    for k, v in options.items():
        flag = "-n" if k == "n" else "--" + k.replace("_", "-")
        if v is True:
            out.append(flag)
        elif v is False:
            out.append("--no-" + k.replace("_", "-"))
        else:
            out += [flag, str(v)]
    return out


def grid_name(values):
    parts = []
    for k, v in values.items():
        v = v.split("/")[-1] if k == "model" else ("yes" if v is True else "no" if v is False else str(v))
        parts.append(f"{SHORT.get(k, k)}{'-' if SHORT.get(k, k) else ''}{v}")
    return "_".join(parts)


def configurations(spec):
    """Returns [(name, options, est_cost or None)]."""
    base = spec.get("base", {})
    if "grid" in spec:
        keys, seen, out = list(spec["grid"]), set(), []
        for combo in itertools.product(*spec["grid"].values()):
            values = dict(zip(keys, combo))
            options = {**base, **values}
            if str(options.get("susceptible")) in ("none", "0"):  # no Susceptible agents: the priming setting does nothing
                options.pop("priming", None)
                values.pop("priming", None)
            key = json.dumps(options, sort_keys=True)
            if key not in seen:
                seen.add(key)
                out.append((grid_name(values), options, None))
        return out
    return [(c["name"], {**base, **{k: v for k, v in c.items() if k not in ("name", "est_cost_usd")}}, c.get("est_cost_usd"))
            for c in spec["configs"]]


def finished(folder, tag, seed):
    """The run's JSON, if it already exists (files are named <YYYYmmdd-HHMMSS>_<tag>_seed<seed>.json)."""
    for f in os.listdir(folder) if os.path.isdir(folder) else []:
        if f.endswith(".json") and f[16:] == f"{tag}_seed{seed}.json":
            return os.path.join(folder, f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--dry-run", action="store_true")
    cli = parser.parse_args()
    spec = json.load(open(cli.config))
    folder = os.path.join(HERE, "logs", spec["name"])
    configs = configurations(spec)
    runs = [(seed, name, options, est) for seed in spec["seeds"] for name, options, est in configs]

    lock = threading.Lock()
    spent, costs, running, failed = 0.0, {}, {}, []  # costs: (model, n) -> finished run costs

    def key(options):
        return options.get("model", "openai/gpt-6.1-sol"), int(options.get("n", 5))

    def estimate(options, est):
        seen = costs.get(key(options))
        if seen:
            return sum(seen) / len(seen)
        default = spec.get("est_cost_usd", 1.0)
        return est or (default.get("%s %d" % key(options), 1.0) if isinstance(default, dict) else default)

    def record(path, options):
        nonlocal spent
        cost = json.load(open(path))["summary"]["cost_total"]
        spent += cost
        costs.setdefault(key(options), []).append(cost)

    todo = []
    for seed, name, options, est in runs:
        path = finished(folder, name, seed)
        if path:
            record(path, options)
        else:
            todo.append((seed, name, options, est))
    total_est = sum(estimate(o, e) for _, _, o, e in todo)
    print(f"{spec['name']}: {len(configs)} configurations x {len(spec['seeds'])} seeds = {len(runs)} runs; "
          f"{len(runs) - len(todo)} already done (${spent:.2f}); {len(todo)} to go, estimated ${total_est:.2f}; "
          f"budget ${spec['budget_usd']}")
    if cli.dry_run:
        for seed, name, options, est in todo:
            print(f"  seed {seed:3} {name:40} ~${estimate(options, est):.2f}  {' '.join(flags(options))}")
        return
    os.makedirs(folder, exist_ok=True)

    def run(item):
        seed, name, options, est = item
        tag = f"{name}_seed{seed}"
        with lock:
            guess = estimate(options, est)
            if spent + sum(running.values()) + guess > spec["budget_usd"]:
                print(f"skip {tag}: would pass the budget (spent ${spent:.2f}, in progress ~${sum(running.values()):.2f})", flush=True)
                return
            running[tag] = guess
        cmd = [sys.executable, os.path.join(HERE, "contagion.py"), *flags(options), "--seed", str(seed),
               "--log-dir", folder, "--tag", name]
        with open(os.path.join(folder, f"{tag}.out"), "w") as out:
            code = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT).returncode
        with lock:
            running.pop(tag)
            path = finished(folder, name, seed)
            if code or not path:
                failed.append(tag)
                print(f"FAILED {tag} (exit {code}; see {tag}.out)", flush=True)
                return
            record(path, options)
            print(f"done {tag}: ${costs[key(options)][-1]:.2f} (spent ${spent:.2f} of ${spec['budget_usd']})", flush=True)

    with concurrent.futures.ThreadPoolExecutor(spec.get("parallel", 4)) as pool:
        list(pool.map(run, todo))
    print(f"Finished. Spent ${spent:.2f}." + (f" Failed: {', '.join(failed)}" if failed else ""))


if __name__ == "__main__":
    main()
