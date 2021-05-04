"""
Read the data frames, and return cleaned up data.

This way, we know that all data frames are read the same way!
"""

import os
import sys
import pandas as pd
import numpy as np
import subprocess

from .correct_entries import file_to_accession, file_to_name
from .correct_dates import DateConverter

from .dtype_definitions import metadata_dtypes, gtdb_dtypes

def read_phages(tsv_file="../data/phages_per_genome.tsv.gz", maxcontigs=100, use_small_data=False, keep_contig=False):
    """
    Read the phages TSV file and return a data frame.
    :param tsv_file: The tsv file with the data
    :param maxcontigs: the maximum number of contigs to include. If set to 0 or less, will return all contigs
    :param use_small_data: use a small (developer) data set
    :param keep_contig: kep the contig name after splitting into accession/assembly. Normally we drop it
    :return: a pandas data frame
    """

    if use_small_data:
        tsv_file = "../small_data/phages_per_genome.tsv.gz"

    phagesdf = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")

    ikp = phagesdf['Kept'].sum()
    ikg = phagesdf.shape[0]

    if maxcontigs > 0:
        phagesdf = phagesdf[phagesdf['Contigs'] > maxcontigs]

    phagesdf['Contig'] = phagesdf['Contig'].astype('str')
    phagesdf = phagesdf.dropna(subset=['Genome length', 'Kept'])

    phagesdf.insert(loc=0, column='assembly_name', value=phagesdf['Contig'].apply(file_to_name))
    phagesdf.insert(loc=0, column='assembly_accession', value=phagesdf['Contig'].apply(file_to_accession))
    if not keep_contig:
        phagesdf = phagesdf.drop('Contig', axis=1)

    githash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()

    sys.stderr.write(f"Please note that this was run with git commit {githash} that has {ikg:,} ")
    sys.stderr.write(f"genomes parsed.\n")
    sys.stderr.write(f"Initially there were {ikp:,.0f} kept phages,")
    sys.stderr.write(f"but after filtering we kept {phagesdf['Kept'].sum():,.0f} prophages ")
    sys.stderr.write(f"from {phagesdf.shape[0]:,} genomes")

    return phagesdf

def read_checkv(tsv_file="../data/checkv.tsv.gz", use_small_data=False):
    if use_small_data:
        tsv_file = "../small_data/checkv.tsv.gz"

    checkv = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    checkv = checkv.rename(columns={"prophage": "Prophage"})
    #checkv = checkv.rename(columns={"BASE": "Contig"})
    #checkv.insert(loc=0, column='assembly_name', value=checkv['Contig'].apply(file_to_name))
    #checkv.insert(loc=0, column='assembly_accession', value=checkv['Contig'].apply(file_to_accession))
    #checkv = checkv.drop('Contig', axis=1)

    return checkv

def read_base_pp(tsv_file="../data/base_pp.tsv.gz", use_small_data=False):
    if use_small_data:
        tsv_file = "../small_data/base_pp.tsv.gz"
    base_pp = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    base_pp = base_pp.rename({'BASE': "Contig"}, axis=1)
    return base_pp

def read_metadata(tsv_file="../data/patric_genome_metadata.tsv.gz", use_small_data=False):
    if use_small_data:
        tsv_file="../small_data/patric_genome_metadata.tsv.gz"

    metadf = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t", dtype=metadata_dtypes())

    # Filter for only the first of each genome assembly. The metadata contains multiple entries for a genome assembly
    # if it is submitted more than once, so here we just filter for the first instance. We might think about
    # something smarter, but this seems to work
    metadf = metadf.groupby('assembly_accession').first().reset_index()

    dc = DateConverter()
    metadf['isolation_date'] = metadf.collection_date.apply(dc.convert_date)

    # clean up the metadata
    metadf['isolation_country'] = metadf['isolation_country'].replace('USA', 'United States')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Ecully', 'France')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Adriatic Sea coasts', 'Adriatic Sea')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Côte', "Cote d'Ivoire")
    metadf['isolation_country'] = metadf['isolation_country'].replace('" Azores"', 'Azores')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Democratic Republic of the Congo (Kinshasa)',
                                                                      'Democratic Republic of the Congo')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Hong kong', 'Hong Kong')
    metadf['isolation_country'] = metadf['isolation_country'].replace(' Republic of Korea', 'Republic of Korea')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Soviet Union', 'USSR')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Vietnam', 'Viet Nam')

    metadf['geographic_location'] = metadf['geographic_location'].replace('USA', 'United States')

    # Finally replace all None with np.nan
    metadf = metadf.fillna(value=np.nan)

    return metadf

def read_gtdb(tsv_file="../data/bac120_metadata_r95.tsv.gz", use_small_data=False):
    if use_small_data:
        sys.stderr.write("Warning: small doesn't do anything with GTDB data\n")
    #gtdb = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t", na_values='none')
    gtdb = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t", dtype=gtdb_dtypes(), na_values='none')
    gtdb = gtdb.rename(columns={'ncbi_genbank_assembly_accession': 'assembly_accession'})
    return gtdb

def read_gbk_metadata(tsv_file="../data/assembly_summary.txt.gz", use_small_data=False):
    if use_small_data:
        sys.stderr.write("Warning: small doesn't do anything with gbk_metadata data\n")
    gbk = pd.read_csv(tsv_file, compression='gzip', header=1, delimiter="\t")
    gbk = gbk.rename(columns={'# assembly_accession': 'assembly_accession'})
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
        tsv_file="../small_data/transposon_counts.tsv.gz"
    tns = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    return tns

def read_logo(tsv_file="../data/country_importance_table.tsv.gz", use_small_data=False):
    if use_small_data:
        sys.stderr.write("Warning: small doesn't do anything with gbk_metadata data\n")
    logo = pd.read_csv(tsv_file, compression='gzip', header=0, delimiter="\t")
    return logo

