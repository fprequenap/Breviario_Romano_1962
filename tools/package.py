import json, os, glob, datetime, shutil, hashlib
B='/root/build'; A=B+'/app'
sec=json.load(open(B+'/data/sec.json')); days=json.load(open(B+'/data/days.json'))
out=A+'/data'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
CH=400
for i in range(0,len(sec),CH):
    json.dump(sec[i:i+CH],open(f'{out}/s-{i//CH}.json','w'),ensure_ascii=False,separators=(',',':'))
months={}
for d,v in days.items(): months.setdefault(d[:7],{})[d]=v
for m,v in months.items(): json.dump(v,open(f'{out}/m-{m}.json','w'),ensure_ascii=False,separators=(',',':'))
ks=sorted(days); h=hashlib.sha1(open(B+'/data/sec.json','rb').read()+open(B+'/data/days.json','rb').read()+open(A+'/index.html','rb').read()).hexdigest()[:8]
meta={'from':ks[0],'to':ks[-1],'chunk':CH,'nchunks':(len(sec)+CH-1)//CH,'v':h,'gen':datetime.date.today().isoformat(),'rubricae':'1960'}
json.dump(meta,open(f'{out}/meta.json','w'))
data=['data/meta.json']+sorted('data/'+os.path.basename(p) for p in glob.glob(out+'/*.json') if not p.endswith('meta.json'))
fonts=sorted('fonts/'+f for f in os.listdir(A+'/fonts'))
sw=open(B+'/sw.template.js').read().replace('__VERSION__',h).replace('__FONTS__',','.join(json.dumps(f) for f in fonts)).replace('__DATA__',json.dumps(data))
open(A+'/sw.js','w').write(sw)
# cache-busting del registro
idx=open(A+'/index.html').read()
import re; idx=re.sub(r"sw\.js\?v=[^']*","sw.js?v="+h,idx); open(A+'/index.html','w').write(idx)
tot=sum(os.path.getsize(p) for p in glob.glob(out+'/*'))
print(meta, len(data),'data files', round(tot/1e6,1),'MB')
