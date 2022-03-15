#!\bin\bash

for path in outputs-*; do 
    echo $path
    /home/pciunkiewicz/miniconda3/envs/covid/bin/python export.py stats2 scenarios/eng301.json $path --flat=1 &> /dev/null; 
done