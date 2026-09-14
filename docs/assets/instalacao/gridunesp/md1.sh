#!/bin/bash

gmx --version

cd rep1

gmx grompp -v \
    -f inputs/md.mdp \
    -c npt.gro \
    -t npt.cpt \
    -o md_200ns.tpr \
    -p topol.top

# VARIANTE A — sistemas com SPC/E, TIP3P (sem virtual site)
# Offloading máximo: NB + PME + bonded + update na GPU
#gmx mdrun -v \
#    -deffnm md_200ns \
#    -ntmpi 1 \
#    -ntomp 16 \
#    -gpu_id 0 \
#    -nb gpu \
#    -pme gpu \
#    -bonded gpu \
#    -update gpu \
#    -pin on \
#    -maxh 23.4
#
# ------------------------------------------------------------
# VARIANTE B — sistemas com TIP4P/TIP4P-Ew (virtual site)
# -para sistemas pequenos/médios de ~150k atomos
# ------------------------------------------------------------
gmx mdrun -v \
    -deffnm md_200ns \
    -ntmpi 1 \
    -ntomp 16 \
    -gpu_id 0 \
    -nb gpu \
    -pme gpu \
    -bonded gpu \
    -pin on \
    -maxh 23.4
#
#
# ------------------------------------------------------------
# Para continuar a simulação
# ------------------------------------------------------------
#gmx mdrun -v \
#    -deffnm md_200ns \
#    -cpi md_200ns.cpt \
#    -ntmpi 1 \
#    -ntomp 16 \
#    -gpu_id 0 \
#    -nb gpu \
#    -pme gpu \
#    -bonded gpu \
#    -pin on \
#    -maxh 23.4