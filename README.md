# 🎧 VibePlaylist AI

**Upload a photo → AI reads the vibe → Get a playlist that matches the mood.**

VibePlaylist AI is an AI-powered music recommendation app built with **Python**, **Streamlit**, and **Google Gemini**. It analyzes the visual context of any image — scene, lighting, colors, mood, atmosphere — and curates a personalized playlist that captures the same energy.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?logo=streamlit)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-4285F4?logo=google)

---

## ✨ Features

- **🔍 Deep Visual Analysis** — Detects scene, environment, lighting, time of day, dominant colors, objects, activities, mood, and overall vibe.
- **🌐 Multi-Language Support** — English · Hindi · Bengali · Punjabi · Tamil · Telugu · Any Language.
- **🎵 10-Song Curated Playlists** — Real songs by real artists, with reasons explaining why each song fits the vibe.
- **🎨 Beautiful Dark UI** — Gradient theming, animated cards, and a polished aesthetic.
- **⚡ Powered by Gemini 2.0 Flash** — Fast, accurate multimodal AI.

---

## 🚀 Quick Start

### 1. Clone & enter the project

```bash
cd muai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your API key

Get a **free** Google Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

**Option A — `.env` file (recommended):**

```bash
cp .env.example .env
# Edit .env and paste your key
```

**Option B — Paste it in the app sidebar** at runtime.

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## 🖼️ How It Works

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐
│  Upload Photo │────▸│  Gemini Vision AI  │────▸│  Vibe Analysis   │
└──────────────┘     │  (image analysis)  │     │  (structured)    │
                     └───────────────────┘     └────────┬─────────┘
                                                        │
                                                        ▼
                     ┌───────────────────┐     ┌──────────────────┐
                     │  Gemini Text AI    │◂────│  Language Choice │
                     │  (playlist gen)   │     └──────────────────┘
                     └────────┬──────────┘
                              │
                              ▼
                     ┌───────────────────┐
                     │  🎶 10-Song       │
                     │     Playlist      │
                     └───────────────────┘
```

### Visual Context Factors Analyzed

| Factor | Example |
|--------|---------|
| Scene / Location | Beach at sunset, city rooftop |
| Environment | Indoor, outdoor, urban, nature |
| Lighting | Warm golden glow, harsh neon |
| Time of Day | Morning, golden-hour, night |
| Dominant Colors | Amber, teal, crimson |
| Nature Elements | Mountains, ocean, rain |
| Objects & Activities | Campfire, dancing, reading |
| Atmosphere | Serene, electric, nostalgic |
| Emotional Mood | Joyful, melancholic, peaceful |
| Visual Aesthetic | Cinematic, vintage, dreamy |
| Overall Vibe | "Rainy café solitude" |

---

## 📁 Project Structure

```
muai/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example            # API key template
├── .streamlit/
│   └── config.toml         # Streamlit dark theme
└── README.md               # This file
```

---

## 🔑 API Key

This app uses **Google Gemini 2.0 Flash**, which offers a generous free tier. Get your key at:

👉 **[aistudio.google.com/apikey](https://aistudio.google.com/apikey)**

---

## 🛠️ Tech Stack

- **Streamlit** — UI framework
- **Google Generative AI (Gemini)** — Vision analysis + playlist generation
- **Pillow** — Image processing
- **python-dotenv** — Environment management

---

## 📜 License

MIT — feel free to use, modify, and share.
