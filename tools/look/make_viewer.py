"""룩 탐색 결과를 크게 보는 페이지(index.html)를 만든다. 화풍 버튼 → 보기(줄) × 낮·후반 낮·밤(칸), 그림 누르면 화면 가득, ←→ 넘기기, Esc 닫기.

  python tools/look/make_viewer.py "<ComfyUI>/output/dorm_look_states"
  → 그 폴더에서 python -m http.server 8765 → http://127.0.0.1:8765/
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
	folder = Path(sys.argv[1])
	cfg = json.loads((HERE / "looks.json").read_text(encoding="utf-8"))
	states = cfg["states"]
	data = []
	for st in cfg["styles"]:
		rows = []
		for sp in cfg["spaces"]:
			cells = []
			for s in states:
				fs = sorted(folder.glob(f"{sp}_{st['id']}_{s['id']}_*.png"))
				cells.append(fs[-1].name if fs else "")
			if any(cells):
				rows.append({"space": sp, "cells": cells})
		if rows:
			data.append({"id": st["id"], "name": st["name"], "rows": rows})
	page = PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__STATES__", json.dumps([s["name"] for s in states], ensure_ascii=False))
	(folder / "index.html").write_text(page, encoding="utf-8")
	print(folder / "index.html", f"화풍 {len(data)}개")


PAGE = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>룩 탐색 — 낮·후반 낮·밤</title>
<style>
body{margin:0;background:#111014;color:#eee;font-family:'Malgun Gothic',sans-serif}
#tabs{position:sticky;top:0;background:#1b1a20;padding:10px;display:flex;flex-wrap:wrap;gap:6px;z-index:2}
#tabs button{background:#2a2930;color:#eee;border:1px solid #444;border-radius:6px;padding:8px 12px;font-size:15px;cursor:pointer}
#tabs button.on{background:#e8c35a;color:#111;border-color:#e8c35a}
h2{margin:14px 12px 4px;font-size:20px}
.row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:0 10px 18px}
.cell div{font-size:14px;color:#bbb;margin:2px 0 4px}
.cell img{width:100%;display:block;border-radius:4px;cursor:zoom-in}
#big{position:fixed;inset:0;background:#000e;display:none;flex-direction:column;align-items:center;justify-content:center;z-index:9}
#big img{max-width:98vw;max-height:90vh}
#big p{margin:8px;font-size:16px}
</style></head><body>
<div id="tabs"></div><div id="main"></div>
<div id="big" onclick="hide()"><img id="bigimg"><p id="cap"></p></div>
<script>
const D=__DATA__, S=__STATES__; let cur=0, flat=[], idx=0;
function show(i){cur=i;document.querySelectorAll('#tabs button').forEach((b,j)=>b.className=j==i?'on':'');
 const st=D[i]; flat=[]; let h='<h2>'+st.id+' '+st.name+'</h2>';
 st.rows.forEach(r=>{h+='<div class="row">';r.cells.forEach((c,k)=>{const n=flat.length;flat.push([c,r.space+' · '+S[k]]);
  h+='<div class="cell"><div>'+r.space+' · '+S[k]+'</div>'+(c?'<img loading="lazy" src="'+c+'" onclick="open_(event,'+n+')">':'<div>(없음)</div>')+'</div>'});h+='</div>'});
 document.getElementById('main').innerHTML=h;window.scrollTo(0,0)}
function open_(e,n){e.stopPropagation();idx=n;draw();document.getElementById('big').style.display='flex'}
function draw(){const [c,t]=flat[idx];document.getElementById('bigimg').src=c;document.getElementById('cap').textContent=D[cur].id+' '+D[cur].name+' — '+t+'   (←→ 넘기기 · ↑↓ 화풍 · Esc 닫기)'}
function hide(){document.getElementById('big').style.display='none'}
document.onkeydown=e=>{const open=document.getElementById('big').style.display=='flex';
 if(e.key=='Escape')hide();
 else if(open&&e.key=='ArrowRight'){idx=(idx+1)%flat.length;draw()}
 else if(open&&e.key=='ArrowLeft'){idx=(idx+flat.length-1)%flat.length;draw()}
 else if(e.key=='ArrowDown'||e.key=='ArrowUp'){const k=idx;show((cur+(e.key=='ArrowDown'?1:D.length-1))%D.length);if(open){idx=Math.min(k,flat.length-1);draw()}e.preventDefault()}};
D.forEach((st,i)=>{const b=document.createElement('button');b.textContent=st.id.split('_')[0]+' '+st.name;b.onclick=()=>show(i);document.getElementById('tabs').appendChild(b)});
show(0);
</script></body></html>"""

if __name__ == "__main__":
	main()
