#!/bin/sh
echo "Make run_settings/ directory."
mkdir run_settings
echo "Fetch run_settings/ from Synapse."
synapse get syn15589424 -r --downloadLocation run_settings/.
echo "Deleting Synapse manifest .tsv files."
for i in `find . -name "*.tsv" -type f`; do
    rm "$i"
done
 
