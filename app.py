"""
VibePlaylist AI — AI-Powered Music Recommendations from Photos
Upload a photo → AI reads the vibe → Get a playlist that matches the mood.
"""

import os
import io
import json
import re
from urllib.parse import quote_plus
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

SUPPORTED_LANGUAGES = [
    "English",
    "Hindi",
    "Bengali",
    "Punjabi",
    "Tamil",
    "Telugu",
    "Any Language",
]

LANGUAGE_EMOJI = {
    "English": "🇬🇧",
    "Hindi": "🇮🇳",
    "Bengali": "🎭",
    "Punjabi": "🎶",
    "Tamil": "🎵",
    "Telugu": "🎬",
    "Any Language": "🌍",
}

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

ANALYSIS_PROMPT = """You are a world-class visual-context analyst and music curator.

Study this image deeply and produce a JSON object (no markdown fencing) with
exactly these keys:

{
  "scene": "one-line description of the scene/location",
  "environment": "indoor / outdoor / urban / nature / mixed",
  "lighting": "description of lighting quality and direction",
  "time_of_day": "morning / afternoon / golden-hour / sunset / evening / night / unclear",
  "dominant_colors": ["color1", "color2", "color3"],
  "nature_elements": "any natural elements visible",
  "objects_activities": "key objects or activities in the frame",
  "atmosphere": "overall atmosphere in 2-3 words",
  "emotional_mood": "the dominant emotion this image evokes",
  "visual_aesthetic": "e.g. cinematic, vintage, minimal, vibrant, moody, dreamy",
  "overall_vibe": "a single evocative phrase that captures the entire vibe"
}

Be perceptive, poetic, and precise.  Return ONLY the JSON object."""

PLAYLIST_PROMPT_TEMPLATE = """You are **VibePlaylist AI**, an elite music curator who can translate
visual moods into perfect playlists.

## Visual Analysis of the uploaded photo
{analysis_json}

## User's preferred music language
{language}

---

### Your task
Based on the visual vibe above, recommend **10 songs** that perfectly match
the mood, atmosphere, and emotional energy of the image.

Rules:
1. Songs MUST be real, well-known tracks by real artists.
2. If the language is "Any Language", freely mix languages that suit the mood.
3. Otherwise, all songs should be in the requested language.
4. Provide variety — don't repeat artists unless absolutely essential.
5. For each song, explain in one sentence *why* it fits the vibe.

Return the result as a JSON array (no markdown fencing) where each element is:
{{
  "rank": 1,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name (if known)",
  "year": "Release year (if known)",
  "genre": "Genre / sub-genre",
  "reason": "Why this song matches the vibe"
}}

Return ONLY the JSON array."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def configure_genai(api_key: str) -> genai.GenerativeModel:
    """Configure the Gemini client and return a vision-capable model."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
    return model


def image_to_pil(uploaded_file) -> Image.Image:
    """Convert a Streamlit UploadedFile to a PIL Image."""
    return Image.open(uploaded_file)


def parse_json_response(text: str):
    """Extract JSON from a model response, tolerating markdown fences."""
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = cleaned.strip().rstrip("`").strip()
    return json.loads(cleaned)


def analyze_image(model: genai.GenerativeModel, img: Image.Image) -> dict:
    """Send the image to Gemini and return the structured vibe analysis."""
    response = model.generate_content(
        [ANALYSIS_PROMPT, img],
        generation_config=genai.types.GenerationConfig(temperature=0.7),
    )
    return parse_json_response(response.text)


def generate_playlist(
    model: genai.GenerativeModel, analysis: dict, language: str
) -> list[dict]:
    """Given the vibe analysis + language, generate a 10-song playlist."""
    prompt = PLAYLIST_PROMPT_TEMPLATE.format(
        analysis_json=json.dumps(analysis, indent=2),
        language=language,
    )
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.9),
    )
    return parse_json_response(response.text)


# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

def inject_css():
    st.markdown(
        """
        <style>
        /* ---------- Global ---------- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        /* Hide default Streamlit branding */
        #MainMenu, footer, header { visibility: hidden; }

        /* ---------- Hero ---------- */
        .hero {
            text-align: center;
            padding: 2rem 1rem 1rem;
        }
        .hero h1 {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #7C3AED, #EC4899, #F59E0B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.3rem;
        }
        .hero p {
            color: #94A3B8;
            font-size: 1.1rem;
            margin-top: 0;
        }

        /* ---------- Upload card ---------- */
        .upload-zone {
            border: 2px dashed #7C3AED55;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            background: #1A1A2E;
            transition: border-color 0.3s;
        }
        .upload-zone:hover { border-color: #7C3AED; }

        /* ---------- Analysis card ---------- */
        .vibe-card {
            background: linear-gradient(145deg, #1E1E36 0%, #16162B 100%);
            border: 1px solid #7C3AED44;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .vibe-card h3 {
            color: #C084FC;
            margin-top: 0;
        }

        /* ---------- Song row ---------- */
        .song-card {
            background: linear-gradient(145deg, #1E1E36, #16162B);
            border: 1px solid #ffffff0d;
            border-radius: 14px;
            padding: 1.1rem 1.3rem;
            margin-bottom: 0.75rem;
            transition: transform 0.2s, border-color 0.3s;
        }
        .song-card:hover {
            transform: translateY(-2px);
            border-color: #7C3AED66;
        }
        .song-rank {
            display: inline-block;
            background: linear-gradient(135deg, #7C3AED, #EC4899);
            color: white;
            font-weight: 700;
            width: 32px; height: 32px;
            line-height: 32px;
            text-align: center;
            border-radius: 50%;
            margin-right: 0.75rem;
            font-size: 0.85rem;
        }
        .song-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #F1F5F9;
        }
        .song-artist { color: #A78BFA; font-weight: 500; }
        .song-meta   { color: #64748B; font-size: 0.82rem; margin-top: 0.25rem; }
        .song-reason { color: #94A3B8; font-size: 0.88rem; margin-top: 0.5rem; font-style: italic; }

        /* ---------- Play buttons ---------- */
        .play-buttons { margin-top: 0.7rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .play-btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 0.35rem 0.9rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            text-decoration: none;
            transition: transform 0.2s, opacity 0.2s;
        }
        .play-btn:hover { transform: translateY(-1px); opacity: 0.9; }
        .play-btn.spotify {
            background: #1DB954;
            color: #fff;
        }
        .play-btn.ytmusic {
            background: #FF0000;
            color: #fff;
        }

        /* ---------- Language pills ---------- */
        div[data-testid="stHorizontalBlock"] button {
            border-radius: 999px !important;
        }

        /* ---------- Colour chips ---------- */
        .color-chip {
            display: inline-block;
            width: 28px; height: 28px;
            border-radius: 50%;
            margin-right: 6px;
            border: 2px solid #ffffff22;
            vertical-align: middle;
        }

        /* ---------- Vibe badge ---------- */
        .vibe-badge {
            display: inline-block;
            background: linear-gradient(135deg, #7C3AED44, #EC489944);
            border: 1px solid #7C3AED66;
            border-radius: 999px;
            padding: 0.4rem 1.2rem;
            font-size: 1rem;
            font-weight: 600;
            color: #E9D5FF;
            letter-spacing: 0.3px;
        }

        /* ---------- Divider ---------- */
        .fancy-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #7C3AED, #EC4899, transparent);
            border: none;
            margin: 2rem 0;
            border-radius: 2px;
        }

        /* ---------- Stat metric ---------- */
        .stat-box {
            background: #1A1A2E;
            border: 1px solid #7C3AED33;
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }
        .stat-box .label { color: #94A3B8; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px; }
        .stat-box .value { color: #C084FC; font-size: 1.2rem; font-weight: 700; margin-top: 0.25rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# UI Components
# ---------------------------------------------------------------------------

def render_hero():
    st.markdown(
        """
        <div class="hero">
            <h1>🎧 VibePlaylist AI</h1>
            <p>Upload a photo — let AI read the vibe — get a playlist that matches the mood</p>
        </div>
        <div class="fancy-divider"></div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis(analysis: dict):
    """Render the vibe analysis in a stylish card."""
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🔍 Vibe Analysis")

    # Top-level vibe badge
    vibe = analysis.get("overall_vibe", "")
    st.markdown(f'<div style="text-align:center;margin-bottom:1.2rem;"><span class="vibe-badge">✨ {vibe}</span></div>', unsafe_allow_html=True)

    # Stat row
    cols = st.columns(4)
    stats = [
        ("🕐 Time of Day", analysis.get("time_of_day", "—")),
        ("🌿 Environment", analysis.get("environment", "—")),
        ("💡 Lighting", analysis.get("lighting", "—")),
        ("🎭 Mood", analysis.get("emotional_mood", "—")),
    ]
    for col, (label, value) in zip(cols, stats):
        col.markdown(
            f'<div class="stat-box"><div class="label">{label}</div>'
            f'<div class="value">{value}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")  # spacer

    # Detail card
    html = '<div class="vibe-card">'
    html += f'<h3>📍 Scene</h3><p>{analysis.get("scene", "—")}</p>'
    html += f'<h3>🎨 Visual Aesthetic</h3><p>{analysis.get("visual_aesthetic", "—")}</p>'
    html += f'<h3>🌤️ Atmosphere</h3><p>{analysis.get("atmosphere", "—")}</p>'

    # Objects / activities
    html += f'<h3>🔎 Objects & Activities</h3><p>{analysis.get("objects_activities", "—")}</p>'

    # Nature
    nature = analysis.get("nature_elements", "")
    if nature:
        html += f'<h3>🌿 Nature</h3><p>{nature}</p>'

    # Dominant colours as chips
    colors = analysis.get("dominant_colors", [])
    if colors:
        html += '<h3>🎨 Dominant Colors</h3><p>'
        for c in colors:
            html += f'<span class="color-chip" style="background:{c};" title="{c}"></span> '
            html += f'<span style="color:#94A3B8;margin-right:12px;">{c}</span>'
        html += "</p>"

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_playlist(playlist: list[dict], language: str):
    """Render the song cards with Spotify & YouTube Music play links."""
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    emoji = LANGUAGE_EMOJI.get(language, "🎵")
    st.markdown(f"### {emoji} Your Vibe Playlist — *{language}*")
    st.caption(f"10 songs hand-picked by AI to match the mood of your photo · Click ▶ to play")

    for song in playlist:
        rank = song.get("rank", "")
        title = song.get("title", "Unknown")
        artist = song.get("artist", "Unknown")
        album = song.get("album", "")
        year = song.get("year", "")
        genre = song.get("genre", "")
        reason = song.get("reason", "")

        # Build search query for music services
        search_query = quote_plus(f"{title} {artist}")
        spotify_url = f"https://open.spotify.com/search/{search_query}"
        yt_music_url = f"https://music.youtube.com/search?q={search_query}"

        meta_parts = []
        if album:
            meta_parts.append(f"💿 {album}")
        if year:
            meta_parts.append(f"📅 {year}")
        if genre:
            meta_parts.append(f"🏷️ {genre}")
        meta_str = " &nbsp;·&nbsp; ".join(meta_parts)

        st.markdown(
            f"""
            <div class="song-card">
                <span class="song-rank">{rank}</span>
                <span class="song-title">{title}</span><br/>
                <span class="song-artist">🎤 {artist}</span>
                <div class="song-meta">{meta_str}</div>
                <div class="song-reason">"{reason}"</div>
                <div class="play-buttons">
                    <a href="{spotify_url}" target="_blank" class="play-btn spotify">
                        ▶ Play on Spotify
                    </a>
                    <a href="{yt_music_url}" target="_blank" class="play-btn ytmusic">
                        ▶ Play on YouTube Music
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="VibePlaylist AI",
        page_icon="🎧",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    inject_css()
    render_hero()

    # ---- Sidebar: how it works ----
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.markdown(
            "**How it works**\n\n"
            "1. Enter your Gemini API key 🔑\n"
            "2. Upload any photo 📸\n"
            "3. AI reads the vibe 🔍\n"
            "4. Pick your language 🌐\n"
            "5. Get your playlist 🎶\n\n"
            "---\n"
            "Built with ❤️ using **Gemini AI** & **Streamlit**"
        )

    # ---- API Key: on main page ----
    env_key = os.getenv("GOOGLE_API_KEY", "")

    if env_key:
        api_key = env_key
    else:
        st.markdown("### 🔑 Connect to Gemini AI")
        st.markdown(
            '<div class="vibe-card">'
            '<p style="color:#94A3B8;margin-top:0;">To get started, you need a <strong>free</strong> Google Gemini API key.</p>'
            '<p style="margin-bottom:0;">👉 <a href="https://aistudio.google.com/apikey" target="_blank" '
            'style="color:#A78BFA;font-weight:600;">Get your free API key here</a></p>'
            '</div>',
            unsafe_allow_html=True,
        )
        api_key = st.text_input(
            "Paste your Google Gemini API Key below",
            type="password",
            placeholder="AIzaSy...",
        )
        if not api_key:
            st.stop()

    # Init model
    try:
        model = configure_genai(api_key)
    except Exception as exc:
        st.error(f"Failed to configure Gemini: {exc}")
        st.stop()

    # ---- Step 1: Upload ----
    st.markdown("### 📸 Step 1 — Upload Your Photo")
    uploaded = st.file_uploader(
        "Drop an image that sets the mood",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if uploaded is None:
        st.markdown(
            '<div class="upload-zone">'
            "<p style='font-size:2.5rem;margin:0;'>📷</p>"
            "<p style='color:#94A3B8;'>Drag & drop or click to upload a photo<br/>"
            "<small>JPG · PNG · WebP</small></p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.stop()

    # Show uploaded image
    img = image_to_pil(uploaded)
    st.image(img, use_container_width=True, caption="Your uploaded photo")

    # ---- Step 2: Analyze ----
    # Use session state to cache analysis so it doesn't re-run on every interaction
    if "analysis" not in st.session_state or st.session_state.get("_last_file") != uploaded.name:
        with st.spinner("🔍 Reading the vibe of your photo…"):
            try:
                analysis = analyze_image(model, img)
                st.session_state["analysis"] = analysis
                st.session_state["_last_file"] = uploaded.name
                st.session_state.pop("playlist", None)  # reset playlist on new image
            except Exception as exc:
                st.error(f"Image analysis failed: {exc}")
                st.stop()

    analysis = st.session_state["analysis"]
    render_analysis(analysis)

    # ---- Step 3: Language selection ----
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🌐 Step 2 — Choose Your Music Language")

    lang_cols = st.columns(len(SUPPORTED_LANGUAGES))
    selected_lang = st.session_state.get("selected_lang", None)

    for col, lang in zip(lang_cols, SUPPORTED_LANGUAGES):
        emoji = LANGUAGE_EMOJI.get(lang, "🎵")
        if col.button(f"{emoji} {lang}", key=f"lang_{lang}", use_container_width=True):
            st.session_state["selected_lang"] = lang
            st.session_state.pop("playlist", None)  # regenerate on language change
            selected_lang = lang

    if not selected_lang:
        st.info("☝️ Select a music language above to generate your playlist!", icon="🎵")
        st.stop()

    st.success(f"**Language selected:** {LANGUAGE_EMOJI.get(selected_lang, '')} {selected_lang}", icon="✅")

    # ---- Step 4: Generate playlist ----
    if "playlist" not in st.session_state:
        with st.spinner(f"🎶 Curating your {selected_lang} playlist…"):
            try:
                playlist = generate_playlist(model, analysis, selected_lang)
                st.session_state["playlist"] = playlist
            except Exception as exc:
                st.error(f"Playlist generation failed: {exc}")
                st.stop()

    render_playlist(st.session_state["playlist"], selected_lang)

    # ---- Footer ----
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;color:#64748B;padding:1rem;'>"
        "🎧 <strong>VibePlaylist AI</strong> · Powered by Google Gemini · "
        "Made with Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
