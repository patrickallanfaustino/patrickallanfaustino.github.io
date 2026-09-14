#!/bin/bash
#SBATCH -t 00:30:00
#SBATCH --job-name=gmx_gpu
#SBATCH --cpus-per-task=32
#SBATCH --mail-user=<yourmail>@unesp.br
#SBATCH --mail-type=BEGIN,END,FAIL

export INPUT="gromacs-gpu.def"
export OUTPUT="*"
export VERBOSE="1"

job-nanny apptainer build gromacs-gpu.sif gromacs-gpu.def
