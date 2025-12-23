# Lie-Dar: Gerçek Zamanlı Çok Modlu Yalan Dedektörü

Lie-Dar, yapay zeka ve biyometrik veri analizi kullanarak real-time (gerçek zamanlı) dürüstlük ve stres analizi yapan bir MVP'dir.

## 🌟 Özellikler

- **Modern Masaüstü Uygulaması:** PyQt5 ile geliştirilmiş, kullanıcı dostu arayüz.
- **Ses Analizi:** Titreme (Jitter), Parlama (Shimmer) ve Perde (Pitch) analizi ile ses stresini ölçer.
- **Nabız Tahmini (rPPG):** Kamera üzerinden temassız kalp atışı tahmini.
- **Dinamik Füzyon:** Farklı kanallardan gelen verileri ağırlıklı olarak birleştirerek tek bir "Dürüstlük Skoru" üretir.

## 🚀 Hızlı Başlangıç

### 1. Kurulum
Terminali açın ve projenin olduğu dizine gidin:
```bash
chmod +x *.sh
./kurulum.sh
```

### 2. Uygulamayı Başlat (GUI)
En iyi deneyim için modern masaüstü arayüzünü kullanın:
```bash
./baslatmak_gui.sh
```

### 3. Klasik Mod (Opsiyonel)
OpenCV penceresi ile çalıştırmak isterseniz:
```bash
./baslatmak.sh
```

## 📊 Nasıl Çalışır?

Sistem üç ana veri kaynağını analiz eder (Mevcut versiyonda MediaPipe kısıtlamaları nedeniyle Ses ve Nabız ön plandadır):

1. **Ses (%60):** Konuşma sırasındaki mikro-seviye frekans ve genlik bozulmalarını analiz eder.
2. **Nabız (%40):** Alın bölgesindeki deri rengi değişimlerinden kalp atış hızındaki ani artışları takip eder.
3. **Yüz (Opsiyonel):** Göz kırpma hızı ve mikro-ifadeleri takip eder (Landmark takibi aktif olduğunda).

## 🛠️ Kontroller

- **Q:** Uygulamadan çıkış yapar.
- **R:** İstatistiki verileri sıfırlayarak kalibrasyonu yeniler.

## ⚠️ Önemli Uyarı
Bu proje eğitim ve araştırma amaçlı bir MVP'dir. Kesin sonuçlar vermeyebilir ve profesyonel bir yalan makinesinin (Poligraf) yerine geçmez.

---
**Geliştirici:** Antigravity AI
