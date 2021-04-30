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
#SBATCH --time=1-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=2000M


if [ $# -ne 1 ]; then echo `basename $0` " <GENOME BASE NAME> (e.g. GCA_000006155.2_ASM615v2)"; exit 1; fi

BASE=$1
PHISPYDIR='phispy'
FILE="$PHISPYDIR/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_phage.gbk.gz"
if [ ! -e "$FILE" ]; then echo "$FILE for $BASE does not exist"; exit 1; fi

OUT=$(echo $FILE | sed -e 's/phage.gbk.gz/annotations.txt/');
if [ -e ${OUT}.gz ]; then rm -f $OUT.gz; fi
python3 ~/GitHubs/EdwardsLab/bin/genbank2sequences.py -g $FILE -f $OUT
gzip $OUT;

