#!/bin/bash
#SBATCH -t 23:30:00
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=8G
#SBATCH --job-name=run_rep1
#SBATCH --mail-user=<youremail>@unesp.br
#SBATCH --mail-type=ALL

export INPUT="rep1 gromacs-gpu.sif md1.sh"
export OUTPUT="*"
export VERBOSE="1"
export WAIT_CHECKPOINT="3600"

module load gcc/14.3.0
module load cuda/12.9

echo "Job iniciado em: $(date)"
echo "Rodando em: $(hostname)"
echo "Diretório: $(pwd)"
echo "Nós alocados: $SLURM_NODELIST"
echo ""

# Executa o script dentro do container
job-nanny apptainer exec --nv gromacs-gpu.sif bash md1.sh

echo ""
echo "Job finalizado em: $(date)"
