#!/usr/bin/env bash
# Data Polygamy jar is stored in $DATA_POLYGAMY_JAR
# Scripts are stored under $SCRIPTS_PATH
# Data Polygamy is stored in $DATA_POLYGAMY

# User provided variables
dataname=$1
latindex=$2
lngindex=$3
zoneid=$4
temporalindex=$5

m="r3.2xlarge"
n=1

# Filter data based on zone
hadoop fs -cat data/$dataname > /tmp/spatialdata
python3 $SCRIPTS_PATH/filternbhd.py $DATA_POLYGAMY/data/neighborhood.txt /tmp/spatialdata /tmp/spatialdata.filtered $latindex $lngindex $zoneid 1>&2

# Store filtered data in hdfs
hadoop fs -rm filtereddata filtereddata.defaults filtereddata.header 1>&2
hadoop fs -rm -r pre-processing/filtereddata* 1>&2
hadoop fs -rm -r aggregates/filtereddata* 1>&2
hadoop fs -rm -r index/filtereddata* 1>&2

hadoop fs -put /tmp/spatialdata.filtered data/filtereddtata 1>&2
hadoop fs -cp data/$dataname.defaults data/filtereddata.defaults 1>&2
hadoop fs -cp data/$dataname.header data/filtereddata.header 1>&2

# TODO Add filtered output to datasets

# Preprocessing, Aggregation, Indexing
hadoop jar $DATA_POLYGAMY_JAR edu.nyu.vida.data_polygamy.pre_processing.PreProcessing -m $m -n $n -dn filtereddata -dh filtereddata.header -dd filtereddata.defaults -t hour -s nbhd -cs points -i $temporalindex $lngindex $latindex 1>&2
hadoop jar $DATA_POLYGAMY_JAR edu.nyu.vida.data_polygamy.scalar_function_computation.Aggregation -m $m -n $n -g filtereddata 0 0 1>&2
hadoop jar $DATA_POLYGAMY_JAR edu.nyu.vida.data_polygamy.feature_identification.IndexCreation -f -m $m -n $n -g filtereddata 1>&2

# Output results
hadoop fs -libjars $DATA_POLYGAMY_JAR -text index/filtereddata/data-r*
