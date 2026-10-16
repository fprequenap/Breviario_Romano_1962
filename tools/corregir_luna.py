#!/usr/bin/env python3
"""Corrige el Martirologio de los años bisiestos (24-29 de febrero).
Divinum Officium da en esos días una Luna errónea: el 24 lleva un valor sin
relación y del 25 al 29 va un día por detrás (salta un número el 1 de marzo).
Regla del propio Martirologio: «In anno Bissextili bis pronuntiatur Sexto
Kaléndas Mártii, et eadem Luna, scilicet die 24 et 25»; y el día 24, tras la
fecha: «Commemorátio plurimórum sanctórum Mártyrum et Confessórum, atque
sanctárum Vírginum», que Divinum Officium omite.
Se recalcula la Luna desde la del 23 (VII Kal.), se repite el 24 y el 25, y se
comprueba que el 29 enlaza con la del 1 de marzo. Corrige latín y español.
Ejecutar después de aplicar_traduccion.py. Idempotente. Uso: corregir_luna.py <raiz_app>"""
import json, glob, os, re, sys, datetime, unicodedata
def strip_acc(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn').lower()
UN={'primo':1,'prima':1,'secundo':2,'secunda':2,'tertio':3,'tertia':3,'quarto':4,'quarta':4,'quinto':5,'quinta':5,'sexto':6,'sexta':6,'septimo':7,'septima':7,'octavo':8,'octava':8,'nono':9,'nona':9,'decimo':10,'decima':10,'undecimo':11,'undecima':11,'duodecimo':12,'duodecima':12,'vicesimo':20,'vicesima':20,'tricesimo':30,'tricesima':30,'duodevicesimo':18,'duodevicesima':18,'undevicesimo':19,'undevicesima':19,'undetricesimo':29,'undetricesima':29,'duodetricesimo':28,'duodetricesima':28}
def latord(words):
    n=0
    for w in words.split():
        w=strip_acc(w).strip('.,')
        if w in UN: n+=UN[w]; continue
        m=re.match(r'^(\w+?)(decimo|decima)$',w)
        if m and m.group(1) in UN: n+=UN[m.group(1)]+10; continue
        return None
    return n
MES={'ianuarii':1,'februarii':2,'martii':3,'aprilis':4,'maii':5,'iunii':6,'iulii':7,'augusti':8,'septembris':9,'octobris':10,'novembris':11,'decembris':12}
MESES=['','enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
ORDM={1:'primero',2:'segundo',3:'tercero',4:'cuarto',5:'quinto',6:'sexto',7:'séptimo',8:'octavo',9:'noveno',10:'décimo',11:'undécimo',12:'duodécimo',13:'decimotercero',14:'decimocuarto',15:'decimoquinto',16:'decimosexto',17:'decimoséptimo',18:'decimoctavo',19:'decimonoveno'}
U_F={1:'primera',2:'segunda',3:'tercera',4:'cuarta',5:'quinta',6:'sexta',7:'séptima',8:'octava',9:'novena'}
def ordf(n):
    if n<10: return U_F[n]
    if n==10: return 'décima'
    if n<20: return {11:'undécima',12:'duodécima',18:'decimoctava'}.get(n,'decimo'+U_F[n-10])
    if n==20: return 'vigésima'
    if n<30: return 'vigésima '+U_F[n-20]
    return 'trigésima'
RX=re.compile(r'^(.*?)\s*(Kal[eé]nd(?:as|is)|Non(?:as|is)|Id(?:us|ibus))\s+(\w+)\s+Luna\s+(.+?)\.\s*Anno\s+D[oó]mini\s+(\d{4})\s*$',re.I)
def parse(line):
    m=RX.match(line)
    if not m: return None
    pre,kind,mon,luna,yr=m.groups()
    k=strip_acc(kind)[:3]; k='idu' if k.startswith('id') else k; mon=MES[strip_acc(mon)]; yr=int(yr); ln=latord(luna)
    pre=pre.strip()
    if strip_acc(pre)=='pridie': n=2
    elif pre=='': n=1
    else: n=latord(pre)
    if n is None or ln is None: return None
    # día de referencia
    if k=='kal':
        ref=datetime.date(yr if mon!=1 or n==1 else yr,mon,1)
    elif k=='non': ref=datetime.date(yr,mon,7 if mon in (3,5,7,10) else 5)
    else: ref=datetime.date(yr,mon,15 if mon in (3,5,7,10) else 13)
    if k=='kal' and n>1:
        # antes de las Calendas: mes anterior (y año anterior si enero)
        pass
    d=ref-datetime.timedelta(days=n-1)
    return dict(n=n,k=k,mon=mon,luna=ln,yr=yr,date=d)
KIND={'kal':'las Calendas','non':'las Nonas','idu':'los Idus'}
def spanish(line,date=None):
    p=parse(line)
    if not p: return None
    d=date or p['date']
    k=KIND[p['k']]; mes=MESES[p['mon']]
    if p['n']==1: head=f'El día de {k} de {mes}'
    elif p['n']==2: head=f'La víspera de {k} de {mes}'
    else: head=f'El día {ORDM[p["n"]]} antes de {k} de {mes}'
    return f'{head} ({d.day} de {MESES[d.month]}). Luna {ordf(p["luna"])}. Año del Señor {p["yr"]}.'

def norm(l):
    t = re.sub(r'<[^>]+>', '', l).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', t).strip()

COMM_LA = 'Commemorátio plurimórum sanctórum Mártyrum et Confessórum, atque sanctárum Vírginum.'
COMM_ES = 'Conmemoración de muchísimos santos Mártires y Confesores, y de santas Vírgenes.'
RXL = re.compile(r'(Luna\s+)(.+?)(\.\s*Anno)')

def main(R):
    CH = json.load(open(os.path.join(R, 'data', 'meta.json')))['chunk']
    files = sorted(glob.glob(os.path.join(R, 'data', 's-*.json')), key=lambda p: int(re.findall(r'(\d+)\.json', p)[0]))
    S = {}
    for f in files:
        K = int(re.findall(r'(\d+)\.json', f)[0]); S[K] = json.load(open(f, encoding='utf-8'))
    sec = lambda i: S[i // CH][i % CH]
    D = {}
    for f in glob.glob(os.path.join(R, 'data', 'm-*.json')): D.update(json.load(open(f, encoding='utf-8')))
    # nombre latino de cada Luna, tal como lo escribe el Martirologio
    LAT = {}; mart = {}
    for d, v in D.items():
        for i in v.get('P', []):
            la = sec(i)[0]
            if la.startswith('<b>Martyrologium'):
                L = la.split('<br>')
                dd = datetime.date.fromisoformat(d) + datetime.timedelta(days=1 if 'anticipatur' in L[0] else 0)
                mart[dd] = i
                m = RXL.search(norm(L[1]))
                if m and latord(m.group(2)): LAT.setdefault(latord(m.group(2)), m.group(2))
    def luna(dd):
        return latord(RXL.search(norm(sec(mart[dd])[0].split('<br>')[1])).group(2))
    cambios = 0
    for y in sorted({d.year for d in mart}):
        if y % 4 or (y % 100 == 0 and y % 400): continue
        dias = [datetime.date(y, 2, k) for k in range(23, 30)] + [datetime.date(y, 3, 1)]
        if not all(d in mart for d in dias): continue
        # secuencias posibles (tras la Luna 29 puede venir la 30 o la 1); vale la que enlaza con el 1 de marzo
        seqs = [[luna(dias[0])]]
        for d in dias[1:]:
            nx = []
            for q in seqs:
                n = q[-1]
                if d.day == 25: nx.append(q + [n])
                elif n == 29: nx += [q + [30], q + [1]]
                else: nx.append(q + [n % 30 + 1])
            seqs = nx
        ok = [q for q in seqs if q[-1] == luna(dias[-1])]
        if len(ok) != 1:
            print('AVISO', y, 'sin solución única; sin cambios'); continue
        val = dict(zip(dias[1:-1], ok[0][1:-1]))
        for d, n in val.items():
            i = mart[d]; la, es = sec(i); L = la.split('<br>'); E = es.split('<br>')
            L[1] = RXL.sub(lambda m: m.group(1) + LAT[n] + m.group(3), L[1], count=1)
            E[1] = re.sub(r'^(\s*<q>.</q>).*$', lambda m: m.group(1) + spanish(norm(L[1]), d)[1:], E[1])
            if d.day == 24 and not any(COMM_LA in norm(x) for x in L):
                L.insert(2, ' <b>C</b>' + COMM_LA[1:]); E.insert(2, ' <b>C</b>' + COMM_ES[1:])
            nl, ne = '<br>'.join(L), '<br>'.join(E)
            if (nl, ne) != (la, es):
                S[i // CH][i % CH] = [nl, ne]; cambios += 1
            print(d, 'Luna', n, '|', norm(E[1]))
    for K, v in S.items():
        json.dump(v, open(os.path.join(R, 'data', 's-%d.json' % K), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('secciones cambiadas:', cambios)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
