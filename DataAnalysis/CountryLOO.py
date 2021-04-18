"""
Run a random forest leave one out analysis on a cluster
"""

import sys
import pandas as pd
import re
from sklearn.ensemble import RandomForestClassifier
from PhiSpyAnalysis import theils_u, DateConverter
import subprocess


def get_acc_name(x):
    regexp = re.compile('(\\w+\.\\d+)_([\\w\.\\-]+)_genomic.gbff.gz')
    m = regexp.match(x)
    if not m:
        sys.stderr.write(f"WARNING: Regexp did not match {x}\n")
        return (None, None)
    return list(m.groups())

def loo():
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

    clf = RandomForestClassifier(random_state=42, n_estimators=1000, bootstrap=True, n_jobs=-1, oob_score=True)

    # fit the initial data
    initial_rf = clf.fit(pmenc, phagemeta.Kept.values.ravel())
    init_importance = dict(zip(pmenc.columns, initial_rf.feature_importances_))

    print(f"Initial importance: {init_importance}")

    print("Country Ommitted\tImportance\tImportance delta")
    imps = {}
    for c in pd.unique(phagemeta['isolation_country']):
        changedc = phagemeta.replace(c, "None")
        pmenc['isolation_country'] = changedc['isolation_country'].astype('category').cat.codes
        rf = clf.fit(pmenc, phagemeta.Kept.values.ravel())
        imps[c] = rf.feature_importances_[0]
        print(f"{c}\t{imps[c]}\t{init_importance['isolation_country'] - imps[c]}")


if __name__ == "__main__":
    loo()
