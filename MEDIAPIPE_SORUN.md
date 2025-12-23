# MediaPipe Uyumluluk Sorunu ve Çözümler

## 🔴 Mevcut Durum

MediaPipe'ın **tüm 0.10.x versiyonları** (0.10.13-0.10.31) Python 3.12 ile aynı graph validation hatasını veriyor:

```
ValueError: while processing the input streams of subgraph node InferenceCalculator: 
TAG:index:name is invalid
```

Bu MediaPipe'ın bilinen bir bug'ı.

## ✅ Kalıcı Çözüm

###Python 3.10 veya 3.11 Kullan

MediaPipe bu Python versiyonlarıyla sorunsuz çalışıyor.

**Seçenek 1: pyenv ile Python 3.10 Kurulumu**
```bash
# pyenv kur (eğer yoksa)
curl https://pyenv.run | bash

# Python 3.10 kur
pyenv install 3.10.13

# Proje için Python 3.10 kullan
cd /home/mirac61/Masaüstü/liedar
pyenv local 3.10.13

# Virtual environment yeniden oluştur
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Çalıştır
python main.py
```

**Seçenek 2: Sistem Python 3.10**
```bash
sudo apt install python3.10 python3.10-venv
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🔧 Alternatif: Basitleştirilmiş Versiyon (MediaPipe'sız)

Eğer Python değiştirmek istemiyorsan, MediaPipe olmadan çalışan basit bir versiyon hazırlayabilirim:

**Özellikler:**
- ✅ **Ses Analizi** (pitch, jitter, shimmer)
- ✅ **Nabız Tahmini** (basit rPPG, yüz tespiti için OpenCV Haar Cascade)
- ❌ Yüz mikro-ifade analizi yok (468 landmark yerine basit yüz tespiti)

**Dürüstlük Skoru:**
- %50 Ses
- %50 Nabız

Bu versiyon hemen çalışır!

## 🎯 Tavsiyem

**Eğer proje ciddi ise:** Python 3.10 kur (30 dakika)
**Eğer hızlı test istiyorsan:** Basit versiyon (5 dakika)

Hangisini tercih edersin?
