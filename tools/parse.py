import re, os, json, sys, hashlib, html, datetime
SRC='/root/render'
HOURS=['Laudes','Prima','Tertia','Sexta','Nona','Vespera','Completorium']
KEY={'Laudes':'L','Prima':'P','Tertia':'T','Sexta':'S','Nona':'N','Vespera':'V','Completorium':'C'}
tr_re=re.compile(r'<TR>(.*?)</TR>',re.S)
td_re=re.compile(r'<TD[^>]*>(.*?)</TD>',re.S)
def clean(s):
    s=s.strip()
    s=re.sub(r'^<p>|</p>$','',s).strip()
    s=re.sub(r'</?a[^>]*>','',s)
    s=s.replace('<span class="ri">','<i>').replace('<span class="rd">','<u>')
    s=s.replace('<span class="w">','<s>').replace('<span class="a">','<q>')
    s=s.replace('<span class="rb">','<u>').replace('<span class="c">','<u>')
    s=re.sub(r'<span class="s m">','<em>',s); s=re.sub(r'<span class="s">','<em>',s)
    s=re.sub(r'<span class="">','<span>',s)
    # close tags: we replaced opening span types; need to close them correctly -> simple stack
    out=[];stack=[];pos=0
    for m in re.finditer(r'<(/?)(i|u|s|q|em|span|b|br/?)>',s):
        out.append(s[pos:m.start()]); pos=m.end()
        cl,tag=m.group(1),m.group(2)
        if tag.startswith('br'): out.append('<br>'); continue
        if not cl:
            stack.append(tag); out.append('<%s>'%tag)
        else:
            if tag=='span' and stack: t=stack.pop(); out.append('</%s>'%t)
            elif stack and stack[-1]==tag: stack.pop(); out.append('</%s>'%tag)
            else: out.append('</%s>'%tag)
    out.append(s[pos:])
    s=''.join(out)
    s=s.replace('<span>','').replace('</span>','')
    s=re.sub(r'\s*\n\s*',' ',s); s=re.sub(r'(<br>\s*)+$','',s)
    s=s.replace('&#10016;','✠').replace('&ensp;',' ')
    return s.strip()
def header(h):
    m=re.search(r'<p class="cen"><span class="([^"]*)">(.*?)<br/></span>(.*?)<span class="c">',h,re.S)
    col=m.group(1); title=m.group(2).strip()
    tp=re.search(r'<span class="s">(?:Tempora: )?(.*?)</span>',m.group(3))
    return title, col, (tp.group(1).strip() if tp else '')
sections={}; secid={}
def sid(pair):
    k=json.dumps(pair,ensure_ascii=False)
    if k not in secid:
        secid[k]=len(sections); sections[len(sections)]=pair
    return secid[k]
days={}
files=sorted(os.listdir(SRC))
dates=sorted(set(f[:10] for f in files))
for d in dates:
    dd={}
    for h in HOURS:
        fn=f'{SRC}/{d}-{h}.html'
        if not os.path.exists(fn) or os.path.getsize(fn)<2000: continue
        t=open(fn,encoding='utf-8').read()
        if h=='Laudes' or 'title' not in dd:
            dd['title'],dd['col'],dd['tp']=header(t)
        if h=='Vespera':
            vt,vc,_=header(t)
            if vt!=dd.get('title'): dd['vt']=vt
        ids=[]
        for row in tr_re.findall(t):
            tds=td_re.findall(row)
            if not tds: continue
            la=clean(tds[0]); es=clean(tds[1]) if len(tds)>1 else ''
            if es.startswith('<b>Martyrology</b>'): es=''
            ids.append(sid([la,es]))
        dd[KEY[h]]=ids
    m,dy,y=d.split('-'); days[f'{y}-{m}-{dy}']=dd
os.makedirs('/root/build/data',exist_ok=True)
json.dump([sections[i] for i in range(len(sections))],open('/root/build/data/sec.json','w'),ensure_ascii=False,separators=(',',':'))
json.dump(days,open('/root/build/data/days.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(days),'days',len(sections),'sections')
