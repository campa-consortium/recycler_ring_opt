#!/bin/sh

#SBATCH --job-name="RR-dpop-grid"
#SBATCH --time=07:59:59
#SBATCH --partition=gpu_gce
#SBATCH --nodelist=wcgpu06
#SBATCH --gres=gpu:1
#SBATCH --error='%A.err'
#SBATCH --output='%A.out'

module load git
module load tmux
module load cmake
module load gnu9
module load openmpi3
module load cuda11

export LOCAL_ROOT=/work1/accelsim/qlu/local
export PATH=$LOCAL_ROOT/bin:$PATH
export LD_LIBRARY_PATH=$LOCAL_ROOT/lib:$LOCAL_ROOT/lib64:$LD_LIBRARY_PATH
export SYN_SRC=/work1/accelsim/gonza839/synergia2
export PYTHONPATH=/work1/accelsim/gonza839/synergia2/build/src

mpirun -np 1 python3 rr_noSC.py

mkdir norf
mv diag_particles_* norf/.
mv diag_full* norf/.
