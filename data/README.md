# Data from different sources

## Section 1. Downloaded Data

This data is sourced from a variety of web locations and compiled to analyse the prophage counts.

We keep all of it as gzip compressed files and then read those into dataframes using the `compression='gzip'` flag to 
`pandas.read_csv`

- GenBank: `assembly_summary.txt.gz`. This is the GenBank metadata associated with all the assemblies
    - Available from [ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt](ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt)
- PATRIC: `patric_genome_metadata.tsv.gz`. PATRIC compiles metadata from a variety of sources. This is a little tricky 
because it is not guaranteed to be unique per assembly ID, and so need to take the first instance. In addition, some of
  the fields like date and country need cleaning up.
    - Available from [ftp://ftp.patricbrc.org/RELEASE_NOTES/genome_metadata](ftp://ftp.patricbrc.org/RELEASE_NOTES/genome_metadata)
- GTDB: `bac120_metadata_r95.tsv.gz` The GTDB taxonomy and _some_ of the metadata available in GenBank or PATRIC
but additional data too. Some of the fields found in PATRIC (notably, _isolation\_date_ are missing from this file.)
  

# Section 2. Computed Data

- `categories.tsv` This is a four column table that we have constructed with our own environmental categories and our 
biome category.
- `checkv.tsv.gz` The results from `checkv` analysis of all the prophages.
- `country_importance.txt.gz` The importance of each country in the analysis.
- 