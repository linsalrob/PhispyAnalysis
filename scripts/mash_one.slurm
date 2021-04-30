#!/bin/bash

###############################################################
#                                                             #
# Run mash on a single genome                                 #
#                                                             #
# We are going to rely on a checking script to run this       #
#                                                             #
#                                                             #
###############################################################


# Time in days-hours. Change this as much as you want
#SBATCH --time=0-6

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=2000M

#SBATCH --output=clean_up/mash_one_%A_%a.out


if [ $# -ne 1 ]; then echo `basename $0` " <GENOME BASE NAME> (e.g. GCA_000006155.2_ASM615v2)"; exit 1; fi

BASE=$1

echo "Running mash_one on $BASE"

eval "$(conda shell.bash hook)"
conda activate mash

if [ ! -e /local/edwa0468/GenBank_phages.msh ]; then cp -n /home/edwa0468/phage/Prophage/phispy/mash/GenBank_phages.msh /local/edwa0468/GenBank_phages.msh; fi

mkdir -p /local/edwa0468/mash
WD=$PWD

PHISPYDIR='phispy'

ODIR=$(mktemp -d -p /local/edwa0468/mash);
echo -e "mash.slurm\t$BASE\tPROCESSING IN $ODIR";
cp $PHISPYDIR/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_phage.gbk.gz $ODIR;
cd $ODIR;
python3 ~/GitHubs/EdwardsLab/bin/genbank2sequences.py -g ${BASE}_VOGS_phage.gbk.gz -n ${BASE};

# mash the genome and compare it to the genbank files
mash sketch -i -p 4 -k 14 -s 10000 ${BASE}.fna -o ${BASE}.msh
mash dist /local/edwa0468/GenBank_phages.msh ${BASE}.msh | awk '$4 < 1e-5 {print}'  | sort -gk3 > genbank_phages.dist
cat genbank_phages.dist | awk '!s[$2]++ {print}' > genbank.besthit
gzip genbank_phages.dist

mkdir -p $WD/$PHISPYDIR/${BASE:0:9}/${BASE:0:13}/VOGS/mash
mv ${BASE}.msh genbank_phages.dist.gz genbank.besthit $WD/$PHISPYDIR/${BASE:0:9}/${BASE:0:13}/VOGS/mash

cd $WD;
rm -rf $ODIR;


