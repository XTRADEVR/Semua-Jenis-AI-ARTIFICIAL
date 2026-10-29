"""Semua Jenis AI - direktori AI + Chat Gemini (Streamlit).

Jalankan:
    pip install -r requirements.txt
    streamlit run app.py
"""

import html
import json
import mimetypes
import os
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
from google import genai
from google.genai import types

# ----------------------------------------------------------------------------
# Konfigurasi dasar
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Semua Jenis AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = DATA_DIR / "settings.json"
CHAT_FILE = DATA_DIR / "chat_history.json"

# ID model. Jika Google mengubah nama ID-nya, pilih "Model kustom" di sidebar
# lalu isi ID model yang benar.
MODEL_OPTIONS = {
    "Gemini 3.5 Flash Lite": "gemini-3.5-flash-lite",
    "Gemini 3.8 Flash": "gemini-3.8-flash",
    "Model kustom…": None,
}
DEFAULT_MODEL_LABEL = "Gemini 3.5 Flash Lite"
MAX_FILE_MB = 15
MAX_HISTORY_MESSAGES = 30
DEFAULT_SYSTEM_PROMPT = (
    "Kamu adalah asisten AI yang membantu. Jawab dengan jelas dan ringkas, "
    "gunakan bahasa yang sama dengan pengguna."
)
TEXT_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".py", ".js", ".html", ".xml",
    ".yaml", ".yml", ".log",
}
UPLOAD_TYPES = [
    "png", "jpg", "jpeg", "webp", "pdf",
    "txt", "md", "csv", "json", "py", "js", "html", "xml", "yaml", "yml", "log",
]

# ----------------------------------------------------------------------------
# Data direktori AI (nama, link)
# ----------------------------------------------------------------------------
CATEGORIES = [
    ("Chatbot / Asisten AI", [
        ("ChatGPT", "https://chatgpt.com"),
        ("Claude", "https://claude.ai"),
        ("Google Gemini", "https://gemini.google.com"),
        ("Microsoft Copilot", "https://copilot.microsoft.com"),
        ("Perplexity AI", "https://www.perplexity.ai"),
        ("Poe", "https://poe.com"),
        ("You.com", "https://you.com"),
        ("Hugging Chat", "https://huggingface.co/chat"),
        ("Copilot (Bing)", "https://www.bing.com/chat"),
        ("Meta AI", "https://www.meta.ai"),
        ("Character.AI", "https://character.ai"),
        ("Replika", "https://replika.com"),
        ("Pi", "https://pi.ai"),
        ("Phind", "https://www.phind.com"),
        ("Kuki AI", "https://www.kuki.ai"),
        ("Chai", "https://www.chai-research.com"),
    ]),
    ("Mesin Pencari AI", [
        ("Perplexity", "https://www.perplexity.ai"),
        ("You.com", "https://you.com"),
        ("Brave Search (Leo)", "https://search.brave.com"),
        ("Andi", "https://andisearch.com"),
        ("Phind", "https://www.phind.com"),
        ("Komo Search", "https://komo.ai"),
        ("Consensus", "https://consensus.app"),
        ("Elicit", "https://elicit.com"),
        ("scite AI", "https://scite.ai"),
        ("ChatPDF", "https://www.chatpdf.com"),
    ]),
    ("AI Penulisan & Konten", [
        ("Jasper", "https://www.jasper.ai"),
        ("Copy.ai", "https://www.copy.ai"),
        ("Writesonic", "https://writesonic.com"),
        ("Rytr", "https://rytr.me"),
        ("Surfer", "https://surferseo.com"),
        ("Anyword", "https://anyword.com"),
        ("Wordtune", "https://www.wordtune.com"),
        ("QuillBot", "https://quillbot.com"),
        ("Grammarly", "https://www.grammarly.com"),
        ("Notion AI", "https://www.notion.com/product/ai"),
        ("Sudowrite", "https://www.sudowrite.com"),
        ("Frase", "https://www.frase.io"),
        ("WriteCream", "https://www.writecream.com"),
        ("TextCortex", "https://textcortex.com"),
        ("Simplified", "https://simplified.com"),
        ("ContentBot", "https://contentbot.ai"),
    ]),
    ("AI Gambar / Desain", [
        ("DALL-E", "https://openai.com/dall-e-3"),
        ("Midjourney", "https://www.midjourney.com"),
        ("Stable Diffusion", "https://stability.ai"),
        ("Leonardo AI", "https://leonardo.ai"),
        ("Adobe Firefly", "https://firefly.adobe.com"),
        ("Bing Image Creator", "https://www.bing.com/images/create"),
        ("Ideogram", "https://ideogram.ai"),
        ("Playground AI", "https://playground.com"),
        ("Canva AI", "https://www.canva.com"),
        ("Krea AI", "https://www.krea.ai"),
        ("BlueWillow", "https://www.bluewillow.ai"),
        ("NightCafe", "https://creator.nightcafe.studio"),
        ("PixAI", "https://pixai.art"),
        ("Tensor.Art", "https://tensor.art"),
        ("Recraft AI", "https://www.recraft.ai"),
        ("Freepik AI", "https://www.freepik.com/ai"),
    ]),
    ("AI Video", [
        ("Runway", "https://runwayml.com"),
        ("Pika", "https://pika.art"),
        ("Synthesia", "https://www.synthesia.io"),
        ("HeyGen", "https://www.heygen.com"),
        ("Descript", "https://www.descript.com"),
        ("VEED.IO", "https://www.veed.io"),
        ("InVideo AI", "https://invideo.io"),
        ("Kaiber", "https://kaiber.ai"),
        ("Luma AI", "https://lumalabs.ai"),
        ("Opus Clip", "https://www.opus.pro"),
        ("Steve AI", "https://www.steve.ai"),
        ("Fliki", "https://fliki.ai"),
    ]),
    ("AI Audio / Musik", [
        ("Suno", "https://suno.com"),
        ("Udio", "https://www.udio.com"),
        ("AIVA", "https://www.aiva.ai"),
        ("Soundraw", "https://soundraw.io"),
        ("Mubert", "https://mubert.com"),
        ("Boomy", "https://boomy.com"),
        ("Beatoven.ai", "https://www.beatoven.ai"),
        ("ElevenLabs", "https://elevenlabs.io"),
        ("Voicemod", "https://www.voicemod.net"),
    ]),
    ("AI Presentasi", [
        ("Tome", "https://tome.app"),
        ("Gamma", "https://gamma.app"),
        ("Beautiful.ai", "https://www.beautiful.ai"),
        ("SlidesAI", "https://www.slidesai.io"),
        ("Decktopus AI", "https://www.decktopus.com"),
        ("Pitch", "https://pitch.com"),
        ("PopAI", "https://www.popai.pro"),
        ("Presentations AI", "https://www.presentations.ai"),
    ]),
    ("AI Kode / Pemrograman", [
        ("GitHub Copilot", "https://github.com/features/copilot"),
        ("Cursor", "https://cursor.com"),
        ("Replit AI", "https://replit.com"),
        ("Amazon CodeWhisperer", "https://aws.amazon.com/q/developer"),
        ("Tabnine", "https://www.tabnine.com"),
        ("Codeium", "https://codeium.com"),
        ("Windsurf", "https://windsurf.com"),
        ("Blackbox AI", "https://www.blackbox.ai"),
        ("Bolt.new", "https://bolt.new"),
        ("Sourcegraph Cody", "https://sourcegraph.com/cody"),
        ("Codiga", "https://www.codiga.io"),
        ("DeepCode", "https://snyk.io/product/snyk-code"),
    ]),
    ("AI Data & Analisis", [
        ("ChatGPT (Advanced Data)", "https://chatgpt.com"),
        ("Claude (Analysis)", "https://claude.ai"),
        ("Google Gemini (Advanced)", "https://gemini.google.com"),
        ("Microsoft Copilot (Excel)", "https://www.microsoft.com/microsoft-365/excel"),
        ("Julius AI", "https://julius.ai"),
        ("DataRobot", "https://www.datarobot.com"),
        ("Akkio", "https://www.akkio.com"),
        ("Rows AI", "https://rows.com"),
        ("MonkeyLearn", "https://monkeylearn.com"),
        ("Obviously AI", "https://www.obviously.ai"),
        ("Narrative BI", "https://narrativebi.com"),
        ("Octoparse", "https://www.octoparse.com"),
    ]),
    ("AI Otomasi & Agent", [
        ("Zapier AI", "https://zapier.com"),
        ("Make (Integromat)", "https://www.make.com"),
        ("n8n", "https://n8n.io"),
        ("Auto-GPT", "https://agpt.co"),
        ("AgentGPT", "https://agentgpt.reworkd.ai"),
        ("BabyAGI", "https://babyagi.org"),
        ("CrewAI", "https://www.crewai.com"),
        ("Flowise AI", "https://flowiseai.com"),
        ("TaskWeaver", "https://github.com/microsoft/TaskWeaver"),
        ("Harpa AI", "https://harpa.ai"),
        ("Do Anything Machine", "https://www.doanythingmachine.com"),
        ("Phala Network", "https://phala.network"),
    ]),
    ("AI Edukasi", [
        ("Khanmigo", "https://www.khanacademy.org/khan-labs"),
        ("Quizlet Q-Chat", "https://quizlet.com"),
        ("Photomath", "https://photomath.com"),
        ("Socratic by Google", "https://socratic.org"),
        ("Coursera Coach", "https://www.coursera.org"),
        ("Duolingo Max", "https://www.duolingo.com"),
        ("Explain Everything AI", "https://explaineverything.com"),
        ("Merlin AI", "https://www.getmerlin.in"),
    ]),
    ("AI Produktivitas", [
        ("Notion AI", "https://www.notion.com"),
        ("Microsoft 365 Copilot", "https://www.microsoft.com/microsoft-365/copilot"),
        ("ClickUp AI", "https://clickup.com"),
        ("Mem AI", "https://mem.ai"),
        ("Otter.ai", "https://otter.ai"),
        ("Fireflies.ai", "https://fireflies.ai"),
        ("Motion", "https://www.usemotion.com"),
        ("Reclaim AI", "https://reclaim.ai"),
        ("Tactiq", "https://tactiq.io"),
        ("Fathom", "https://fathom.video"),
        ("Xembly", "https://www.xembly.com"),
        ("HyperWrite AI", "https://www.hyperwriteai.com"),
    ]),
    ("AI Voice / Speech", [
        ("ElevenLabs", "https://elevenlabs.io"),
        ("Descript Overdub", "https://www.descript.com"),
        ("PlayHT", "https://play.ht"),
        ("Murf AI", "https://murf.ai"),
        ("Resemble AI", "https://www.resemble.ai"),
        ("WellSaid Labs", "https://wellsaidlabs.com"),
        ("Speechify", "https://speechify.com"),
        ("Lovo AI", "https://lovo.ai"),
        ("Voicemod", "https://www.voicemod.net"),
        ("Listnr AI", "https://listnr.ai"),
        ("TTSMaker", "https://ttsmaker.com"),
        ("Replica Studios", "https://www.replicastudios.com"),
    ]),
    ("AI 3D & Modeling", [
        ("Luma AI", "https://lumalabs.ai"),
        ("Kaedim", "https://www.kaedim3d.com"),
        ("Meshy AI", "https://www.meshy.ai"),
        ("Sloyd AI", "https://www.sloyd.ai"),
        ("Vizcom", "https://www.vizcom.ai"),
        ("Tripo AI", "https://www.tripo3d.ai"),
        ("CSM", "https://www.csm.ai"),
        ("Masterpiece X", "https://www.masterpiecex.com"),
    ]),
    ("AI Kesehatan", [
        ("Athelas", "https://www.athelas.com"),
        ("Aidoc", "https://www.aidoc.com"),
        ("Insilico Medicine", "https://insilico.com"),
        ("Tempus", "https://www.tempus.com"),
        ("Caption Health", "https://captionhealth.com"),
        ("Hippocratic AI", "https://www.hippocraticai.com"),
        ("PathAI", "https://www.pathai.com"),
        ("Baidu Health AI", "https://www.baidu.com"),
    ]),
    ("AI Keuangan", [
        ("AlphaSense", "https://www.alpha-sense.com"),
        ("FinChat", "https://finchat.io"),
        ("Numerai", "https://numer.ai"),
        ("Koyfin", "https://www.koyfin.com"),
        ("Cleo", "https://web.meetcleo.com"),
        ("Upstart", "https://www.upstart.com"),
        ("Trinka (Akuntansi/AI)", "https://www.trinka.ai"),
        ("Botkeeper", "https://www.botkeeper.com"),
    ]),
]

FRAMEWORKS = [
    ("OpenAI", "https://openai.com"),
    ("Anthropic", "https://www.anthropic.com"),
    ("Google DeepMind", "https://deepmind.google"),
    ("Meta AI (Llama)", "https://www.llama.com"),
    ("Mistral AI", "https://mistral.ai"),
    ("Cohere", "https://cohere.com"),
    ("Hugging Face", "https://huggingface.co"),
    ("LangChain", "https://www.langchain.com"),
    ("Pinecone", "https://www.pinecone.io"),
    ("TensorFlow", "https://www.tensorflow.org"),
    ("PyTorch", "https://pytorch.org"),
    ("Scikit-learn", "https://scikit-learn.org"),
]

OTHER_CATEGORIES = [
    ("AI Hukum", [
        ("Harvey AI", "https://www.harvey.ai"),
        ("Casetext CoCounsel", "https://casetext.com"),
        ("LawGeex", "https://www.lawgeex.com"),
    ]),
    ("AI Marketing", [
        ("AdCreative.ai", "https://www.adcreative.ai"),
        ("Predis.ai", "https://predis.ai"),
        ("Surfer AI", "https://surferseo.com"),
    ]),
    ("AI E-Commerce", [
        ("Shopify Magic", "https://www.shopify.com/magic"),
        ("Recombee", "https://www.recombee.com"),
        ("Clerk.io", "https://www.clerk.io"),
    ]),
    ("AI Game", [
        ("Inworld AI", "https://inworld.ai"),
        ("Scenario", "https://www.scenario.com"),
        ("Layer AI", "https://www.layer.ai"),
    ]),
    ("AI Keamanan (Cybersec)", [
        ("Darktrace", "https://darktrace.com"),
        ("CrowdStrike AI", "https://www.crowdstrike.com"),
        ("Vectra AI", "https://www.vectra.ai"),
    ]),
]

FUN_FACTS = [
    "Ribuan AI baru bermunculan setiap bulan",
    "Manfaatkan AI sesuai kebutuhanmu",
    "AI adalah tools, kreativitas tetap milikmu!",
]

# ----------------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------------
CSS = """
<style>
.ai-hero{text-align:center;padding:26px 12px 18px;border-radius:18px;
  background:linear-gradient(135deg,#070a1f 0%,#1a1245 55%,#070a1f 100%);
  border:1px solid #2a2f6b;margin-bottom:14px;}
.ai-hero .sub{color:#fff;font-weight:800;font-size:22px;letter-spacing:1px;}
.ai-hero .row{display:flex;align-items:center;justify-content:center;gap:18px;flex-wrap:wrap;}
.ai-hero .big{font-size:84px;font-weight:900;line-height:1;
  background:linear-gradient(90deg,#5ec8ff,#a855f7,#ff7ac6);
  -webkit-background-clip:text;background-clip:text;color:transparent;}
.ai-hero .title{color:#fff;font-weight:900;font-size:40px;line-height:1.05;text-align:left;}
.ai-hero .pill{display:inline-block;margin-top:14px;padding:7px 22px;border-radius:999px;
  background:linear-gradient(90deg,#3b2bd9,#7c3aed);color:#fff;font-weight:700;
  font-size:14px;letter-spacing:.5px;border:1px solid #6d5cff;}
.ai-panel{background:#0c1030;border:1px solid #2a2f6b;border-radius:14px;
  padding:10px;margin-bottom:12px;}
.ai-panel-title{text-align:center;background:linear-gradient(90deg,#3b2bd9,#7c3aed);
  color:#fff;font-weight:800;font-size:12px;padding:6px 8px;border-radius:9px;
  margin-bottom:10px;text-transform:uppercase;letter-spacing:.4px;}
.ai-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(72px,1fr));gap:8px;}
.ai-grid.wide{grid-template-columns:repeat(auto-fill,minmax(110px,1fr));}
a.ai-item,a.ai-item:hover,a.ai-item:visited{text-decoration:none !important;color:#dfe3ff !important;}
a.ai-item{display:flex;flex-direction:column;align-items:center;text-align:center;
  font-size:10.5px;padding:6px 2px;border-radius:10px;transition:all .15s ease;}
a.ai-item:hover{background:#1a1f55;transform:translateY(-2px);}
a.ai-item img{width:40px;height:40px;border-radius:10px;background:#fff;padding:3px;
  object-fit:contain;box-sizing:border-box;}
a.ai-item span{margin-top:5px;line-height:1.15;word-break:break-word;}
.ai-other{color:#dfe3ff;font-size:13px;line-height:1.9;}
.ai-other b{color:#fff;}
.ai-other a,.ai-other a:visited{color:#8fb4ff !important;text-decoration:none;}
.ai-other a:hover{text-decoration:underline;}
.ai-fact{color:#dfe3ff;font-size:13px;line-height:1.9;}
.ai-fact li{margin-left:16px;}
.ai-footer{text-align:center;font-weight:800;color:#7ea6ff;padding:10px 0 4px;letter-spacing:.5px;}
</style>
"""


# ----------------------------------------------------------------------------
# Helper: penyimpanan
# ----------------------------------------------------------------------------
def read_json(path: Path, default):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def write_json(path: Path, data) -> None:
    try:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception as exc:  # penyimpanan tidak boleh membuat aplikasi crash
        st.sidebar.warning(f"Gagal menyimpan data: {exc}")


def save_settings() -> None:
    ss = st.session_state
    data = {
        "model_choice": ss.get("model_choice", DEFAULT_MODEL_LABEL),
        "custom_model": ss.get("custom_model", ""),
        "system_prompt": ss.get("system_prompt", DEFAULT_SYSTEM_PROMPT),
        "temperature": ss.get("temperature", 0.7),
        "save_key": bool(ss.get("save_key", True)),
    }
    if data["save_key"]:
        data["api_key"] = (ss.get("api_key") or "").strip()
    write_json(SETTINGS_FILE, data)


def save_chat() -> None:
    write_json(CHAT_FILE, st.session_state.messages)


def env_api_key() -> str:
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = os.environ.get(name)
        if value:
            return value
    try:
        for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            if name in st.secrets:
                return str(st.secrets[name])
    except Exception:
        pass
    return ""


def init_state() -> None:
    ss = st.session_state
    if ss.get("_initialized"):
        return
    saved = read_json(SETTINGS_FILE, {})
    if not isinstance(saved, dict):
        saved = {}
    choice = saved.get("model_choice", DEFAULT_MODEL_LABEL)
    ss.model_choice = choice if choice in MODEL_OPTIONS else DEFAULT_MODEL_LABEL
    ss.custom_model = saved.get("custom_model", "")
    ss.system_prompt = saved.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
    try:
        ss.temperature = float(saved.get("temperature", 0.7))
    except (TypeError, ValueError):
        ss.temperature = 0.7
    ss.save_key = bool(saved.get("save_key", True))
    ss.api_key = saved.get("api_key") or env_api_key()
    messages = read_json(CHAT_FILE, [])
    ss.messages = messages if isinstance(messages, list) else []
    ss.uploader_n = 0
    ss._initialized = True


# ----------------------------------------------------------------------------
# Helper: tampilan direktori
# ----------------------------------------------------------------------------
def favicon(url: str) -> str:
    host = urlparse(url).netloc
    return f"https://www.google.com/s2/favicons?domain={host}&sz=128"


def panel_html(title: str, items, wide: bool = False) -> str:
    cells = []
    for name, url in items:
        n = html.escape(name)
        u = html.escape(url, quote=True)
        cells.append(
            f'<a class="ai-item" href="{u}" target="_blank" rel="noopener noreferrer" title="{n}">'
            f'<img src="{html.escape(favicon(url), quote=True)}" alt="{n}" loading="lazy">'
            f"<span>{n}</span></a>"
        )
    grid_cls = "ai-grid wide" if wide else "ai-grid"
    return (
        f'<div class="ai-panel"><div class="ai-panel-title">{html.escape(title)}</div>'
        f'<div class="{grid_cls}">{"".join(cells)}</div></div>'
    )


def render_directory() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="ai-hero">'
        '<div class="sub">SEMUA JENIS</div>'
        '<div class="row"><div class="big">AI</div>'
        '<div class="title">ARTIFICIAL<br>INTELLIGENCE</div></div>'
        '<div class="pill">SEMUA AI POPULER DALAM SATU HALAMAN</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Cari AI",
        placeholder="🔎 Cari AI, misalnya: video, ChatGPT, musik…",
        label_visibility="collapsed",
        key="search_query",
    ).strip().lower()

    visible = []
    for title, items in CATEGORIES:
        if query:
            filtered = [it for it in items if query in it[0].lower() or query in title.lower()]
        else:
            filtered = items
        if filtered:
            visible.append((title, filtered))

    if not visible and query:
        st.info("Tidak ada AI yang cocok dengan pencarian.")

    for start in range(0, len(visible), 4):
        chunk = visible[start:start + 4]
        cols = st.columns(4, gap="small")
        for col, (title, items) in zip(cols, chunk):
            with col:
                st.markdown(panel_html(title, items), unsafe_allow_html=True)

    fw = [it for it in FRAMEWORKS if not query or query in it[0].lower() or "framework" in query]
    if fw:
        st.markdown(panel_html("Framework / Platform AI", fw, wide=True), unsafe_allow_html=True)

    if not query:
        left, right = st.columns(2, gap="small")
        with left:
            lines = []
            for cat, items in OTHER_CATEGORIES:
                links = ", ".join(
                    f'<a href="{html.escape(u, quote=True)}" target="_blank" '
                    f'rel="noopener noreferrer">{html.escape(n)}</a>'
                    for n, u in items
                )
                lines.append(f"• <b>{html.escape(cat)}:</b> {links}")
            st.markdown(
                '<div class="ai-panel"><div class="ai-panel-title">Kategori Lainnya</div>'
                f'<div class="ai-other">{"<br>".join(lines)}</div></div>',
                unsafe_allow_html=True,
            )
        with right:
            facts = "".join(f"<li>{html.escape(f)}</li>" for f in FUN_FACTS)
            st.markdown(
                '<div class="ai-panel"><div class="ai-panel-title">Fakta Menarik</div>'
                f'<ul class="ai-fact">{facts}</ul></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            '<div class="ai-footer">🚀 DUNIA AI TERUS BERKEMBANG – TERUS BELAJAR, TERUS BERKARYA!</div>',
            unsafe_allow_html=True,
        )


# ----------------------------------------------------------------------------
# Helper: Gemini
# ----------------------------------------------------------------------------
def current_model_id() -> str:
    ss = st.session_state
    model_id = MODEL_OPTIONS.get(ss.model_choice)
    if model_id is None:
        model_id = (ss.get("custom_model") or "").strip()
    return model_id


def file_to_part(uploaded) -> types.Part:
    data = uploaded.getvalue()
    name = uploaded.name
    ext = Path(name).suffix.lower()
    mime = uploaded.type or mimetypes.guess_type(name)[0] or "application/octet-stream"
    if ext in TEXT_EXTENSIONS or mime.startswith("text/"):
        text = data.decode("utf-8", errors="replace")
        return types.Part(text=f"[Isi file: {name}]\n{text}")
    return types.Part.from_bytes(data=data, mime_type=mime)


def build_contents(history, prompt: str, files) -> list:
    contents = []
    for m in history[-MAX_HISTORY_MESSAGES:]:
        if m.get("error"):
            continue
        text = (m.get("content") or "").strip()
        if not text:
            continue
        role = "user" if m.get("role") == "user" else "model"
        if role == "user" and m.get("files"):
            text += "\n\n[Lampiran sebelumnya: " + ", ".join(m["files"]) + "]"
        contents.append(types.Content(role=role, parts=[types.Part(text=text)]))

    parts = [file_to_part(f) for f in files]
    parts.append(types.Part(text=prompt))
    contents.append(types.Content(role="user", parts=parts))
    return contents


def stream_reply(api_key: str, model_id: str, contents: list):
    client = genai.Client(api_key=api_key)
    system_prompt = (st.session_state.get("system_prompt") or "").strip()
    config = types.GenerateContentConfig(
        system_instruction=system_prompt or None,
        temperature=float(st.session_state.get("temperature", 0.7)),
    )
    for chunk in client.models.generate_content_stream(
        model=model_id, contents=contents, config=config
    ):
        text = getattr(chunk, "text", None)
        if text:
            yield text


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
def render_sidebar() -> None:
    ss = st.session_state
    with st.sidebar:
        st.header("⚙️ Pengaturan Gemini")
        st.text_input(
            "Gemini API Key",
            type="password",
            key="api_key",
            on_change=save_settings,
            help="Dapatkan gratis di https://aistudio.google.com/apikey",
        )
        st.checkbox(
            "Simpan API key di perangkat ini",
            key="save_key",
            on_change=save_settings,
            help="Disimpan di folder data/ agar tidak hilang saat halaman di-refresh.",
        )
        st.selectbox(
            "Model",
            options=list(MODEL_OPTIONS.keys()),
            key="model_choice",
            on_change=save_settings,
        )
        if MODEL_OPTIONS.get(ss.model_choice) is None:
            st.text_input(
                "ID model kustom",
                key="custom_model",
                placeholder="contoh: gemini-3.5-flash-lite",
                on_change=save_settings,
            )
        else:
            st.caption(f"ID model: `{current_model_id()}`")
        st.slider(
            "Temperature", 0.0, 2.0, step=0.1, key="temperature", on_change=save_settings
        )
        st.text_area(
            "Instruksi sistem",
            key="system_prompt",
            height=110,
            on_change=save_settings,
        )

        st.divider()
        if st.button("🗑️ Hapus riwayat chat", use_container_width=True):
            ss.messages = []
            save_chat()
            st.rerun()
        if st.button("🔑 Hapus API key tersimpan", use_container_width=True):
            ss.api_key = ""
            save_settings()
            st.rerun()
        st.caption(f"💾 Chat tersimpan: {len(ss.messages)} pesan")


# ----------------------------------------------------------------------------
# Chat
# ----------------------------------------------------------------------------
def render_chat() -> None:
    ss = st.session_state
    st.divider()
    st.subheader("💬 Chat Gemini")

    api_key = (ss.get("api_key") or "").strip()
    model_id = current_model_id()

    if not api_key:
        st.info("Masukkan Gemini API Key di sidebar untuk mulai chat.")
    elif not model_id:
        st.info("Isi ID model kustom di sidebar.")

    for m in ss.messages:
        with st.chat_message(m.get("role", "assistant")):
            if m.get("files"):
                st.caption("📎 " + ", ".join(m["files"]))
            if m.get("error"):
                st.error(m.get("content", ""))
            else:
                st.markdown(m.get("content", ""))

    uploaded = st.file_uploader(
        "📎 Unggah file / gambar (opsional, ikut dikirim pada pesan berikutnya)",
        type=UPLOAD_TYPES,
        accept_multiple_files=True,
        key=f"uploader_{ss.uploader_n}",
    )

    prompt = st.chat_input(
        "Ketik pesan…",
        disabled=not (api_key and model_id),
    )
    if not prompt:
        return

    files = list(uploaded or [])
    too_big = [f.name for f in files if f.size > MAX_FILE_MB * 1024 * 1024]
    if too_big:
        st.error(f"File terlalu besar (maks {MAX_FILE_MB} MB): {', '.join(too_big)}")
        return

    try:
        contents = build_contents(ss.messages, prompt, files)
    except Exception as exc:
        st.error(f"Gagal membaca file: {exc}")
        return

    ss.messages.append(
        {"role": "user", "content": prompt, "files": [f.name for f in files]}
    )
    save_chat()

    with st.chat_message("user"):
        if files:
            st.caption("📎 " + ", ".join(f.name for f in files))
        for f in files:
            if (f.type or "").startswith("image/"):
                st.image(f.getvalue(), caption=f.name, width=300)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(stream_reply(api_key, model_id, contents))
            reply = reply if isinstance(reply, str) else str(reply)
            if not reply.strip():
                reply = "(Model tidak mengembalikan teks. Coba ulangi atau ubah pertanyaan.)"
            ss.messages.append({"role": "assistant", "content": reply})
        except Exception as exc:
            ss.messages.append(
                {
                    "role": "assistant",
                    "content": f"Terjadi kesalahan: {type(exc).__name__}: {exc}",
                    "error": True,
                }
            )
    save_chat()
    ss.uploader_n += 1  # kosongkan uploader setelah terkirim
    st.rerun()


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main() -> None:
    init_state()
    render_sidebar()
    render_directory()
    render_chat()


main()
