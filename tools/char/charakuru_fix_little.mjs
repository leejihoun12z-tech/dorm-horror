// 손가락이 3개뿐인 손: 허공에 뜬 새끼손가락 뼈를 약지 뼈 옆(같은 손가락 살 안)으로 옮긴다.
import fs from 'node:fs/promises';
import path from 'node:path';
const kit='file:///C:/Users/leeji/ck/kit/charakuru/';
const {writeProject,digest}=await import(kit+'scripts/project-write.mjs');
const {unpackProject,packProject}=await import(kit+'public/project.mjs');
const input=process.argv[2];
const original=await fs.readFile(input),{project:p,files}=await unpackProject(original);
const by=Object.fromEntries(p.rigGuide.bones.map(b=>[b.name,b]));
let n=0;
for(const side of ['L','R'])for(const k of ['1','2','3']){
  const little=by[`J_Bip_${side}_Little${k}`],ring=by[`J_Bip_${side}_Ring${k}`];
  if(!little||!ring)throw Error('bone missing '+side+k);
  const off=[0,0.004,0];
  little.head=ring.head.map((v,i)=>v+off[i]);little.tail=ring.tail.map((v,i)=>v+off[i]);little.rollAxis=[...ring.rollAxis];n++;
}
const result=await packProject(p,files);
await writeProject(input,new Uint8Array(await result.blob.arrayBuffer()),{input,expected:digest(original)});
console.log(JSON.stringify({moved:n,names:p.rigGuide.bones.filter(b=>/Little|Ring/.test(b.name)).map(b=>[b.name,b.head.map(v=>+v.toFixed(3))])}));
