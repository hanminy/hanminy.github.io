/* 발표 뷰 — F: 발표 모드 전환, →/PageDown/Space: 다음, ←/PageUp: 이전, Home/End: 처음/끝, Esc: 종료
   ?slide=N : N번 슬라이드에서 발표 모드로 시작 (FES2026 v2 덱과 같은 동작) */
(()=>{
  const slides=[...document.querySelectorAll('.slide')];
  let i=0,on=false;
  const badge=document.createElement('div');badge.className='navbadge';document.body.appendChild(badge);
  function fit(){const s=Math.min(innerWidth/960,innerHeight/540);document.documentElement.style.setProperty('--fit',s)}
  function show(){slides.forEach((el,k)=>el.classList.toggle('on',k===i));badge.textContent=(i+1)+' / '+slides.length}
  function go(n){i=Math.max(0,Math.min(slides.length-1,n));show()}
  const q=new URLSearchParams(location.search).get('slide');
  if(q){i=Math.max(0,Math.min(slides.length-1,parseInt(q,10)-1));on=true;document.body.classList.add('present');fit();show()}
  addEventListener('keydown',e=>{
    if(e.key==='f'||e.key==='F'){on=!on;document.body.classList.toggle('present',on);fit();show();return}
    if(!on)return;
    if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){go(i+1);e.preventDefault()}
    else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){go(i-1);e.preventDefault()}
    else if(e.key==='Home'){go(0);e.preventDefault()}
    else if(e.key==='End'){go(slides.length-1);e.preventDefault()}
    else if(e.key==='Escape'){on=false;document.body.classList.remove('present')}
  });
  addEventListener('resize',fit);
  window.__deck={count:()=>slides.length,index:()=>i,isPresent:()=>on};
})();
