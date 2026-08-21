# AI Failure Observatory

🇹🇷 Türkçe Dokümantasyon | 🇺🇸 [English Documentation](README.md)

> Üretken Yapay Zeka ve Büyük Dil Modelleri için davranışsal güvenlik, kırılganlık testi ve ürün riski denetim platformu.

Büyük Dil Modellerini (LLM) canlı iş akışlarına veya üretime almadan önce **6 kritik hata ve başarısızlık modunu** tespit etmek, izlemek, stres testine tabi tutmak ve raporlamak için tasarlanmış hafif ve yerel bir gözlemevi platformu.

---

## 🚀 Öne Çıkan Özellikler

### 1. 🧠 Davranışsal Hata Tespit Motoru
- **Halüsinasyonlar (`hallucinations`):** Olmayan akademik makale, sahte yazar/dergi alıntıları ve uydurma olgusal iddiaları yakalar.
- **Sahte Güven (`fake_confidence`):** Yanlış bir bilgiyi şüphe payı veya epistemik koruma olmadan aşırı kesin bir dille savunan ifadeleri işaretler.
- **Bağlam Kaybı (`context_loss`):** Çok turlu konuşmalarda kısa süreli hafıza kaybını ve geçmiş talimatların unutulmasını tespit eder.
- **Talimat Sapması (`instruction_drift`):** Olumsuzluk kısıtlamalarını ve yasaklanan anahtar kelime kurallarını ihlal eden yanıtları yakalar.
- **Manipülasyon & Yönlendirme (`manipulation`):** Kullanıcıyı ticari veya psikolojik baskıyla aceleye getiren veya yönlendiren dilleri tespit eder.
- **Özyinelemeli Akıl Yürütme Çöküşü (`recursive_reasoning_collapse`):** Döngüsel mantık kilitlenmelerini ve tekrarlayan çöküşleri yakalar.

### 2. ⚡ Canlı Çoklu LLM Stres Testi
- Harici bağımlılık gerektirmeyen `urllib.request` entegrasyonu ile canlı model sorgulama:
  - 🟢 **Dahili Sezgisel Simülatör:** API anahtarı gerekmez, anında çevrimdışı çalışır.
  - ✨ **Google Gemini:** `gemini-2.0-flash`, `gemini-1.5-pro`
  - 🧠 **OpenAI:** `gpt-4o-mini`, `gpt-4o`, `o3-mini`
  - ⚡ **Anthropic Claude:** `claude-3-5-sonnet-20241022`

### 3. 💾 Kalıcı Olay Deposu & Gerçek Zamanlı Risk Endeksi
- Yapılan her manuel analiz ve canlı stres testi otomatik olarak `data/incidents.json` dosyasına kaydedilir.
- Dashboard risk skoru, olay sayıları ve ciddiyet grafikleri gerçek test verileriyle anlık güncellenir.

### 4. 📄 Yönetici Uyum ve Denetim Raporu İndirme (Export)
- Tespit edilen açıkları, ciddiyet seviyelerini ve risk azaltma önerilerini içeren biçimlendirilmiş Markdown denetim raporu üretir ve indirir.

### 5. 🌐 Tam İki Dilli Arayüz (TR ⟷ EN)
- Kontrol paneli, kontroller, tablolar ve tuzak istemler arasında tek tıkla dinamik Türkçe/İngilizce geçişi.

### 6. 🔌 Dinamik Port Çakışma Yönetimi
- Varsayılan olarak `5089` portunda başlar; port meşgulse otomatik olarak bir sonraki boş porta geçer.

---

## 🛠️ Kurulum ve Başlangıç

### 1. Bağımlılıkları Yükleyin
```bash
git clone https://github.com/adacreativeco/ai-failure-observatory.git
cd ai-failure-observatory
pip install -r requirements.txt
```

### 2. Gözlemevi Sunucusunu Başlatın
```bash
python server.py
```
Tarayıcınızda [http://localhost:5089](http://localhost:5089) adresini açın.

### 3. Otomatik Birim Testlerini Çalıştırın
```bash
python -m unittest tests/test_observatory.py
```

### 4. Tekrarlanabilir Kıyaslama Testlerini Çalıştırın
```bash
python experiments/reproducible_evals/run_all_evals.py
```

---

## 📂 Proje Mimarisi

```
ai-failure-observatory/
├── server.py                       # HTTP sunucusu ve REST API'ları (Port 5089)
├── index.html                      # Tek sayfa iki dilli web arayüzü
├── src/
│   ├── failure_analyzer.py         # Sezgisel hata tespit motoru
│   ├── storage.py                  # Kalıcı JSON olay depolama katmanı
│   ├── llm_client.py               # Çoklu sağlayıcı canlı LLM istemcisi
│   ├── eval_generator.py           # Değerlendirme test vakası üreticisi
│   └── utils.py                    # Metin işleme ve token yardımcıları
├── taxonomy/
│   ├── ai_failure_taxonomy.md      # Kapsamlı hata taksonomisi referansı
│   └── taxonomy_utils.py           # Taksonomi yükleyici ve yardımcıları
├── analysis/
│   └── risk_analysis.py            # Ürün riski puanlama formülleri ve raporlar
├── experiments/
│   ├── reproducible_evals/         # 6 adet tekrarlanabilir kıyaslama testi
│   └── synthetic/                  # Sentetik hata verisi üreticileri
├── tests/
│   └── test_observatory.py         # Kapsamlı birim test paketi (13 test)
├── data/                           # Olay depolama dizini (incidents.json)
└── requirements.txt                # Hafif bağımlılıklar
```

---

## 📄 Lisans

Apache 2.0 Lisansı kapsamında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.
