#!/bin/bash

###############################################################
#                                                             #
# Extract all the VOG hits for each genome. We run 1000       #
# genomes for each job so that we can get them all done!      #
#                                                             #
#                                                             #
# submit with this command:                                   #
#                                                             #
# sbatch --array=1-130:1000 ./array.slurm                     #
#                                                             #
###############################################################


# Time in days-hours. Change this as much as you want
#SBATCH --time=5-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=2000M

#SBATCH --output=clean_up/vog_output.%A_%a.out


BASE=$1
PHISPYDIR='phispy'
FILE="$PHISPYDIR/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_phage.gbk.gz"

perl print_vog_hits.pl $FILE;

