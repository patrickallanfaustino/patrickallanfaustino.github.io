#!/bin/bash

gmx --version

cd rep1

gmx grompp -v -f inputs/md.mdp -c npt.gro -t npt.cpt -o md_200ns.tpr -p topol.top

gmx mdrun -v -deffnm md_200ns -cpt 10 -ntmpi 1 -ntomp 16 -gpu_id 0 -nb gpu -pme gpu -bonded gpu -pin on -maxh 23.4

#gmx mdrun -v -deffnm md_200ns -cpi md_200ns.cpt -cpt 10 -ntmpi 1 -ntomp 16 -gpu_id 0 -nb gpu -pme gpu -bonded gpu -pin on -maxh 23.4
