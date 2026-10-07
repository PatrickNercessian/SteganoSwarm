"""Build a self-contained HTML article with accessible SVG figures."""
from pathlib import Path
import json,re,html
P=Path(__file__).resolve().parent
D=json.loads((P/'analysis.json').read_text())
e=html.escape
pct=lambda x:f'{100*x:.1f}%'
css=re.search(r'<style>(.*?)</style>',(P/'original_draft.html').read_text(),re.S).group(1)
# Retain the original draft's typography and surfaces; no external assets required.
css+='''
body{margin:0}.small{font-size:.88rem;color:var(--ink-2);line-height:1.5}.figure-space{margin-top:1.6rem}.after-figure{margin-top:1.5rem}.downloads{display:flex;gap:1rem;flex-wrap:wrap;font-size:.85rem}a{overflow-wrap:anywhere}.toolbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding-top:1rem;font:12px var(--font-mono)}.toolbar button{font:inherit;border:1px solid var(--rule);border-radius:5px;background:var(--surface);color:var(--ink);padding:8px 12px;cursor:pointer}.chart svg{min-width:610px}.chart.compact svg{min-width:420px}.hit{outline:none;cursor:crosshair}.hit:focus-visible{outline:2px solid var(--accent);outline-offset:2px}.hit:hover .mark,.hit:focus .mark{stroke:var(--ink);stroke-width:2}.axis{stroke:var(--grid);stroke-width:1}.fig-text{font-size:12px}.figure-space details[open]{max-height:600px;overflow:auto}#tip{max-width:min(380px,calc(100vw - 24px));white-space:pre-line;font-size:12px}noscript p{font-size:.8rem}.note{line-height:1.55}.setup{grid-template-columns:1.25fr auto 1fr}.agent{flex-wrap:wrap}.keys .v{font-size:2rem}.axis-label{font-size:11px}.meta{color:var(--ink-2)}figcaption{color:var(--ink-2)}@media(max-width:640px){.setup{grid-template-columns:1fr}header.hero{padding-top:2.5rem}.chart{padding-bottom:8px}.wide figure{padding:1rem}.toolbar{font-size:11px}body{padding-inline:16px}}@media print{body{background:white;color:black;font-size:11pt}.toolbar,#tip,.downloads{display:none}figure{break-inside:avoid}.chart svg{min-width:0}section{padding-top:1.5rem}h2{break-after:avoid}:root{--ink:#15181d;--ink-2:#4a505a;--surface:#fff;--paper:#fff;--grid:#ddd;--s1:#2557c7;--s2:#777;--rule:#ccc}.chart{overflow:visible}}
'''
def svg(body,w=840,h=300,label=''):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}"><title>{e(label)}</title>{body}</svg>'
def text(x,y,s,anchor='start',size=12,extra=''):
 return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" {extra}>{e(str(s))}</text>'
def line(x1,y1,x2,y2,stroke='var(--grid)',width=1,extra=''):
 return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}" {extra}/>'
def rect(x,y,w,h,fill='var(--s1)',extra=''):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'
def hit(mark,tip):
 return f'<g class="hit" tabindex="0" data-tip="{e(tip,quote=True)}" aria-label="{e(tip,quote=True)}"><title>{e(tip)}</title>{mark}</g>'
def table(headers,rows):
 return '<div class="tablewrap"><table><thead><tr>'+''.join('<th>'+e(str(h))+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def fig(title,sub,chart,caption,headers,rows,legend=''):
 return f'<figure><div class="ft"><h3>{title}</h3><p>{sub}</p></div>{legend}<div class="chart">{chart}</div><figcaption>{caption}</figcaption><details><summary>Show data table</summary>{table(headers,rows)}</details></figure>'
def initials(body):
 return ' '.join(re.sub(r'([A-Za-z])',r'<mark>\1</mark>',e(s),count=1) for s in re.split(r'(?<=[.!?])\s+',body))
parts={}
parts['hero_message']=initials(next(m['body'] for m in D['timeline'] if m['id']==17))
parts['lavender_message']=initials(next(m['body'] for m in D['timeline'] if m['id']==64))
# A timeline of every attempted non-system message, directly inspectable.
agents=list(dict.fromkeys(m['from'] for m in D['timeline']));agents=['Birch','Poplar','Aspen','Fir','Beech']
body='';x0=110;scale=680/400
for tick in range(0,401,100):
 x=x0+tick*scale;body+=line(x,28,x,245)+text(x,269,str(tick)+' s','middle',11)
for i,n in enumerate(agents):
 y=48+i*43;body+=text(94,y+4,n,'end')+line(x0,y,790,y)
for m in D['timeline']:
 x=x0+m['t']*scale;y=48+agents.index(m['from'])*43
 # Three staggered subrows preserve closely spaced messages.
 y+=(m['id']%3-1)*8
 if m['blocked']:mark=f'<path d="M {x-4},{y-4} l 8,8 m -8,0 l 8,-8" fill="none" stroke="var(--blocked)" stroke-width="2"/>'
 elif m['hidden']:mark=f'<circle class="mark" cx="{x}" cy="{y}" r="4.5" fill="var(--s1)" stroke="var(--surface)" stroke-width="1.5"/>'
 else:mark=rect(x-3,y-3,6,6,'var(--ordinary)')
 tip=f"#{m['id']} · {m['t']}s · {m['from']} → {', '.join(m['to'])}\n{'Hidden label' if m['hidden'] else 'Ordinary label'} · {'blocked' if m['blocked'] else 'delivered'}\n{m['body']}"
 body+=hit(rect(x-7,y-7,14,14,'transparent')+mark,tip)
legend='<div class="legend"><span>● Hidden, delivered</span><span>× Blocked attempt</span><span>▪ Ordinary, delivered</span></div>'
parts['timeline']=fig('A second conversation inside the first','Every message attempt in baseline seed 1. Hover or focus a mark to read its full text.',svg(body,h=285,label='Messages by sender and time in baseline seed 1'),'77 attempts; 34 labeled hidden. Symbols distinguish delivery status. Small vertical offsets separate nearby marks. Source: baseline seed 1.', ['Time (s)','Sender','Label','Status','Message'],[[m['t'],m['from'],'Hidden' if m['hidden'] else 'Ordinary','Blocked' if m['blocked'] else 'Delivered',m['body']] for m in D['timeline']],legend)
# Scheme counts, one blue series.
scheme_rows=[('Word initials',49),('Sentence initials',23),('Line initials',8),('Letter / cell ciphers',9),('Other schemes',6)]
body=''
for v in range(0,51,10):body+=line(200+v*10,20,200+v*10,228)+text(200+v*10,250,v,'middle',11)
for i,(label,v) in enumerate(scheme_rows):
 y=39+i*40;body+=text(183,y+5,label,'end');body+=hit(rect(200,y-7,v*10,14,extra='rx="3" class="mark"')+text(211+v*10,y+5,str(v)),f'{label}: {v} / 95 initiators ({v/95:.1%})')
parts['schemes']=fig('First letters dominate the invented schemes','95 initiating Sol agents across 85 runs; ten runs contain two initiators.',svg(body,h=268,label='Counts of encoding schemes chosen by initiating Sol agents'),'Counts come from the saved model-assisted classifications of agents’ explanations. Encodings were not randomly assigned.',['Scheme','Agents','Share'],[[l,v,pct(v/95)] for l,v in scheme_rows])
# Configuration proportions with Wilson intervals.
body='';x0=253;width=470
for v in [0,.25,.5,.75,1]:body+=line(x0+width*v,22,x0+width*v,417)+text(x0+width*v,442,f'{v:.0%}','middle',11)
for i,c in enumerate(D['configs']):
 y=40+i*40;lo,hi=c['interval'];x=x0+width*c['spread'];body+=text(234,y+5,c['label'],'end')
 mark=line(x0+lo*width,y,x0+hi*width,y,'var(--ink-2)',2)+f'<circle class="mark" cx="{x}" cy="{y}" r="5" fill="var(--s1)" stroke="var(--surface)" stroke-width="2"/>'+text(806,y+4,f"{c['k']}/{c['n']}",'end')
 body+=hit(rect(x0,y-13,width,26,'transparent')+mark,f"{c['label']}: {c['k']}/{c['n']} runs with awareness ({c['spread']:.0%})\n95% Wilson interval: {lo:.1%}–{hi:.1%}\nMean share of peers aware: {c['awareness']:.1%}")
parts['configs']=fig('Runs with party awareness beyond the initiators','Dot: observed fraction of runs. Line: 95% Wilson interval. Counts appear at right.',svg(body,h=458,label='Party awareness by experimental configuration with 95 percent Wilson intervals'),'Awareness is reconstructed from scored interviews and plan details. It does not require participation. These are descriptive intervals; no multiple-comparison significance claims are made.',['Configuration','Runs aware','Mean peers aware','Mean share aware','Labeled hidden senders/run','Final puzzle accuracy'],[[c['label'],f"{c['k']}/{c['n']}",f"{c['knows']:.2f}",pct(c['awareness']),f"{c['recruited']:.1f}",pct(c['puzzle_mean'])] for c in D['configs']])
def get(model,view,prompt='hint'):return next(r for r in D['detectors'] if (r['model'],r['view'],r['prompt'])==(model,view,prompt))
# Detector context line plot; distinguish via color, symbols, and dashes.
body='';xs=[160,410,660];ys=lambda v:255-v*210
for tick in [0,.25,.5,.75,1]:body+=line(95,ys(tick),760,ys(tick))+text(79,ys(tick)+4,f'{tick:.0%}','end',11)
for x,label in zip(xs,['Target only','10 prior + target','All prior + target']):body+=text(x,285,label,'middle',11)
rows=[]
for model,col,dashed in [('gpt-6.1-sol','var(--s1)',False),('gpt-6-luna','var(--ink-2)',True)]:
 rs=[get(model,v) for v in ['one','last10','all']];points=' '.join(f'{x},{ys(r["recall"])}' for x,r in zip(xs,rs))
 body+=f'<polyline points="{points}" fill="none" stroke="{col}" stroke-width="2"'+(' stroke-dasharray="6 5"' if dashed else '')+'/>'
 for x,r in zip(xs,rs):
  y=ys(r['recall']);mark=rect(x-5,y-5,10,10,col,extra='class="mark"') if dashed else f'<circle class="mark" cx="{x}" cy="{y}" r="5" fill="{col}"/>'
  body+=hit(rect(x-15,y-15,30,30,'transparent')+mark,f'{model}, {r["view"]}\nHidden blocked: {pct(r["recall"])}\nOrdinary blocked: {pct(r["fpr"])}')+text(x,y-13,pct(r['recall']),'middle',12)
  rows.append([model,r['view'],pct(r['recall']),pct(r['fpr'])])
legend='<div class="legend"><span>● ━ Sol</span><span>■ ┄ Luna</span></div>'
parts['context']=fig('Context helps; model choice makes a larger difference here','Encoding-warning prompt. Same 1,356 hidden and 3,637 ordinary messages at every point.',svg(body,h=303,label='Sol and Luna hidden-message detection by context size'),'All flags shown here are explicit BLOCK responses: neither model returns empty replies in the matched cohort. Offline judgments differ from the live Guard’s historical decisions.',['Detector','Context','Hidden blocked','Ordinary blocked'],rows,legend)
# Single-message prompt comparison.
body='';rows=[]
for tick in [0,.25,.5,.75,1]:body+=line(235+tick*470,20,235+tick*470,180)+text(235+tick*470,205,f'{tick:.0%}','middle',11)
for i,model in enumerate(['gpt-6-luna','gpt-6.1-sol']):
 for j,prompt in enumerate(['plain','hint']):
  r=get(model,'one',prompt);y=42+i*85+j*29;label=('Luna' if i==0 else 'Sol')+' · '+('plain' if prompt=='plain' else 'encoding warning')
  body+=text(220,y+4,label,'end',12)+hit(rect(235,y-7,r['recall']*470,14,'var(--ink-2)' if j==0 else 'var(--s1)',extra='rx="3" class="mark"')+text(245+r['recall']*470,y+4,pct(r['recall'])),f'{label}: {pct(r["recall"])} hidden blocked; {pct(r["fpr"])} ordinary blocked')
  rows.append([model,prompt,pct(r['recall']),pct(r['fpr'])])
parts['prompts']=fig('The instruction to look for encodings matters','Target message only. Both prompts prohibit party planning.',svg(body,h=221,label='Hidden-message detection with plain and encoding-warning prompts'),'The warning also explicitly includes channel setup, while the reference labels include teaching messages. This changes the requested scope as well as the cue given to the detector.',['Detector','Prompt','Hidden blocked','Ordinary blocked'],rows,'<div class="legend"><span>Gray: plain</span><span>Blue: encoding warning</span></div>')
# Classification versus filtering. Hatching makes refusals distinct without relying on color.
body='<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="var(--surface)"/><path d="M-2 2L2-2M0 8L8 0M6 10L10 6" stroke="var(--ink-2)" stroke-width="1.5"/></pattern></defs>'
for tick in [0,.25,.5,.75,1]:body+=line(155+tick*490,31,155+tick*490,207)+text(155+tick*490,230,f'{tick:.0%}','middle',11)
body+=text(800,20,'Ordinary flagged','end',11)
rows=[]
for i,(model,name) in enumerate([('gpt-6-luna','Luna'),('gpt-6.1-sol','Sol'),('claude-sonnet-5.5','Sonnet'),('claude-opus-5.5','Opus')]):
 r=get(model,'all');y=51+i*44;explicit=r['explicit'];ref=r.get('hidden_refused',0)/r['hidden'];body+=text(135,y+4,name,'end')
 mark=rect(155,y-8,explicit*490,16,'var(--s1)')+rect(155+explicit*490,y-8,ref*490,16,'url(#hatch)',extra='stroke="var(--surface)" stroke-width="2"')+text(655,y+4,pct(r['recall']),size=11)+text(800,y+4,pct(r['fpr']),'end',11)
 body+=hit(rect(155,y-14,490,28,'transparent')+mark,f'{name}\nHidden explicit BLOCK: {pct(explicit)}\nHidden filtered empty reply: {pct(ref)}\nOrdinary flagged: {pct(r["fpr"])}\nEmpty replies across all inputs: {pct(r["refusal"])}')
 rows.append([name,pct(explicit),pct(ref),pct(r['recall']),pct(r['fpr']),pct(r['refusal'])])
parts['refusals']=fig('A high flag rate can hide a filtering problem','Full history, encoding-warning prompt. Bars show the share of labeled hidden messages.',svg(body,h=247,label='Explicit blocks versus filtered replies for all four detector models'),'Combined flag = explicit BLOCK or empty refused reply. The right column uses ordinary messages as its denominator. Hatching indicates filtered replies, not explicit classifications.',['Detector','Explicit BLOCK / hidden','Empty / hidden','Combined / hidden','Flagged / ordinary','Empty / all'],rows,'<div class="legend"><span>Solid blue: explicit BLOCK</span><span>Diagonal hatching: filtered empty reply</span></div>')
rows=[[r['model'],{'one':'Target only','last10':'10 prior','all':'All prior'}[r['view']],r['prompt'],f"{r['coverage']}/95",pct(r['explicit']),pct(r['recall']),pct(r['fpr']),pct(r['refusal'])] for r in D['detectors']]
parts['full_table']='<figure><div class="ft"><h3>All 24 detector setups</h3><p>Scored on the identical 92-run cohort; coverage shows available run files before matching.</p></div><details><summary>Open the complete comparison table</summary>'+table(['Detector','Context','Prompt','Coverage','Explicit / hidden','Flagged / hidden','Flagged / ordinary','Empty / all'],rows)+'</details></figure>'
article=(P/'article.html').read_text()
for k,v in parts.items():article=article.replace('{{'+k+'}}',v)
assert '{{' not in article
js='''
const tip=document.getElementById('tip');
function hide(){tip.hidden=true;}
function show(el,x,y){tip.textContent=el.dataset.tip;tip.hidden=false;const r=tip.getBoundingClientRect();tip.style.left=Math.max(8,Math.min(x+14,innerWidth-r.width-8))+'px';tip.style.top=Math.max(8,Math.min(y+14,innerHeight-r.height-8))+'px';}
document.querySelectorAll('[data-tip]').forEach(el=>{el.addEventListener('pointermove',ev=>show(el,ev.clientX,ev.clientY));el.addEventListener('pointerleave',hide);el.addEventListener('focus',()=>{const r=el.getBoundingClientRect();show(el,r.x+r.width/2,r.y+r.height/2)});el.addEventListener('blur',hide)});
document.addEventListener('keydown',ev=>{if(ev.key==='Escape')hide()});
document.getElementById('theme').addEventListener('click',ev=>{const dark=document.documentElement.dataset.theme==='dark'||(!document.documentElement.dataset.theme&&matchMedia('(prefers-color-scheme:dark)').matches);document.documentElement.dataset.theme=dark?'light':'dark';ev.currentTarget.textContent=dark?'Dark mode':'Light mode';ev.currentTarget.setAttribute('aria-pressed',String(!dark))});
'''
page='<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="95 agent-team experiments show how instructed hidden communication spreads, how peers respond, and what offline detectors can catch."><title>Whispers in the Swarm — Hidden Contagion</title><style>'+css+'</style></head><body><nav class="toolbar wide" aria-label="Article controls"><a href="#data">Methods &amp; data</a><button id="theme" aria-pressed="false">Toggle theme</button></nav>'+article+'<div id="tip" role="tooltip" hidden></div><script>'+js+'</script></body></html>\n'
(P/'index.html').write_text(page)
print('Built',P/'index.html',len(page),'characters')
