#!/bin/bash


###########################################################################################
#                                                                                         #
# Analyse the phispy output, but run only on one directory, and put the results in        #
# that directory in the output directory. We will then concatenate those outputs          #
# to create a single file with all the data                                               #
#                                                                                         #
#                                                                                         #
#                                                                                         #
#                                                                                         #
#                                                                                         #
#                                                                                         #
#                                                                                         #
#                                                                                         #
###########################################################################################


# Time in days-hours. Change this as much as you want
#SBATCH --time=5-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=18

#SBATCH --mem=64000M
#SBATCH --output=analyse_all/analysis.%j.out


# get the phispy environment
source /home/edwa0468/GitHubs/PhispyAnalysis/venv/bin/activate

PHGFILES=$1
MYDIR=$2

if [ "$#" -ne 2 ]; then
	echo `basename $0` " <list of processed phages> <my directory to process>";
	exit 1;
fi


if [ ! -e "$PHGFILES" ]; then
	echo "$PHGFILES not found.";
	exit 1;
fi


DATE=`date +"%Y%m%d"`
OUTDIR="phispy_analysis_$DATE/phispy/$MYDIR"
mkdir -p $OUTDIR

echo -e "prophage\tcontig_length\tgene_count\tcheckv_quality" > $OUTDIR/checkv.tsv
echo -e "Phage Proteins\tHMM hits\tProteins Unknown Function\tTotal Proteins" > $OUTDIR/phage_protein_counts.tsv


C=0
for GBK in $(grep "phispy/$MYDIR" $PHGFILES); do
	# here we replace both _VOGS_phage.gbk.gz and _genomic.gbff.gz so we should mostly be correct
	BASE=$(basename `basename $GBK _VOGS_phage.gbk.gz` _genomic.gbff.gz)

	if [ ! -e "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/" ]; then 
		echo "Skipped $BASE not processed" >> $OUTDIR/processed_prophages.txt;
		continue;
	fi

	echo $BASE >> $OUTDIR/processed_prophages.txt
	perl count_phages.pl phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_phispy.log.gz >> $OUTDIR/phage_counts.tsv &
	perl phage_lengths.pl phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_phispy.log.gz >> $OUTDIR/phage_lengths.tsv &
	if [ -e phispy/${BASE:0:9}/${BASE:0:13}/${BASE}_genomic.gbff.gz ]; then
		perl dnaA_locations.pl phispy/${BASE:0:9}/${BASE:0:13}/${BASE}_genomic.gbff.gz >> $OUTDIR/dnaA_locations.tsv &
		perl count_genbank_lengths.pl phispy/${BASE:0:9}/${BASE:0:13}/${BASE}_genomic.gbff.gz >> $OUTDIR/genome_lengths.tsv &
	fi 

	if [ -e  phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_phage.gbk.gz ]; then
		python3 ~/GitHubs/PhispyAnalysis/scripts/gene_counts.py -g phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_phage.gbk.gz >> $OUTDIR/phage_protein_counts.tsv &
	fi 

	if [ -e "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/checkv/phispy_summary.tsv" ]; then
		cat phispy/${BASE:0:9}/${BASE:0:13}/VOGS/checkv/phispy_summary.tsv >> $OUTDIR/checkv.tsv
	fi

	if [ -e phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_hits_counts.txt.gz ]; then
		cat phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_hits_counts.txt.gz >>  $OUTDIR/vogs_hits_counts.txt.gz
	fi

	if [ -e "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/mash/genbank.besthit" ]; then
		cat phispy/${BASE:0:9}/${BASE:0:13}/VOGS/mash/genbank.besthit >> $OUTDIR/genbank.besthits.tsv
	fi
	

	# on every tenth submission wait for everything to finish. Hopefully we won't flood the IO
	REMAINDER=$(echo $C%10 | bc);
	if [ "$REMAINDER" -eq "0" ]; then wait; fi
	C=$((C+1))

done

wait


perl -i -npe 's#^.*/##' $OUTDIR/genome_lengths.tsv
gunzip -c /home/edwa0468/GitHubs/PhispyAnalysis/data/phages_per_genome.tsv.gz | head -n 1 > $OUTDIR/phages_per_genome.tsv
joinlists.pl $OUTDIR/genome_lengths.tsv $OUTDIR/phage_counts.tsv >> $OUTDIR/phages_per_genome.tsv
rm -f $OUTDIR/genome_lengths.tsv $OUTDIR/phage_counts.tsv


wait
