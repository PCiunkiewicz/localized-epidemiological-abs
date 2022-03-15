#!\bin\bash

for i in `seq 0 1000 9000`; do 
    sync && echo 3 | tee /proc/sys/vm/drop_caches
    /home/pciunkiewicz/miniconda3/envs/covid/bin/python launch.py run-parallel scenarios/eng301.json -n 6 -r 1000 -o $i; 
done