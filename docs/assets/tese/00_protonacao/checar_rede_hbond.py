#!/usr/bin/env python3
"""Triagem estrutural dos estados das His (e vizinhos do heme) COM o heme presente.

O PROPKA ignora o HEM (nao e residuo padrao), entao as His e Lys junto aos
propionatos saem com pKa sem sentido. Este script olha a geometria: para
cada N da His, lista os parceiros polares a menos de CORTE e classifica-os
como aceitador, doador ou ambos. Regra de triagem:
  - Amida de Asn/Gln conta como "ambos" (o flip OD1/ND2 nao se resolve
    por raio-X), assim como OH de Ser/Thr/Tyr e agua.
  - N com parceiro so-aceitador (O de carbonila, O de carboxilato/propionato)
    deve carregar H; N com parceiro so-doador (N-H de amida, NZ, NH de Arg)
    nao deve.
  - Os dois N pedindo H -> HIP; so ND1 -> HID; so NE2 -> HIE.
E triagem, nao decisao: confira no visualizador e registre a fonte no JSON.
Uso: python3 checar_rede_hbond.py proteina_heme[_substrato].pdb [corte=3.5]
"""
import sys
import numpy as np

pdb = sys.argv[1]
CORTE = float(sys.argv[2]) if len(sys.argv) > 2 else 3.5

ACEITADOR = {("*", "O"), ("*", "OXT"), ("ASP", "OD1"), ("ASP", "OD2"), ("GLU", "OE1"),
             ("GLU", "OE2"), ("MET", "SD"),
             ("HEM", "O1A"), ("HEM", "O2A"), ("HEM", "O1D"), ("HEM", "O2D")}
DOADOR = {("*", "N"), ("LYS", "NZ"), ("ARG", "NE"), ("ARG", "NH1"), ("ARG", "NH2"),
          ("TRP", "NE1")}
AMBOS = {("SER", "OG"), ("THR", "OG1"), ("TYR", "OH"), ("HOH", "O"), ("WAT", "O"),
         ("HIS", "ND1"), ("HIS", "NE2"),
         # amida de Asn/Gln: O e N sao indistinguiveis por raio-X (flip); nao decide
         ("ASN", "OD1"), ("ASN", "ND2"), ("GLN", "OE1"), ("GLN", "NE2")}
HIS = {"HIS", "HID", "HIE", "HIP", "HSD", "HSE", "HSP"}

def papel(res, nome):
    r = "HIS" if res in HIS else res
    if (r, nome) in AMBOS: return "ambos"
    if (r, nome) in ACEITADOR or ("*", nome) in ACEITADOR and nome in ("O", "OXT"): return "aceitador"
    if (r, nome) in DOADOR or (nome == "N" and r != "PRO"): return "doador"
    if nome[0] == "O": return "aceitador"          # carboxilato de substrato, etc.
    return None

atomos = []
for l in open(pdb):
    if l.startswith(("ATOM", "HETATM")):
        el = (l[76:78].strip() or l[12:16].strip()[0]).upper()
        if el == "H": continue
        atomos.append((l[17:20].strip(), int(l[22:26]), l[12:16].strip(),
                       np.array([float(l[30:38]), float(l[38:46]), float(l[46:54])])))
xyz = np.array([a[3] for a in atomos])

print(f"{'His':>7s}  {'ND1 (parceiros)':<45s} {'NE2 (parceiros)':<45s} sugestao")
for res, num, nome, x in atomos:
    if res not in HIS or nome != "ND1": continue
    quer_h, desc = {}, {}
    for n_his in ("ND1", "NE2"):
        xa = next(a[3] for a in atomos if a[1] == num and a[2] == n_his and a[0] == res)
        d = np.linalg.norm(xyz - xa, axis=1)
        parc = []
        for k in np.argsort(d):
            if d[k] >= CORTE: break
            r2, n2, a2, _ = atomos[k]
            if n2 == num and r2 == res: continue
            p = papel(r2, a2)
            if p: parc.append((r2, n2, a2, d[k], p))
        acc = any(p == "aceitador" for *_, p in parc)
        don = any(p == "doador" for *_, p in parc)
        quer_h[n_his] = acc and not don if (acc or don) else None
        desc[n_his] = "; ".join(f"{r}{n}:{a} {dd:.2f} ({p[:3]})" for r, n, a, dd, p in parc) or "-"
    nd, ne = quer_h["ND1"], quer_h["NE2"]
    if nd and ne: sug = "HIP"
    elif nd and ne is False: sug = "HID"
    elif ne and nd is False: sug = "HIE"
    elif nd: sug = "HID ou HIP"
    elif ne: sug = "HIE ou HIP"
    elif nd is None and ne is None: sug = "sem parceiros: PROPKA/solvente"
    else: sug = "ambigua: inspecionar"
    print(f"{res}{num:<4d}  {desc['ND1'][:45]:<45s} {desc['NE2'][:45]:<45s} {sug}")

print(f"\nLys/Arg em ponte com propionato (< {CORTE} A): manter carregadas")
prop = [a for a in atomos if a[0] == "HEM" and a[2] in ("O1A", "O2A", "O1D", "O2D")]
for res, num, nome, x in atomos:
    if (res, nome) in {("LYS", "NZ"), ("ARG", "NH1"), ("ARG", "NH2"), ("ARG", "NE")}:
        for p in prop:
            d = np.linalg.norm(x - p[3])
            if d < CORTE:
                print(f"  {res}{num}:{nome} ... HEM:{p[2]} {d:.2f} A")
