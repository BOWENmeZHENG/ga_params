import os
import numpy as np
import ga_func


task = 'R_eff'
params = np.arange(3.0, 15.0, 1.0)
cuts = params + 3.0

seeds = [12, 13, 14, 15, 16]

os.makedirs(task, exist_ok=True)
for index, param in enumerate(params):
    for seed in seeds:
        ga_func.gen_ga(taskname=task, num_total=100, num_inc=100, mass_inc=1.0, sigma=param, cut=cuts[index],
                       num_cycle=8, ts=50000, anneal_temp=2000, nodes=4, time=5, seed=seed)
os.system(f"scp -r {task}/ bwzheng@login.expanse.sdsc.edu:/expanse/lustre/scratch/bwzheng/temp_project/paper/")