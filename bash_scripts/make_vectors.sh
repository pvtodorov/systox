#!/bin/sh
cd process_data/
echo "Making image vector."
./process_data_img.sh
echo "Making genes vector."
./process_data_genes.sh
cd ..