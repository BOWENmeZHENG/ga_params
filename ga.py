import numpy as np
import math
import os, shutil
import utils, write

MASS_C = 12.01e-3 / 6.0221e23  # kg
DENSITY_INITIAL = 1  # kg/m3

num_total = 400
num_inc = 1200
mass_inc = 0.1
seed = 12
sigma = 15
cut = 21
num_cycle = 10
ts = 100000
anneal_temp = 4000
nodes = 16
tasks_per_node = 32
mem = 16
time = 5

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
# utils.plot_3D(coors_flakes_all, coors_inclusions)


data_prefix, in_prefix, all_prefix = write.write_files(num_total_real, coors_flakes_all, coors_inclusions, L_box, mass_inc, seed,
                                                       sigma, cut, num_cycle, ts, anneal_temp,
                                                       nodes, tasks_per_node, mem, time)
folder = '_' + all_prefix
os.makedirs(folder, exist_ok=True)
files = os.listdir('./')
for file in files:
    if file.startswith('data.') or file.startswith('in.') or file.startswith('sh.'):
        shutil.move(file, f'{folder}/{file}')
shutil.copyfile('CH.airebo', f'{folder}/CH.airebo')


# upload files to supercomputer
os.system(f"scp -r {folder}/ bwzheng@login.expanse.sdsc.edu:/expanse/lustre/scratch/bwzheng/temp_project/")

# Automatically run
# os.system("ssh bwzheng@login.expanse.sdsc.edu")
# os.system(f"cd /expanse/lustre/scratch/$USER/temp_project")  # /{folder}
# os.system(f"sbatch sh.{all_prefix}")