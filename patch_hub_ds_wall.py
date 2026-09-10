#!/usr/bin/env python3
"""HUB_DS_WALL - DATASTREAMERS minted out, so its section becomes a wall like Corrupted Pips.

- shared wall machinery, swappable id set (pips / ds)
- ds card 0 is the live renderer, the other 18 are stills
- ds detail panel goes sold out, Buy on OpenSea primary, mint + turnstile off the page
- lightbox is data driven so it can show either collection
- enables the .wall.open hover pop that the CSS always described but nothing ever switched on
"""
import io, sys, pathlib

P = pathlib.Path('index.html')
s = P.read_text(encoding='utf-8')

if 'HUB_DS_WALL' in s:
    print('already patched, nothing to do')
    sys.exit(0)

n = 0
def sub(old, new, label):
    global s, n
    if old not in s:
        print('ANCHOR MISS: ' + label)
        sys.exit(1)
    if s.count(old) != 1:
        print('ANCHOR NOT UNIQUE (%d): %s' % (s.count(old), label))
        sys.exit(1)
    s = s.replace(old, new, 1)
    n += 1

# ---------------------------------------------------------------- 1. CSS
sub(
"""  .work:hover .cap{opacity:1; transform:translateY(0);}""",
"""  .work:hover .cap{opacity:1; transform:translateY(0);}
  /* HUB_DS_WALL: same wall, DATASTREAMERS palette */
  .work iframe{width:100%; height:100%; border:0; display:block;}
  #wall.ds .work{border-color:var(--ds-edge);
    box-shadow:0 0 0 1px rgba(92,30,168,.55), 0 16px 44px rgba(0,0,0,.92);}
  #wall.ds .work .cap{background:var(--ds-edge);}
  #wall.ds.open .work:hover{border-color:var(--ds);
    box-shadow:0 26px 60px rgba(0,0,0,.7),
               0 0 50px rgba(180,76,255,.55), 0 0 90px rgba(0,0,0,.6);}
  .piece.ds .piece-info .pcol{color:var(--ds);}
  .piece.ds .piece-info .acts a.pri{background:var(--ds); border-color:var(--ds); color:#000;}
  .piece.ds .piece-info .acts a:hover{background:var(--ds-edge); border-color:var(--ds-edge); color:var(--bone);}""",
"css")

# ------------------------------------------------- 2. wall build becomes swappable
sub(
"""const nodes = WORKS.map(([x,y,s,id,rot], i) => {
  const d=document.createElement('div'); d.className='work';
  d.innerHTML=`<img src="${img(id)}" loading="lazy" alt="#${id}"><div class="cap">#${id}</div>`;
  d.onclick=()=>openPiece(i);
  wall.appendChild(d); return d;
});""",
"""/* HUB_DS_WALL: one wall, two collections. Geometry is shared, the id set swaps. */
const WALLSETS = {
  pips:{
    ids: WORKS.map(w=>w[3]),
    img: img, live:null, col:'Corrupted.Pips V3',
    rows:[['Chain','Ink Mainnet'],['Standard','ERC-721'],['Supply','3,210'],['Mint','Free']],
    acts: id=>[['Buy on OpenSea',`https://opensea.io/assets/ink/${V3.contract}/${id}`,true],
               ['View on Explorer',`${V3.explorer}/token/${V3.contract}/instance/${id}`,false]]
  },
  ds:{
    /* slot 0 is the biggest card and runs live. The rest are stills, picked for
       colour spread and for legibility at 100-170px. */
    ids:[630,934,39,833,133,29,311,973,114,67,157,737,167,286,987,666,326,860,6],
    img: dsImg, live: DS.liveUrl, col:'Datastreamers',
    rows:[['Chain','Ink Mainnet'],['Standard','ERC-721'],['Supply','1,000'],['Mint','Free']],
    acts: id=>[['Buy on OpenSea',`https://opensea.io/item/ink/${DS.contract}/${id}`,true],
               ['Read the paper',`${DS.paper}#/s/${id}`,false],
               ['View on Explorer',`${DS.explorer}/token/${DS.contract}/instance/${id}`,false]]
  }
};
let nodes = [], curWall = null;
function buildWall(key){
  if(curWall===key) return;
  curWall = key;
  const set = WALLSETS[key];
  wall.innerHTML = '';
  wall.classList.toggle('ds', key==='ds');
  nodes = WORKS.map(([x,y,s,,rot], i) => {
    const id = set.ids[i];
    const face = (i===0 && set.live)
      ? `<iframe src="${set.live}" loading="lazy" title="Live"></iframe>`
      : `<img src="${set.img(id)}" loading="lazy" alt="#${id}">`;
    const d=document.createElement('div'); d.className='work';
    d.innerHTML = `${face}<div class="cap">#${id}</div>`;
    d.onclick = ()=>openPiece(i);
    d.style.left=x+'px'; d.style.top=y+'px';
    d.style.width=s+'px'; d.style.height=s+'px';
    wall.appendChild(d); return d;
  });
  layoutStack();
}""",
"buildWall")

# precompute must not depend on nodes any more, it is pure geometry
sub(
"""  nodes.forEach((d,i)=>{
    const [x,y,s]=WORKS[i];
    const off=i===0?0:Math.min(22,4+i*1.1);""",
"""  WORKS.forEach((w,i)=>{
    const [x,y,s]=WORKS[i];
    const off=i===0?0:Math.min(22,4+i*1.1);""",
"precompute")

# geometry is written by buildWall now
sub(
"""/* geometry written once at startup */
(function setGeometry(){
  nodes.forEach((d,i)=>{
    const [x,y,s]=WORKS[i];
    d.style.left=x+'px'; d.style.top=y+'px';
    d.style.width=s+'px'; d.style.height=s+'px';
  });
})();

""",
"""/* geometry is written by buildWall, once per collection */

""",
"setGeometry")

sub(
"""function layoutStack(){
  nodes.forEach((d,i)=>{ d.style.transform = STACK_TF[i]; d.style.zIndex = 100-i; });
}""",
"""function layoutStack(){
  wall.classList.remove('open');
  nodes.forEach((d,i)=>{ d.style.transform = STACK_TF[i]; d.style.zIndex = 100-i; });
}""",
"layoutStack")

sub(
"""function layoutWall(){
  nodes.forEach((d,i)=>{
    d.style.transform = `translate3d(0,0,0) rotate(${WORKS[i][4]}deg) scale(1)`;
    d.style.zIndex = 10+(i%9);
  });
}
layoutStack();""",
"""function layoutWall(){
  wall.classList.add('open');
  nodes.forEach((d,i)=>{
    d.style.transform = `translate3d(0,0,0) rotate(${WORKS[i][4]}deg) scale(1)`;
    d.style.zIndex = 10+(i%9);
  });
}""",
"layoutWall")

# ------------------------------------------------- 3. detail record goes sold out
sub(
"""  ds: {
    title:['Data','streamers'],
    sub:'Free mint · Ink Mainnet',
    body:'Something in the simulation failed. The gravity is still correct. Everything else is falling in.',
    rows:[['Supply','1,000'],['Minted','<span id="ds-minted">—</span>'],['Mint','Free · 1 per wallet'],['Pips holders','Free · 2 per wallet']],
    acts:[
      ['Mint','js:mintDS',true],
      ['Read the paper','#paper',false],
      ['View on OpenSea','#opensea',false],
      ['Contract','#contract',false]
    ]
  },""",
"""  ds: {
    title:['Data','streamers'],
    sub:'Sold Out · Ink Mainnet',
    body:'1,000 black holes, minted out in a night. Something in the simulation failed. The gravity is still correct. Everything else is falling in.',
    rows:[['Supply','1,000'],['Mint','Free'],['Standard','ERC-721'],
          ['Contract','<span class="code">0xd0bd…2C386</span>']],
    acts:[
      ['Buy on OpenSea','#opensea',true],
      ['Read the paper','#paper',false],
      ['Contract','#contract',false]
    ]
  },""",
"ds record")

# turnstile mount point in the panel is gone with the mint button
sub(
"""  }).join('') + (key==='ds' ? '<div id="ds-turnstile-m" style="margin-top:8px"></div>' : '');""",
"""  }).join('');""",
"turnstile mount")

# ------------------------------------------------- 4. openDS drives the wall
sub(
"""function openDS(){
  const reentry = onWall;
  onWall = true;
  holdGlitch(700);
  renderDetail('ds');
  markActive('ds');
  $('detail').classList.add('ds'); $('detail').classList.remove('pp');
  const box=$('ds-box');
  box.innerHTML = DS.liveUrl
    ? `<iframe src="${DS.liveUrl}" allow="autoplay" loading="lazy"></iframe>`
    : `<img class="teaser" src="${dsFace()}" alt="Datastreamers">`;
  $('home').classList.add('gone');
  $('wall-stage').classList.remove('live');
  $('soon-stage').classList.remove('live');
  $('ds-stage').classList.add('live');
  $('detail').classList.add('live');
  refreshDS(); dsStartPoll(); setTimeout(dsMountTurnstile, 50);
  fx(()=>{ SFX.open(); AMBIENT.duck(1.1); });
  setTimeout(()=>fx(()=>{ fireSweep(); if(!reentry) fireTear(); stampBlocks(5); }), 700);
}""",
"""function openDS(){ /* HUB_DS_WALL: minted out, so it gets the wall */
  const reentry = onWall;
  onWall = true;
  holdGlitch(820);
  renderDetail('ds');
  markActive('ds');
  $('detail').classList.add('ds'); $('detail').classList.remove('pp');
  $('home').classList.add('gone');
  $('soon-stage').classList.remove('live');
  $('ds-stage').classList.remove('live');
  buildWall('ds');
  $('wall-stage').classList.add('live');
  $('detail').classList.add('live');
  render();
  requestAnimationFrame(()=>requestAnimationFrame(()=>{ layoutWall(); }));
  setTimeout(render, 800);
  fx(()=>{ SFX.open(); AMBIENT.duck(1.1); });
  setTimeout(()=>fx(()=>{ fireSweep(); if(!reentry) fireTear(); stampBlocks(6); }), 780);
}""",
"openDS")

sub(
"""  renderDetail('pips');
  $('detail').classList.remove('ds'); $('detail').classList.remove('pp');
  $('soon-stage').classList.remove('live');
  $('ds-stage').classList.remove('live');
  $('home').classList.add('gone');
  $('wall-stage').classList.add('live');
  $('detail').classList.add('live');
  if(!reentry) layoutStack();
  render();""",
"""  renderDetail('pips');
  $('detail').classList.remove('ds'); $('detail').classList.remove('pp');
  $('soon-stage').classList.remove('live');
  $('ds-stage').classList.remove('live');
  $('home').classList.add('gone');
  buildWall('pips');
  $('wall-stage').classList.add('live');
  $('detail').classList.add('live');
  if(!reentry) layoutStack();
  render();""",
"openWall")

# ------------------------------------------------- 5. lightbox is data driven
sub(
"""      <div class="pcol">Corrupted.Pips V3</div>
      <dl>
        <dt>Chain</dt><dd>Ink Mainnet</dd>
        <dt>Standard</dt><dd>ERC-721</dd>
        <dt>Supply</dt><dd>3,210</dd>
        <dt>Mint</dt><dd>Free</dd>
      </dl>
      <div class="acts">
        <a class="pri" id="pc-os" href="#" target="_blank" rel="noopener">Buy on OpenSea</a>
        <a id="pc-scan" href="#" target="_blank" rel="noopener">View on Explorer</a>
      </div>""",
"""      <div class="pcol" id="pc-col">Corrupted.Pips V3</div>
      <dl id="pc-dl"></dl>
      <div class="acts" id="pc-acts"></div>""",
"lightbox html")

sub(
"""function openPiece(i){
  if(moved) return;
  cur=((i%WORKS.length)+WORKS.length)%WORKS.length;
  const id=WORKS[cur][3];
  $('pc-img').src = img(id);
  $('pc-id').textContent='#'+id;
  $('pc-os').href=`https://opensea.io/assets/ink/${V3.contract}/${id}`;
  $('pc-scan').href=`${V3.explorer}/token/${V3.contract}/instance/${id}`;
  const p=$('piece'); p.classList.remove('open'); void p.offsetWidth; p.classList.add('open');
  fx(()=>stampBlocks(4));
}""",
"""function openPiece(i){ /* HUB_DS_WALL: reads whichever collection the wall is showing */
  if(moved) return;
  const set = WALLSETS[curWall] || WALLSETS.pips;
  cur=((i%WORKS.length)+WORKS.length)%WORKS.length;
  const id=set.ids[cur];
  $('pc-img').src = set.img(id);
  $('pc-id').textContent='#'+id;
  $('pc-col').textContent=set.col;
  $('pc-dl').innerHTML=set.rows.map(([k,v])=>`<dt>${k}</dt><dd>${v}</dd>`).join('');
  $('pc-acts').innerHTML=set.acts(id).map(([t,u,pri])=>
    `<a class="${pri?'pri':''}" href="${u}" target="_blank" rel="noopener">${t}</a>`).join('');
  const p=$('piece');
  p.classList.toggle('ds', curWall==='ds');
  p.classList.remove('open'); void p.offsetWidth; p.classList.add('open');
  fx(()=>stampBlocks(4));
}""",
"openPiece")

# ------------------------------------------------- 6. labels
sub(
"""<div class="st" id="cl-ds-st">Live · Ink</div>""",
"""<div class="st" id="cl-ds-st">Sold Out · Ink</div>""",
"drawer label")

sub(
"""  <div class="cs-lbl">Live · Free mint</div>`;""",
"""  <div class="cs-lbl">Sold out</div>`;""",
"home tile label")

P.write_text(s, encoding='utf-8')
print('HUB_DS_WALL applied, %d replacements' % n)
