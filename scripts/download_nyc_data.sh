#!/usr/bin/env bash
data_from=1
data_to=2
mkdir data
pushd .
cd data

#for i in $(seq -f "%02g" "$data_from" "$data_to")
#do
#    echo $i
#done

for i in $(seq -f "%02g" "$data_from" "$data_to")
do
    axel -a "https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2016-$i.csv"
done

# concatenate all the data
for i in $(seq -f "%02g" "$data_from" "$data_to")
do
    cat "yellow_tripdata_2016-$i.csv" >> data.csv
done

popd

# write the zones in the files
java -cp $SPATIAL_EXP_JAR edu.asu.misc.GeoSparkZoneWriter data/data.csv boundaries.csv

# upload files to hadoop
hadoop dfs -put data/yellowdata_columns.csv data.csv




