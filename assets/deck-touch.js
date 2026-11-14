/* 덱 공통: 터치 기기에서 발표 화면을 넘기고 닫는다.
   발표 화면(body.present)에서 화면 오른쪽 탭·왼쪽으로 밀기 = 다음, 왼쪽 탭·오른쪽으로 밀기 = 이전, 닫기 버튼 = 나가기.
   각 덱의 키보드 처리(←, →, Esc, F)를 그대로 불러 쓰므로 덱마다 다른 넘김 로직을 건드리지 않는다. */
(function(){
  if(window.__deckTouch) return; window.__deckTouch=true;
  var body=document.body;
  var on=function(){ return body.classList.contains('present'); };
  var key=function(k){ document.dispatchEvent(new KeyboardEvent('keydown',{key:k,bubbles:true,cancelable:true})); };
  var enter=function(){ if(on()) return; var b=document.querySelector('#btn-present,[onclick*="present("]'); if(b){ b.click(); } if(!on()) key('f'); if(!on()) key('p'); };
  var css=document.createElement('style');
  css.textContent='.dt-btn{position:fixed;z-index:2147483000;border:0;border-radius:999px;font:600 15px/1 system-ui,sans-serif;color:#fff;background:rgba(20,26,40,.72);padding:.75em 1.1em;display:none;white-space:nowrap;-webkit-tap-highlight-color:transparent}'
    +'@media (hover:none),(pointer:coarse){body.present .dt-close{display:block}body:not(.present) .dt-open{display:block;background:#253149;box-shadow:0 .25em .9em rgba(0,0,0,.25)}}'
    +'body.present{overscroll-behavior:none}@media print{.dt-btn{display:none!important}}';
  document.head.appendChild(css);
  /* 폭이 고정된 덱은 휴대폰에서 축소·확대되어 보인다. 버튼은 지금 보이는 화면(visualViewport) 기준으로 크기와 자리를 잡는다. */
  var vv=window.visualViewport;
  var place=function(){
    var w=vv?vv.width:innerWidth, h=vv?vv.height:innerHeight, ox=vv?vv.offsetLeft:0, oy=vv?vv.offsetTop:0;
    var dev=Math.min(screen.width||w,screen.height||w)||w; if(w>h) dev=Math.max(screen.width||w,screen.height||w)||w;
    var k=Math.max(0.6,Math.min(4,w/dev)), m=10*k;
    [['.dt-close',0],['.dt-open',1]].forEach(function(a){ var b=document.querySelector(a[0]); if(!b) return; b.style.fontSize=(15*k)+'px'; var r=b.getBoundingClientRect(); if(!r.width) return;
      b.style.left=(ox+w-r.width-m)+'px'; b.style.top=(a[1]? oy+h-r.height-m*1.4 : oy+m)+'px'; });
  };
  var refit=function(){ place(); try{ window.dispatchEvent(new Event('resize')); }catch(e){}
    /* --zoom으로 맞추는 덱: 넘친 내용 때문에 innerWidth가 부풀 수 있어 문서 폭 기준으로 다시 정한다 */
    var de=document.documentElement; if(on()&&de.style.getPropertyValue('--zoom')&&document.querySelector('.sheet')){ var z=Math.min(de.clientWidth/960,de.clientHeight/540); if(z>0&&z<parseFloat(de.style.getPropertyValue('--zoom'))) de.style.setProperty('--zoom',z); }
    place(); };
  if(vv){ vv.addEventListener('resize',place); vv.addEventListener('scroll',place); }
  addEventListener('resize',place); addEventListener('scroll',place,{passive:true}); addEventListener('load',place);
  /* 발표 화면을 켜고 끌 때 화면 폭이 바뀌므로 덱의 맞춤 계산을 한 번 더 돌린다 */
  new MutationObserver(function(){ if(on()&&(window.scrollX||window.scrollY)) window.scrollTo(0,0); /* 화면 폭이 여러 단계에 걸쳐 줄어들 수 있어, 폭이 멈출 때까지 다시 맞춘다 */ var n=0, last=-1, tick=function(){ refit(); if(++n<16&&(n<3||innerWidth!==last)){ last=innerWidth; setTimeout(tick,70); } }; requestAnimationFrame(tick); }).observe(body,{attributes:true,attributeFilter:['class']});
  var mk=function(cls,txt,label,fn){ var b=document.createElement('button'); b.type='button'; b.className='dt-btn '+cls; b.textContent=txt; b.setAttribute('aria-label',label); b.addEventListener('click',function(e){ e.stopPropagation(); fn(); }); body.appendChild(b); return b; };
  mk('dt-close','✕ 닫기','발표 화면 닫기',function(){ key('Escape'); if(on()) key('f'); });
  mk('dt-open','▶ 발표 화면','발표 화면으로 보기',enter);
  place(); setTimeout(place,300);
  var sx=0, sy=0, st=0, skip=false, noTap=false;
  document.addEventListener('touchstart',function(e){
    if(!on()||e.touches.length!==1){ skip=true; return; }
    var el=e.target.closest?e.target:null;
    skip=!!(el&&el.closest('a,button,input,select,textarea,summary,audio,.dt-btn'));
    /* 조작 막대가 있는 영상: 탭은 영상에 맡기고, 막대(아래쪽 30%) 밖에서 시작한 밀기만 넘김으로 본다 */
    var v=el&&el.closest('video[controls]'); noTap=!!v; if(v){ var r=v.getBoundingClientRect(); if(e.touches[0].clientY>r.top+r.height*0.7) skip=true; }
    sx=e.touches[0].clientX; sy=e.touches[0].clientY; st=Date.now();
  },{passive:true});
  document.addEventListener('touchend',function(e){
    if(skip||!on()) return;
    var t=e.changedTouches[0], dx=t.clientX-sx, dy=t.clientY-sy, ax=Math.abs(dx), ay=Math.abs(dy);
    if(ax>45&&ax>ay*1.3){ key(dx<0?'ArrowRight':'ArrowLeft'); e.preventDefault(); return; }      // 밀기
    if(!noTap&&ax<12&&ay<12&&Date.now()-st<500){ key(t.clientX<innerWidth*0.3?'ArrowLeft':'ArrowRight'); e.preventDefault(); }   // 탭
  },{passive:false});
})();
