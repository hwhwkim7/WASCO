#!/usr/bin/env bash

# run_experiments.sh
# usage: bash run_experiments.sh

ALGO="exp"
S=5
B=10

# 모든 3자리 이진 조합(F/F→0, T/ T→1)
TACTICS=(
  "FFF"
  "FFT"
  "FTF"
  "FTT"
  "TFF"
  "TFT"
  "TTF"
  "TTT"
)

for t in "${TACTICS[@]}"; do
  echo ">>> Running tactics=$t"
  python main.py --algorithm "$ALGO" --s "$S" --b "$B" --tactics "$t"
  echo
done