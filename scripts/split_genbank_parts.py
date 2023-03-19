"""
Read the phispy log and a genbank file and write out the pieces and parts
"""

import os
import sys
import argparse
import gzip
from PhiSpyAnalysis import is_gzip_file, parse_genbank

__author__ = 'Rob Edwards'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=' ')
    parser.add_argument('-l', '--log', help='phispy log file', required=True)
    parser.add_argument('-g', '--genbank', help='genbank file', required=True)
    output_group = parser.add_argument_group('outputs')
    output_group.add_argument('-k', '--kept', help='Keep kept genomes', action='store_true')
    output_group.add_argument('-p', '--no_phage', help='Keep no phage genes', action='store_true')
    output_group.add_argument('-s', '--too_short', help='Keep too short regions', action='store_true')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    if is_gzip_file(args.log):
        log = gzip.open(args.log, 'rt')
    else:
        log = open(args.log, 'r')

    in_phage = False
    kept = {}
    no_phage = {}
    too_short = {}
    for f in log:
        if f.contains('Contig\tStart'):
            in_phage = True
            continue
        if f.contains('Creating output files') or f.contains('\tPROPHAGE:'):
            in_phage = False
            continue
        if not in_phage:
            continue
        p = f.strip().split("\t")
        if p[-1] == 'Kept':
            if



