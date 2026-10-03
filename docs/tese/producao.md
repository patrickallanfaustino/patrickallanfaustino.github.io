# Dinâmica Molecular da OleT_JE    {#dinamica-molecular-da-olet-je}

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
## Sistemas

- md.mdp: 400 ns no Tier 1, Tier 2 e no APO.
- Réplicas: 5 no Tier 1 e no APO, 3 no Tier 2.
- Sistemas com etanol a 10 %: ainda precisam de uma etapa de montagem própria antes de rodar.

---
## Estrutura do ambiente

```
sistema_4L54_IC6_apo
├── rep1
│   ├── em
│   ├── inputs
│   │   ├── em1_rest.mdp
│   │   ├── em2_rest.mdp
│   │   ├── em3_rest.mdp
│   │   ├── em4_free.mdp
│   │   ├── md.mdp
│   │   ├── npt1.mdp
│   │   ├── npt2.mdp
│   │   ├── npt3.mdp
│   │   ├── npt4.mdp
│   │   ├── nvt1_heat.mdp
│   │   └── nvt2_hold.mdp
│   ├── md
│   ├── npt
│   ├── nvt
│   ├── posre_bb.itp
│   ├── posre_heme.itp
│   ├── posre_sc.itp
│   ├── sistema_GMX.gro
│   ├── sistema_GMX.top
│   └── workflow.txt
├── rep2
├── rep3
├── rep4
└── rep5
```

Cada sistema terá a sua estrutura de pastas, com as devidas réplicas.

Os arquivos de entrada (`.mdp`) estão em `inputs/` e podem ser baixados em [oleT_mdp.zip](../assets/tese/oleT_mdp.zip).

---
## Sementes das réplicas

Cada semente segue o padrão **777 + réplica + etapa**: `777` fixo, um dígito
para a réplica (1–5) e dois dígitos para a ordem da semente no protocolo
(01–08). Assim, cada réplica parte de velocidades próprias e usa um ruído
próprio no termostato V-rescale.

| Etapa | Parâmetro | rep1 | rep2 | rep3 | rep4 | rep5 |
|---|---|---|---|---|---|---|
| `nvt1_heat` | `gen-seed` | 777101 | 777201 | 777301 | 777401 | 777501 |
| `nvt1_heat` | `ld-seed` | 777102 | 777202 | 777302 | 777402 | 777502 |
| `nvt2_hold` | `ld-seed` | 777103 | 777203 | 777303 | 777403 | 777503 |
| `npt1` | `ld-seed` | 777104 | 777204 | 777304 | 777404 | 777504 |
| `npt2` | `ld-seed` | 777105 | 777205 | 777305 | 777405 | 777505 |
| `npt3` | `ld-seed` | 777106 | 777206 | 777306 | 777406 | 777506 |
| `npt4` | `ld-seed` | 777107 | 777207 | 777307 | 777407 | 777507 |
| `md` | `ld-seed` | 777108 | 777208 | 777308 | 777408 | 777508 |

Os arquivos do `oleT_mdp.zip` trazem as sementes da rep1. Nas demais réplicas,
troque o dígito da réplica antes do `grompp`. O Tier 2 usa só rep1–rep3.

---
## Configuração do ambiente

```
Versão do GROMACS         : 2026.4
Campo de força            : ff19SB + OPC
Parametrização não-padrão : GAFF2/AM1-BCC (ACPYPE)
Estrutura de partida      : https://www.rcsb.org/structure/4L54
Protonação                : Notebook v17 | MODELLER | PDBFIXER | PDB2PQR | PROPKA | pH 7.5
Sementes                  : 5 rep. x 400 ns
Arquivos .mdp             : mdout.mdp
Ambiente                  : Ubuntu 26.04.1 LTS | CUDA 13.4 | Ryzen 9 5900XT | RTX 4070 Ti
```

---
## Workflow

```bash
=============
MINIMIZAÇÃO
=============
gmx grompp -v -f ../inputs/em1_rest.mdp -c ../sistema_GMX.gro -r ../sistema_GMX.gro -p ../sistema_GMX.top -o em1.tpr
gmx mdrun -v -deffnm em1

gmx grompp -v -f ../inputs/em2_rest.mdp -c em1.gro -r ../sistema_GMX.gro -p ../sistema_GMX.top -o em2.tpr
gmx mdrun -v -deffnm em2

gmx grompp -v -f ../inputs/em3_rest.mdp -c em2.gro -r ../sistema_GMX.gro -p ../sistema_GMX.top -o em3.tpr
gmx mdrun -v -deffnm em3

gmx grompp -v -f ../inputs/em4_free.mdp -c em3.gro -r ../sistema_GMX.gro -p ../sistema_GMX.top -o em4.tpr
gmx mdrun -v -deffnm em4
gmx energy -f em4.edr -s em4.tpr -o em4_potential.xvg
xmgrace em4_potential.xvg

==========================
CONFERENCIA DE CMAPS (limite 1,7–1,8×10³ kJ/mol)
==========================

printf "CMAP-Dih.\n\n" | gmx energy -f em1.edr -o cmap_em1.xvg && grep -v '^[#@]' cmap_em1.xvg | head -1
xmgrace cmap_em1.xvg

=============
NVT REPLICAS AQUI
=============
gmx grompp -v -f ../inputs/nvt1_heat.mdp -c ../em/em4.gro -r ../em/em4.gro -p ../sistema_GMX.top -o nvt1.tpr
gmx mdrun -v -deffnm nvt1
gmx energy -f nvt1.edr -o qc_temperatura.xvg
xmgrace qc_temperatura.xvg

gmx grompp -v -f ../inputs/nvt2_hold.mdp -c nvt1.gro -r ../em/em4.gro -t nvt1.cpt -p ../sistema_GMX.top -o nvt2.tpr
gmx mdrun -v -deffnm nvt2

=============
NPT
=============
gmx grompp -v -f ../inputs/npt1.mdp -c ../nvt/nvt2.gro -r ../em/em4.gro -t ../nvt/nvt2.cpt -p ../sistema_GMX.top -o npt1.tpr
gmx mdrun -v -deffnm npt1

gmx grompp -v -f ../inputs/npt2.mdp -c npt1.gro -r ../em/em4.gro -t npt1.cpt -p ../sistema_GMX.top -o npt2.tpr
gmx mdrun -v -deffnm npt2

gmx grompp -v -f ../inputs/npt3.mdp -c npt2.gro -r ../em/em4.gro -t npt2.cpt -p ../sistema_GMX.top -o npt3.tpr
gmx mdrun  -v -deffnm npt3

gmx grompp -v -f ../inputs/npt4.mdp -c npt3.gro -t npt3.cpt -p ../sistema_GMX.top -o npt4.tpr
gmx mdrun -v -deffnm npt4
gmx energy -f npt4.edr -o qc_densidade.xvg
xmgrace qc_densidade.xvg
gmx energy -f npt4.edr -o qc_energia.xvg
xmgrace qc_energia.xvg
gmx energy -f npt4.edr -o qc_pressao.xvg
xmgrace qc_pressao.xvg

=============
MD
=============
gmx grompp -v -f ../inputs/md.mdp -c ../npt/npt4.gro -t ../npt/npt4.cpt -p ../sistema_GMX.top -o md_400ns.tpr
gmx mdrun -v -deffnm md_400ns
```

As replicas de cada sistema serão executadas no gridUNESP.

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
