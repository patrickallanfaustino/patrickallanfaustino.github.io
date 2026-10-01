#!/usr/bin/env python3
"""Extrai mol2 e frcmod do material suplementar de Shahrokh et al. (2012).

Entrada: o .doc do SI convertido para texto puro (UTF-8):
    soffice --headless --convert-to "txt:Text (encoded):UTF8" jcc_21922_sm_suppinfo.doc
Saida:  <ESTADO>_HEM.mol2, <ESTADO>_CYP.mol2, <ESTADO>.frcmod e um
        relatorio com a soma das cargas de cada mol2.

Nenhum valor e alterado: as linhas sao copiadas como estao no SI, so as
linhas em branco dentro dos blocos mol2 sao descartadas.
"""
import re, sys, hashlib
from pathlib import Path

SI = Path(sys.argv[1] if len(sys.argv) > 1 else "jcc_21922_sm_suppinfo.txt")
linhas = SI.read_text(encoding="utf-8").splitlines()

# nome da molecula no SI -> arquivo de saida
MOL2 = {"HEM-IC6": "IC6_HEM.mol2", "CYP-IC6": "IC6_CYP.mol2",
        "HEM-O2": "DIOXY_HEM.mol2", "CYP-O2": "DIOXY_CYP.mol2",
        "HEM-CPDI": "CPDI_HEM.mol2", "CYP-CPDI": "CPDI_CYP.mol2"}
# linha de titulo do frcmod no SI -> arquivo de saida
FRCMOD = {"Ferric-high-spin.frcmod-": "IC6.frcmod",
          "DIOXY.frcmod-": "DIOXY.frcmod", "CPDI.frcmod-": "CPDI.frcmod"}

def bloco_mol2(i):
    """Do '@<TRIPOS>MOLECULE' da linha i ate a linha apos '@<TRIPOS>SUBSTRUCTURE'."""
    out, j = [], i
    while True:
        l = linhas[j]
        if l.strip():
            out.append(l.rstrip())
        if l.startswith("@<TRIPOS>SUBSTRUCTURE"):
            k = j + 1
            while not linhas[k].strip():
                k += 1
            out.append(linhas[k].rstrip())
            return out
        j += 1

def bloco_frcmod(i):
    """Do titulo ate o fim da secao NONBON (primeira linha em branco depois dela)."""
    out, j, em_nonbon = [], i, False
    while j < len(linhas):
        l = linhas[j].rstrip()
        if em_nonbon and not l.strip():
            break
        if l.strip() == "NONBON":
            em_nonbon = True
        out.append(l)
        j += 1
    return out

def soma_cargas(mol2):
    dentro, q, n = False, 0.0, 0
    for l in mol2:
        if l.startswith("@<TRIPOS>ATOM"):
            dentro = True; continue
        if l.startswith("@<TRIPOS>"):
            dentro = False; continue
        if dentro:
            q += float(l.split()[8]); n += 1
    return n, q

relatorio = []
for i, l in enumerate(linhas):
    if l.startswith("@<TRIPOS>MOLECULE"):
        nome = linhas[i + 1].strip()
        if nome in MOL2:
            bloco = bloco_mol2(i)
            Path(MOL2[nome]).write_text("\n".join(bloco) + "\n")
            n, q = soma_cargas(bloco)
            relatorio.append(f"{MOL2[nome]:16s} {n:3d} atomos  carga {q:+.4f}")
    for titulo, arq in FRCMOD.items():
        if l.startswith(titulo):
            Path(arq).write_text("\n".join(bloco_frcmod(i)) + "\n")
            relatorio.append(f"{arq:16s} extraido")

for est in ("IC6", "DIOXY", "CPDI"):
    h, c = Path(f"{est}_HEM.mol2"), Path(f"{est}_CYP.mol2")
    if h.exists() and c.exists():
        qh = soma_cargas(h.read_text().splitlines())[1]
        qc = soma_cargas(c.read_text().splitlines())[1]
        relatorio.append(f"{est:6s} HEM + CYP = {qh:+.4f} {qc:+.4f} = {qh + qc:+.4f}")

relatorio.append("sha256 do SI em texto: " + hashlib.sha256(SI.read_bytes()).hexdigest())
Path("extracao_si.log").write_text("\n".join(relatorio) + "\n")
print("\n".join(relatorio))
