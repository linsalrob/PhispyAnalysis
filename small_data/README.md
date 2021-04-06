## Data Sources

 - `phages_per_genome.tsv` is the data created here
 - `bac120_metadata_r95.tsv` is a sample of the data from the GTDB current release (release 95) in the bac120_metadata.tar.gz compressed archive
 - `patric_genome_metadata.tsv` is a sample of the PATRIC metadata that contains the records in `phages_per_genome.tsv`

to make the GTDB data I used:

```
head -n 1 ../data/bac120_metadata_r95.tsv > ba
grep -v Contig phages_per_genome.tsv  | perl -ne 'm/^(GCA_\d+\.\d+)/; print "$1\n"' | xargs -i grep -Fw {} ../data/bac120_metadata_r95.tsv > bb
cat ba bb > bac120_metadata_r95.tsv
```


To make the PATRIC data set I used:

```
head -n 1 ~/PATRIC/patric_genome_metadata_20210406.tsv > pa
grep -v Contig phages_per_genome.tsv  | perl -ne 'm/^(GCA_\d+\.\d+)/; print "$1\n"' | xargs -i grep -Fw {} ~/PATRIC/patric_genome_metadata_20210406.tsv | awk -F'\t' '!s[$18]++' > pt
cat pa pt > patric_genome_metadata.tsv
```

Note that the `awk` here only prints the first record for each assembly accession.
