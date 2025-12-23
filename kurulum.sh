#!/bin/bash
# Lie-Dar Hızlı Kurulum Scripti

echo "=================================="
echo "Lie-Dar Kurulum Scripti"
echo "=================================="
echo ""

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment bulunamadı!"
    echo "Önce şunu çalıştırın: python3 -m venv venv"
    exit 1
fi

echo "✓ Virtual environment bulundu"
echo ""

# Sistem bağımlılıklarını kontrol et
echo "🔍 Sistem bağımlılıkları kontrol ediliyor..."
if ! dpkg -l | grep -q portaudio19-dev; then
    echo "⚠️  portaudio19-dev bulunamadı"
    echo "📦 Sistem paketleri kuruluyor (sudo gerektirir)..."
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pyaudio
else
    echo "✓ portaudio19-dev zaten kurulu"
fi

echo ""
echo "📦 Python bağımlılıkları kuruluyor..."

# Virtual environment'ı aktif et ve paketleri kur
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Kurulum başarılı!"
    echo "=================================="
    echo ""
    echo "🚀 Sistemi başlatmak için:"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    echo ""
    echo "🧪 Test için:"
    echo "   source venv/bin/activate"
    echo "   python test_components.py"
else
    echo ""
    echo "=================================="
    echo "❌ Kurulum başarısız oldu"
    echo "=================================="
    echo ""
    echo "Manuel kurulum için KURULUM.md dosyasına bakın."
fi
