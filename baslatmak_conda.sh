#!/bin/bash
# Lie-Dar Conda Environment Başlatma Scripti

# Conda environment'ı aktif et ve uygulamayı başlat
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate liedar
python main.py
