#!/bin/bash
# Lie-Dar GUI Başlatma Scripti

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment bulunamadı!"
    exit 1
fi

# Avoid Qt conflicts between OpenCV and PyQt5
export QT_QPA_PLATFORM_PLUGIN_PATH=$(./venv/bin/python -c "import PyQt5; import os; print(os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins', 'platforms'))")
export QT_DEBUG_PLUGINS=0

# GUI versiyonu başlat
echo "🚀 Lie-Dar GUI başlatılıyor..."
./venv/bin/python main_gui.py
