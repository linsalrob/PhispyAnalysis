#!/bin/bash


# Time in days-hours. Change this as much as you want
#SBATCH --time=5-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=18

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=64000M

set -euo pipefail

# get the phispy environment
source /home/edwa0468/GitHubs/PhispyAnalysis/venv/bin/activate

DATE=`date +"%Y%m%d"`

OUTDIR="phispy_analysis_$DATE"

echo -e "Phage Proteins\tHMM hits\tProteins Unknown Function\tTotal Proteins\n" > $OUTDIR/phage_protein_counts.tsv
echo -e "BASE\tcontig_id\tcontig_length\tgene_count\tviral_genes\thost_genes\tcheckv_quality\tmiuvig_quality\tcompleteness" > $OUTDIR/checkv.tsv


mkdir -p $OUTDIR/faa $OUTDIR/fns $OUTDIR/fna 
C=0
for GBK in $(find phispy/ -name \*_genomic.gbff.gz -printf "%f\n"); do 
	BASE=$(echo $GBK | sed -e 's/\_[^_]*$//');
	echo $BASE >> $OUTDIR/processed_prophages.txt
	perl count_phages.pl phispy/${GBK:0:9}/${GBK:0:13}/VOGS/${BASE}_VOGS_phispy.log.gz >> $OUTDIR/phage_counts.tsv &
	perl phage_lengths.pl phispy/${GBK:0:9}/${GBK:0:13}/VOGS/${BASE}_VOGS_phispy.log.gz >> $OUTDIR/phage_lengths.tsv &
	perl dnaA_locations.pl phispy/${GBK:0:9}/${GBK:0:13}/$GBK >> $OUTDIR/dna_locations.tsv &
	perl count_genbank_lengths.pl phispy/${GBK:0:9}/${GBK:0:13}/$GBK >> $OUTDIR/genome_lengths.tsv &

	if [ -e  phispy/${GBK:0:9}/${GBK:0:13}/VOGS/${BASE}_VOGS_phage.gbk.gz ]; then
		python3 ~/GitHubs/EdwardsLab/bin/genbank2sequences.py -a $OUTDIR/faa/$BASE -f $OUTDIR/fns/$BASE.functions -n $OUTDIR/fna/$BASE -g phispy/${GBK:0:9}/${GBK:0:13}/VOGS/${BASE}_VOGS_phage.gbk.gz &
		python3 ~/GitHubs/PhispyAnalysis/scripts/gene_counts.py -g phispy/${F:0:9}/${F:0:13}/VOGS/${F}_VOGS_phage.gbk.gz >> $OUTDIR/phage_protein_counts.tsv &
	fi 
	
	if [ -e phispy/${GBK:0:9}/${GBK:0:13}/VOGS/checkv/quality_summary.tsv.gz ]; then
		IFSOLD=$IFS; 
		IFS=$'\n'; 
		for CHV in $(gunzip -c $PWD/phispy/${GBK:0:9}/${GBK:0:13}/VOGS/checkv/quality_summary.tsv.gz | grep -v contig_id | cut -f 1,2,5,6,7,8,9,10); do 
			echo -e "$GBK\t$CHV" >> $OUTDIR/checkv.tsv;
		done
		IFS=$OLDIFS;
	fi

	# on every third submission wait for everything to finish. Hopefully we won't flood the IO
	REMAINDER=$(echo $C%3 | bc);
	if [ "$REMAINDER" -eq "0" ]; then wait; fi
	C=$((C+1))

done

wait



perl -i -npe 's#^.*/##' $OUTDIR/genome_lengths.tsv
gunzip -c /home/edwa0468/GitHubs/PhispyAnalysis/data/phages_per_genome.tsv.gz | head -n 1 > $OUTDIR/phages_per_genome.tsv
echo "PLEASE FIX THE NUMBER OF CONTIGS HEADERS (CONTIGS IS 2nd COL) AND THEN DELETE THIS LINE FROM ANALYSIS.SLURM"
joinlists.pl $OUTDIR/genome_lengths.tsv $OUTDIR/phage_counts.tsv >> $OUTDIR/phages_per_genome.tsv
gzip $OUTDIR/phages_per_genome.tsv
gzip $OUTDIR/checkv.tsv

cat $OUTDIR/faa/* > $OUTDIR/all.proteins.faa                                                                                                                                             
cat $OUTDIR/fns/* > $OUTDIR/all.proteins.fns
rm -rf $OUTDIR/faa $OUTDIR/fns 
python3 /home/edwa0468/GitHubs/EdwardsLab/proteins/protein_md5_fast.py -f $OUTDIR/all.proteins.faa -i $OUTDIR/all.proteins.md5.ids -o $OUTDIR/all.proteins.md5.faa
for F in $OUTDIR/all.proteins.faa $OUTDIR/all.proteins.md5.faa $OUTDIR/all.proteins.fns $OUTDIR/all.proteins.md5.ids $OUTDIR/genome_lengths.tsv $OUTDIR/dna_locations.tsv $OUTDIR/phage_lengths.tsv $OUTDIR/phage_counts.tsv; do
	gzip $F &
done

wait
