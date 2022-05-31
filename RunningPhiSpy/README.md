
# Running PhiSpy on all genomes in GenBank

Note: you will need a cluster to do this. And some patience! 

We use a snakemake script to download the genomes from GenBank and run PhiSpy on those genomes. From PhiSpy, we only keep
the GenBank format file that has the prophage predictions, the prophage coordinates file, and the PhiSpy log. We keep the 
log file because it has additional data that we parsed for the paper.

Because we are dealing with hundreds of thousands of files, we want each assembly to end up in its own location. We create
a directory structure based on the name of the genome, and use `bash` substrings to locate the file.

If we have a genome like `GCA_000367705.1_ASM36770v1_genomic.gbff.gz` we create a directory `phispy/GCA_00036/GCA_000367705/` 
to house the data. We create a variable (in this example called BASE), and then use that to make the directory. For example:

```bash
BASE=GCA_000367705.1_ASM36770v1_genomic.gbff.gz
mkdir -p phispy/${BASE:0:9}/${BASE:0:13}
```

The substring `${BASE:0:9}` is the first nine characters, in this example `GCA_00036`, and the substring `${BASE:0:13}` is
the first 13 characters, in this case `GCA_000367705`, so together we have the path `phispy/GCA_00036/GCA_000367705/`. We 
use this for all of our files.

## Step 1. Find the genomes to analyse

We start by downloading the GenBank assembly summary file, and then identifying the genomes we have not yet parsed.
We convert those genomes into several lists so we can run them concurrently across a cluster,
and then use a `snakemake` script to get those genomes.

We use today's date so that we know the last time the file was downloaded!

<small>Note. We do not dynamically set the date, because if you want to use this file tomorrow it will be wrong, and so we 
hardcode it in scripts, etc.</small>

```bash
DATE=20220601
curl -Lo assembly_summary_${DATE}.txt ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt
```


Identify which genomes we don't have analysed yet

```bash
mkdir $DATE
for BASE in $(grep -v ^# assembly_summary_${DATE}.txt | cut -f 1); do
	if [ ! -e phispy/${BASE:0:9}/${BASE:0:13}/VOGS/ ]; then 
		echo $BASE; 
	fi;
done > $DATE/needed.all
```

Next, we split those files into separate files with 1000 entries per file so we can process them across an entire
cluster. This makes a series of files that are numbered `x0001`, `x0002`, `x0003`, `...`

```bash
mkdir $DATE/needed
pushd $DATE/needed
split -a 4 --numeric-suffixes=1 -l 1000 ../needed.all
popd
```

I usually set a variable with the number of files created to make the downstream processing easier:


```bash
FILES=533
```

# Step 2. Downlaod all the genomes and run PhiSpy on all the assemblies.

We use a `snakemake` file to download all of the genomes, run `phispy.py` and compress the outputs. The `snakemake`
script is the same, but we have different submission scripts for SGE and SLURM clusters.

For clusters that use SGE:

```bash
rm -rf sge_err sge_out; mkdir sge_err sge_out; 
qsub -cwd -q smallmem -o sge_out -e sge_err -V -t 1-$FILES:1 ./submit_phispy_vogs_download_sge.sh
```

For clusters that use SLURM:
```bash
rm -rf logs_slurm/ submit_phispy; mkdir logs_slurm/ submit_phispy
sbatch --array=1-454%5 submit_phispy_vogs_download.slurm
```


# Step 3. Now we can run some analysis on this data.

COUNT THE NUMBER OF CONTIGS IN EACH FILE:

find phispy/ -name \*genomic.gbff.gz -printf "%f\t" -exec zgrep -c LOCUS "{}" \; > contig_counts.tsv

perl -ne 'BEGIN {$n=100} chomp; @a=split /\t/; $a[1] > $n ? $g++ : $l++; END {print "For $n bp Less: $l Greater: $g\n"}' contig_counts.tsv


COUNT THE NUMBER OF PROPHAGES IN EACH PREDICTION

find phispy/ -name \*prophage_coordinates.tsv.gz -printf "%f\t" -exec zgrep -c ^ "{}" \;


COUNT THE NUMBER OF DIFFERENT GENERA IN THE ASSEMBLY FILE

This requires [taxonkit](https://bioinf.shenwei.me/taxonkit) that you can install with `bioconda`
```bash
taxonkit lineage taxonomy_ids.tsv | taxonkit reformat -f "{g}" -F  > genera.tsv
perl -F"\t" -lane 'if (!$F[2]) {$F[2] = "Unknown"} print $F[2]' genera.tsv | sort  | uniq -c | perl -pe 's/^\s+(\d+)\s+(.*)/$2\t$1/' > genera_counts.tsv
```
