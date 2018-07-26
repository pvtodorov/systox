#!/bin/sh
echo "Make data/processed_data/folds/ directory."
mkdir data/processed_data/folds/
echo "Fetch data/processed_data/folds/ from Synapse."
synapse get syn13901651 -r --downloadLocation data/processed_data/folds/.
echo "Deleting Synapse manifest .tsv files."
for i in `find ./data/processed_data/folds/. -name "*.tsv" -type f`; do
    rm "$i"
done
 
