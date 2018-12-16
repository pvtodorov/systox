#!/bin/sh
echo "Make feature_selection/ directory."
mkdir feature_selection
echo "Make feature_selection/01/ directory."
mkdir feature_selection/01/
echo "Make feature_selection/01/genes/ directory."
mkdir feature_selection/01/genes/
echo "Make feature_selection/01/genes/NORMAL/ directory."
mkdir feature_selection/01/genes/NORMAL/
echo "Fetch feature_selection/01/genes/NORMAL/ from Synapse."
synapse get syn14082290 -r --downloadLocation feature_selection/01/genes/NORMAL/.
echo "Make feature_selection/01/genes/NORMAL_scrambled/ directory."
mkdir feature_selection/01/genes/NORMAL_scrambled/
echo "Fetch feature_selection/01/genes/NORMAL_scrambled/ from Synapse."
synapse get syn14085387 -r --downloadLocation feature_selection/01/genes/NORMAL_scrambled/.
echo "Make feature_selection/01/imaging/NORMAL/ directory."
mkdir feature_selection/01/imaging/NORMAL/
echo "Fetch feature_selection/01/imaging/NORMAL/ from Synapse."
synapse get syn14088780 -r --downloadLocation feature_selection/01/imaging/NORMAL/.
echo "Make feature_selection/01/imaging/NORMAL_scrambled/ directory."
mkdir feature_selection/01/imaging/NORMAL_scrambled/
echo "Fetch feature_selection/01/imaging/NORMAL_scrambled/ from Synapse."
synapse get syn14092112 -r --downloadLocation feature_selection/01/imaging/NORMAL_scrambled/.
echo "Deleting Synapse manifest .tsv files."
for i in `find . -name "*.tsv" -type f`; do
    rm "$i"
done
