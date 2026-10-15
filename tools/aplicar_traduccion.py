#!/usr/bin/env python3
"""Aplica los diccionarios trad/*.json (línea latina normalizada -> línea española)
sobre data/s-*.json. Idempotente. Uso: aplicar_traduccion.py <raiz_app>"""
import json,re,glob,os,sys
ROOT=sys.argv[1] if len(sys.argv)>1 else '.'
VERSE=re.compile(r'^\s*<s>(\d+:\d+[a-z]?)</s>')
def norm(l):
    t=re.sub(r'<s>‡</s>','',l); t=re.sub(r'<[^>]+>','',t)
    t=t.replace('‡','').replace(' ',' ')
    return re.sub(r'\s+',' ',t).strip()
D={}
for f in sorted(glob.glob(os.path.join(ROOT,'trad','*.json'))):
    if f.endswith('glosario.json'): continue
    D.update(json.load(open(f,encoding='utf-8'))['lineas'])
stats=dict(secciones=0,lineas=0,desalineadas=0)
desal=[]
for f in sorted(glob.glob(os.path.join(ROOT,'data','s-*.json')),key=lambda p:int(re.findall(r'(\d+)\.json',p)[0])):
    secs=json.load(open(f,encoding='utf-8')); ch=False
    for n,(la,es) in enumerate(secs):
        L=la.split('<br>'); E=es.split('<br>') if es else []
        hits=[(i,D[norm(l)]) for i,l in enumerate(L) if VERSE.match(l) and norm(l) in D]
        if not hits: continue
        if len(L)!=len(E):
            # Reconstrucción guiada por el latín: versos de la traducción propia,
            # resto de líneas (antífonas, títulos, Gloria) del español anterior, en orden.
            nvL=[l for l in L if not VERSE.match(l)]; nvE=[l for l in E if not VERSE.match(l)]
            allv=all(norm(l) in D for l in L if VERSE.match(l))
            if len(nvL)!=len(nvE) or not allv:
                stats['desalineadas']+=1; desal.append((os.path.basename(f),n)); continue
            it=iter(nvE); E=[]
            for l in L:
                if VERSE.match(l):
                    ref=VERSE.match(l).group(1); E.append(' <s>%s</s> %s'%(ref,D[norm(l)]))
                else: E.append(next(it))
            secs[n]=[la,'<br>'.join(E)]; stats['secciones']+=1; stats['reconstruidas']=stats.get('reconstruidas',0)+1; ch=True
            continue
        for i,t in hits:
            ref=VERSE.match(L[i]).group(1)
            new=' <s>%s</s> %s'%(ref,t) if E[i].startswith(' ') else '<s>%s</s> %s'%(ref,t)
            if E[i]!=new: E[i]=new; ch=True; stats['lineas']+=1
        secs[n]=[la,'<br>'.join(E)]; stats['secciones']+=1
    if ch: json.dump(secs,open(f,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(json.dumps(stats))
if desal: print('desalineadas (se conserva el español anterior):',desal[:30])
