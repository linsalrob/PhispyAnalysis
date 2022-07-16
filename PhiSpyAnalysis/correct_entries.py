"""
Methods to correct text in entries
"""

import os
import sys
import re
import numpy as np
from .correct_dates import DateConverter

def file_to_accession_name(x):
    regexp = re.compile('(\w+\.\d+)_([\w\.\-]+)_genomic.gbff.gz')
    m = regexp.match(x)
    if not m:
        sys.stderr.write(f"WARNING: Regexp did not match {x}\n")
        return (None, None)
    return list(m.groups())

def file_to_accession(x):
    regexp = re.compile('(\w+\.\d+)_([\w\.\-]+)_genomic.gbff.gz')
    m = regexp.match(x)
    if not m:
        sys.stderr.write(f"WARNING: Regexp did not match {x}\n")
        return None
    return m.groups()[0]

def file_to_name(x):
    regexp = re.compile('(\w+\.\d+)_([\w\.\-]+)_genomic.gbff.gz')
    m = regexp.match(x)
    if not m:
        sys.stderr.write(f"WARNING: Regexp did not match {x}\n")
        return None
    return m.groups()[1]


def clean_metadata(metadf):
    """
    Clean a bunch of mistakes in the metadata
    """

    dc = DateConverter()
    metadf['isolation_date'] = metadf.collection_date.apply(dc.convert_date)

    # clean up the metadata
    metadf['isolation_country'] = metadf['isolation_country'].replace('USA', 'United States')
    metadf['geographic_location'] = metadf['geographic_location'].replace('USA', 'United States')
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
