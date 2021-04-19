#!/bin/bash


# Time in days-hours. Change this as much as you want
#SBATCH --time=5-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=20000M

python3 CountryLOO.py

