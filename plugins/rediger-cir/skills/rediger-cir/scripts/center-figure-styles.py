#!/usr/bin/env python3
"""Centre les styles de figure et de légende dans un reference.docx pandoc.
Convention de mise en page : images et légendes centrées, corps de texte à gauche.
Usage : center-figure-styles.py <reference.docx>
"""
import sys, os, zipfile
import xml.etree.ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W)
def q(t): return f"{{{W}}}{t}"

TARGETS = {"Figure", "ImageCaption", "CaptionedFigure", "Caption"}

src = sys.argv[1]
z = zipfile.ZipFile(src)
data = {n: z.read(n) for n in z.namelist()}
z.close()

root = ET.fromstring(data["word/styles.xml"])
done = []
for st in root.findall(q("style")):
    if st.get(q("styleId")) not in TARGETS:
        continue
    ppr = st.find(q("pPr"))
    if ppr is None:
        ppr = ET.Element(q("pPr"))
        rpr = st.find(q("rPr"))
        st.insert(list(st).index(rpr) if rpr is not None else len(list(st)), ppr)
    jc = ppr.find(q("jc"))
    if jc is None:
        jc = ET.SubElement(ppr, q("jc"))
    jc.set(q("val"), "center")
    done.append(st.get(q("styleId")))

data["word/styles.xml"] = ET.tostring(root, xml_declaration=True, encoding="UTF-8")
tmp = src + ".tmp"
zo = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
for n, b in data.items():
    zo.writestr(n, b)
zo.close()
os.replace(tmp, src)
print("Styles centrés :", ", ".join(done))
