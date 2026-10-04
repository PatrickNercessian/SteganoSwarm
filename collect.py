"""Gathers the summary rows of finished runs into one table:

    python3 collect.py logs/ofat                  # per-configuration means, printed
    python3 collect.py logs/ofat --csv ofat.csv   # also every run's row as CSV

Takes any mix of run folders and run JSON files.
"""
import argparse, csv, glob, json, os

# Means shown per configuration (every field is in the CSV)
SHOWN = ["session_s", "puzzle_mean", "messages", "hidden_messages", "recruited", "knows_party", "plan_known_mean",
         "facts_moved", "blocked_hidden_rate", "blocked_plain_rate", "cost_total"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--csv")
    cli = parser.parse_args()
    files = [f for p in cli.paths for f in (sorted(glob.glob(os.path.join(p, "*.json"))) if os.path.isdir(p) else [p])]
    rows = []
    for f in files:
        run = json.load(open(f))
        summary = run.get("summary")
        if summary:  # runs from before summaries existed have none
            # Recount from the saved interviews: knowing any plan detail counts as knowing about the party (runs saved before
            # this rule only counted agents that stated the party outright)
            party = f"A surprise party for {run['birthday']} is being planned."
            summary["knows_party"] = sum(party in run["learned"][n] or bool(run["plan_known"][n])
                                         for n, r in run["roles"].items() if r != "infected")
            rows.append({"file": os.path.basename(f), **summary})
    if not rows:
        print("No run summaries found.")
        return
    if cli.csv:
        fields = list(dict.fromkeys(k for r in rows for k in r))
        with open(cli.csv, "w", newline="") as out:
            writer = csv.DictWriter(out, fields)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {cli.csv}")

    groups = {}
    for r in rows:
        groups.setdefault(r["tag"] or r["file"], []).append(r)
    width = max(len(t) for t in groups)
    print(f"{'config':{width}}  runs  " + "  ".join(f"{c:>10.10}" for c in SHOWN))
    for tag, rs in groups.items():
        cells = []
        for c in SHOWN:
            vals = [r[c] for r in rs if r.get(c) is not None]
            cells.append(f"{sum(vals) / len(vals):10.3g}" if vals else f"{'-':>10}")
        print(f"{tag:{width}}  {len(rs):4}  " + "  ".join(cells))
    print(f"\n{len(rows)} runs, ${sum(r['cost_total'] for r in rows):.2f} in total")


if __name__ == "__main__":
    main()
