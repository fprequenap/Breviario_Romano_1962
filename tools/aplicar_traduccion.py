#!/usr/bin/env python3
"""Aplica los diccionarios trad/*.json sobre data/s-*.json (columna española).
- "lineas": línea latina normalizada -> texto español (sin marcado). El marcado
  (número de verso, etiquetas Ant./℣./℟., capitulares, cabeceras, rúbricas, ✠)
  se reconstruye a partir de la línea latina.
- "html": línea latina normalizada -> línea española con su marcado completo.
Idempotente. Uso: aplicar_traduccion.py <raiz_app>"""
import json, re, glob, os, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
VERSE = re.compile(r'^(\s*)<s>(\d+:\d+[a-z]?)</s>')
LAB = re.compile(r'^(\s*)<i>([^<]*)</i>\s*(.*)$')
LABT = {'Ant.': 'Ant.', '℟.': '℟.', '℣.': '℣.', '℟.br.': '℟. br.', 'Benedictio.': 'Bendición.', 'Hymnus': 'Himno'}

def norm(l):
    t = re.sub(r'<s>‡</s>', '', l); t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('‡', '').replace(' ', ' ')
    return re.sub(r'\s+', ' ', t).strip()

def cross(t):
    return t.replace('✠', '<u>✠</u>')

def initial(tag, t):
    m = re.match(r'^([¡¿«"(]*\w)(.*)$', t, re.S)
    return '<%s>%s</%s>%s' % (tag, m.group(1), tag, m.group(2)) if m else t

def build(lat, es):
    """Reconstruye la línea española con el marcado de la línea latina."""
    lead = re.match(r'^\s*', lat).group(0)
    s = lat.strip()
    m = VERSE.match(lat)
    if m:
        return '%s<s>%s</s> %s' % (m.group(1), m.group(2), cross(es))
    m = LAB.match(lat)
    if m:
        if m.group(2) in LABT and not norm(m.group(3)):
            return '%s<i>%s</i>' % (m.group(1), LABT[m.group(2)])
        if m.group(2) in LABT:
            return '%s<i>%s</i> %s' % (m.group(1), LABT[m.group(2)], cross(es))
        return '%s<i>%s</i>' % (m.group(1), es)
    if s.startswith('<b>'):
        mm = re.match(r'^<b>([^<]*)</b>\s*(?:<em>(.*?)</em>)?\s*$', s)
        if mm:
            h, _, r = es.partition(' | ')
            return lead + '<b>%s</b> ' % h.strip() + ('<em>%s</em> ' % r.strip() if r else '')
        if re.match(r'^<b>\w</b>', s):
            return lead + initial('b', cross(es))
    if s.startswith('<q>'):
        return lead + initial('q', cross(es))
    if s.startswith('<em>') and s.endswith('</em>'):
        return lead + '<em>%s</em>' % es
    if s.startswith('<s>'):
        return lead + '<s>%s</s>' % es
    return lead + cross(es)

D = {}; H = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'trad', '*.json'))):
    if f.endswith('glosario.json'): continue
    j = json.load(open(f, encoding='utf-8'))
    D.update(j.get('lineas', {})); H.update(j.get('html', {}))

def tr(l):
    k = norm(l)
    if not k: return l if not l.strip() else None
    if k in H:
        return re.match(r'^\s*', l).group(0) + H[k].strip()
    if k in D: return build(l, D[k])
    return None

stats = dict(secciones=0, lineas=0, reconstruidas=0, parciales=0)
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 's-*.json')), key=lambda p: int(re.findall(r'(\d+)\.json', p)[0])):
    secs = json.load(open(f, encoding='utf-8')); ch = False
    for n, (la, es) in enumerate(secs):
        if la.startswith('<b>Martyrologium'): continue  # bloque propio (sesiones 5-7)
        L = la.split('<br>'); E = es.split('<br>') if es else []
        T = [tr(l) for l in L]
        if all(t is None for t in T): continue
        if len(L) == len(E):
            newE = [t if t is not None else e for t, e in zip(T, E)]
        elif all(t is not None for t in T):
            newE = T; stats['reconstruidas'] += 1
        else:
            # Solo versos traducidos; resto de líneas del español anterior en orden
            nvL = [i for i, l in enumerate(L) if not VERSE.match(l)]
            nvE = [e for e in E if not VERSE.match(e)]
            if len(nvL) != len(nvE) or any(T[i] is None for i, l in enumerate(L) if VERSE.match(l)):
                stats['parciales'] += 1; continue
            it = iter(nvE); newE = []
            for i, l in enumerate(L):
                newE.append(T[i] if VERSE.match(l) else (T[i] if T[i] is not None else next(it)))
                if not VERSE.match(l) and T[i] is not None: next(it)
            stats['reconstruidas'] += 1
        new = '<br>'.join(newE)
        stats['lineas'] += sum(1 for a, b in zip(newE, E) if a != b) if len(newE) == len(E) else len(newE)
        if new != es:
            secs[n] = [la, new]; ch = True
        stats['secciones'] += 1
    if ch: json.dump(secs, open(f, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(json.dumps(stats))
