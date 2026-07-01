NAVY   = "#0f1b35"
NAVY2  = "#1a3360"
BLUE   = "#2d6bc4"
GOLD   = "#c9a84c"
GOLD_L = "#f5d060"
GOLD_P = "#fdf6e3"
WHITE  = "#ffffff"
GRAY   = "#6b7280"
SERIF   = "Newsreader, serif"
DISPLAY = "Cormorant, serif"
GOLD_T  = "#a87f2c"


def css_global():
    return f"""<style>
    .stApp {{ background-color: #efeae6; }}
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg,{NAVY},#13213f) !important;
    }}
    section[data-testid="stSidebar"] * {{ color:{WHITE} !important; }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        display:flex; align-items:center; gap:14px;
        padding:13px 14px; border-radius:12px; margin:3px 0;
        cursor:pointer; transition:background .15s;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ background:rgba(255,255,255,.07); }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {{ display:none; }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {{
        background:rgba(45,107,196,.26); box-shadow:inset 3px 0 0 {GOLD_L};
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] p {{ font-size:17px; font-weight:600; }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background:rgba(255,255,255,.06) !important;
        border:1px solid rgba(255,255,255,.14) !important; border-radius:10px !important;
    }}
    div[data-testid="stTextInput"] input, div[data-testid="stDateInput"] input {{
        border-radius:10px !important; border:1px solid rgba(15,27,53,.14) !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        border-radius:10px !important; background:#f4f6fb !important;
        border:1px solid rgba(15,27,53,.1) !important;
    }}
    div[data-testid="stNumberInput"] input {{
        border-radius:9px !important; border:1px solid rgba(15,27,53,.14) !important;
        font-family:{SERIF} !important; font-size:16px !important;
        text-align:right !important; color:{NAVY} !important; background:#fff !important;
    }}
    .stButton > button[kind="primary"] {{
        background:linear-gradient(135deg,{NAVY},{BLUE}) !important;
        color:#fff !important; font-weight:700 !important;
        border:none !important; border-radius:12px !important;
    }}
    div[data-testid="stForm"] button[kind="primaryFormSubmit"],
    div[data-testid="stForm"] button[kind="secondaryFormSubmit"] {{
        background:linear-gradient(135deg,{NAVY},{BLUE}) !important;
        color:#fff !important; border:none !important; border-radius:12px !important;
        font-weight:700 !important;
    }}
    div[data-testid="column"] button[kind="secondary"] {{
        border:1.5px solid rgba(45,107,196,.4) !important;
        color:{BLUE} !important; border-radius:9px !important; font-weight:700 !important;
        padding:4px 6px !important; min-height:36px !important;
    }}
    @media(max-width:640px) {{
        div[data-testid="column"] button[kind="secondary"] {{
            font-size:15px !important; padding:2px 0 !important;
        }}
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{ color:{NAVY} !important; }}
    div[data-baseweb="tab-highlight"] {{ background:{GOLD} !important; }}
    h1 {{ color:{NAVY} !important; }}
    h2, h3 {{ color:{NAVY2} !important; }}
    hr {{ border-color:#e2e8f0 !important; }}
    .tag-p1 {{ background:{BLUE}; color:{WHITE}; border-radius:6px; padding:3px 10px; font-size:12px; font-weight:700; }}
    .tag-p2 {{ background:{GOLD}; color:{NAVY}; border-radius:6px; padding:3px 10px; font-size:12px; font-weight:700; }}
    .g-card {{ background:{WHITE}; border-radius:14px; padding:20px 24px; box-shadow:0 2px 12px rgba(15,27,53,0.08); margin-bottom:16px; }}
    div[data-testid="stSidebarNav"] {{ display:none; }}
    div[data-testid="stToggle"] div[aria-checked="true"],
    div[data-testid="stToggle"] input:checked ~ div {{
        background-color:{GOLD} !important; border-color:{GOLD} !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background:white !important; border:1px solid rgba(15,27,53,.08) !important;
        border-top:none !important; border-radius:0 0 20px 20px !important;
        box-shadow:0 6px 24px rgba(15,27,53,.1) !important;
        margin-top:-4px !important; padding:0 6px 8px !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background:rgba(255,255,255,.10) !important; border:1px solid rgba(255,255,255,.22) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] span,
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] svg {{
        color:{WHITE} !important; fill:{WHITE} !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background:rgba(255,255,255,.07) !important; color:rgba(255,255,255,.6) !important;
        border:1px solid rgba(255,255,255,.12) !important; border-radius:10px !important;
        font-size:13px !important; font-weight:500 !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background:rgba(255,255,255,.13) !important; color:{WHITE} !important;
        border-color:rgba(255,255,255,.22) !important;
    }}
</style>"""
