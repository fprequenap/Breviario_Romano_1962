#!/usr/bin/env python3
"""Recalcula la versión de datos y del service worker tras modificar data/ o index.html.
Uso: publicar.py <raiz_app>"""
import json,glob,os,re,sys,hashlib,datetime
R=sys.argv[1] if len(sys.argv)>1 else '.'
h=hashlib.sha1()
for p in sorted(glob.glob(os.path.join(R,'data','*.json')))+[os.path.join(R,'index.html')]:
    if p.endswith('meta.json'): continue
    h.update(open(p,'rb').read())
v=h.hexdigest()[:8]
mp=os.path.join(R,'data','meta.json'); m=json.load(open(mp)); m['v']=v; m['gen']=datetime.date.today().isoformat()
tr=sorted(os.path.basename(p) for p in glob.glob(os.path.join(R,'trad','*.json')) if 'glosario' not in p)
m['traduccion']=[json.load(open(os.path.join(R,'trad',t),encoding='utf-8'))['bloque'] for t in tr]
json.dump(m,open(mp,'w'),ensure_ascii=False)
sw=open(os.path.join(R,'sw.js'),encoding='utf-8').read()
sw=re.sub(r"const VERSION='[^']*'","const VERSION='%s'"%v,sw)
open(os.path.join(R,'sw.js'),'w',encoding='utf-8').write(sw)
ix=open(os.path.join(R,'index.html'),encoding='utf-8').read()
ix=re.sub(r"sw\.js\?v=[^']*","sw.js?v="+v,ix)
open(os.path.join(R,'index.html'),'w',encoding='utf-8').write(ix)
print('versión',v,m.get('traduccion'))
