#!/bin/bash

###############################################################
#                                                             #
# Check that we have processed all the prophage data, and     #
# start additional jobs as required. This slurm profile only  #
# checks for the presence of the output files, and then       #
# submits sbatch scripts to fire other things off.            #
#                                                             #
# It will consume the cluster, but it does finish. Should     #
# perhaps submit them at a lower priority!                    #
#                                                             #
###############################################################


# Time in days-hours. Change this as much as you want
#SBATCH --time=5-0

# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

# How much memory. I usually request 2000M (2 GB) if I am not sure
#SBATCH --mem=2000M


################################################################################################################################
# 
# Before beginning, run find_files.slurm that runs very quickly and finds all the genbank files.
# 
# Use this script to test for appropriate outputs.
# 
# For each entry we should have the following files:
# e.g.
# BASE="GCA_006089895.1_PDT000065163.2"
# 
#  phispy/GCA_00608/GCA_006089895
#  ├── GCA_006089895.1_PDT000065163.2_genomic.gbff.gz
#  └── VOGS
#      ├── checkv
#      │   ├── completeness.tsv.gz
#      │   ├── contamination.tsv.gz
#      │   ├── phispy_summary.tsv
#      │   └── quality_summary.tsv.gz
#      ├── mash
#      │   ├── GCA_006089895.1_PDT000065163.2.msh
#      │   ├── genbank.besthit
#      │   └── genbank_phages.dist.gz
#      ├── GCA_006089895.1_PDT000065163.2_VOG_hits.txt.gz
#      ├── GCA_006089895.1_PDT000065163.2_VOGS_annotations.txt.gz
#      ├── GCA_006089895.1_PDT000065163.2_VOGS_phage.gbk.gz
#      ├── GCA_006089895.1_PDT000065163.2_VOGS_phispy.log.gz
#      ├── GCA_006089895.1_PDT000065163.2_VOGS_prophage_coordinates.tsv.gz
#
#
#	- checkv output:
#		- completeness.tsv.gz  - from checkv
#		- contamination.tsv.gz - from checkv
#		- quality_summary.tsv.gz - from checkv
#		- phispy_summary.tsv (this is one we make and is `gunzip -c $PWD/phispy/${BASE:0:9}/${BASE:0:13}/VOGS/checkv/quality_summary.tsv.gz | grep -v contig_id | cut -f 1,2,5,8`. not gzip compressed)
#	- mash
#		- GCA_006089895.1_PDT000065163.2.msh - the mash file
#		- genbank_phages.dist.gz  (all hits with e value < 1e-5)
#		- genbank.besthit         (single best hit. not gzip compressed)
#
################################################################################################################################

mkdir -p clean_up

FINDF=$1
if [ -z "$FINDF" ]; then
	echo `basename $0` " <output from find_files.slurm with one genome per line>";
	echo "The genomes should have _genomic.gbff.gz in the file name so we can properly parse them."
	exit 1;
fi

for FILE in $(cat $FINDF); do 
	FNAME=`basename $FILE`
	BASE=`basename $FILE _genomic.gbff.gz`
	echo -e "CHECKING\t$BASE"

	# check that we actually ran PhiSpy!
	if [ ! -e "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/" ]; then
		echo -e "TODO\tphispy\t$BASE"
		continue
	fi

	# Check if PhiSpy completed correctly. The last line in the log file is contains "Done"
	DONE=$(gunzip -c phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_phispy.log.gz | grep Done)
	if [ -z "$DONE" ]; then
		echo -e "TODO\tRerun PhiSpy\t$BASE"; 
		continue
	fi
	
	# Check the output. If it is less than 100c we don't find any phages in this genome
	SIZE=$(stat --printf="%s" phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_phage.gbk.gz);
	if [ "$SIZE" -lt 100 ]; then
		echo -e "$BASE\t0\tPHAGECOUNT";
		continue
	fi

	# extract just the VOG hits file
	if [ -e "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOG_hits.txt" ]; then
		T=$(srun gzip phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOG_hits.txt);
	elif [ ! -e "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOG_hits.txt.gz" ]; then
		echo "Extracting vogs for $BASE with job ", $(sbatch --parsable get_vog_hits_one.slurm $BASE)
	fi

	# extract the annotations
	if [ ! -e "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/${BASE}_VOGS_annotations.txt.gz" ]; then
		echo "Extracting annotations for $BASE with job ", $(sbatch --parsable extract_annotations_one.slurm $BASE)
	fi 

	
	# check we have run checkv and initiate it if needed.
	if [ ! -e "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/checkv/NOHITS.txt" ] && [ ! -e "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/checkv/quality_summary.tsv.gz" ]; then
		echo "Running checkv for $BASE with job ", $(sbatch --parsable checkv_one.slurm $BASE)
	fi


	# check we have run mash and initiate it if needed
	if [ ! "phispy/${BASE:0:9}/${BASE:0:13}/VOGS/mash" ]; then
		echo "Running mash for $BASE with job ", $(sbatch --parsable mash_one.slurm $BASE)
	fi

done
