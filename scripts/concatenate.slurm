#!/bin/bash

# we make separate versions of all the data in a working directory now,
# one per top level hierarcy, and this just combines all the outputs we need.


# Time in days-hours. Change this as much as you want
#SBATCH --time=1-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=2000M

for FILE in checkv.tsv dnaA_locations.tsv genbank.besthits.tsv phage_lengths.tsv phage_protein_counts.tsv phages_per_genome.tsv processed_prophages.txt vogs_hits_counts.txt.gz;
do
	rm -f $FILE
	find phispy -type f -name $FILE -exec cat {} \; > $FILE;
done

wait

awk '!s[$1]++' checkv.tsv > tmp && mv -f tmp checkv.tsv
awk '!s[$1]++' phage_protein_counts.tsv > tmp && mv -f tmp phage_protein_counts.tsv
awk '!s[$1]++' phages_per_genome.tsv > tmp && mv -f tmp phages_per_genome.tsv

echo -e "BASE\tProphage" > base_pp.tsv; gunzip -c vogs_hits_counts.txt.gz | perl -pe 's#^/##; s#_VOGS_phage.gbk.gz##; s#\t\d+$##'  >> base_pp.tsv

for FILE in checkv.tsv dnaA_locations.tsv genbank.besthits.tsv phage_lengths.tsv phage_protein_counts.tsv phages_per_genome.tsv processed_prophages.txt base_pp.tsv;
do
	gzip $FILE;
done

wait

