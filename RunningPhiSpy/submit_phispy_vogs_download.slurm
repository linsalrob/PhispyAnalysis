#!/bin/bash

###############################################################
#                                                             #
#                                                             #
# submit with this command:                                   #
#                                                             #
# sbatch --array=1-130:1 ./array.slurm                        #
#                                                             #
# to submit so that only 4 jobs run at a time                 #
#                                                             #
# sbatch --array=1-130%4 ./array.slurm                        #
#                                                             #
###############################################################


# Time in days-hours. Change this as much as you want
#SBATCH --time=5-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=16G
#SBATCH -o submit_phispy/submit_phispy-%j.out
#SBATCH -e submit_phispy/submit_phispy-%j.err

## How to get the files 
#
# DATE=`date +%Y%m%d`
# mkdir $DATE
# curl -Lo $DATE/assembly_summary_$DATE.txt ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt
# get a file we need some how and then split it up
# mkdir -p $DATE/needed/; cd $DATE/needed
# scp ah:/home3/redwards/phage/prophage/phispy_prophage_20200618/20220525/needed/deepthought_needed .
# split -a 4 --numeric-suffixes=1 -l 100 deepthought_needed
# cd ..


DATE=20220606
ASS=$DATE/assembly_summary_$DATE.txt.gz
VOGS=/home/edwa0468/VOGs/vog99/VOGs.hmm

NEED=0000$SLURM_ARRAY_TASK_ID
NEED=${NEED:(-4)}

snakemake -s ~/GitHubs/PhispyAnalysis/RunningPhiSpy/phispy_vogs_download.snakefile --config filelist=$DATE/needed/x$NEED gbk=$DATE/gbk output=$DATE/phispy assembly=$ASS vogs=$VOGS --profile slurm_small
