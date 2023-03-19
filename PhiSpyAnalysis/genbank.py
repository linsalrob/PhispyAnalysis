"""
Helper functions to read a genbank file
"""

import sys
import gzip
from Bio import SeqIO
import binascii

def is_gzip_file(f):
    """
    This is an elegant solution to test whether a file is gzipped by reading the first two characters.
    I also use a version of this in fastq_pair if you want a C version :)
    See https://stackoverflow.com/questions/3703276/how-to-tell-if-a-file-is-gzip-compressed for inspiration
    :param f: the file to test
    :return: True if the file is gzip compressed else false
    """
    with open(f, 'rb') as i:
        return binascii.hexlify(i.read(2)) == b'1f8b'



def parse_genbank(filename, verbose=False):
    """
    Parse a genbank file and return a Bio::Seq object
    """


    try:
        if is_gzip_file(filename):
            handle = gzip.open(filename, 'rt')
        else:
            handle = open(filename, 'r')
    except IOError as e:
        print(f"There was an error opening {filename}", file=sys.stderr)
        sys.exit(20)

    return SeqIO.parse(handle, "genbank")

