"""

"""

import os
import sys
import argparse
from taxon import taxonomy_hierarchy_as_list, get_taxonomy_db

__author__ = 'Rob Edwards'





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=' ')
    #parser.add_argument('-f', help='input file', required=True)
    #parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    conn = get_taxonomy_db()
    l = taxonomy_hierarchy_as_list(conn, 485913)
    print(l)



