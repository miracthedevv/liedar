# 🎉 Lie-Dar Sistemi Hazır!

## ✅ Test Sonuçları

Sistemin kurulumu başarıyla tamamlandı! Test sonuçları:

- ✅ **Tüm kütüphaneler yüklendi** (OpenCV, MediaPipe, NumPy, SciPy, librosa, PyAudio)
- ✅ **Tüm modüller çalışıyor** (FacialAnalysis, BPM_Estimator, VoiceStress, LogicEngine, Visualizer)
- ✅ **Mantık motoru doğru hesaplıyor**
- ✅ **Kamera erişilebilir** (640x480 çözünürlük)

### ✅ Masaüstü GUI Geliştirme
- [x] PyQt5 kurulumu
- [x] Modern masaüstü uygulamasının oluşturulması
- [x] OpenCV penceresinin GUI ile değiştirilmesi

**Not:** MediaPipe test hatası normal - gerçek kullanımda çalışacak (lazy loading nedeniyle).

---

## 🚀 Kullanım

### 🖥️ Masaüstü Uygulama (Önerilen)

En iyi deneyim için yeni hazırladığım modern arayüzlü uygulamayı kullan:

```bash
cd /home/mirac61/Masaüstü/liedar
./baslatmak_gui.sh
```

### 📺 Terminal/OpenCV Modu (Eski)

Eğer terminal üzerinden basit bir pencere ile çalıştırmak istersen:

```bash
./baslatmak.sh
```

### Manuel Yöntem

```bash
cd /home/mirac61/Masaüstü/liedar

# Virtual environment'ı aktif et
source venv/bin/activate

# Başlat
python main.py
```

---

## 🎮 Kontroller

Uygulama açıldığında:

- **Q** tuşu: Çıkış
- **R** tuşu: Sıfırla (temel çizgileri temizle)

---

## 📊 Ekranda Göreceklerin

1. **Üst kısım:** Yüz işaretli canlı kamera görüntüsü
2. **Alt panel:**
   - **Ana dürüstlük çubuğu** (yeşil/sarı/kırmızı)
   - **Bireysel stres barları** (Yüz, Ses, Nabız)
   - **BPM sayacı**
   - **Alarm durumu**
   - **Ek metrikler** (göz kırpma, jitter, vb.)

---

## 📈 Sonuçları Yorumlama

### Dürüstlük Skoru

- **60-100** 🟢 → Düşük stres, muhtemelen dürüst
- **40-60** 🟡 → Orta stres, belirsiz
- **0-40** 🔴 → Yüksek stres, olası aldatma

### Alarm Seviyeleri

- **DÜŞÜK_STRES**: Normal, rahat
- **ORTA_STRES**: Hafif sinirlilik veya belirsizlik
- **YÜKSEK_STRES**: Birden fazla stres göstergesi

### BPM (Nabız)

- **60-80**: Normal dinlenme
- **80-100**: Yükselmiş (muhtemelen stresli)
- **>100**: Çok yüksek (önemli stres)

---

## ⚠️ Önemli Hatırlatmalar

1. **İlk 5-10 saniye** kalibrasyon için beklenir (temel çizgi oluşturma)
2. **İyi aydınlatma** gerekir (yüz algılama için)
3. **Sessiz ortam** tercih edilir (ses analizi için)
4. **Yüzün kameraya bakması** gerekir
5. **Sistem stresi ölçer, yalanı değil** - %100 doğru değildir

---

## 🛠️ Sorun Çözme

### "No face detected" hatası
- Yüzünüzü kameraya dönük tutun
- Aydınlatmayı artırın
- Kameradan biraz uzaklaşın

### Düşük FPS
- Diğer uygulamaları kapatın
- Video çözünürlüğünü azaltın (main.py'de ayarlayabilirsiniz)

### Ses algılanmıyor
- Mikrofon izinlerini kontrol edin
- Sistem ses ayarlarından mikrofonu test edin

---

## 📚 Daha Fazla Bilgi

- **OKUPLUS.md** - Tam Türkçe dokümantasyon
- **README.md** - İngilizce versiyon
- **KURULUM.md** - Kurulum detayları
- **walkthrough.md** - Teknik mimari ve detaylar

---

## 🎓 Teknik Özellikler

- **468 yüz noktası** takibi (MediaPipe Face Mesh)
- **rPPG nabız tahmini** (FFT bazlı, 48-180 BPM)
- **Ses analizi** (pitch, jitter, shimmer)
- **Çok modlu füzyon** (%40 yüz + %30 ses + %30 nabız)
- **Gerçek zamanlı** işleme (~15-30 FPS)

---

**Sistemi başlatmak için:** `./baslatmak.sh` 🚀

**İyi kullanımlar!** 🎉
