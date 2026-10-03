# Sistemas e moléculas de interesse { #sistemas-e-moleculas-de-interesse }

!!! info "Diário do doutorado"

    Esta página faz parte do acompanhamento das etapas do meu doutorado.

!!! info "Versões fixadas para reprodutibilidade"

    Visando assegurar a reprodutibilidade computacional, o ambiente de simulação será 
    mantido estável nas versões Ubuntu 26.04 e GROMACS 2026.x, juntamente com suas respectivas bibliotecas. 
    Nenhuma atualização de software será realizada ao longo da pesquisa, salvo sob estrita necessidade 
    de correção para preservar a confiabilidade dos dados.

---
## :lucide-file-text: Preprint e publicação relacionada

Este conteúdo também servirá como material suplementar do artigo
relacionado a esta etapa da pesquisa.

!!! warning "Em construção"

    Preprint e publicação serão adicionados aqui assim que disponíveis.

---
## Matrizes de sistemas

**Decisões fixadas:** ff19SB + OPC (proteína e água), GAFF2/AM1-BCC
(substratos), Shahrokh et al. 2012 (heme IC6 e CPDI), pH 7,5, NaCl 0,30 M,
298,15 K e 1 bar.

**Princípio:** o Amber cria os arquivos, o GROMACS realiza a dinâmica. Proteína, heme, substrato, água e
íons entram num único `prmtop` (tleap); o `acpype` converte para GROMACS com os
CMAPs do ff19SB.

| Estrutura | Heme | Substrato | His85 | Sistemas | Réplicas |
|---|---|---|---|---|---|
| 4L40 | IC6 | C8, C14, C20 (Tier 1) | HIE | 3 | 5 |
| 4L40 | IC6 | C10, C12, C16, C18 (Tier 2) | HIE | 4 | 3 |
| 4L40 | CPDI | C8, C14, C20 (Tier 1) | HIE | 3 | 5 |
| 4L40 | CPDI | C10, C12, C16, C18 (Tier 2) | HIE | 4 | 3 |
| 4L54 (APO) | IC6 | — | HIE | 1 | 5 |

---
## Estrutura do ambiente

```
oleT_montagem/
├── 00_protonacao/   4l40.json  4l54.json  checar_rede_hbond.py
├── 01_parametros/   IC6_*.mol2  IC6.frcmod  CPDI_*.mol2  CPDI.frcmod  CPDI_errata.frcmod
│                    extrair_shahrokh_si.py  extracao_si.log
├── 02_montagem/     preparar_heme.py  juntar_aguas.py  montar_sistema.py
├── 03_substrato/    preparar_substrato.py  normalizar_carga_mol2.py  parametrizar_substratos.sh
└── 04_gromacs/      renumerar_residuos.py  gerar_posres.py  validar_energias.py  rerun.mdp
```

---
## Passo 0 — Ambiente

```bash
python3 -m venv venv     # criar ambiente virtual
source venv/bin/activate
pip install acpype parmed openmm rdkit     # instalar dependências

A=$(python3 -c "import acpype,os;print(os.path.dirname(acpype.__file__))")
export AMBERHOME=$A/amber_linux  PATH=$A/amber_linux/bin:$PATH
tleap -h > /dev/null && echo "tleap ok"
gmx --version     # precisa ser >= 2026.x
```

O acpype traz o AmberTools 26 (tleap, antechamber, sqm). O GROMACS ≥ 2026.x é
obrigatório para o ff19SB.

---
## Passo 1 — Pasta de trabalho

Download dos arquivos 4L40 e 4L54 do PDB, e criação das pastas de trabalho conforme a estrutura do ambiente.

- Moléculas: [4L40](https://www.rcsb.org/structure/4L40) e [4L54](https://www.rcsb.org/structure/4L54).
- Scripts: [GitHub](../assets/tese/oleT_montagem.zip).
- Notebook: [v17](../assets/notebooks/protein_builder.ipynb) *necessita de adaptação!*

---
## Passo 2 — Parâmetros do heme (apenas conferir)

Os mol2/frcmod de IC6 e CPDI já estão em `01_parametros`, extraídos sem
alteração do suplementar de Shahrokh et al. (2012).

Conferência (`extracao_si.log`): HEM + CYP = −2,0000 em IC6 e em CPDI.
`CPDI_errata.frcmod` corrige o erro de digitação `cd-nd-fe-sh` do SI (sem ele
o tleap aborta).

---
## Passo 3 — Proteína: notebook v17 (duas execuções)

Rode o notebook com `00_protonacao/4l40.json` e depois com
`00_protonacao/4l54.json`. Os dois JSON fixam o **mesmo** conjunto de estados, cada um com fonte:

| Resíduo | Estado | Base |
|---|---|---|
| Cys365 | CYM | tiolato axial (cargas da CYP de Shahrokh aplicadas no Passo 8) |
| His363 | HIP | ND1···O2D propionato 2,68–2,77 Å; NE2···OD1 Asp88 2,80–2,86 Å |
| His92 | HIE | NE2 voltado ao propionato O1D |
| His210, His259, His325 | HIE | NE2 voltado a carbonilas |
| His120, His222 | HID | PROPKA neutras, sem parceiros polares |
| Lys96 | LYS | PROPKA 7,8–7,9 sem o heme; NZ em ponte salina com o propionato D (2,56–2,73 Å) |
| Arg245 | ARG | PROPKA 8,3 sem substrato; pKa intrínseco da Arg ≈ 13,8 (Fitch et al. 2015); liga o carboxilato |
| His85 | HIE | por decisão |

**pH 7,5.** É a condição de máxima atividade relatada para a OleT_JE (Phaisan
et al. 2025, *JBC*; tampão 50 mM NaH₂PO₄, 300 mM NaCl, pH 7,5). O perfil de pH
desse trabalho é esparso (fosfato só em 7,5, acetato até 6, pirofosfato a
partir de 9): escreva "condição de máxima atividade relatada", não "pH ótimo
determinado". Os Kd da série (Belcher et al. 2014) foram medidos a pH 7,0; os
estados atribuídos são os mesmos a 7,0 e 7,5 (único limítrofe: His210, pKa
6,3, protonada ~6 % a 7,5 e ~17 % a 7,0), então a comparação com esses Kd não
tem viés de pH.

pH 7,5; `keep_ligands: false` (heme e substrato entram nos Passos 5 e 7);
`aguas_enterradas: true`. Guarde de cada execução:

- `protonated.pdb` → copie como `02_montagem/protonated_4L40.pdb` e
  `02_montagem/protonated_4L54.pdb`;
- o arquivo de águas enterradas do notebook (`waters/proteina_com_aguas.pdb`),
  para 4L40 e 4L54, se quiser incluí-las no Passo 6.

---
## Passo 4 — Conferir a protonação na geometria final

O PDB2PQR gira anéis de His e amidas de Asn/Gln (N e C são indistinguíveis por
raio-X); por isso a conferência é feita no `protonated.pdb` com o heme, nunca
no cristal bruto. Os arquivos de heme IC6 gerados aqui, já com a His85 em HIE,
são os mesmos usados na montagem (Passo 8): não é preciso refazê-los no
Passo 5.

4L40:

```bash
cd 02_montagem
python3 preparar_heme.py protonated_4L40.pdb ../4L40.pdb IC6 ph_4L40_IC6.pdb 85=HIE
python3 ../00_protonacao/checar_rede_hbond.py ph_4L40_IC6.pdb
```

4L54:

```bash
python3 preparar_heme.py protonated_4L54.pdb ../4L54.pdb IC6 ph_4L54_IC6.pdb 85=HIE
python3 ../00_protonacao/checar_rede_hbond.py ph_4L54_IC6.pdb
```

São só essas duas triagens: o CPDI (Passo 5) usa o mesmo
`protonated_4L40.pdb`, e o O ferrila não alcança as His triadas.

O `preparar_heme.py` deve imprimir, em cada uma:

- "Residuo 85: HID -> HIE" (ou "HIE -> HIE");
- Fe–SG entre 2,0 e 2,6 Å (4L40: 2,28; 4L54: 2,21);
- HEM com 43 átomos e "HEM renumerado para 423".

Triagem esperada nas duas estruturas:

| His | Sugestão esperada | Estado fixado |
|---|---|---|
| His363 | HIP | HIP |
| His92, His210, His259, His325 | "HIE ou HIP" | HIE |
| His85 | sem parceiros (as águas só entram no Passo 6) | HIE |
| His120, His222 | sem parceiros | HID |

---
## Passo 5 — Heme do CPDI

Os dois arquivos IC6 já saíram do Passo 4. Falta só o CPDI do 4L40:

```bash
python3 preparar_heme.py protonated_4L40.pdb ../4L40.pdb CPDI ph_4L40_CPDI.pdb 85=HIE
```

Deve imprimir "Residuo 85: … -> HIE", Fe–SG 2,28 Å, "O1 posicionado: Fe-O1
1.639 A, S-Fe-O1 171 graus" e HEM com 44 átomos (43 + O1), renumerado para
423. O `85=HIE` troca só o nome do resíduo; o tleap reconstrói os H pelo nome,
então não é preciso rodar o notebook de novo.

Ao fim dos Passos 4 e 5, em `02_montagem`:

| Arquivo | Estrutura | Heme | Usado no Passo 8 para |
|---|---|---|---|
| `ph_4L40_IC6.pdb` | 4L40 | IC6 | complexos IC6, C8–C20 |
| `ph_4L40_CPDI.pdb` | 4L40 | CPDI | complexos CPDI, C8–C20 |
| `ph_4L54_IC6.pdb` | 4L54 | IC6 | APO |

---
## Passo 6 — Águas cristalográficas

```bash
python3 juntar_aguas.py ../4L40.pdb "709 710" aguas_4L40_IC6.pdb ../00_protonacao/output_4L40_A/waters/proteina_com_aguas.pdb
python3 juntar_aguas.py ../4L40.pdb "710" aguas_4L40_CPDI.pdb ../00_protonacao/output_4L40_A/waters/proteina_com_aguas.pdb
python3 juntar_aguas.py ../4L54.pdb "628 689 691" aguas_4L54.pdb ../00_protonacao/output_4L54_A/waters/proteina_com_aguas.pdb
```

São dois grupos de águas, e os dois são necessários:

- **Águas do bolso distal**, escolhidas pelo número (seleção deste guia: todas
  as águas do cristal a até ~7 Å do Fe):
  - 4L40, IC6: W709 (3,3 Å do Fe, ponte com o carboxilato; é a água descrita
    por Belcher et al. 2014) e W710 (His85).
  - 4L40, CPDI: só a W710 — a W709 fica a 1,86 Å do O ferrila, que ocupa o
    sítio dela.
  - 4L54: W691 (2,81 Å do Fe), W689 (His85, Arg245) e W628 (conformação A, no
    lugar do carboxilato; opcional, densidade suspeita — registre a escolha).
- **Águas enterradas do notebook**

---
## Passo 7 — Substratos C8–C20

```bash
cd ../03_substrato
bash parametrizar_substratos.sh ../4L40.pdb 8 10 12 14 16 18 20
cd ../02_montagem
```

O script confere antes se `antechamber`, `parmchk2` e `sqm` estão no PATH (o
Passo 0 precisa ter sido feito **no mesmo terminal**) e imprime qual
`antechamber` vai usar; se algum ambiente conda tiver outro AmberTools, o
caminho mostra. Se o antechamber falhar, o script mostra o final do log e do
`sqm.out`. O aviso do RDKit "More than one matching pattern found" é esperado:
os dois O do carboxilato são equivalentes.

Cada cadeia sai da pose do C20 cristalográfico (carboxilato na posição exata,
ponte com a Arg245; só a cauda é encurtada), com GAFF2/AM1-BCC e carga
normalizada a −1,000000. Saída por cadeia: `Cn_pose.sdf`, `Cn.mol2`,
`Cn.frcmod`, `Cn_antechamber.log`, `Cn_sqm.out`.

---
## Passo 8 — Montagem

```bash
for n in 8 10 12 14 16 18 20; do
  python3 montar_sistema.py --estado IC6  --substrato C$n --pdb ph_4L40_IC6.pdb --aguas aguas_4L40_IC6.pdb  --rotulo 4L40
  python3 montar_sistema.py --estado CPDI --substrato C$n --pdb ph_4L40_CPDI.pdb --aguas aguas_4L40_CPDI.pdb --rotulo 4L40
done

python3 montar_sistema.py --estado IC6 --substrato none --pdb ph_4L54_IC6.pdb --aguas aguas_4L54.pdb --rotulo 4L54
```

Cerca de 3 min por sistema. Cada um gera `sistema_<rotulo>_<estado>_<Cn|apo>/`
com `sistema.prmtop`, `soluto.prmtop`, `relatorio_montagem.json` e
`sistema.amb2gmx/` (`sistema_GMX.top`, `sistema_GMX.gro`, `posre_*.itp`).
Os demais parâmetros (ff19SB/OPC, octaedro de 12 Å, NaCl 0,30 M) ficam no topo
do script.

O script para, com mensagem, se:

- a carga de proteína+heme, de HEM+CYM ou do substrato não for inteira;
- o ff19SB não tiver 14 tipos de CMAP;
- uma água cristalográfica estiver em choque ou for trocada por íon;
- o `.gro` e o `.top` divergirem em qualquer átomo.

Valores esperados no relatório:

| | proteína+heme | HEM+CYM | substrato | total | Fe–SG r₀ |
|---|---|---|---|---|---|
| IC6 + Cn | −8 | −2 | −1 | −9 | 2,660 Å |
| CPDI + Cn | −8 | −2 | −1 | −9 | 2,565 Å |
| APO (IC6) | −8 | −2 | — | −8 | 2,660 Å |


Íons pelo SLTCAP a partir da contagem de águas do bulk (ex.: 27 036 águas,
Q = −9 → 152 Na⁺ e 142 Cl⁻).

---
## :lucide-book-search: Referências
- Shahrokh K, Orendt A, Yost GS, Cheatham TE III. *J Comput Chem* 2012, 33, 119–133.
- Belcher J et al. *J Biol Chem* 2014, 289, 6535–6550 (PDB 4L40, 4L54).
- Matthews S et al. *J Biol Chem* 2017, 292 (His85, Phe79, Arg245).
- Tian C et al. *J Chem Theory Comput* 2020, 16, 528–552 (ff19SB).
- Izadi S, Anandakrishnan R, Onufriev AV. *J Phys Chem Lett* 2014, 5, 3863–3871 (OPC).
- Sengupta A et al. *J Chem Inf Model* 2021, 61 (íons 12-6 para OPC).
- Schmit JD et al. *J Chem Theory Comput* 2018, 14, 1823–1827 (SLTCAP).
- Sousa da Silva AW, Vranken WF. *BMC Res Notes* 2012, 5, 367 (ACPYPE).
- Roe DR, Brooks BR. *J Chem Phys* 2020, 153, 054123 (equilibração).
- Olsson MHM et al. *J Chem Theory Comput* 2011, 7, 525–537 (PROPKA3).
- Wyman J. *Adv Protein Chem* 1964, 19, 223–286.
- Yadav S et al. (grupo de S. Shaik e K. D. Dubey). Local electric fields dictate function: the different product selectivities observed for fatty acid oxidation by two deceptively very similar P450-peroxygenases OleT and BSβ. *J Chem Inf Model* 2022. doi:10.1021/acs.jcim.1c01453
- Grupo de S. Shaik e K. D. Dubey. On the engineering of reductase-based-monooxygenase activity in CYP450 peroxygenases. *Chem Sci* 2024. doi:10.1039/D3SC06538C
- Phaisan et al. Unique structural features define the decarboxylation activity of a CYP152 fatty acid decarboxylase from *Lacicoccus alkaliphilus*. *J Biol Chem* 2025.
- Fitch CA et al. Arginine: its pKa value revisited. *Protein Sci* 2015, 24, 752–761.
- Wang et al. Mutagenesis and redox partners analysis of the P450 fatty acid decarboxylase OleTJE. *Sci Rep* 2017, 7, 44258.
- Timasheff SN. *Proc Natl Acad Sci USA* 2002, 99, 9721–9726.

---
## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
