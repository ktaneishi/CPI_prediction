#!/bin/bash
#SBATCH --partition xdg-003-compute

export OMP_NUM_THREADS=20
export MKL_NUM_THREADS=$OMP_NUM_THREADS

DATASET=human
# DATASET=celegans
# DATASET=yourdata

radius=2

ngram=3

dim=10

layer_gnn=3

window=5  # The window size is 2*window+1.

layer_cnn=3

lr=1e-4

lr_decay=0.5

decay_interval=10

iteration=100

setting=$DATASET--radius$radius--ngram$ngram--dim$dim--layer_gnn$layer_gnn--window$window--layer_cnn$layer_cnn--lr$lr--lr_decay$lr_decay--decay_interval$decay_interval

echo $OMP_NUM_THREADS

python run_training.py $DATASET $radius $ngram $dim $layer_gnn $window $layer_cnn $lr $lr_decay $decay_interval $iteration $setting
