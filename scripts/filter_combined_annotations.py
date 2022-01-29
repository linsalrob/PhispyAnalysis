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
    parser.add_argument('-n', help='minimum number of entries', type=int, required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    os.makedirs(args.o, exist_ok=True)
    noan = re.compile('^.*?\t')

    filecount = 0
    for f in os.listdir(args.d):
        filecount += 1
        if args.v:
            sys.stderr.write(f"Parsing {filecount} {f}\n")
        with open(os.path.join(args.d, f)) as fin, open(os.path.join(args.o, f)) as out:
            for l in f:
                if l.startswith('Function'):
                    out.write(l)
                    continue
                if len([x for x in map(int, noan.sub('', l).strip().split("\t")) if x > 0]) > args.n:
                    out.write(l)


