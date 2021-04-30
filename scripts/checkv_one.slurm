#!/bin/bash


# Time in days-hours. Change this as much as you want
#SBATCH --time=5-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=2000M

#SBATCH --output=clean_up/checkv_one_%A_%a.out

if [ $# -ne 1 ]; then echo `basename $0` " <GENOME BASE NAME> (e.g. GCA_000006155.2_ASM615v2)"; exit 1; fi

FILE=$1

echo "Running checkv_one on $FILE"

eval "$(conda shell.bash hook)"
conda activate checkv
export CHECKVDB=~/opt/checkv/checkv-db-v1.0/

WD=/local/edwa0468/checkv
mkdir -p $WD
ODIR=$(mktemp -d -p $WD)
echo "Analysing $FILE in $ODIR"

cp phispy/${FILE:0:9}/${FILE:0:13}/VOGS/${FILE}_VOGS_phage.gbk.gz $ODIR

cd $ODIR
python3 ~/GitHubs/EdwardsLab/bin/genbank2sequences.py -g ${FILE}_VOGS_phage.gbk.gz -n ${FILE}
checkv end_to_end ${FILE}.fna ${FILE}.checkv -t 8 > checkv.${FILE}.out  2> checkv.${FILE}.err

mkdir -p $SLURM_SUBMIT_DIR/phispy/${FILE:0:9}/${FILE:0:13}/VOGS/checkv

# check for the stop iteration problem
SI=$(grep StopIteration checkv.${FILE}.err)
if [ ! -z "$SI" ]; then 
	echo "NO HITS" > $SLURM_SUBMIT_DIR/phispy/${FILE:0:9}/${FILE:0:13}/VOGS/checkv/NOHITS.txt;
	cd $SLURM_SUBMIT_DIR;
	rm -rf $ODIR;
	exit 0;
fi


grep -v contig_id quality_summary.tsv.gz | cut -f 1,2,5,8 > phispy/${FILE:0:9}/${FILE:0:13}/VOGS/checkv/phispy_summary.tsv;
for OUTPUT in completeness.tsv contamination.tsv quality_summary.tsv; do
	if [ -e ${FILE}.checkv/$OUTPUT ]; then
		gzip ${FILE}.checkv/$OUTPUT;
		mv ${FILE}.checkv/$OUTPUT.gz $SLURM_SUBMIT_DIR/phispy/${FILE:0:9}/${FILE:0:13}/VOGS/checkv;
	fi;
done;
cd $SLURM_SUBMIT_DIR;
rm -rf $ODIR;


