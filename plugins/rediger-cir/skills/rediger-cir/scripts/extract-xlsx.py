import sys, zipfile
from xml.etree import ElementTree as ET
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def col(ref):
    import re; return re.match(r'[A-Z]+', ref).group()
z=zipfile.ZipFile(sys.argv[1])
shared=[]
if 'xl/sharedStrings.xml' in z.namelist():
    r=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in r.findall(NS+'si'):
        shared.append(''.join(t.text or '' for t in si.iter(NS+'t')))
wb=ET.fromstring(z.read('xl/workbook.xml'))
sheets=[(s.get('name'), s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')) for s in wb.iter(NS+'sheet')]
rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
relmap={r.get('Id'):r.get('Target') for r in rels}
for name,rid in sheets:
    tgt=relmap.get(rid,'')
    path='xl/'+tgt if not tgt.startswith('/') else tgt[1:]
    if path not in z.namelist(): continue
    print(f"\n===== SHEET: {name} =====")
    sh=ET.fromstring(z.read(path))
    for row in sh.iter(NS+'row'):
        cells=[]
        for c in row.findall(NS+'c'):
            v=c.find(NS+'v'); t=c.get('t')
            if v is None: val=''
            elif t=='s': val=shared[int(v.text)]
            else: val=v.text
            cells.append(val.replace('\n',' ') if val else '')
        if any(cells): print(' | '.join(cells))
