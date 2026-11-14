import re, html
SRC='/home/claude/hanminy.github.io/assets/sjtu-excavator-vla/index.html'
OUT='/home/claude/hanminy.github.io/assets/vla-talk-20261114/index.html'
src=open(SRC,encoding='utf-8').read()
style=src[src.find('<style>'):src.find('</style>')]
script=src[src.rfind('<script>'):src.rfind('</script>')+9]
cover_art=re.search(r'<svg class="cover-art".*?</svg>',src,re.S).group(0)
# 소리 있는 요약 영상은 자동 음소거·반복에서 제외
script=script.replace("const videos=[...s.querySelectorAll('video')];","const videos=[...s.querySelectorAll('video:not([data-sound])')];")
script=script.replace("document.querySelectorAll('video').forEach(v=>{if(!s.contains(v))v.pause()});","document.querySelectorAll('video').forEach(v=>{if(!s.contains(v))v.pause()});")
script=script.replace("document.querySelectorAll('video').forEach(v=>{v.addEventListener('click'","document.querySelectorAll('video:not([data-sound])').forEach(v=>{v.addEventListener('click'")
extra='''
.fig text{font-family:Freesentation,sans-serif}
.media.clip{grid-template-columns:560px 1fr;gap:22px}.media.clip video,.media.clip img{border-radius:8px;background:#000}
.media.clip aside li{margin-bottom:16px;font-size:19px}
.bigvideo{height:100%;display:grid;place-items:center}.bigvideo video,.bigvideo img{height:368px;aspect-ratio:16/9;border-radius:8px;background:#000}
.bigvideo .print-poster{display:none}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;height:100%;align-items:center}
.metrics article{border:1px solid #d9dde3;border-top:8px solid var(--color);border-radius:6px;padding:18px 14px;text-align:center;min-height:250px}
.metrics{align-items:stretch;padding:40px 0}.metrics b{white-space:nowrap;display:block;font-size:38px;font-weight:800;color:var(--color);margin:26px 0 12px;letter-spacing:-1px}
.metrics strong{display:block;font-size:21px;margin-bottom:10px}.metrics span{font-size:17px;color:#595959;line-height:1.4;display:block}
.srcs{font-size:16px;columns:2;column-gap:34px}.srcs p{margin:0 0 10px;break-inside:avoid;line-height:1.4}.srcs b{color:var(--color)}
'''
SEC={1:('요약','한눈에<br>보기','#3d52ad','#253667'),2:('계보','어떤 모델이<br>있나','#31a17e','#245e4f'),3:('구조','안은 어떻게<br>생겼나','#54833d','#365126'),
     4:('굴착기','어떻게<br>맞추나','#b0601e','#6e3a10'),5:('필드로봇','여러 장비를<br>한 모델로','#6a1b3e','#431129'),6:('데이터','모으고<br>내다보기','#3d52ad','#253667')}
slides=[]
def sheet(sec,title,key,content,wide=False,foot=''):
    n=len(slides)+1; name,small,c,d=SEC[sec]
    side='' if wide else f'<div class="sidebar"><b>{sec:02d}</b><strong>{name}</strong><small>{small}</small></div>'
    f=f'<div class="foot">{foot}</div>' if foot else ''
    slides.append(f'<section class="sheet {"wide" if wide else ""}" id="slide-{n}" style="--color:{c};--deep:{d}">{side}<h2 class="title">{title}</h2><img class="logo" src="assets/kimm_logo.png" alt="KIMM"><div class="keybar"><span>{key}</span></div><div class="content">{content}</div>{f}<div class="page">{n:02d}</div></section>')
# ---------- svg helpers ----------
def R(x,y,w,h,fill='none',stroke='none',rx=8,sw=2,extra=''): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'
def T(x,y,s,size=18,fill='#1a1a1a',w=600,a='middle'): return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{a}">{s}</text>'
def A(x1,y1,x2,y2,color='#253149',sw=2.5,dash=''): 
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" marker-end="url(#ah-{color[1:]})"{d}/>'
def L(x1,y1,x2,y2,color='#253149',sw=2,dash=''):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>'
def C(x,y,r,fill='none',stroke='none',sw=2): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
COLS=['#253149','#3d52ad','#31a17e','#54833d','#b0601e','#6a1b3e','#d6336c','#8a93a0']
_svgn=[0]
def SVG(body,w=790,h=368):
    _svgn[0]+=1; k=_svgn[0]
    defs=''.join(f'<marker id="ah{k}-{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for c in COLS)
    return f'<svg class="fig" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body.replace("url(#ah-",f"url(#ah{k}-")}</svg>'
NAVY,BLUE,TEAL,GREEN,ORG,MAR,PINK,GRAY=COLS
def chip(x,y,w,s,fill,fg='#fff',h=38,size=17,sub=''):
    o=R(x,y,w,h,fill,rx=h/2)+T(x+w/2,y+h/2+6,s,size,fg,700)
    return o
def clip(name,items):
    lis=''.join(f'<li>{i}</li>' for i in items)
    return f'<div class="media clip"><figure><video src="assets/clips/{name}.mp4" poster="assets/clips/{name}.jpg" muted loop playsinline preload="metadata"></video><img class="print-poster" src="assets/clips/{name}.jpg" alt=""></figure><aside><ul>{lis}</ul></aside></div>'

# ---------- 1 cover ----------
slides.append(f'<section class="sheet wide" id="slide-1" style="--color:#3d52ad;--deep:#253667">{cover_art}<div class="covercopy"><small>VLA 대화 정리 · 음성 세션</small><h1>VLA, 구조에서<br>굴착기 적용까지</h1><p>계보와 구조를 짚고, 굴착기와 필드로봇에 어떻게 맞출지 정리</p><span>2026.11.14<br>이한민 · hmlee@kimm.re.kr</span></div><div class="page">01</div></section>')
# ---------- 2 flow ----------
sheet(1,'전체 흐름','구조를 이해하고 <em>굴착기에 맞추는 순서</em>를 정한다',
 '<div class="flow five"><div><b>01</b><strong>계보</strong><span>쓸 수 있는 모델 · 세 단계의 변화</span></div><div><b>02</b><strong>구조</strong><span>한 박자와 분리 · GR00T와 π0</span></div><div><b>03</b><strong>굴착기</strong><span>동기식 먼저 · 지형 정보 넣기</span></div><div><b>04</b><strong>필드로봇</strong><span>본체 하나 · 장비별 모듈</span></div><div><b>05</b><strong>데이터</strong><span>월드 모델 · 영상에서 행동</span></div></div>',wide=True)
# ---------- 3 full video ----------
sheet(1,'3분 요약 영상','손그림으로 보는 <em>구조와 굴착기 적용</em> · 소리 있음',
 '<div class="bigvideo"><video src="assets/vla-tori-techtalk.mp4" poster="assets/clips/cover.jpg" controls playsinline preload="metadata" data-sound></video><img class="print-poster" src="assets/clips/cover.jpg" alt=""></div>')
# ---------- 4 landscape ----------
b=R(0,0,505,368,'#f4f8f5',TEAL,10)+T(20,32,'가중치 공개 · 직접 파인튜닝',20,TEAL,800,'start')
b+=R(22,52,225,92,'#fff',ORG,10,3)+T(134,90,'GR00T N1.7',26,NAVY,800)+T(134,122,'3B · 상업 사용 가능',16,'#595959',500)
b+=R(262,52,225,92,'#fff',ORG,10,3)+T(374,90,'π0 · π0.5',26,NAVY,800)+T(374,122,'openpi · 이후 버전은 비공개',16,'#595959',500)
b+=chip(170,152,170,'우리 후보 두 축',ORG,h=30,size=15)
for i,(n,s) in enumerate([('X-VLA','0.9B · 소프트 프롬프트'),('OpenVLA','7B · 행동 토큰'),('SmolVLA','0.45B · 빠른 실험'),('MolmoAct','경로를 먼저 그림'),('InternVLA-M1','공간 그라운딩'),('RoboDual','이중 시스템 참고')]):
    x=22+(i%3)*157; y=200+(i//3)*82
    b+=R(x,y,147,70,'#fff','#b9d8cb',8)+T(x+73,y+29,n,19,NAVY,700)+T(x+73,y+53,s,14,'#595959',500)
b+=R(525,0,265,368,'#f6f4f7',MAR,10)+T(545,32,'비공개 · API만',20,MAR,800,'start')
for i,(n,s) in enumerate([('Gemini Robotics 2','VLA 본체 · 협력사만'),('Gemini Robotics-ER 2','추론 모델 · API로 사용'),('Helix · Helix 02','논문·가중치 없음')]):
    y=52+i*102
    b+=R(543,y,229,86,'#fff','#d9c3cf',8)+T(657,y+36,n,20,NAVY,700)+T(657,y+62,s,15,'#595959',500)
sheet(2,'1. 지금 쓸 수 있는 VLA','직접 고쳐 쓸 수 있는 건 <em>GR00T N1.7과 π0.5</em>까지',SVG(b),foot='2026년 11월 검색 기준 · Gemini Robotics 2는 2026.7.30 발표')
# ---------- 5 three stages ----------
b=''
cols=[(125,'RT-2',BLUE,'행동을 토큰으로','한 모델 · 수 Hz'),(395,'π0 · GR00T',GREEN,'VLM + 액션 헤드','연속 청크 · 실행 50 Hz'),(665,'Helix',MAR,'생각과 반사를 분리','S2 7~9 Hz · S1 200 Hz')]
for x,n,c,s1,s2 in cols:
    b+=R(x-120,0,240,368,'#fff','#d9dde3',10)+R(x-120,0,240,48,c,rx=10)+R(x-120,30,240,18,c,rx=0)+T(x,33,n,23,'#fff',800)
    b+=T(x,318,s1,20,NAVY,700)+T(x,346,s2,16,'#595959',500)
x=125; b+=R(x-80,75,160,90,BLUE)+T(x,128,'VLM',26,'#fff',800)+A(x,165,x,198,NAVY)
for i,d in enumerate(['1','127','91','8','42']): b+=R(x-98+i*40,205,34,34,'#e8ecf8',BLUE,5)+T(x-81+i*40,228,d,14,BLUE,700)
b+=T(x,270,'한 스텝씩 토큰으로',15,'#595959',500)
x=395; b+=R(x-100,75,92,90,BLUE)+T(x-54,128,'VLM',22,'#fff',800)+R(x+8,75,92,90,GREEN)+T(x+54,118,'액션',20,'#fff',800)+T(x+54,142,'헤드',20,'#fff',800)
for i in range(4): b+=L(x-8,90+i*20,x+8,90+i*20,'#8a93a0',2)
b+=A(x+54,165,x+54,198,NAVY)+f'<path d="M{x-95} 235 C{x-60} 195,{x-30} 265,{x} 228 S{x+60} 200,{x+95} 232" fill="none" stroke="{ORG}" stroke-width="4"/>'+T(x,270,'동작 수십 개 묶음',15,'#595959',500)
x=665; b+=R(x-90,68,180,58,BLUE)+T(x,104,'시스템 2 · 느리게',18,'#fff',700)+A(x,126,x,170,PINK,3)+C(x,148,7,PINK)+R(x-90,174,180,58,GREEN)+T(x,210,'시스템 1 · 빠르게',18,'#fff',700)
for i in range(19): b+=L(x-90+i*10,246,x-90+i*10,262,GREEN,3)
b+=T(x,286,'잠재 벡터 하나로 연결',15,'#595959',500)
b+=A(248,184,272,184,NAVY,3)+A(518,184,542,184,NAVY,3)
sheet(2,'2. 세 단계의 변화','보는 눈과 움직이는 손이 <em>점점 떨어진다</em>',SVG(b))
# ---------- 6 clip b3 ----------
sheet(3,'3. 두 부분과 청크','이해하는 모델 + 움직임을 만드는 모델 → <em>동작 묶음(청크)</em>',clip('b3',['<b>앞</b> · 영상과 지시문을 이해하는 VLM','<b>뒤</b> · 플로우 매칭으로 행동 생성','한 번에 16~50스텝을 묶어 출력']))
# ---------- 7 clip b4 ----------
sheet(3,'4. 한 박자 vs 생각·반사 분리','π0는 <em>청크</em>로, Helix는 <em>모듈 분리</em>로 속도 차를 만든다',clip('b4',['<b>한 박자(π0)</b> · 추론 수 Hz, 청크 실행 50 Hz','실행 중에는 새 관측을 못 봄','<b>분리(Helix)</b> · S2 7~9 Hz, S1 200 Hz','S1은 자기 눈으로 최신 영상을 봄']))
# ---------- 8 GR00T vs pi0 ----------
b=T(190,24,'π0 · 한 몸',22,BLUE,800)+T(600,24,'GR00T · 떼어 낸 구조',22,GREEN,800)
for i in range(9):
    y=42+i*24
    b+=R(70,y,100,18,'#dfe5f6',BLUE,4,1.5)+R(210,y,100,18,'#e3efdc',GREEN,4,1.5)+L(170,y+9,210,y+9,ORG,2.5)
b+=T(120,274,'VLM',16,BLUE,700)+T(260,274,'액션 전문가',16,GREEN,700)+R(56,34,268,222,'none','#8a93a0',10,1.5,'stroke-dasharray="6 5"')
for i in range(9):
    y=42+i*24; hi=(i==4)
    b+=R(470,y,100,18,'#ffd43b' if hi else '#dfe5f6',BLUE,4,1.5)
b+=T(520,274,'VLM',16,BLUE,700)
for i in range(5): b+=R(650,70+i*34,120,26,'#e3efdc',GREEN,4,1.5)
b+=T(710,274,'DiT',16,GREEN,700)+A(570,147,646,147,ORG,4)
b+=L(395,34,395,290,'#d9dde3',2)
for i,(l,r) in enumerate([('모든 층의 K·V를 공유','중간층 출력 토큰 하나'),('두 트랜스포머 구조가 같음','DiT를 따로 설계'),('입출력 공용 32칸','장비별 전용 모듈')]):
    y=298+i*24
    b+=T(190,y+14,l,17,NAVY,600)+T(600,y+14,r,17,NAVY,600)+C(395,y+9,10,NAVY)+T(395,y+14,str(i+1),13,'#fff',700)
sheet(3,'5. GR00T와 π0의 구조 차이','가장 근본은 <em>묶느냐, 떼느냐</em> · 떼어 낸 쪽이 비동기로 바꾸기 쉽다',SVG(b))
# ---------- 9 conditioning ----------
b=''
pan=[(125,'토큰으로 붙이기','작은 벡터 하나','Helix'),(395,'크로스 어텐션','공간 구조가 있는 큰 정보','π0 · GR00T'),(665,'adaLN','요약 벡터로 층을 조절','DiT · DigNet')]
for x,n,s1,s2 in pan:
    b+=R(x-120,0,240,368,'#fff','#d9dde3',10)+T(x,36,n,23,GREEN,800)+T(x,316,s1,18,NAVY,700)+chip(x-60,330,120,s2,'#eef3eb',GREEN,30,15)
x=125
for i in range(5): b+=R(x-108+i*37,130,30,44,'#dfe5f6',BLUE,5,1.5)
b+=R(x-108+5*37-2,126,34,52,PINK,rx=5)+T(x,215,'같은 줄에 서서 함께 섞임',15,'#595959',500)
x=395
for i in range(6): b+=R(x-105+i*36,80,28,36,'#dfe5f6',BLUE,5,1.5)
for i in range(4): b+=R(x-70+i*38,200,30,40,'#e3efdc',GREEN,5,1.5)
for i in range(4):
    for j in (i,i+1,i+2): b+=L(x-55+i*38,200,x-91+j*36,116,ORG,1.5)
b+=T(x,66,'VLM 토큰 (고정)',15,'#595959',500)+T(x,262,'행동 토큰이 필요한 곳을 꺼내 봄',15,'#595959',500)
x=665
b+=R(x-100,120,46,60,PINK,rx=6)+T(x-77,157,'z',22,'#fff',800)+A(x-52,150,x-14,150,NAVY)
for i in range(4): b+=R(x-8,84+i*36,100,26,'#e3efdc',GREEN,5,1.5)+C(x+104,97+i*36,7,ORG)
b+=T(x,262,'층마다 크기·이동 값을 조절',15,'#595959',500)
sheet(3,'6. 조건을 넣는 세 가지 방법','기준은 크기보다 <em>공간 구조가 있느냐</em>',SVG(b))
# ---------- 10 clip b5 ----------
sheet(4,'7. 굴착기는 동기식 먼저','박힘·튐이 보이면 그때 <em>압력을 느끼는 빠른 모델</em>을 붙인다',clip('b5',['<b>주력 GR00T</b>, 비교 기준 π0.5','청크를 10~15스텝만 쓰고 다시 계획','반응이 늦으면 비동기 S1 또는 잔차 RL','3.5톤 장비 · 단단한 흙이 시험대']))
# ---------- 11 control rate ----------
b=''
tiers=[('VLA','20~50 Hz','실린더 속도·목표 위치',BLUE),('서보 제어기','100 Hz+','밸브 전류',TEAL),('유압 밸브 · 실린더','대역폭 수 Hz','지연 수십~백 ms',ORG)]
for i,(n,hz,s,c) in enumerate(tiers):
    y=14+i*120
    b+=R(0,y,400,92,c,rx=10)+T(24,y+40,n,24,'#fff',800,'start')+T(24,y+70,s,16,'#fff',500,'start')+T(380,y+56,hz,26,'#ffff6c',800,'end')
    if i<2: b+=A(200,y+92,200,y+118,NAVY,3)
    n_t=[6,14,3][i]
b+=R(440,14,350,150,'#f4f6f8','#d9dde3',10)+T(615,62,'제어 주기',20,'#595959',600)+T(615,112,'대역폭 × 5~10',40,NAVY,800)+T(615,146,'나이퀴스트 2배는 최소일 뿐',16,'#595959',500)
b+=R(440,184,168,170,'#fff','#d9dde3',10)+T(524,222,'10배',22,BLUE,800)+T(524,280,'18°',50,BLUE,800)+T(524,326,'위상 지연',17,'#595959',500)
b+=R(622,184,168,170,'#fff','#d9dde3',10)+T(706,222,'5배',22,PINK,800)+T(706,280,'36°',50,PINK,800)+T(706,326,'위상 지연',17,'#595959',500)
sheet(4,'8. 제어 주기를 정하는 기준','VLA는 <em>20~50 Hz</em>면 충분 · 추론 지연도 위상 지연에 넣어 계산',SVG(b),foot='위상 지연은 반 주기 지연(영차 홀드) 기준 · 정확한 값은 시뮬레이터 유압 모델의 응답 시간을 재서 정함')
# ---------- 12 clip b6 ----------
sheet(4,'9. 땅의 높낮이를 넣는 법','감독(VLM)에는 <em>차이 맵</em>, 실무자(액션)에는 <em>버킷 주변 점군</em>',clip('b6',['라이다 점군 → 2D 높이맵 → 차이 맵','지형은 2.5D라 높이맵으로도 손실이 적음','점군은 버킷·장비 기준 좌표로 잘라서','색 범위는 반드시 고정']))
# ---------- 13 matrix ----------
b=''
cx=[330,490,650]; cw=150; ry=[84,164,244]; rh=70
for i,n in enumerate(['2D 높이맵 이미지','CNN 토큰','점군 인코더']): b+=R(cx[i]-cw/2,20,cw,48,ORG,rx=8)+T(cx[i],51,n,18,'#fff',700)
for j,n in enumerate(['VLM (감독)','액션 엑스퍼트 (실무자)','둘 다']): b+=R(0,ry[j],236,rh,NAVY,rx=8)+T(118,ry[j]+42,n,19,'#fff',700)
mark={(0,0):('① 기본안','#fdf1e3',ORG),(1,1):('② 따로 넣기','#fdf1e3',ORG),(1,2):('③ 점군 그대로','#fdf1e3',ORG)}
for j in range(3):
    for i in range(3):
        m=mark.get((j,i))
        if j==2: continue
        if m: b+=R(cx[i]-cw/2,ry[j],cw,rh,m[1],m[2],8,2.5)+T(cx[i],ry[j]+42,m[0],18,m[2],800)
        else: b+=R(cx[i]-cw/2,ry[j],cw,rh,'#f4f6f8','#d9dde3',8)+T(cx[i],ry[j]+42,'–',20,'#8a93a0',500)
b+=R(cx[0]-cw/2,ry[2],cw*3+20,rh,'#fbe9f0',PINK,8,2.5)+T(cx[1],ry[2]+30,'④ 역할 분담',19,PINK,800)+T(cx[1],ry[2]+55,'VLM = 차이 맵 이미지 · 액션 = 버킷 주변 점군',15,NAVY,600)
b+=T(118,50,'넣는 위치 × 표현 방식',17,'#595959',600)
b+=chip(0,330,170,'기준선: 카메라만','#eef1f5',NAVY,32,15)
for i,n in enumerate(['목표 지형 오차','사이클당 굴착량','지시 따르기','라이다 노이즈 내성']): b+=chip(190+i*152,330,144,n,'#fdf1e3',ORG,32,15)
sheet(4,'10. 논문 주제: 지형 정보 넣는 방법 비교','<em>어디에, 어떤 형태로</em> 넣어야 굴착이 잘 되는가 · AGX 시뮬레이터로 검증',SVG(b))
# ---------- 14 attack point ----------
sheet(4,'11. 공격점을 정하는 세 갈래','외부 모델은 <em>데이터 공급원</em>, 최종 목표는 직접 학습',
 '<div class="flow"><div><b>A</b><strong>외부에 묻기</strong><span>Gemini Robotics-ER 2 · 범용 LLM<br>좌표 찍기는 ER, 숫자 격자는 LLM</span></div><div><b>B</b><strong>직접 학습</strong><span>GR00T · π0 파인튜닝<br>공격점을 보조 정답으로 함께 학습</span></div><div><b>C</b><strong>섞어 쓰기</strong><span>A·휴리스틱으로 데이터를 모아<br>B를 학습 → 엔드투엔드</span></div></div>')
# ---------- 15 hub ----------
b=C(395,170,92,NAVY)+T(395,162,'공유 본체',24,'#fff',800)+T(395,192,'VLM + DiT',18,'#ffff6c',700)
nodes=[(110,70,'굴착기',ORG),(680,70,'트랙터',GREEN),(110,270,'사족 로봇',BLUE),(680,270,'수확 로봇',PINK)]
for x,y,n,c in nodes:
    b+=R(x-100,y-42,200,84,'#fff',c,10,3)+T(x,y-4,n,23,NAVY,800)+T(x,y+24,'상태·행동 전용 모듈',15,'#595959',500)
    tx=395+(-78 if x<395 else 78); ty=170+(-50 if y<170 else 50)
    sx=x+(100 if x<395 else -100)
    b+=L(sx,y,tx,ty,c,3)+C((sx+tx)/2,(y+ty)/2,9,c)
b+=R(150,326,490,40,'#f4f6f8','#d9dde3',20)+T(395,352,'장비 간 약속 = 시간 맞춘 영상·상태·행동·작업 설명 + 값 설명서',16,NAVY,700)
sheet(5,'12. 필드로봇 파운데이션 모델','<em>본체는 하나</em>, 입출력 모듈만 장비별로 · 데이터를 모아 한 번에 학습',SVG(b),foot='모델 머징·LoRA 어댑터는 중간 단계 · 카메라는 공유 VLM으로 들어가므로 장비 안에서는 구성을 고정')
# ---------- 16 experiment ----------
sheet(5,'13. 제너럴리스트 vs 스페셜리스트','비교 변수는 <em>다른 장비 데이터가 있느냐</em> 하나만',
 '<div class="flow five"><div><b>01</b><strong>굴착만 시험</strong><span>처음 보는 지형·흙·지시문</span></div><div><b>02</b><strong>굴착 데이터 동일</strong><span>추가분만 다른 장비</span></div><div><b>03</b><strong>학습량 맞춤</strong><span>전체 스텝 · 굴착 노출 횟수</span></div><div><b>04</b><strong>데이터 곡선</strong><span>10 · 30 · 100%로 비교</span></div><div><b>05</b><strong>섞는 장비 둘</strong><span>흙 다루는 장비 vs 무관한 팔</span></div></div>',wide=True,foot='RT-X: 데이터가 적은 로봇은 섞으면 오르고, 많은 로봇은 떨어지기도 함(음의 전이)')
# ---------- 17 clip b7 ----------
sheet(6,'14. 미리 내다보기: 굴착 전용 월드 모델','높이맵 + 버킷 경로 → <em>파고 난 뒤 지형</em> · 후보 중 최고만 실행',clip('b7',['범용 영상 모델은 아직 흙에 약함','작은 전용 예측기는 이미 쓸 만함','버킷이 계획대로 간다는 가정이 한계','<b>확장안</b> · 압력 한계 → 실제 궤적 예측']))
# ---------- 18 metrics ----------
sheet(6,'15. DigNet과 휠로더 WAM','행동을 숫자가 아니라 <em>지도로 그려 넣은 것</em>이 핵심',
 '<div class="metrics"><article><strong>DigNet 크기</strong><b>6.3만</b><span>파라미터 · U-Net<br>2채널 입력(높이맵+굴착 깊이)</span></article><article><strong>시뮬레이터 속도</strong><b>200+ FPS</b><span>DEM을 대신해<br>그 안에서 PPO 학습</span></article><article><strong>스쿱 횟수</strong><b>652→541</b><span>월드 모델 순위로 17% 감소<br>32/32 완주 (WAM)</span></article><article><strong>온보드 추론</strong><b>72.4 ms</b><span>후보 5개 평가<br>Jetson AGX Orin</span></article></div>',
 foot='DigNet: Duan &amp; Yang (UBC), SSRN 6662199 · 축소 로봇팔로 검증 · WAM: Zhang et al., arXiv 2609.15382 · 정량 결과는 높이맵 시뮬레이터 기준')
# ---------- 19 video to action ----------
b=''
steps=[(110,'공사장 영상','CCTV · 외부 카메라',BLUE),(395,'관절값 추출','키포인트 + 기구학',TEAL),(680,'행동 라벨','역동역학 · 잠재 행동',ORG)]
for x,n,s,c in steps:
    b+=R(x-110,0,220,250,'#fff',c,10,3)+T(x,216,n,23,NAVY,800)+T(x,240,s,15,'#595959',500)
b+=A(224,125,282,125,NAVY,3)+A(509,125,567,125,NAVY,3)
def exc(ox,oy,s=1,kp=False):
    o=f'<g transform="translate({ox},{oy}) scale({s})">'+R(0,96,120,22,'#3b4656',rx=11)+R(4,62,108,34,'#e3a03a',rx=4)+'<path d="M56 62 L56 24 L90 24 L100 44 L100 62 Z" fill="#e3a03a"/><path d="M61 30 L87 30 L94 44 L61 44 Z" fill="#cfe3f3"/>'
    o+='<line x1="104" y1="58" x2="166" y2="-8" stroke="#e3a03a" stroke-width="13" stroke-linecap="round"/><line x1="166" y1="-8" x2="210" y2="72" stroke="#d4922f" stroke-width="9" stroke-linecap="round"/><path d="M204 68 L232 78 L226 104 Q210 106 200 92 Z" fill="#59626e"/>'
    if kp:
        o+=f'<polyline points="104,58 166,-8 210,72 222,100" fill="none" stroke="{PINK}" stroke-width="3"/>'
        for px,py in [(104,58),(166,-8),(210,72),(222,100)]: o+=C(px,py,8,PINK,'#fff',2)
    return o+'</g>'
b+=exc(18,70,0.72)+R(150,18,44,26,NAVY,rx=4)+f'<path d="M150 31 L132 22 L132 40 Z" fill="{NAVY}"/>'+L(140,44,60,96,'#8a93a0',1.5,'5 4')+L(150,44,120,150,'#8a93a0',1.5,'5 4')
b+=exc(303,70,0.72,True)
for i,(c,ph) in enumerate([(BLUE,0),(TEAL,1.3),(ORG,2.4),(PINK,3.6)]):
    import math
    pts=' '.join(f'{590+k*4.5:.0f},{40+i*38+14*math.sin(k*0.22+ph):.1f}' for k in range(41))
    b+=f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="3"/>'
b+=R(0,276,790,92,'#f4f6f8','#d9dde3',10)+T(395,312,'CCTV에서는 동작 리듬·작업 순서 같은 움직임의 사전 지식을 배운다',19,NAVY,700)+T(395,344,'어디를 팔지는 라이다 높이맵이 있는 시뮬레이터·실장비 데이터로',17,'#595959',500)
sheet(6,'16. 영상에서 행동 데이터 얻기','굴착기는 단단한 링크 네 개 → <em>바깥 영상으로도 자세가 잘 보인다</em>',SVG(b),foot='다음에 더 깊이 논의하기로 한 주제 · 옆에서 찍힌 영상이면 붐·암·버킷 각도는 2D로도 가능, 스윙은 더 어려움')
# ---------- 20 data / rl / real ----------
sheet(6,'17. 데이터, 강화학습, 실장비','<em>다양한 지형과 회복 장면</em>이 양보다 중요',
 '<div class="flow"><div><b>수집</b><strong>자동 생성 + 사람 조금</strong><span>TO+MPC·RL 정책으로 대량 생성<br>사람 시연은 어려운 장면·회복 위주</span></div><div><b>RL</b><strong>잔차 정책으로 다듬기</strong><span>VLA는 얼리고 작은 보정만 학습<br>흙 저항에 맞춘 깊이 조절</span></div><div><b>실장비</b><strong>차이 세 군데</strong><span>흙 · 센서 · 유압 응답<br>실데이터 수십~백 개로 마무리</span></div></div>',foot='탑재는 Jetson AGX 급 · 비상정지와 작업 영역 제한은 VLA와 분리된 제어기에')
# ---------- 21 next ----------
sheet(1,'다음 걸음','실패 장면이 보일 때마다 <em>한 단계씩</em> 더한다',
 '<div class="flow five"><div><b>01</b><strong>동기식 기준선</strong><span>GR00T · π0.5를 같은 데이터로</span></div><div><b>02</b><strong>지형 주입 비교</strong><span>맵·CNN·점군 → 논문</span></div><div><b>03</b><strong>프로빙</strong><span>공격점 정보가 넘어가는지 확인</span></div><div><b>04</b><strong>빠른 반사</strong><span>비동기 S1 · 잔차 RL</span></div><div><b>05</b><strong>내다보기</strong><span>DigNet 확장 · 영상 데이터</span></div></div>',wide=True)
# ---------- 22 sources ----------
srcs=[('GR00T N1.7','NVIDIA, Hugging Face 블로그 (2026.4) · github.com/NVIDIA/Isaac-GR00T'),('Helix','Figure AI 발표 글 · S2 7B 7~9 Hz, S1 80M 200 Hz'),('RoboDual','Bu et al., arXiv 2410.08001 · 15 Hz vs OpenVLA 3.9 Hz'),('X-VLA','arXiv 2510.10274 (ICLR 2026) · Florence-Large 기반 0.9B'),('Gemini Robotics 2','Google DeepMind (2026.7.30) · ER 2만 공개'),('DigNet','Duan &amp; Yang, SSRN 6662199 (2026)'),('WAM','Zhang et al., arXiv 2609.15382 (2026.9)'),('Size Doesn\'t Matter','MPM 입자 시뮬레이션 RL · 11.5톤 굴착기와 탁상 로봇'),('DiT','조건 주입 방식 비교(토큰·크로스 어텐션·adaLN)'),('RT-X','Open X-Embodiment · 여러 로봇 데이터 공동 학습')]
sheet(1,'출처','대화에서 확인한 자료 · <em>기억에 기댄 수치는 원문 확인 필요</em>','<div class="srcs">'+''.join(f'<p><b>{a}</b><br>{c}</p>' for a,c in srcs)+'</div>',wide=True,foot='OpenVLA 약 6 Hz, π0 추론 시간, GR00T 16스텝 청크 등은 검색 없이 말한 값')
head='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VLA, 구조에서 굴착기 적용까지 — NST</title>'
body='<body><header class="toolbar"><b>VLA 대화 정리</b><button onclick="show(current-1)">←</button><span id="count"></span><button onclick="show(current+1)">→</button><button onclick="present()">발표 F</button><button onclick="print()">PDF 인쇄</button></header>'
open(OUT,'w',encoding='utf-8').write(head+style+extra+'</style>'+body+''.join(slides)+script+'<script src="../deck-touch.js"></script></body></html>')
print(len(slides),'slides')
