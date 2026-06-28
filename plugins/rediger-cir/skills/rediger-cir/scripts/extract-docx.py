import sys, zipfile, re
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def docx_to_text(path):
    z = zipfile.ZipFile(path)
    xml = z.read('word/document.xml')
    root = ET.fromstring(xml)
    out = []
    body = root.find(W+'body')
    def para_text(p):
        return ''.join(t.text or '' for t in p.iter(W+'t'))
    def style(p):
        ppr = p.find(W+'pPr')
        if ppr is None: return None
        st = ppr.find(W+'pStyle')
        return st.get(W+'val') if st is not None else None
    for el in body:
        tag = el.tag.replace(W,'')
        if tag == 'p':
            txt = para_text(el)
            st = style(el) or ''
            if re.search(r'[Hh]eading|[Tt]itre', st):
                lvl = re.search(r'(\d)', st)
                n = int(lvl.group(1)) if lvl else 1
                if txt.strip():
                    out.append('\n' + '#'*n + ' ' + txt.strip())
            elif txt.strip():
                out.append(txt)
            else:
                out.append('')
        elif tag == 'tbl':
            out.append('\n[TABLE]')
            for row in el.findall(W+'tr'):
                cells = []
                for c in row.findall(W+'tc'):
                    ct = ' '.join(''.join(t.text or '' for t in p.iter(W+'t')) for p in c.findall(W+'p'))
                    cells.append(ct.strip())
                out.append(' | '.join(cells))
            out.append('[/TABLE]')
    return '\n'.join(out)

if __name__ == '__main__':
    print(docx_to_text(sys.argv[1]))
