import re,sys,json
# Builds a draft guidance markdown from a spec JSON and a verse packet. Used with tools/compile_guidance.py --dry (gate) and then the real compile.
# usage: mkgen.py surah packet.txt verses.json out.md  (no +auto line: auto fill is retired)
surah=sys.argv[1]
pk=open(sys.argv[2]).read()
en={int(m.group(1)):m.group(2).strip() for m in re.finditer(r'=== '+surah+r':(\d+).*?\nEN: (.*?)\n',pk,re.S)}
V=json.load(open(sys.argv[3]))
out=[]
for n in sorted(V,key=int):
    d=V[n]
    out.append(f'### {surah}:{n}')
    out.append('> '+en[int(n)])
    out.append('~ '+d['lead'])
    out.append('')
    for h,ids in d['secs']:
        out.append(f'## {h}')
        out += ['- '+i for i in ids]
        out.append('')
open(sys.argv[4],'w').write('\n'.join(out)+'\n')
print('ok',len(V))
