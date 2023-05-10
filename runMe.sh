module load git
module load tmux
module load cmake
module load gnu9
module load openmpi3
module load cuda11

export LOCAL_ROOT=/work1/accelsim/qlu/local
export PATH=$LOCAL_ROOT/bin:$PATH
export LD_LIBRARY_PATH=$LOCAL_ROOT/lib:$LOCAL_ROOT/lib64:$LD_LIBRARY_PATH

export SYN_SRC='/work1/accelsim/gonza839/synergia2'
export PYTHONPATH='/work1/accelsim/gonza839/synergia2/build/src'
