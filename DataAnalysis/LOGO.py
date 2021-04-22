"""
Run a random forest leave one out analysis on a cluster
"""

import sys
import pandas as pd
import re

from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, LeaveOneGroupOut
import numpy as np

from PhiSpyAnalysis import theils_u, DateConverter
import subprocess

import argparse

def get_acc_name(x):
    regexp = re.compile('(\\w+\.\\d+)_([\\w\.\\-]+)_genomic.gbff.gz')
    m = regexp.match(x)
    if not m:
        sys.stderr.write(f"WARNING: Regexp did not match {x}\n")
        return (None, None)
    return list(m.groups())

def loo(check_country, check_category):
    """
    Run the leave one out analysis

    :return:
    """
    phagesdf = pd.read_csv("../data/phages_per_genome.tsv.gz", compression='gzip', header=0, delimiter="\t")
    githash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    print(
        f"Please note that this was run with git commit {githash} that has {phagesdf.shape[0]:,} genomes parsed and {phagesdf['Total Predicted Prophages'].sum():,} total prophages")

    acccol = 'assembly_accession'

    phagesdf = pd.concat(
        [pd.DataFrame.from_records(phagesdf['Contig'].apply(get_acc_name), columns=[acccol, 'Name']), phagesdf['Kept']],
        axis=1)
    phagesdf = phagesdf.drop('Name', axis=1)

    metadf = pd.read_csv("../data/patric_genome_metadata.tsv.gz", compression='gzip', header=0, delimiter="\t")
    dc = DateConverter()
    metadf['isolation_date'] = metadf.collection_date.apply(dc.convert_date)

    metadf = metadf.groupby('assembly_accession').first().reset_index()

    metadf['isolation_country'] = metadf['isolation_country'].replace('USA', 'United States')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Ecully', 'France')
    metadf['geographic_location'] = metadf['geographic_location'].replace('USA', 'United States')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Adriatic Sea coasts', 'Adriatic Sea')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Côte', "Cote d'Ivoire")
    metadf['isolation_country'] = metadf['isolation_country'].replace('" Azores"', 'Azores')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Democratic Republic of the Congo (Kinshasa)',
                                                                      'Democratic Republic of the Congo')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Hong kong', 'Hong Kong')
    metadf['isolation_country'] = metadf['isolation_country'].replace(' Republic of Korea', 'Republic of Korea')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Soviet Union', 'USSR')
    metadf['isolation_country'] = metadf['isolation_country'].replace('Vietnam', 'Viet Nam')

    # Finally replace all None with np.nan
    metadf = metadf.fillna(value=np.nan)

    catdf = pd.read_csv("../data/categories.tsv.gz", compression='gzip', header=0, delimiter="\t")
    if 'gbff' in catdf:
        catdf = catdf.drop('gbff', axis=1)
    catdf = catdf.groupby('assembly_accession').first().reset_index()

    interesting_cols = [acccol, 'isolation_country', 'isolation_date']

    tempdf = metadf[interesting_cols]
    # tempdf = metadf[few_interesting_cols]
    temp1 = pd.merge(tempdf, catdf, how='left', left_on=acccol, right_on=acccol)
    # phagemeta = pd.merge(tempdf, phagesdf, how='inner', left_on=acccol, right_on=acccol)
    # phagemeta.to_csv(os.path.join('results', 'example_isolations.tsv'), sep='\t')

    phagemeta = pd.merge(temp1, phagesdf, how='right', left_on=acccol, right_on=acccol)

    pmenc = pd.DataFrame()
    for c in ['isolation_country', 'Category']:
        pmenc[c] = phagemeta[c].astype('category').cat.codes
    pmenc['isolation_date'] = phagemeta['isolation_date'].fillna(-1)

    # print a list of the countries and their IDs for the LOGO analysis.
    seen=set()
    if check_country:
        print("\n***********************************\n")
        print("Code\tCountry")
        for index, row in phagemeta.iterrows():
            if pmenc.loc[index, 'isolation_country'] not in seen:
                print(f"{pmenc.loc[index, 'isolation_country']}\t{phagemeta.loc[index, 'isolation_country']}")
                seen.add(pmenc.loc[index, 'isolation_country'])

        x_train, x_test, y_train, y_test = train_test_split(pmenc['isolation_country'], phagemeta.Kept.values.ravel())
        clf = RandomForestClassifier(random_state=42, n_estimators=1000, bootstrap=True, n_jobs=32, oob_score=True)
        clf.fit(x_train.ravel().reshape(-1, 1), y_train)
        y_pred = clf.predict(x_test.ravel().reshape(-1, 1))
        print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
        f1base = metrics.f1_score(y_test, y_pred, average='weighted')
        print(f"f1\t{f1base}")

        logo = LeaveOneGroupOut()
        print("\n***********************************\n")
        print("Leaving Out\tf1 delta")

        for trainidx, testidx in logo.split(x_train, y_train, groups=x_train):
            clf.fit(x_train.iloc[trainidx].ravel().reshape(-1, 1), y_train[trainidx])
            new_pred = clf.predict(x_test.ravel().reshape(-1, 1))
            f1measure = metrics.f1_score(y_test, new_pred, average='weighted')
            print(f"{pd.unique(x_train.iloc[testidx].values)}\t{f1base - f1measure}")


    if check_category:
        print("\n***********************************\n")
        print("Code\tCategory")
        seen=set()
        for index, row in phagemeta.iterrows():
            if pmenc.loc[index, 'Category'] not in seen:
                print(f"{pmenc.loc[index, 'Category']}\t{phagemeta.loc[index, 'Category']}")
                seen.add(pmenc.loc[index, 'Category'])


        x_train, x_test, y_train, y_test = train_test_split(pmenc['Category'], phagemeta.Kept.values.ravel())
        clf = RandomForestClassifier(random_state=42, n_estimators=1000, bootstrap=True, n_jobs=32, oob_score=True)
        clf.fit(x_train.ravel().reshape(-1, 1), y_train)
        y_pred = clf.predict(x_test.ravel().reshape(-1, 1))
        print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
        f1base = metrics.f1_score(y_test, y_pred, average='weighted')
        print(f"f1\t{f1base}")

        logo = LeaveOneGroupOut()
        print("\n***********************************\n")
        print("Leaving Out\tf1 delta")

        for trainidx, testidx in logo.split(x_train, y_train, groups=x_train):
            clf.fit(x_train.iloc[trainidx].ravel().reshape(-1, 1), y_train[trainidx])
            new_pred = clf.predict(x_test.ravel().reshape(-1, 1))
            f1measure = metrics.f1_score(y_test, new_pred, average='weighted')
            print(f"{pd.unique(x_train.iloc[testidx].values)}\t{f1base - f1measure}")







if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run leave one group out analysis')
    parser.add_argument('--check_category', help='check the categories', action='store_true')
    parser.add_argument('--check_country', help='check the countries', action='store_true')
    parser.add_argument('-v', help='verbose output', action='store_true')
    args = parser.parse_args()

    if not (args.check_country or args.check_category):
        sys.stderr.write("ERROR: Either --check_category or --check_country must be specified")
        sys.exit(0)

    loo(args.check_country, args.check_category)
