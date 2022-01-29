"""
Merge all the annotations into a presence/absence table.
"""
import gzip
import os
import sys
import argparse


def convert_string(x):
    """
    Convert the string to lower case and strip all non [z-z0-9-_] characters
    :param str x: the string to convert
    :return: the converted string
    :rtype: str
    """
    # we define the things to keep this way, just for clarity and in case we want to add other things.
    wanted = set()
    # lower case letters
    wanted.update(set(range(97, 123)))
    # numbers
    wanted.update(set(range(48, 58)))
    # - and _
    wanted.update({45, 95})
    # space
    wanted.add(32)

    s = ''
    for c in x:
        if ord(c) in wanted:
            s += c
        elif 65 <= ord(c) <= 90:
            s += chr(ord(c) + 32)
    if s.startswith('conserved '):
        s = s.replace('conserved ', '')
    return s


def read_file(inf, verbose=False):
    """
    Read the file and return a dict of functions present in the file
    :param str inf: filename to read
    :param bool verbose: more output
    :return: a dict of the annotations and their frequencies
    :rtype: dict[str, int]
    """

    if verbose:
        sys.stderr.write(f"Reading {inf}\n")

    fn = {}
    if inf.endswith('.gz'):
        fin = gzip.open(inf, 'rt')
    else:
        fin = open(inf, 'r')
    for li in fin:
        p = li.strip().split('\t')
        f = convert_string(p[2])
        fn[f] = fn.get(f, 0) + 1

    fin.close()

    return fn


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=' ')
    parser.add_argument('-d', '--directory', help='directory of three column annotation files', required=True)
    parser.add_argument('-o', '--output', help='output file to write', required=True)
    parser.add_argument('-e', '--existing', help='existing tsv output with genomes in columns and annotations in rows')
    parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    args = parser.parse_args()

    allfns = set()
    existing_genomes = []
    existing_data = {}
    nzeros = ""
    if args.existing:
        firstline = True
        with open(args.existing, 'r') as f:
            for li in f:
                p = li.strip().split("\t")
                if firstline:
                    existing_genomes = p[1:]
                    firstline = False
                    continue
                allfns.add(p[0])
                existing_data[p[0]] = "\t".join(p[1:])
        nzeros = "\t".join(map(str, [0 for i in existing_genomes]))

    allfiles = set()
    fn2file = {}
    for inf in os.listdir(args.directory):
        fns = read_file(os.path.join(args.directory, inf), args.verbose)
        allfns.update(set(fns.keys()))
        allfiles.add(inf)
        fn2file[inf] = fns

    sfns = sorted(allfns)
    sfiles = sorted(allfiles)

    with open(args.output, 'w') as out:
        out.write("\t".join(["Function"] + existing_genomes + sfiles))
        out.write("\n")
        for func in sorted(sfns):
            out.write(func)
            if existing_data:
                if func in existing_data:
                    out.write(f"\t{existing_data[func]}")
                else:
                    out.write(f"\t{nzeros}")

            for fl in sfiles:
                if func in fn2file[fl]:
                    out.write(f"\t{fn2file[fl][func]}")
                else:
                    out.write("\t0")
            out.write("\n")
