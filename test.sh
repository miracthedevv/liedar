#!/bin/bash
# Lie-Dar Test Scripti - Virtual environment otomatik aktif eder

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment bulunamadı!"
    echo "Önce ./kurulum.sh çalıştırın"
    exit 1
fi

# Virtual environment'ı aktif et ve test çalıştır
echo "🧪 Testler çalıştırılıyor..."
./venv/bin/python test_components.py
