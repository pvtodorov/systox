#!/bin/sh
echo "Make data/ directory."
mkdir data
echo "Make data/original_data/ directory."
mkdir data/original_data
echo "Fetch data/original_data/ from Synapse."
synapse get syn11697966 -r --downloadLocation data/original_data/.
echo "Make data/lists/ directory."
mkdir data/lists
echo "Fetch lists from Synapse."
synapse get syn13922909 --downloadLocation data/lists/.
echo "Deleting Synapse manifest .tsv files."
for i in `find . -name "*.tsv" -type f`; do
    rm "$i"
done
 
