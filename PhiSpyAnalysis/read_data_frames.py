"""
Read the data frames, and return cleaned up data.

This way, we know that all data frames are read the same way!
"""

import sys
import pandas as pd
import subprocess
from .correct_entries import clean_metadata

from .gtdb_manipulations import split_taxonomy

from .dtype_definitions import metadata_dtypes, gtdb_dtypes, phage_loc_dtypes, phages_per_genome_dtypes


def read_phages(tsv_file="../data/phages_per_genome.tsv.gz", maxcontigs=100, use_small_data=False,
                keep_incomplete=False):
    """
    Read the phages TSV file and return a data frame.

    This file has the format
        GENOMEID
        Genome length
        # Contigs
        # Phage Contigs
        Total Predicted Prophages
        Kept
        No phage genes
        Not enough genes
        bp prophage

    :param tsv_file: The tsv file with the data
    :param maxcontigs: Remove genomes with more than this many contigs. If set to 0 or less, will return all contigs.
    :param use_small_data: use a small (developer) data set
    :param keep_incomplete: ignore those results from searches that did not finish
    :return: a pandas data frame
    """

    if use_small_data:
        tsv_file = "../small_data/phages_per_genome.tsv.gz"

    phagesdf = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t", index_col=False,
                           dtype=phages_per_genome_dtypes())

    ikp = phagesdf['Kept'].sum()
    ikg = phagesdf.shape[0]

    if not keep_incomplete:
        phagesdf = phagesdf[phagesdf["Note"] == "Complete"]

    if maxcontigs > 0:
        phagesdf = phagesdf[phagesdf['Contigs'] < maxcontigs]

    phagesdf['GENOMEID'] = phagesdf['GENOMEID'].astype('str')
    phagesdf = phagesdf.dropna(subset=['Total_bp', 'Kept'])

    # In the current version, we are using assembly accesion only as GENOMEID, not the whole filename
    # phagesdf.insert(loc=0, column='assembly_name', value=phagesdf['GENOMEID'].apply(file_to_name))
    phagesdf.insert(loc=0, column='assembly_accession', value=phagesdf['GENOMEID'])

    githash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()

    sys.stderr.write(f"Please note that this was run with git commit {githash} that has {ikg:,} ")
    sys.stderr.write(f"genomes parsed.\n")
    sys.stderr.write(f"Initially there were {ikp:,.0f} kept phages, ")
    sys.stderr.write(f"but after filtering we kept {phagesdf['Kept'].sum():,.0f} prophages ")
    sys.stderr.write(f"from {phagesdf.shape[0]:,} genomes")

    return phagesdf


def read_checkv(tsv_file="../data/checkv.tsv.gz", use_small_data=False):
    if use_small_data:
        tsv_file = "../small_data/checkv.tsv.gz"

    checkv = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    checkv = checkv.rename(columns={"prophage": "Prophage"})
    # checkv = checkv.rename(columns={"BASE": "GENOMEID"})
    # checkv.insert(loc=0, column='assembly_name', value=checkv['GENOMEID'].apply(file_to_name))
    checkv.insert(loc=0, column='assembly_accession', value=checkv['GENOMEID'])
    # checkv = checkv.drop('GENOMEID', axis=1)

    return checkv


def read_base_pp(tsv_file="../data/base_pp.tsv.gz", use_small_data=False):
    if use_small_data:
        tsv_file = "../small_data/base_pp.tsv.gz"
    base_pp = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    base_pp = base_pp.rename({'BASE': "GENOMEID"}, axis=1)
    return base_pp


def read_metadata(tsv_file="../data/patric_genome_metadata.tsv.gz", use_small_data=False):
    if use_small_data:
        tsv_file = "../small_data/patric_genome_metadata.tsv.gz"

    metadf = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t", dtype=metadata_dtypes())

    # Filter for only the first of each genome assembly. The metadata contains multiple entries for a genome assembly
    # if it is submitted more than once, so here we just filter for the first instance. We might think about
    # something smarter, but this seems to work
    metadf = metadf.groupby('assembly_accession').first().reset_index()

    metadf = clean_metadata(metadf)

    return metadf


"""
### Split the taxonomy into separate columns

We split on `_` but unfortunately the `_` means something specific in GTDB. This is taken from the 
[FAQ](https://gtdb.ecogenomic.org/faq)
> If the organism had been assigned a binomial species name such as Prevotella oralitaxus str. F0040, and it 
is not part of true Prevotella in GTDB, we would assign it to the placeholder genus g__Prevotella_A to indicate 
it is not a true Prevotella species, but that there are representative genomes that have been assigned to a species

We at least remove the `g__` at the beginning and then leave the appendages.
"""


def read_gtdb(tsv_file="../data/bac120_metadata_r207.tsv.gz", use_small_data=False, representatives=False):
    if use_small_data:
        sys.stderr.write("Warning: small doesn't do anything with GTDB data\n")
    # gtdb = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t", na_values='none')
    gtdb = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t", dtype=gtdb_dtypes(), na_values='none')

    gtdb.insert(loc=0, column='assembly_accession', value=gtdb['ncbi_genbank_assembly_accession'])

    # split the gtdb taxonomy into individual columns
    tc = ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species']
    gtdb = pd.concat(
        [gtdb, pd.DataFrame.from_records(gtdb['gtdb_taxonomy'].apply(split_taxonomy), columns=tc)],
        axis=1)

    if representatives:
        return gtdb[gtdb['gtdb_representative'] == 't']
    return gtdb


def read_phage_locations(tsv_file="../data/prophage_locations.tsv.gz", use_small_data=False):
    """
    Read the phage locations file which has the following columns:
    GENOMEID
    Contig
    Start
    Stop
    Length
    # CDS
    Decision

    Note that this is the standard output from phispy that is in the log file, but I added the length of the prophage
    as (stop-start)+1 to make things easier

    Also note there are two different outputs for Decision (I know, I know) which are the same, but here I normalize
    them to be Dropped. Region too small (Not enough genes)
        Dropped. Not enough genes
        Dropped. Region too small (Not enough genes)

    """
    if use_small_data:
        tsv_file = '../small_data/prophage_locations.tsv.gz'
    phage_locations = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t", dtype=phage_loc_dtypes(),
                                  na_values='none')
    return phage_locations


def read_gbk_metadata(tsv_file="../data/assembly_summary_20220601.txt.gz", use_small_data=False):
    if use_small_data:
        sys.stderr.write("Warning: small doesn't do anything with gbk_metadata data\n")
    gbk = pd.read_csv(tsv_file, compression='gzip', header=1, delimiter="\t")
    gbk.insert(loc=0, column='assembly_accession', value=gbk['# assembly_accession'])
    return gbk


def read_categories(tsv_file="../data/categories.tsv.gz", use_small_data=False):
    if use_small_data:
        sys.stderr.write("Warning: small doesn't do anything with gbk_metadata data\n")
    catdf = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    if 'gbff' in catdf:
        catdf = catdf.drop('gbff', axis=1)
    catdf = catdf.groupby('assembly_accession').first().reset_index()
    return catdf


def read_transposons_per_phage(tsv_file="../data/transposase_per_phage.tsv.gz", use_small_data=False):
    if use_small_data:
        tsv_file = "../small_data/transposase_per_phage.tsv.gz"
    tns = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    return tns


def read_transposons(tsv_file="../data/transposon_counts.tsv.gz", use_small_data=False):
    if use_small_data:
        tsv_file = "../small_data/transposon_counts.tsv.gz"
    tns = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    return tns


def read_logo(tsv_file="../data/country_importance_table.tsv.gz", use_small_data=False):
    if use_small_data:
        sys.stderr.write("Warning: small doesn't do anything with gbk_metadata data\n")
    logo = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    return logo


def read_insertion_lengths(tsv_file="../data/insertion_lengths.tsv.gz", use_small_data=False):
    if use_small_data:
        sys.stderr.write("Warning: small doesn't do anything with gbk_metadata data\n")
    insl = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    return insl
