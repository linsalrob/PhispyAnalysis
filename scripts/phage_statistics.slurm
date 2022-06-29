#!/bin/bash


###############################################################
#                                                             #
# Count some statistics about our phages                      #
#                                                             #
# submit with                                                 #
#                                                             #
#     sbatch --array=1-479%50 scripts/phage_statistics.slurm  #
#                                                             #
###############################################################


# How many tasks and processes. Generally set tasks to 1 and cpus-per-task to number of threads you call
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

# How much memory. I usually request 2G
#SBATCH --mem=2G

#SBATCH -e phage_stats/phage_statistics.%A_%a.err
#SBATCH -o phage_stats/phage_statistics.%A_%a.out

echo -e "GENOMEID\tGenome Name\tContigs > 5kb\tGenome Contigs\tNumber of Coding Sequences\tToo short\tNot enough phage hits\tKept\tNote"

LINES=2500
HEADN=$((SLURM_ARRAY_TASK_ID * LINES))

DATE=20220601

for BASE in $(gunzip -c assembly_summary_${DATE}.txt.gz | head -n $HEADN | tail -n $LINES | cut -f 1); do 
	if [[ ${BASE:0:1} == "#" ]]; then continue; fi
	LOG=phispy/${BASE:0:5}/${BASE:0:9}/${BASE:0:13}/${BASE}_VOGS_phispy.log.gz
	if [ ! -e $LOG ]; then
		echo "$BASE NO LOG FILE" >&2;
		continue
	fi
		
	GBK=genbank/${BASE:0:5}/${BASE:0:9}/${BASE:0:13}/${BASE}_genomic.gbff.gz
	if [ -e $GBK ]; then
		DEFN=$(zgrep DEFINITION  $GBK| head -n 1 | sed -e 's/DEFINITION\s\+//');
		# note that GC sneakily has a tab in it!
		GC=$(zgrep LOCUS $GBK | awk 'BEGIN {OFS="\t"} $3 > 5000 {fk++} END {print fk,NR}')
		CDS=$(zgrep -c '^     CDS' $GBK)
	else
		DEFN="GenBank Not Found"
		GC=0
	fi

	KEPT=$(zgrep -c Kept $LOG)
	NOHITS=$(zgrep -c "No genes were identified as phage genes" $LOG)
	SHORT1=$(zgrep -c "Dropped. Not enough genes" $LOG)
	SHORT2=$(zgrep -c "Dropped. Region too small" $LOG)
	SHORT=$((SHORT1+SHORT2))

	NOTE="Unfinished"
	SRCH=$(zgrep "Done!!!" $LOG)
	if [[ ! -z $SRCH ]]; then
		NOTE="Complete";
	fi

	if [[ $((KEPT+NOHITS+SHORT)) == 0 ]]; then
		SRCH=$(zgrep "This is not enough to identify prophages." $LOG);
		if [[ ! -z $SRCH ]]; then 
			#NOTE=$(echo $SRCH | sed -e 's/^.*INFO\s*//')
			NOTE="Too few ORFs"
		fi
		SRCH=$(zgrep 'FATAL: none of protein features had protein ID - can' $LOG);
		if [[ ! -z $SRCH ]]; then
			# NOTE=$(echo $SRCH | sed -e 's/^.*INFO\s*//')
			NOTE="None of the features have protein sequences"
		fi

		SRCH=$(zgrep 'a total of zero total_at\*total_gc' $LOG);
		if [[ ! -z $SRCH ]]; then
			# NOTE=$(echo $SRCH | sed -e 's/^.*INFO\s*//')
			NOTE="A really short gene (pseudo?) crashed phispy"
		fi

		SRCH=$(zgrep "There is no data to process" $LOG)
		if [[ ! -z $SRCH ]]; then
			NOTE="Contigs are less than the cutoff (5000bp)"
		fi

	fi
		

	echo -e "$BASE\t$DEFN\t$GC\t$CDS\t$SHORT\t$NOHITS\t$KEPT\t$NOTE";

done

