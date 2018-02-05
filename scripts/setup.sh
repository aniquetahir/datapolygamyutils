#!/usr/bin/env bash
apt install axel default-jdk maven git
git clone https://github.com/aniquetahir/yellowtaxi.git
pushd ./
cd yellowtaxi
mvn clean install
# TODO Fix filename
export SPATIAL_EXP_JAR=$(pwd)/target/yellowtaxi-1.0-SNAPSHOT-jar-with-dependencies.jar
popd
