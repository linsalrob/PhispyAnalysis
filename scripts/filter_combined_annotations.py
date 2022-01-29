"""
~/GitHubs/PhispyAnalysis/scripts/merge_annotations.py makes about 900 large files, and the total size is 29TB. Oops!

We filter them for annotations that appear in more than n genomes


"""

import os
import sys
import argparse
import re

__author__ = 'Rob Edwards'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter annotations')
    parser.add_argument('-d', help='directory of annotations', required=True)
    parser.add_argument('-o', help='output directory of annotations', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', help='minimum number of entries', type=int)
    group.add_argument('-p', help='percent of the records that must be non zero', type=float)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    os.makedirs(args.o, exist_ok=True)
    noan = re.compile('^.*?\t')

    if args.p and args.p > 1:
        args.p /= 100

    filecount = 0
    for f in os.listdir(args.d):
        filecount += 1
        if args.v:
            sys.stderr.write(f"Parsing {filecount} {f}\n")
        with open(os.path.join(args.d, f), 'r') as fin, open(os.path.join(args.o, f), 'w') as out:
            for l in f:
                if l.startswith('Function'):
                    out.write(l)
                    continue
                if args.n:
                    if len([x for x in map(int, noan.sub('', l).strip().split("\t")) if x > 0]) > args.n:
                        out.write(l)
                else:
                    if len([x for x in map(int, noan.sub('', l).strip().split("\t")) if x > 0])/l.count("\t") > args.p:
                        out.write(l)


