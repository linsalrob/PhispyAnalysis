#!/bin/bash

###############################################################
#                                                             #
# Check for PhiSpy completeness, whether the job finished     #
# and whether we have run checkv and mash.                    #
#                                                             #
#                                                             #
###############################################################


# Time in days-hours. Change this as much as you want
#SBATCH --time=5-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=200M

#SBATCH --output=find_files_%A.txt

find phispy -type f -mindepth 3 -maxdepth 3
