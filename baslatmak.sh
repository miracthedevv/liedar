#!/bin/bash
# Lie-Dar Başlatma Scripti - Virtual environment otomatik aktif eder

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment bulunamadı!"
    echo "Önce ./kurulum.sh çalıştırın"
    exit 1
fi

# Virtual environment'ı aktif et ve uygulamayı başlat
echo "🚀 Lie-Dar sistemi başlatılıyor..."
echo ""
./venv/bin/python main.py
