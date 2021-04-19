"""
Count some information about the phages
"""

import os
import sys
import argparse
from PhiSpyModules import is_gzip_file, is_phage_func, is_unknown_func
from Bio import SeqIO
import gzip
import re


def count_phage_proteins(inputfile, verbose=False):
    """
    Count some information
    :param inputfile: the input file
    :param verbose:  more output
    :return:
    """
    try:
        if is_gzip_file(inputfile):
            handle = gzip.open(inputfile, 'rt')
        else:
            handle = open(inputfile, 'r')
    except IOError as e:
        sys.stderr.write(f"There was an error reading {inputfile}: {e}\n")
        sys.exit(20)

    phagecount = 0
    unkfunc = 0
    phmms = 0
    featcount = 0
    for seq in SeqIO.parse(handle, "genbank"):
        for feat in seq.features:
            if feat.type != 'CDS':
                continue
            featcount += 1
            isphage = False
            ishypo  = False

            if 'product' in feat.qualifiers:
                for p in feat.qualifiers['product']:
                    if is_phage_func(p):
                        isphage = True
                    if is_unknown_func(p):
                        ishypo = True
                    if re.match('[a-z]{2,3}\d+[^:\+\-0-9]', p.lower()):
                        ishypo = False
            if isphage:
                phagecount += 1
            if ishypo:
                unkfunc += 1
            if verbose and isphage and ishypo:
                sys.stderr.write(f"ERROR: Both phage and hypothetical for |{p}|\n")
            if 'phmm' in feat.qualifiers:
                phmms += 1
        yield [seq.id, phagecount, phmms, unkfunc, featcount]
    handle.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=' ')
    parser.add_argument('-g', help='input genbank file', required=True)
    parser.add_argument('-t', help='print column titles', action='store_true')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    if args.t:
        print("Phage proteins\tPVOG HMMS\tUnknown Proteins\tTotal Proteins")
    
    for sid, phagecount, phmms, unkfunc, featcount in count_phage_proteins(args.g, args.v):
        print(f"{sid}\t{phagecount}\t{phmms}\t{unkfunc}\t{featcount}")


