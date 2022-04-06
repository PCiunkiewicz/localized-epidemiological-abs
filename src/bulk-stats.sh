#!\bin\bash

for path in data/outputs-*; do
    echo $path
    /home/pciunkiewicz/miniconda3/envs/covid/bin/python export.py stats2 data/scenarios/eng301.json $path --flat=1 &> /dev/null;
done
