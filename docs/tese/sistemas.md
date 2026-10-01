# Sistemas e moléculas de interesse { #sistemas-e-moleculas-de-interesse }

!!! info "Diário do doutorado"

    Esta página faz parte do acompanhamento das etapas do meu doutorado.

!!! info "Versões fixadas para reprodutibilidade"

    Visando assegurar a reprodutibilidade computacional, o ambiente de simulação será 
    mantido estável nas versões Ubuntu 26.04 e GROMACS 2026.x, juntamente com suas respectivas bibliotecas. 
    Nenhuma atualização de software será realizada ao longo da pesquisa, salvo sob estrita necessidade 
    de correção para preservar a confiabilidade dos dados.

> Primeira etapa do projeto de doutorado: seleção, preparo e ajuste das
> moléculas de interesse que serão utilizadas nas simulações subsequentes.

## :lucide-file-text: Preprint e publicação relacionada

Este conteúdo também servirá como material suplementar do artigo
relacionado a esta etapa da pesquisa.

!!! warning "Em construção"

    Preprint e publicação serão adicionados aqui assim que disponíveis.

---
## Matrizes de sistemas

**Decisões fixadas:** ff19SB + OPC (proteína e água), GAFF2/AM1-BCC
(substratos), Shahrokh et al. 2012 (heme IC6 e CPDI), pH 7,5, NaCl 0,30 M,
298,15 K. A His85 é definida por um teste de sensibilidade (Etapa 1) antes da
produção.

**Princípio:** o Amber monta, o GROMACS roda. Proteína, heme, substrato, água e
íons entram num único `prmtop` (tleap); o `acpype` converte para GROMACS com os
CMAPs do ff19SB.

**Etapa 1 — teste de sensibilidade da His85**

| Estrutura | Heme | Substrato | His85 | Sistemas | Réplicas |
|---|---|---|---|---|---|
| 4L40 | IC6 | C14 | HID, HIE, HIP | 3 | 3 |
| 4L40 | CPDI | C14 | HID, HIE, HIP | 3 | 3 |

**Etapa 2 — produção, com o estado escolhido (X)**

| Estrutura | Heme | Substrato | His85 | Sistemas | Réplicas |
|---|---|---|---|---|---|
| 4L40 | IC6 | C8, C14, C20 (Tier 1) | X | 3 | 5 |
| 4L40 | IC6 | C10, C12, C16, C18 (Tier 2) | X | 4 | 3 |
| 4L40 | CPDI | C8, C14, C20 (Tier 1) | X | 3 | 5 |
| 4L40 | CPDI | C10, C12, C16, C18 (Tier 2) | X | 4 | 3 |
| 4L54 (APO) | IC6 | — | X | 1 | 5 |

São 6 montagens no teste e 15 na produção. O APO tem 5 réplicas porque é o
estado de referência de parâmetro de solvatação preferencial para o Tier 1 e precisa da mesma incerteza dos
complexos. APO só em IC6: o Composto I só se forma com substrato ligado. Os sistemas com etanol a 10 % entram depois,
na mesma estrutura de Tiers.

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
gmx --version     # precisa ser >= 2026.x
```

O acpype traz o AmberTools 26 (tleap, antechamber, sqm). O GROMACS ≥ 2026.x é
obrigatório para o ff19SB. O notebook de ajuste roda no ambiente dele.

---
## Passo 1 — Pasta de trabalho

Download dos arquivos 4L40 e 4L54 do PDB, e criação das pastas de trabalho conforme a estrutura do ambiente.

- Moléculas: [4L40](https://www.rcsb.org/structure/4L40) e [4L54](https://www.rcsb.org/structure/4L54).
- Scripts: [GitHub](https://github.com/patrickallanfaustino/patrickallanfaustino.github.io/tree/main/docs/assets/tese).
- Notebook: [v17](../assets/notebooks/protein_builder.ipynb)

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
| His85 | HID no JSON; HIE e HIP gerados no Passo 5 | só águas no NE2 nos dois cristais; decidido pelo teste (Passo 8a) |

pH 7,5; `keep_ligands: false` (heme e substrato entram nos Passos 5 e 7);
`aguas_enterradas: true`. Guarde de cada execução:

- `protonated.pdb` → copie como `02_montagem/protonated_4L40.pdb` e
  `02_montagem/protonated_4L54.pdb`;
- o arquivo de águas enterradas do notebook (`waters/proteina_com_aguas.pdb`),
  se quiser incluí-las no Passo 6.

---
## Passo 4 — Conferir a protonação na geometria final

O PDB2PQR gira anéis de His e amidas de Asn/Gln (N e C são indistinguíveis por
raio-X); por isso a conferência é feita no `protonated.pdb`, nunca no cristal
bruto. Primeiro junte o heme (Passo 5, só IC6), depois:

```bash
cd 02_montagem
python3 preparar_heme.py protonated_4L40.pdb ../4L40.pdb IC6 ph_4L40_IC6_h85HID.pdb
python3 ../00_protonacao/checar_rede_hbond.py ph_4L40_IC6_h85HID.pdb
```

Faça o mesmo com o 4L54 (`ph_4L54_IC6_h85HID.pdb`). São só duas triagens:
o CPDI usa o mesmo `protonated_4L40.pdb` (o O ferrila não alcança as His
triadas) e as variantes da His85 não mudam a rede das outras.

Esperado: His363 → HIP; His92/210/259/325 → "HIE ou HIP"; His85 → sem
parceiros (as águas só entram no Passo 6); Lys96 e Arg66 em ponte com os
propionatos.

---
## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
