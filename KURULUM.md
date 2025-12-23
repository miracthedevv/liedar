# Lie-Dar Kurulum Rehberi

## ⚡ Süper Hızlı Başlangıç (Önerilen)

Tüm kurulum ve çalıştırma için hazır scriptler var! 

```bash
cd /home/mirac61/Masaüstü/liedar

# 1. Kurulum (sadece ilk seferde)
./kurulum.sh

# 2. Test (opsiyonel)
./test.sh

# 3. Başlat!
./baslatmak.sh
```

**Not:** `source venv/bin/activate` yapmana gerek yok, scriptler otomatik hallediyor! 🎉

---

## 📖 Detaylı Kurulum (Manuel)

Eğer scriptleri kullanmak istemezsen:

### 1. Virtual Environment Oluşturma

Sisteminiz "externally-managed-environment" kullandığı için, bir sanal ortam (virtual environment) oluşturmanız gerekiyor:

```bash
# Proje dizinine gidin
cd /home/mirac61/Masaüstü/liedar

# Virtual environment oluşturun
python3 -m venv venv

# Virtual environment'ı aktif edin
source venv/bin/activate
```

### 2. Bağımlılıkları Yükleyin

Virtual environment aktif iken:

```bash
# Pip'i güncelleyin
pip install --upgrade pip

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 3. PyAudio Sorunu Çözümü

Eğer PyAudio kurulumu hata verirse:

```bash
# Sistem paketlerini yükleyin
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio

# Sonra tekrar deneyin
pip install pyaudio
```

### 4. Uygulamayı Çalıştırın

```bash
# Virtual environment aktif durumdayken
python main.py
```

### 5. Virtual Environment'tan Çıkma

İşiniz bittiğinde:

```bash
deactivate
```

## Her Seferinde Çalıştırma

Sonraki kullanımlarda:

```bash
cd /home/mirac61/Masaüstü/liedar
source venv/bin/activate
python main.py
```

## Test Etme

Kurulumu test etmek için:

```bash
source venv/bin/activate
python test_components.py
```

Bu komut tüm bileşenlerin düzgün yüklendiğini doğrulayacaktır.

---

**Not:** İlk kurulumda venv klasörü oluşacak (yaklaşık 100-200 MB). Bu normal ve gereklidir.
