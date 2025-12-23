# Lie-Dar: Gerçek Zamanlı Yalan Dedektörü Sistemi

![Versiyon](https://img.shields.io/badge/versiyon-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![Lisans](https://img.shields.io/badge/lisans-MIT-orange)

## ⚠️ Önemli Uyarı

**Bu sistem yalnızca eğitim ve araştırma amaçlıdır.** Yalan algılama teknolojisi tartışmalıdır ve %100 doğru değildir. Bu araç şunlar için kullanılmamalıdır:
- Yasal işlemler
- İstihdam kararları
- Güvenlik taramaları
- Herhangi bir kritik karar verme süreci

Sistem yalan değil, stres göstergelerini tespit eder. Birçok faktör (sinirlilik, tıbbi durumlar, çevresel faktörler) yanlış pozitif sonuçlara neden olabilir.

KISACA BU BİR TIBBİ ARAÇ YADA KESİN DEDEKTÖR DEĞİLDİR!

## 🎯 Özellikler

### 1. **Yüz Mikro-İfade Analizi**
- MediaPipe Face Mesh kullanarak **468 yüz işaretini** takip eder
- Mikro-ifadeleri tespit eder:
  - Kaş hareketleri (gerginlik göstergeleri)
  - Dudak sıkıştırma kalıpları
  - Anormal göz kırpma oranları
- Kayan pencere ile istatistiksel anomali tespiti

### 2. **rPPG Nabız Tahmini**
- **Uzaktan fotopletismografi** kullanarak videodan kalp atış hızı tahmin eder
- Alın bölgesindeki renk değişimlerini analiz eder (kan akışı)
- FFT tabanlı BPM hesaplama (48-180 BPM aralığı)
- Stres göstergesi olarak yüksek kalp atış hızını tespit eder

### 3. **Ses Stres Analizi**
- Gerçek zamanlı mikrofon ses yakalama
- Akustik özellik çıkarımı:
  - **Perde değişimi** (F0 analizi)
  - **Jitter** (frekans bozulması)
  - **Shimmer** (genlik bozulması)
- Vokal gerilime dayalı stres puanlaması

### 4. **Çok Modlu Füzyon**
- Ağırlıklı ortalama ile üç veri akışını birleştirir:
  - %40 Yüz analizi
  - %30 Ses stresi
  - %30 Nabız tahmini
- **Dürüstlük Skoru** çıktısı verir (0-100 ölçeği)

### 5. **Gerçek Zamanlı Görselleştirme**
- Yüz işaretli canlı video
- Renkli dürüstlük çubuğu (yeşil/sarı/kırmızı)
- Bireysel modalite stres göstergeleri
- BPM sayacı ve alarm durumu

## 🚀 Hızlı Başlangıç

### Ön Gereksinimler

- Python 3.8 veya üzeri
- Web kamerası
- Mikrofon
- Linux/macOS/Windows

### Kurulum

**KURULUM.md dosyasına bakın!** Virtual environment kurulumu gereklidir.

Kısa özet:

```bash
cd /home/mirac61/Masaüstü/liedar

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Test et
python test_components.py

# Çalıştır
python main.py
```

**Not:** `pyaudio` kurulumu için ek adımlar gerekebilir. KURULUM.md dosyasına bakın.

## 📊 Nasıl Çalışır?

### Sistem Mimarisi

```
┌─────────────┐
│   Kamera    │
└──────┬──────┘
       │
       v
┌────────────────────────────────────────┐
│     Yüz Analizi Modülü                 │
│  - MediaPipe işaret takibi             │
│  - Mikro-ifade tespiti                 │
│  - Anomali puanlaması                  │
└──────┬─────────────────────────────────┘
       │
       v
┌────────────────────────────────────────┐
│     rPPG Nabız Tahmincisi              │
│  - Alın ROI çıkarımı                   │
│  - Yeşil kanal PPG sinyali             │
│  - FFT tabanlı BPM hesaplama           │
└──────┬─────────────────────────────────┘
       │
       v
┌─────────────┐         ┌─────────────────────────────────┐
│  Mikrofon   │────────>│  Ses Stres Analizörü            │
└─────────────┘         │  - Perde değişimi               │
                        │  - Jitter/Shimmer hesaplama     │
                        │  - Stres puanlaması             │
                        └──────┬──────────────────────────┘
                               │
                               v
                        ┌──────────────────────────────┐
                        │     Mantık Motoru            │
                        │  - Çok modlu füzyon          │
                        │  - Ağırlıklı puanlama        │
                        │  - Alarm sınıflandırması     │
                        └──────┬───────────────────────┘
                               │
                               v
                        ┌──────────────────────────────┐
                        │     Görselleştirici          │
                        │  - Gerçek zamanlı ekran      │
                        │  - Renkli çubuklar           │
                        │  - Metrik overlay            │
                        └──────────────────────────────┘
```

### Matematiksel Yaklaşım

#### Yüz Analizi
- **Kaş Mesafesi:** `mesafe = göz_y - kaş_y`
- **Anomali Skoru:** `z_skoru = |mevcut - ortalama| / std_sapma`
- **Normalizasyon:** `skor = min(100, (z_skoru / 2σ) × 100)`

#### rPPG Tahmini
- **PPG Sinyali:** Alın ROI'sinde ortalama yeşil kanal yoğunluğu
- **Filtreleme:** Butterworth bandpass (0.8-3.0 Hz)
- **BPM:** FFT ile `frekans_tepe × 60`

#### Ses Stresi
- **Jitter:** `(1/N) × Σ|T_i - T_(i+1)| / ortalama(T) × 100`
- **Shimmer:** `(1/N) × Σ|A_i - A_(i+1)| / ortalama(A) × 100`

#### Çok Modlu Füzyon
```
birleşik_stres = 0.4×yüz + 0.3×ses + 0.3×nabız
dürüstlük_skoru = 100 - birleşik_stres
```

## 🎮 Kullanım

### Kontroller

- **Q** - Uygulamadan çık
- **R** - Tüm analizörleri sıfırla (temel çizgileri temizle)

### Sonuçların Yorumlanması

**Dürüstlük Skoru:**
- **60-100** (Yeşil): Düşük stres, muhtemelen dürüst
- **40-60** (Sarı): Orta stres, belirsiz
- **0-40** (Kırmızı): Yüksek stres, olası aldatma

**Alarm Seviyeleri:**
- `DÜŞÜK_STRES`: Minimal aldatma göstergeleri
- `ORTA_STRES`: Karışık sinyaller, olası sinirlilik
- `YÜKSEK_STRES`: Birden fazla aldatma göstergesi tespit edildi

**BPM (Kalp Atış Hızı):**
- Normal dinlenme: 60-80 BPM
- Yüksek (stres): 80-100 BPM
- Çok yüksek (önemli stres): >100 BPM

## 🔧 Yapılandırma

`main.py` dosyasındaki başlangıç ayarlarını değiştirerek sistem parametrelerini ayarlayabilirsiniz:

```python
# Yüz analizi hassasiyeti
facial_analyzer = FacialAnalysis(
    window_size=30,      # Temel pencere (kare)
    sensitivity=2.0      # Standart sapma eşiği
)

# Nabız tahmini tamponu
bpm_estimator = BPM_Estimator(
    fps=30,
    buffer_seconds=10    # Sinyal tampon süresi
)

# Ses analizi
voice_analyzer = VoiceStress(
    sample_rate=16000,
    chunk_duration=1.0
)

# Füzyon ağırlıkları
logic_engine = LogicEngine(
    facial_weight=0.40,  # %40 ağırlık
    voice_weight=0.30,   # %30 ağırlık
    pulse_weight=0.30    # %30 ağırlık
)
```
Eğer üşeniyorsanız yapılandırmanıza gerek yok. Çünkü zaten en iyi şekilde yapılandırılmış olarak sunulmaktadır :)
## 📁 Proje Yapısı

```
liedar/
├── main.py                 # Uygulama giriş noktası
├── requirements.txt        # Python bağımlılıkları
├── OKUPLUS.md             # Bu dosya (Türkçe README)
├── KURULUM.md             # Kurulum rehberi
├── test_components.py     # Test scripti
└── src/
    ├── facial_analysis.py  # MediaPipe yüz takibi
    ├── bpm_estimator.py    # rPPG nabız tahmini
    ├── voice_stress.py     # Ses stres analizi
    ├── logic_engine.py     # Çok modlu füzyon
    └── visualizer.py       # Gerçek zamanlı UI
```

## 🐛 Sorun Giderme

### Kamera Açılmıyor
- Başka bir uygulamanın web kamerasını kullanmadığından emin olun
- Farklı kamera ID'leri deneyin: `LieDar(camera_id=1)`
- Kamera izinlerini kontrol edin

### Ses Sorunları
- Mikrofon izinlerini doğrulayın
- Test edin: `python -m sounddevice`
- `pyaudio` kurulumunu kontrol edin (KURULUM.md'ye bakın)

### Düşük FPS
- Video çözünürlüğünü azaltın
- Diğer uygulamaları kapatın
- MediaPipe için GPU hızlandırmasını düşünün

### "Yüz tespit edilmedi" Hataları
- Yüzün iyi aydınlatıldığından ve görünür olduğundan emin olun
- Yüzü kamera çerçevesi içinde konumlandırın
- MediaPipe tespit güvenini ayarlayın

## 🔬 Teknik Detaylar

### Bağımlılıklar

- **OpenCV** (>=4.8.0): Video yakalama ve işleme
- **MediaPipe** (>=0.10.0): Yüz işaret tespiti
- **NumPy** (>=1.24.0): Sayısal işlemler
- **SciPy** (>=1.11.0): Sinyal işleme (FFT, filtreler)
- **librosa** (>=0.10.0): Ses özellik çıkarımı
- **PyAudio** (>=0.2.13): Mikrofon girişi

### Performans Optimizasyonu

- Yüz işaretleri kare başına bir kez hesaplanır
- FFT tabanlı BPM tahmini (verimli frekans analizi)
- Asenkron ses yakalama
- Temel hesaplama için kayan pencereler
- BPM kararlılığı için medyan yumuşatma

## ⚖️ Sınırlamalar

- **%100 doğru değil** - yalan değil stresi tespit eder
- **Çevresel faktörler** ölçümleri etkiler (aydınlatma, gürültü)
- **Bireysel değişkenlik** - bazı insanlar farklı stres kalıpları gösterir
- **Temel bağımlılık** - başlangıç kalibrasyon süresi gerektirir
- **Donanım bağımlılığı** - kalite kamera/mikrofona göre değişir

## 🤝 Katkıda Bulunma

Bu eğitimsel bir projedir. Potansiyel iyileştirmeler:

- [ ] Kural tabanlı puanlama yerine makine öğrenimi sınıflandırması
- [ ] Bireysel temel çizgiler için kalibrasyon aşaması
- [ ] Geçmiş veri kayıt ve analizi
- [ ] Çoklu yüz takibi
- [ ] Göz bakış yönü analizi
- [ ] Termal görüntüleme entegrasyonu

## 📄 Lisans

MIT Lisansı - Detaylar için LICENSE dosyasına bakın

## 🙏 Teşekkürler

- Google'daki MediaPipe ekibine yüz işaret tespiti için
- librosa geliştiricilerine ses analizi araçları için
- OpenCV topluluğuna bilgisayarlı görü çerçevesi için

---

**Eğitim amaçlı ❤️ ile yapılmıştır**

*Unutmayın: Bu, çok modlu sinyal işlemenin bir gösterimidir, profesyonel bir poligraf sistemi değildir.*
