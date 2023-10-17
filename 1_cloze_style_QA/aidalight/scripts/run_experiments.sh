#!/bin/bash

# Run it like this:
# run_experiments.sh -p path_to_collection -d collection_type -s path_to/similarities.properties -a alpha (-x if exhaustive search should be used)

LIB_DIRS=( "lib" )
RES_DIRS=( "settings" )

# Build Classpath
CLPA=bin

for dir in ${LIB_DIRS[@]}
do
    for jarf in $dir/*.jar
    do
        CLPA=$CLPA:$jarf
    done
done

for dir in ${RES_DIRS[@]}
do
    CLPA=$CLPA:$dir
done

# Run experiments: the argument must be one of "CoNLL", "MW", "WIKI_LINKS" and "WIKIPEDIA"
java -Xmx8G -cp $CLPA:/home/datnb/Downloads/gurobi550/linux64/lib/* mpi.aidalight.exp.RunExp $@
