import numpy as np
import math
import os, shutil
import utils, write

MASS_C = 12.01e-3 / 6.0221e23  # kg
DENSITY_INITIAL = 1  # kg/m3

def gen_ga(taskname, num_total, num_inc, mass_inc, sigma, cut, num_cycle, ts, anneal_temp, seed):

    np.random.seed(seed)

    flakes, p = utils.load_flakes()
    C_num_flakes = [len(flake) for flake in flakes]
    num_flakes = [int(num) for num in num_total * p]
    num_total_real = sum(num_flakes)
    C_num_atoms = np.inner(C_num_flakes, num_flakes)

    Total_mass_C = C_num_atoms * MASS_C
    volume_initial = Total_mass_C / DENSITY_INITIAL * 1e30  # A3
    L_box = volume_initial**(1/3)  # A


    # Placing flakes & inclusions
    # Initial points: 0.05 to 0.95 box
    coors_inclusions = []
    for i in range(num_inc):
        coors_inclusion = (0.05 + 0.95 * np.random.random(3) - 0.5) * L_box
        coors_inclusions.append(coors_inclusion)
    coors_inclusions = np.array(coors_inclusions)

    # All points
    coors_flakes_all = []
    for index, num in enumerate(num_flakes):
        coors_flake_local = flakes[index]
        for i in range(num):
            coor_init = (0.05 + 0.95 * np.random.random(3) - 0.5) * L_box
            t = np.random.random() * math.pi
            Rx = np.array([[1, 0, 0], [0, math.cos(t), -math.sin(t)], [0, math.sin(t), math.cos(t)]]) #  [1,0,0;0,cos(t),-sin(t);0,sin(t),cos(t)]
            Ry = np.array([[math.cos(t), 0, math.sin(t)], [0, 1, 0], [-math.sin(t), 0, math.cos(t)]]) #  [cos(t),0,sin(t);0,1,0;-sin(t),0,cos(t)]
            Rz = np.array([[math.cos(t), -math.sin(t), 0], [math.sin(t), math.cos(t), 0], [0, 0, 1]]) #  [cos(t),-sin(t),0;sin(t),cos(t),0;0,0,1]
            R = Rx @ Ry @ Rz
            coors_flake_global = coor_init + coors_flake_local @ R
            coors_flakes_all.append(coors_flake_global)
    coors_flakes_all = np.vstack(coors_flakes_all)

    data_prefix, in_prefix, all_prefix = write.write_files(num_total_real, coors_flakes_all, coors_inclusions, L_box, mass_inc, seed,
                                                           sigma, cut, num_cycle, ts, anneal_temp)
    folder = '_' + all_prefix
    os.makedirs(folder, exist_ok=True)
    files = os.listdir('./')
    for file in files:
        if file.startswith('data.') or file.startswith('in.'): #  or file.startswith('sh.'):
            shutil.move(file, f'{folder}/{file}')
    shutil.copyfile('CH.airebo', f'{folder}/CH.airebo')
    shutil.move(folder, f'{taskname}/{folder}')

    return data_prefix, in_prefix, folder


def write_sh(task, folder_list, in_prefix, param, nodes, time, tasks_per_node=32, mem=16):
    filename = f'{task}_{param}.sh'
    with open(filename, 'w') as f:
        f.write('#!/bin/bash\n')
        f.write(f'#SBATCH --job-name="{task}_{param}"\n')
        f.write(f'#SBATCH --output="out.{task}_{param}"\n')
        f.write('#SBATCH --partition=compute\n')
        f.write('#SBATCH --constraint="lustre"\n')
        f.write(f'#SBATCH --nodes={nodes}\n')
        f.write(f'#SBATCH --ntasks-per-node={tasks_per_node}\n')
        f.write(f'#SBATCH --mem={mem}G\n')
        f.write('#SBATCH --account="ucb312"\n')
        f.write('#SBATCH --export=ALL\n')
        f.write(f'#SBATCH -t {time}:00:00\n')
        f.write('\n')
        f.write('module load   slurm\n')
        f.write('module load   gcc/10.2.0\n')
        f.write('module load   openmpi/4.0.4\n')
        f.write('module load   lammps/20200721-openblas\n')
        f.write('\n')
        for folder in folder_list:
            f.write(f'cd {folder}\n')
            f.write(f'srun lmp -in in.{in_prefix}\n')
            f.write(f'srun lmp -in in.tension\n')
            f.write(f'srun lmp -in in.compression\n')
            f.write('cd ..\n')
            f.write('\n')
    return filename