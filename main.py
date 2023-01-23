import os, shutil
import numpy as np
import ga_func


seeds = [12, 13, 14, 15, 16]

# Varying parameter(s)
task = 'num_inc'
params = np.arange(100, 1200, 200, dtype=int)
# cuts = params + 3.0

# Constants
num_total = 200
# num_inc = 200
sigma = 5
cut = 8
mass_inc = 1.0
num_cycle = 10
ts = 50000
anneal_temp = 2000

# Job settings
nodes = 8
time = 25

# Main code
os.makedirs(task, exist_ok=True)
for index, param in enumerate(params):
    folder_list = []
    for seed in seeds:
        _, in_prefix, folder = ga_func.gen_ga(taskname=task, num_total=num_total, num_inc=param,
                                              mass_inc=mass_inc, sigma=sigma, cut=cut,
                                              num_cycle=num_cycle, ts=ts, anneal_temp=anneal_temp, seed=seed)
        folder_list.append(folder)
    # Write shell script to run many tasks
    filename = ga_func.write_sh(task, folder_list, in_prefix, param, nodes, time)
    shutil.move(filename, f'{task}/{filename}')
os.system(f"scp -r {task}/ bwzheng@login.expanse.sdsc.edu:/expanse/lustre/scratch/bwzheng/temp_project/paper/")