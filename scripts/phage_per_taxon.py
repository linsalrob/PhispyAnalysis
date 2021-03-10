"""
Count the number of phages at the lowest taxonomic level so we can accumulate them later
"""

import os
import sys
import argparse
from multiprocessing import Process, Queue
import gzip
import re
from taxon import taxonomy_hierarchy_as_list, get_taxonomy_db, EntryNotInDatabaseError

__author__ = 'Rob Edwards'


def get_taxonomy(gbkf, q):
    """ get the taxonomy array and return it in the queue"""

    # read the genbank file and get the taxonomy id
    if gbkf.endswith('.gz'):
        f = gzip.open(gbkf, 'rt')
    else:
        f = open(gbkf, 'r')

    dbxref = re.compile('/db_xref="taxon:(\d+)"')

    tid = 0
    for l in f:
        if 'taxon' in l:
            match = dbxref.search(l)
            if match:
                tid = int(match.groups()[0])
                break
    if tid == 0:
        sys.stderr.write(f"FATAL: Could not find a tax id in {gbkf}\n")
        sys.exit(-1)

    f.close()



    conn = get_taxonomy_db()
    try:
        l = taxonomy_hierarchy_as_list(conn, tid)
    except EntryNotInDatabaseError as e:
        l = ['DELETED TAXONOMY']
    l.insert(0, tid)
    q.put(l)

def count_phages(phagef, q):
    """ Count the phages in the log file"""
    # read the phage log file
    if phagef.endswith('.gz'):
        f = gzip.open(phagef, 'rt')
    else:
        f = open(phagef, 'r')

    inphage = False
    phages = 0
    for l in f:
        if 'Number of potential genes' in l:
            inphage = True
        if 'PROPHAGE' in l or 'Creating output files' in l:
            break
        if inphage and 'Kept' in l:
            phages+=1
    q.put(phages)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=' ')
    parser.add_argument('-g', help='genbank source file for the genome', required=True)
    parser.add_argument('-l', help='phispy log file', required=True)
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    # read the genbank file
    gbkq = Queue()
    g = Process(target=get_taxonomy, args=(args.g, gbkq,))
    g.start()

    phageq = Queue()
    p = Process(target=count_phages, args=(args.l, phageq,))
    p.start()


    taxonomy = gbkq.get()
    phagen = phageq.get()
    print("\t".join(map(str, [args.g] + taxonomy + [phagen])))
    p.join()
    g.join()
