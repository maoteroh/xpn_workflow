#!/bin/bash
#SBATCH --job-name=motero
#SBATCH --output=/beegfs/home/javier.garciablas/m_otero/RES/mpi_%j.out
#SBATCH --error=/beegfs/home/javier.garciablas/m_otero/RES/mpi_%j.out
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --cpus-per-task=2
#SBATCH --time=01:00:00

echo ${SLURM_JOBID}
echo ${SLURM_NNODES}
echo ${SLURM_JOB_NODELIST}

scontrol show hostnames ${SLURM_JOB_NODELIST} > $HOME/m_otero/tmp/machinefile.${SLURM_JOBID}

echo "[partition]"                 > $HOME/m_otero/tmp/config.${SLURM_JOBID}.txt
echo "bsize = 512k"               >> $HOME/m_otero/tmp/config.${SLURM_JOBID}.txt
echo "replication_level = 0"      >> $HOME/m_otero/tmp/config.${SLURM_JOBID}.txt
echo "partition_name = xpn"       >> $HOME/m_otero/tmp/config.${SLURM_JOBID}.txt
ITER=1
while IFS= read -r line
do
   echo "server_url = mpi_server://$line//dev/shm"    >> $HOME/m_otero/tmp/config.${SLURM_JOBID}.txt
   #echo "server_url = mpi_server://$line/$TMPDIR"     >> $HOME/m_otero/tmp/config.${SLURM_JOBID}.txt
   ITER=$((${ITER}+1))
done < $HOME/m_otero/tmp/machinefile.${SLURM_JOBID}

echo "---------------- SERVER ------------------"

#export LD_LIBRARY_PATH=/beegfs/home/javier.garciablas/m_otero/xpn/bin/mpich/lib/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/beegfs/home/javier.garciablas/m_otero/xpn/bin/mpich/lib/:/beegfs/home/javier.garciablas/m_otero/xpn/syscall_intercept/lib:/beegfs/home/javier.garciablas/m_otero/xpn/capstone/lib:$LD_LIBRARY_PATH
export PATH=/beegfs/home/javier.garciablas/m_otero/xpn/bin/mpich/bin/:$PATH
export PSM2_KASSIST_MODE=none

srun -n ${SLURM_NNODES} --exclusive \
     -w $HOME/m_otero/tmp/machinefile.${SLURM_JOBID} \
     --export=ALL \
     --cpus-per-task=20 --verbose \
     /beegfs/home/javier.garciablas/m_otero/xpn/bin/xpn/bin/xpn_server &

sleep 2

echo "---------------- CLIENT ------------------"

export XPN_CONF=$HOME/m_otero/tmp/config.${SLURM_JOBID}.txt 
export XPN_LOCALITY=0
export XPN_SESSION=0
export XPN_THREAD=0
export XPN_DEBUG=1
#export LD_PRELOAD=$HOME/m_otero/xpn/bin/xpn/lib/xpn_bypass.so
export LD_PRELOAD=$HOME/m_otero/xpn/bin/xpn/lib/xpn_syscall_intercept.so
export INTERCEPT_LOG=logs/intercept.log-

NP=$((${SLURM_NNODES} * 8))
NP=1
srun -n ${NP} --exclusive \
     -w $HOME/m_otero/tmp/machinefile.${SLURM_JOBID} \
     --export=ALL \
     --cpus-per-task=2 --verbose \
     $HOME/m_otero/xpn/data/workflow/load_files demo1.txt /tmp/expand/xpn/demo1.txt
     
srun -n ${NP} --exclusive \
     -w $HOME/m_otero/tmp/machinefile.${SLURM_JOBID} \
     --export=ALL \
     --cpus-per-task=2 --verbose \
     $HOME/m_otero/xpn/data/workflow/validar_pgms demo1.txt /tmp/expand/xpn/demo1.txt 

sleep 2
pkill mpiexec
pkill xpn_server
