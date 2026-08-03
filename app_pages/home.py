"""Home / landing page — hero title + card-button navigation to every page."""
import streamlit as st
from database.database import get_stats

NAV_CARDS = [
    ("dashboard", "📊", "Dashboard", "Live KPIs & system status"),
    ("image_detection", "🖼️", "Image Detection", "Upload a photo, detect a plate"),
    ("live_camera", "📷", "Live Camera", "Real-time capture & recognition"),
    ("video_detection", "🎬", "Video Detection", "Process footage frame-by-frame"),
    ("vehicle_manager", "🗂️", "Vehicle Database", "Owners, challans & blacklist"),
    ("history", "🕘", "Detection History", "Search, filter & export records"),
    ("analytics", "📈", "Analytics", "Trends, charts & confidence stats"),
    ("settings", "⚙️", "Settings", "Thresholds, cache & storage"),
]

CSS = """
<style>
.hero-wrap {
    text-align: center;
    padding: 3.5rem 1rem 2rem 1rem;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1.15;
    background: linear-gradient(90deg, #3DDC97 0%, #6EC6FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.6rem 0;
}
.hero-sub {
    color: #9DA7B3;
    font-size: 1.05rem;
    max-width: 640px;
    margin: 0 auto;
}
.stat-strip {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    margin-top: 1.8rem;
    flex-wrap: wrap;
}
.stat-chip {
    text-align: center;
}
.stat-chip .num {
    font-size: 1.6rem;
    font-weight: 700;
    color: #E6EDF3;
}
.stat-chip .lbl {
    font-size: 0.78rem;
    color: #7C8794;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
div[data-testid="stButton"] > button {
    width: 100%;
    height: 6.4rem;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    background: #161B22;
    text-align: left;
    white-space: pre-wrap;
    line-height: 1.35;
    transition: border-color 0.15s ease, transform 0.15s ease;
}
div[data-testid="stButton"] > button:hover {
    border-color: #3DDC97;
    transform: translateY(-2px);
    color: #E6EDF3;
}
</style>
"""


def render(services: dict):
    st.markdown(CSS, unsafe_allow_html=True)
    stats = get_stats()

    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-title">Smart Vehicle Number Plate<br>Recognition &amp; Management System</div>
            <div class="hero-sub">
                Detect, read and validate license plates from images, live camera,
                or video — with history, analytics and configurable thresholds.
            </div>
            <div class="stat-strip">
                <div class="stat-chip"><div class="num">{stats['total']}</div><div class="lbl">Total</div></div>
                <div class="stat-chip"><div class="num">{stats['valid']}</div><div class="lbl">Valid</div></div>
                <div class="stat-chip"><div class="num">{stats['invalid']}</div><div class="lbl">Invalid</div></div>
                <div class="stat-chip"><div class="num">{stats['today']}</div><div class="lbl">Today</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    rows = [NAV_CARDS[i:i + 4] for i in range(0, len(NAV_CARDS), 4)]
    for row in rows:
        cols = st.columns(len(row))
        for col, (key, icon, label, desc) in zip(cols, row):
            with col:
                if st.button(f"{icon}  {label}\n{desc}", key=f"nav_{key}"):
                    st.session_state.page = key
                    st.rerun()
