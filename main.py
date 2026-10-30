import copy
import datetime
import json
import os
import threading
import time
import flet as ft

DATA_FILE = "oled_workout_v5.json"

# Популярные кириллические шрифты из Google Fonts + варианты толщины
FONT_FAMILIES = {
    "Montserrat (Bold Sport)": {
        "family": "Montserrat",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
        "hero": ft.FontWeight.W_900,
        "title": ft.FontWeight.W_800,
        "body": ft.FontWeight.W_600,
        "desc": "Широкий геометрический шрифт в премиальном спортивном стиле",
    },
    "Montserrat (Minimal Light)": {
        "family": "Montserrat",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
        "hero": ft.FontWeight.W_500,
        "title": ft.FontWeight.W_400,
        "body": ft.FontWeight.W_300,
        "desc": "Тонкие изящные линии для эстетики чистого минимализма",
    },
    "Unbounded (Cyber Wide)": {
        "family": "Unbounded",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/unbounded/Unbounded%5Bwght%5D.ttf",
        "hero": ft.FontWeight.W_900,
        "title": ft.FontWeight.W_700,
        "body": ft.FontWeight.W_500,
        "desc": "Футуристичный акцентный шрифт с поддержкой кириллицы",
    },
    "Rubik (Soft Rounded)": {
        "family": "Rubik",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/rubik/Rubik%5Bwght%5D.ttf",
        "hero": ft.FontWeight.W_800,
        "title": ft.FontWeight.W_700,
        "body": ft.FontWeight.W_500,
        "desc": "Мягкие скругленные углы, максимально комфортные для глаз",
    },
    "JetBrains Mono (Tech Code)": {
        "family": "JetBrainsMono",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
        "hero": ft.FontWeight.W_800,
        "title": ft.FontWeight.W_700,
        "body": ft.FontWeight.W_500,
        "desc": "Моноширинный техно-шрифт: идеальная ровность цифр и весов",
    },
    "Comfortaa (Modern Thin)": {
        "family": "Comfortaa",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/comfortaa/Comfortaa%5Bwght%5D.ttf",
        "hero": ft.FontWeight.W_700,
        "title": ft.FontWeight.W_600,
        "body": ft.FontWeight.W_400,
        "desc": "Плавный округлый шрифт с необычным современным характером",
    },
}

# Контрастные темы на OLED-фоне
THEMES = {
    "Stealth Monochrome": {
        "accent": "#FFFFFF",
        "secondary": "#A1A1AA",
        "glow1": "#0DFFFFFF",
        "glow2": "#08FFFFFF",
        "badge_bg": "#18FFFFFF",
        "desc": "Чистый бело-черный монохром",
    },
    "Liquid Ice (Cyan)": {
        "accent": "#38BDF8",
        "secondary": "#818CF8",
        "glow1": "#1438BDF8",
        "glow2": "#12818CF8",
        "badge_bg": "#1838BDF8",
        "desc": "Ледяной голубой неон iOS 26",
    },
    "Eclipse Crimson": {
        "accent": "#F43F5E",
        "secondary": "#FDA4AF",
        "glow1": "#14F43F5E",
        "glow2": "#10881337",
        "badge_bg": "#18F43F5E",
        "desc": "Агрессивный рубиново-красный акцент",
    },
    "Venom Emerald": {
        "accent": "#10B981",
        "secondary": "#6EE7B7",
        "glow1": "#1410B981",
        "glow2": "#10064E3B",
        "badge_bg": "#1810B981",
        "desc": "Яркий изумрудный кибер-зеленый",
    },
    "Ultraviolet": {
        "accent": "#A855F7",
        "secondary": "#D8B4FE",
        "glow1": "#14A855F7",
        "glow2": "#124C1D95",
        "badge_bg": "#18A855F7",
        "desc": "Глубокий фиолетовый неон",
    },
    "Solar Gold": {
        "accent": "#FBBF24",
        "secondary": "#FDE68A",
        "glow1": "#14FBBF24",
        "glow2": "#1078350F",
        "badge_bg": "#18FBBF24",
        "desc": "Премиальное титановое золото",
    },
    "Sunset Orange": {
        "accent": "#F97316",
        "secondary": "#FDBA74",
        "glow1": "#14F97316",
        "glow2": "#107C2D12",
        "badge_bg": "#18F97316",
        "desc": "Заряженный огненно-оранжевый",
    },
}

# Встроенные векторные SVG-схемы тренажеров
EXERCISE_SVGS = {
    "lat": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="65" y1="15" x2="65" y2="125" stroke="#27272A" stroke-width="6"/>
        <line x1="65" y1="18" x2="155" y2="18" stroke="#27272A" stroke-width="6"/>
        <line x1="145" y1="18" x2="145" y2="46" stroke="#71717A" stroke-width="2"/>
        <path d="M 105 50 L 120 44 L 170 44 L 185 50" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
        <circle cx="145" cy="64" r="9" fill="#FFFFFF"/>
        <line x1="145" y1="76" x2="145" y2="108" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <line x1="140" y1="80" x2="115" y2="48" stroke="#A1A1AA" stroke-width="5" stroke-linecap="round"/>
        <line x1="150" y1="80" x2="175" y2="48" stroke="#A1A1AA" stroke-width="5" stroke-linecap="round"/>
        <rect x="122" y="108" width="46" height="7" rx="3" fill="#3F3F46"/>
    </svg>""",
    "row": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="30" y1="115" x2="230" y2="115" stroke="#27272A" stroke-width="5"/>
        <rect x="45" y="40" width="22" height="75" rx="4" fill="#27272A"/>
        <line x1="67" y1="82" x2="145" y2="82" stroke="#71717A" stroke-width="3" stroke-dasharray="3,3"/>
        <circle cx="172" cy="52" r="9" fill="#FFFFFF"/>
        <line x1="172" y1="64" x2="172" y2="104" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <line x1="172" y1="104" x2="110" y2="104" stroke="#A1A1AA" stroke-width="7" stroke-linecap="round"/>
        <polyline points="172,72 155,84 142,82" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>""",
    "chest_machine": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <rect x="70" y="20" width="16" height="105" rx="4" fill="#27272A"/>
        <line x1="105" y1="35" x2="105" y2="115" stroke="#3F3F46" stroke-width="8" stroke-linecap="round"/>
        <circle cx="122" cy="52" r="9" fill="#FFFFFF"/>
        <line x1="120" y1="65" x2="120" y2="102" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <line x1="124" y1="72" x2="168" y2="72" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round"/>
        <line x1="145" y1="25" x2="172" y2="78" stroke="#A1A1AA" stroke-width="4"/>
        <path d="M 180 72 L 198 72 M 192 67 L 198 72 L 192 77" stroke="#71717A" stroke-width="2.5" fill="none"/>
    </svg>""",
    "fly": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <rect x="60" y="16" width="140" height="108" rx="10" fill="none" stroke="#27272A" stroke-width="4"/>
        <circle cx="130" cy="46" r="10" fill="#FFFFFF"/>
        <rect x="116" y="60" width="28" height="42" rx="8" fill="#FFFFFF"/>
        <path d="M 75 74 Q 100 92 122 80" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
        <path d="M 185 74 Q 160 92 138 80" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
        <circle cx="75" cy="74" r="6" fill="#FFFFFF"/>
        <circle cx="185" cy="74" r="6" fill="#FFFFFF"/>
    </svg>""",
    "leg_ext": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <polyline points="90,45 90,92 142,92" fill="none" stroke="#3F3F46" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="100" y1="92" x2="95" y2="125" stroke="#27272A" stroke-width="6"/>
        <circle cx="106" cy="44" r="9" fill="#FFFFFF"/>
        <line x1="105" y1="56" x2="105" y2="86" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <line x1="105" y1="86" x2="145" y2="86" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round"/>
        <line x1="145" y1="86" x2="188" y2="64" stroke="#A1A1AA" stroke-width="7" stroke-linecap="round"/>
        <circle cx="184" cy="72" r="7" fill="#FFFFFF"/>
    </svg>""",
    "leg_curl": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <polyline points="65,92 135,84 185,92" fill="none" stroke="#3F3F46" stroke-width="8" stroke-linecap="round"/>
        <line x1="85" y1="90" x2="80" y2="122" stroke="#27272A" stroke-width="6"/>
        <line x1="165" y1="90" x2="170" y2="122" stroke="#27272A" stroke-width="6"/>
        <circle cx="72" cy="74" r="8" fill="#FFFFFF"/>
        <line x1="84" y1="78" x2="140" y2="74" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round"/>
        <line x1="140" y1="74" x2="165" y2="44" stroke="#A1A1AA" stroke-width="7" stroke-linecap="round"/>
        <circle cx="160" cy="46" r="6" fill="#FFFFFF"/>
    </svg>""",
    "leg_press": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="55" y1="115" x2="115" y2="115" stroke="#3F3F46" stroke-width="8" stroke-linecap="round"/>
        <line x1="140" y1="35" x2="195" y2="95" stroke="#52525B" stroke-width="6"/>
        <rect x="132" y="45" width="38" height="12" rx="4" transform="rotate(-42 150 50)" fill="#FFFFFF"/>
        <circle cx="72" cy="88" r="9" fill="#FFFFFF"/>
        <line x1="80" y1="98" x2="112" y2="108" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <polyline points="112,108 122,82 146,64" fill="none" stroke="#A1A1AA" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>""",
    "smith": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <rect x="75" y="16" width="110" height="110" fill="none" stroke="#27272A" stroke-width="5"/>
        <line x1="100" y1="16" x2="100" y2="126" stroke="#52525B" stroke-width="2" stroke-dasharray="3,3"/>
        <line x1="160" y1="16" x2="160" y2="126" stroke="#52525B" stroke-width="2" stroke-dasharray="3,3"/>
        <line x1="65" y1="62" x2="195" y2="62" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
        <rect x="72" y="48" width="9" height="28" rx="3" fill="#A1A1AA"/>
        <rect x="179" y="48" width="9" height="28" rx="3" fill="#A1A1AA"/>
        <circle cx="130" cy="46" r="9" fill="#FFFFFF"/>
        <line x1="130" y1="60" x2="130" y2="96" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <polyline points="130,96 116,110 116,125" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
        <polyline points="130,96 144,110 144,125" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
    </svg>""",
    "hyper": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="65" y1="120" x2="165" y2="120" stroke="#27272A" stroke-width="6"/>
        <line x1="85" y1="120" x2="125" y2="75" stroke="#3F3F46" stroke-width="6"/>
        <rect x="118" y="66" width="22" height="12" rx="5" fill="#71717A"/>
        <line x1="82" y1="106" x2="126" y2="74" stroke="#A1A1AA" stroke-width="8" stroke-linecap="round"/>
        <line x1="126" y1="74" x2="168" y2="48" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <circle cx="180" cy="40" r="9" fill="#FFFFFF"/>
    </svg>""",
    "calves": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <rect x="95" y="114" width="70" height="10" rx="3" fill="#3F3F46"/>
        <circle cx="130" cy="34" r="9" fill="#FFFFFF"/>
        <rect x="106" y="46" width="48" height="8" rx="4" fill="#71717A"/>
        <line x1="130" y1="50" x2="130" y2="84" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round"/>
        <line x1="130" y1="84" x2="130" y2="112" stroke="#A1A1AA" stroke-width="8" stroke-linecap="round"/>
        <path d="M 155 108 L 155 86 M 150 92 L 155 85 L 160 92" stroke="#FFFFFF" stroke-width="2.5" fill="none"/>
    </svg>""",
    "bench": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <rect x="65" y="88" width="115" height="8" rx="4" fill="#3F3F46"/>
        <line x1="85" y1="96" x2="85" y2="122" stroke="#3F3F46" stroke-width="6"/>
        <line x1="160" y1="96" x2="160" y2="122" stroke="#3F3F46" stroke-width="6"/>
        <circle cx="88" cy="76" r="9" fill="#FFFFFF"/>
        <line x1="100" y1="80" x2="150" y2="80" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round"/>
        <polyline points="150,80 175,84 182,118" fill="none" stroke="#A1A1AA" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="110" y1="80" x2="110" y2="44" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
        <line x1="65" y1="44" x2="155" y2="44" stroke="#71717A" stroke-width="3"/>
        <rect x="70" y="28" width="10" height="32" rx="3" fill="#FFFFFF"/>
        <rect x="140" y="28" width="10" height="32" rx="3" fill="#FFFFFF"/>
    </svg>""",
    "incline_db": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="85" y1="58" x2="135" y2="102" stroke="#3F3F46" stroke-width="8" stroke-linecap="round"/>
        <line x1="135" y1="102" x2="165" y2="102" stroke="#3F3F46" stroke-width="8" stroke-linecap="round"/>
        <circle cx="96" cy="50" r="9" fill="#FFFFFF"/>
        <line x1="104" y1="62" x2="136" y2="92" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round"/>
        <polyline points="136,92 168,94 176,120" fill="none" stroke="#A1A1AA" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="116" y1="70" x2="116" y2="34" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
        <rect x="102" y="28" width="28" height="8" rx="3" fill="#FFFFFF"/>
    </svg>""",
    "crunch": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="45" y1="112" x2="215" y2="112" stroke="#27272A" stroke-width="5" stroke-linecap="round"/>
        <circle cx="88" cy="70" r="9" fill="#FFFFFF"/>
        <path d="M 96 80 Q 115 105 140 104" fill="none" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <polyline points="140,104 162,74 184,106" fill="none" stroke="#A1A1AA" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>""",
    "tricep": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="80" y1="15" x2="150" y2="15" stroke="#27272A" stroke-width="6"/>
        <line x1="145" y1="15" x2="145" y2="75" stroke="#71717A" stroke-width="2.5" stroke-dasharray="3,3"/>
        <circle cx="110" cy="40" r="9" fill="#FFFFFF"/>
        <line x1="110" y1="52" x2="110" y2="108" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round"/>
        <polyline points="114,58 118,80 144,88" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 152 72 L 152 96 M 147 90 L 152 96 L 157 90" stroke="#FFFFFF" stroke-width="2" fill="none"/>
    </svg>""",
    "dips": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="90" y1="74" x2="170" y2="74" stroke="#3F3F46" stroke-width="6" stroke-linecap="round"/>
        <line x1="100" y1="74" x2="100" y2="124" stroke="#27272A" stroke-width="5"/>
        <line x1="160" y1="74" x2="160" y2="124" stroke="#27272A" stroke-width="5"/>
        <circle cx="130" cy="36" r="9" fill="#FFFFFF"/>
        <line x1="130" y1="48" x2="130" y2="88" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round"/>
        <polyline points="122,54 106,62 110,74" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="138,54 154,62 150,74" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>""",
    "scott": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <polygon points="125,65 155,95 125,95" fill="#3F3F46"/>
        <line x1="138" y1="95" x2="138" y2="124" stroke="#27272A" stroke-width="6"/>
        <circle cx="105" cy="46" r="9" fill="#FFFFFF"/>
        <line x1="105" y1="58" x2="105" y2="105" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <polyline points="110,64 136,76 156,56" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="158" cy="54" r="8" fill="#FFFFFF"/>
    </svg>""",
    "hammer": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <circle cx="118" cy="38" r="10" fill="#FFFFFF"/>
        <line x1="118" y1="52" x2="118" y2="112" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round"/>
        <polyline points="122,58 126,86 152,68" fill="none" stroke="#A1A1AA" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="148" y="54" width="8" height="24" rx="3" fill="#FFFFFF"/>
    </svg>""",
    "shoulder_press": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <circle cx="130" cy="58" r="10" fill="#FFFFFF"/>
        <line x1="130" y1="72" x2="130" y2="116" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round"/>
        <polyline points="122,76 96,68 96,40" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="138,76 164,68 164,40" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="84" y="34" width="24" height="7" rx="3" fill="#FFFFFF"/>
        <rect x="152" y="34" width="24" height="7" rx="3" fill="#FFFFFF"/>
    </svg>""",
    "lat_raise": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <circle cx="130" cy="44" r="10" fill="#FFFFFF"/>
        <line x1="130" y1="58" x2="130" y2="114" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round"/>
        <path d="M 122 64 Q 95 58 74 68" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
        <path d="M 138 64 Q 165 58 186 68" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
        <rect x="64" y="64" width="16" height="7" rx="3" fill="#FFFFFF"/>
        <rect x="180" y="64" width="16" height="7" rx="3" fill="#FFFFFF"/>
    </svg>""",
    "pullup": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="60" y1="22" x2="200" y2="22" stroke="#3F3F46" stroke-width="6" stroke-linecap="round"/>
        <circle cx="130" cy="48" r="9" fill="#FFFFFF"/>
        <line x1="130" y1="60" x2="130" y2="102" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round"/>
        <polyline points="122,64 102,44 102,22" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="138,64 158,44 158,22" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="125" y1="102" x2="120" y2="126" stroke="#71717A" stroke-width="6" stroke-linecap="round"/>
        <line x1="135" y1="102" x2="140" y2="126" stroke="#71717A" stroke-width="6" stroke-linecap="round"/>
    </svg>""",
    "cable_cross": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="45" y1="16" x2="45" y2="124" stroke="#27272A" stroke-width="6"/>
        <line x1="215" y1="16" x2="215" y2="124" stroke="#27272A" stroke-width="6"/>
        <line x1="45" y1="18" x2="215" y2="18" stroke="#27272A" stroke-width="5"/>
        <line x1="48" y1="24" x2="108" y2="82" stroke="#71717A" stroke-width="2.5" stroke-dasharray="3,3"/>
        <line x1="212" y1="24" x2="152" y2="82" stroke="#71717A" stroke-width="2.5" stroke-dasharray="3,3"/>
        <circle cx="130" cy="48" r="9" fill="#FFFFFF"/>
        <line x1="130" y1="60" x2="130" y2="112" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round"/>
        <path d="M 124 66 Q 112 80 112 84" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
        <path d="M 136 66 Q 148 80 148 84" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
    </svg>""",
    "t_bar": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="50" y1="118" x2="165" y2="68" stroke="#52525B" stroke-width="6" stroke-linecap="round"/>
        <rect x="148" y="52" width="14" height="30" rx="4" transform="rotate(-24 155 67)" fill="#FFFFFF"/>
        <circle cx="152" cy="40" r="9" fill="#FFFFFF"/>
        <line x1="144" y1="50" x2="112" y2="80" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <line x1="112" y1="80" x2="105" y2="118" stroke="#A1A1AA" stroke-width="7" stroke-linecap="round"/>
        <line x1="136" y1="58" x2="150" y2="74" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
    </svg>""",
    "bb_curl": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <circle cx="130" cy="38" r="10" fill="#FFFFFF"/>
        <line x1="130" y1="52" x2="130" y2="114" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round"/>
        <path d="M 100 68 Q 130 78 160 68" fill="none" stroke="#A1A1AA" stroke-width="6" stroke-linecap="round"/>
        <line x1="82" y1="68" x2="178" y2="68" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
        <rect x="86" y="56" width="8" height="24" rx="3" fill="#FFFFFF"/>
        <rect x="166" y="56" width="8" height="24" rx="3" fill="#FFFFFF"/>
    </svg>""",
    "hack_squat": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="75" y1="25" x2="185" y2="118" stroke="#27272A" stroke-width="8" stroke-linecap="round"/>
        <line x1="155" y1="118" x2="195" y2="95" stroke="#3F3F46" stroke-width="7" stroke-linecap="round"/>
        <circle cx="105" cy="44" r="9" fill="#FFFFFF"/>
        <line x1="112" y1="54" x2="142" y2="80" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <polyline points="142,80 132,100 165,108" fill="none" stroke="#A1A1AA" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>""",
    "leg_raise": """<svg viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
        <rect width="260" height="140" rx="16" fill="#050507"/>
        <line x1="95" y1="18" x2="95" y2="124" stroke="#27272A" stroke-width="7"/>
        <line x1="95" y1="58" x2="135" y2="58" stroke="#3F3F46" stroke-width="6" stroke-linecap="round"/>
        <circle cx="114" cy="36" r="9" fill="#FFFFFF"/>
        <line x1="112" y1="48" x2="112" y2="84" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>
        <line x1="112" y1="84" x2="168" y2="84" stroke="#A1A1AA" stroke-width="8" stroke-linecap="round"/>
    </svg>""",
}

EXERCISE_CATALOG = [
    {
        "category": "Грудь",
        "items": [
            {"name": "Жим лежа", "svg": "bench", "tip": "Лопатки сведены, жесткий упор ногами, опускайте гриф на низ груди.", "default_w": "70"},
            {"name": "Жим гантелями на наклонной скамье", "svg": "incline_db", "tip": "Угол скамьи 30°, опускайте гантели глубоко вдоль линии ключиц.", "default_w": "24"},
            {"name": "Жим от груди в тренажере сидя", "svg": "chest_machine", "tip": "Прижмите лопатки к спинке, выжимайте рукояти плавно без рывков.", "default_w": "55"},
            {"name": "Тренажер «Бабочка» (Пек-дек)", "svg": "fly", "tip": "Локти чуть согнуты, сводите руки перед грудью с паузой 1 сек.", "default_w": "45"},
            {"name": "Сведение рук в кроссовере", "svg": "cable_cross", "tip": "Корпус чуть наклонен вперед, сводите рукояти по дуге перед грудью.", "default_w": "20"},
            {"name": "Отжимание на брусьях в тренажере", "svg": "dips", "tip": "Опускайтесь до прямого угла в локтях, слегка наклоняя корпус вперед.", "default_w": "40"},
        ],
    },
    {
        "category": "Спина",
        "items": [
            {"name": "Верхняя тяга", "svg": "lat", "tip": "Тяните рукоять к верху груди, сводя и опуская лопатки.", "default_w": "60"},
            {"name": "Горизонтальная тяга блока", "svg": "row", "tip": "Держите спину прямой, тяните рукоять к поясу, сводя лопатки.", "default_w": "55"},
            {"name": "Подтягивания / Гравитрон", "svg": "pullup", "tip": "Тянитесь грудью к перекладине без рывков и раскачки корпуса.", "default_w": "0"},
            {"name": "Тяга Т-грифа в упоре", "svg": "t_bar", "tip": "Плотно прижмите грудь к подушке, тяните рукояти локтями назад.", "default_w": "45"},
            {"name": "Гиперэкстензия", "svg": "hyper", "tip": "Поднимайте корпус до прямой линии с ногами без переразгибания поясницы.", "default_w": "10"},
        ],
    },
    {
        "category": "Ноги",
        "items": [
            {"name": "Жим ногами", "svg": "leg_press", "tip": "Не отрывайте поясницу от спинки и не выпрямляйте колени до щелчка.", "default_w": "120"},
            {"name": "Гакк-приседания в тренажере", "svg": "hack_squat", "tip": "Прижмите спину к каретке, опускайтесь до параллели бедер с платформой.", "default_w": "80"},
            {"name": "Машина Смита (Присед / Выпады)", "svg": "smith", "tip": "Контролируйте траекторию грифа, держите кор в жестком тонусе.", "default_w": "60"},
            {"name": "Разгибание ног сидя", "svg": "leg_ext", "tip": "Плавно разгибайте колени до пикового сокращения квадрицепса.", "default_w": "50"},
            {"name": "Сгибание ног сидя / лежа", "svg": "leg_curl", "tip": "Прижимайте таз к скамье, сгибайте голень без отрыва бедер.", "default_w": "40"},
            {"name": "Тренажер для икр", "svg": "calves", "tip": "Максимальная растяжка внизу и пауза на носках в верхней точке.", "default_w": "50"},
        ],
    },
    {
        "category": "Плечи",
        "items": [
            {"name": "Жим от плеч (гантели / тренажер)", "svg": "shoulder_press", "tip": "Выжимайте вес строго вверх без излишнего прогиба в пояснице.", "default_w": "20"},
            {"name": "Махи в стороны (гантели)", "svg": "lat_raise", "tip": "Поднимайте локти до уровня плеч, слегка наклонив корпус вперед.", "default_w": "10"},
            {"name": "Отведение назад в Пек-деке (Задняя дельта)", "svg": "fly", "tip": "Сядьте лицом к спинке тренажера и отводите прямые руки назад.", "default_w": "30"},
        ],
    },
    {
        "category": "Руки",
        "items": [
            {"name": "Разгибание рук на блоке (Трицепс)", "svg": "tricep", "tip": "Локти прижаты к корпусу, разгибайте предплечья до конца.", "default_w": "25"},
            {"name": "Сгибание рук на скамье Скотта", "svg": "scott", "tip": "Плечи плотно лежат на пюпитре, поднимайте вес без раскачки.", "default_w": "30"},
            {"name": "Подъем EZ-штанги на бицепс", "svg": "bb_curl", "tip": "Локти зафиксированы у корпуса, поднимайте гриф без заброса спиной.", "default_w": "30"},
            {"name": "Сгибание рук молот", "svg": "hammer", "tip": "Нейтральный хват (ладони друг к другу), локти неподвижны.", "default_w": "16"},
        ],
    },
    {
        "category": "Пресс",
        "items": [
            {"name": "Скручивание", "svg": "crunch", "tip": "Скручивайте грудной отдел к тазу на выдохе, не тяните шею руками.", "default_w": "0"},
            {"name": "Подъем ног в упоре", "svg": "leg_raise", "tip": "Прижмите поясницу к спинке и поднимайте колени к груди подконтрольно.", "default_w": "0"},
        ],
    },
]

CATALOG_MAP = {
    item["name"]: item
    for group in EXERCISE_CATALOG
    for item in group["items"]
}


def make_ex_entry(name, svg, tip, weight):
    return {
        "name": name,
        "svg": svg,
        "tip": tip,
        "done": False,
        "last_date": None,
        "sets_data": [
            {"weight": str(weight), "reps": "10", "done": False, "prev_weight": None, "prev_reps": None}
            for _ in range(4)
        ],
    }


DEFAULT_PROGRAMS = {
    "Верх тела • База": [
        make_ex_entry("Жим лежа", "bench", CATALOG_MAP["Жим лежа"]["tip"], "70"),
        make_ex_entry("Верхняя тяга", "lat", CATALOG_MAP["Верхняя тяга"]["tip"], "60"),
        make_ex_entry("Тренажер «Бабочка» (Пек-дек)", "fly", CATALOG_MAP["Тренажер «Бабочка» (Пек-дек)"]["tip"], "45"),
        make_ex_entry("Разгибание рук на блоке (Трицепс)", "tricep", CATALOG_MAP["Разгибание рук на блоке (Трицепс)"]["tip"], "25"),
    ]
}


def safe_float(val, default=0.0):
    try:
        s = str(val).replace(",", ".").strip()
        if not s:
            return default
        return float(s)
    except Exception:
        return default


def safe_int(val, default=10):
    try:
        s = str(val).strip()
        if not s:
            return default
        return int(float(s.replace(",", ".")))
    except Exception:
        return default


def format_weight(val):
    num = safe_float(val, 0.0)
    return str(int(num) if num.is_integer() else round(num, 1))


def format_duration(seconds: int) -> str:
    m, s = divmod(max(0, int(seconds)), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def load_state():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "programs" in data and "settings" in data:
                    if "account" not in data:
                        data["account"] = {"name": "Атлет", "completed_count": 0, "history": []}
                    if "font_choice" not in data["settings"]:
                        data["settings"]["font_choice"] = "Montserrat (Bold Sport)"
                    if not data["programs"]:
                        data["programs"] = copy.deepcopy(DEFAULT_PROGRAMS)
                    return data
        except Exception:
            pass
    return {
        "settings": {
            "theme": "Stealth Monochrome",
            "glass_mode": "ios26",
            "font_choice": "Montserrat (Bold Sport)",
        },
        "account": {
            "name": "Атлет",
            "completed_count": 0,
            "history": [],
        },
        "programs": copy.deepcopy(DEFAULT_PROGRAMS),
        "current_program": "Верх тела • База",
    }


def save_state(state):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)


def make_border(width, color):
    if hasattr(ft, "Border") and hasattr(ft.Border, "all"):
        return ft.Border.all(width, color)
    return ft.border.all(width, color)


def make_padding(left=0, top=0, right=0, bottom=0):
    if hasattr(ft, "Padding"):
        return ft.Padding(left=left, top=top, right=right, bottom=bottom)
    return ft.padding.only(left=left, top=top, right=right, bottom=bottom)


def make_anim(duration=320):
    try:
        return ft.Animation(duration, ft.AnimationCurve.EASE_OUT_CUBIC)
    except Exception:
        return duration


def render_svg(svg_key: str, width=240, height=130):
    svg_code = EXERCISE_SVGS.get(svg_key, EXERCISE_SVGS["bench"])
    try:
        return ft.Image(src=svg_code, width=width, height=height, fit=ft.ImageFit.CONTAIN)
    except Exception:
        try:
            return ft.Image(src=svg_code, width=width, height=height)
        except Exception:
            return ft.Icon(ft.Icons.FITNESS_CENTER_ROUNDED, size=48, color="#FFFFFF")


def main(page: ft.Page):
    page.title = "OLED GYM"
    page.bgcolor = "#000000"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 450
    page.window.height = 900

    # Подключаем популярные кириллические шрифты из Google Fonts
    page.fonts = {
        info["family"]: info["url"]
        for info in FONT_FAMILIES.values()
    }

    if os.path.exists(os.path.join("assets", "icon.ico")):
        page.window.icon = "icon.ico"
    elif os.path.exists(os.path.join("assets", "icon.png")):
        page.window.icon = "icon.png"

    state = load_state()
    programs = state["programs"]
    settings = state["settings"]
    account = state["account"]

    current_program = state.get("current_program", "")
    if current_program not in programs:
        current_program = list(programs.keys())[0] if programs else ""
        state["current_program"] = current_program

    def apply_page_font():
        f_choice = settings.get("font_choice", "Montserrat (Bold Sport)")
        f_info = FONT_FAMILIES.get(f_choice, FONT_FAMILIES["Montserrat (Bold Sport)"])
        page.theme = ft.Theme(font_family=f_info["family"])
        page.dark_theme = ft.Theme(font_family=f_info["family"])

    apply_page_font()

    # Состояния экранов: "workouts", "create_program", "catalog", "detail", "themes", "account"
    active_view = "workouts"
    selected_ex_idx = None
    selected_cat_filter = "Все"

    # Временный черновик упражнения при открытии экрана подходов (для кнопок ✓ и ✕)
    detail_temp_ex = None

    # Состояние конструктора новой программы
    builder_program_name = ""
    builder_selected_items = []
    builder_cat_filter = "Все"

    # Состояние секундомера активной тренировки
    workout_active = False
    workout_start_ts = 0.0
    timer_text_control = ft.Text("00:00", size=14, weight=ft.FontWeight.W_900, color="#FFFFFF")

    def timer_worker():
        while True:
            time.sleep(1)
            if workout_active and workout_start_ts > 0:
                elapsed = int(time.time() - workout_start_ts)
                timer_text_control.value = format_duration(elapsed)
                try:
                    timer_text_control.update()
                except Exception:
                    pass

    threading.Thread(target=timer_worker, daemon=True).start()

    def get_theme():
        t_name = settings.get("theme", "Stealth Monochrome")
        return THEMES.get(t_name, THEMES["Stealth Monochrome"])

    def fw(level="title"):
        f_choice = settings.get("font_choice", "Montserrat (Bold Sport)")
        f_info = FONT_FAMILIES.get(f_choice, FONT_FAMILIES["Montserrat (Bold Sport)"])
        return f_info.get(level, ft.FontWeight.W_700)

    def show_toast(msg: str):
        theme = get_theme()
        snack = ft.SnackBar(
            bgcolor="#121216",
            content=ft.Text(msg, color=theme["accent"], weight=fw("title"), size=13),
            duration=2200,
        )
        try:
            page.open(snack)
        except Exception:
            page.snack_bar = snack
            snack.open = True
            page.update()

    def ios26_glass(content, padding=14, radius=22, is_highlighted=False, on_click=None):
        theme = get_theme()
        is_abyss = settings.get("glass_mode") == "abyss"

        if is_highlighted:
            bg_color = theme["badge_bg"]
            border_color = theme["accent"]
        else:
            bg_color = "#04FFFFFF" if is_abyss else "#09FFFFFF"
            border_color = "#14FFFFFF" if is_abyss else "#22FFFFFF"

        return ft.Container(
            content=content,
            padding=padding,
            border_radius=radius,
            bgcolor=bg_color,
            blur=ft.Blur(40, 40),
            border=make_border(1.2, border_color),
            animate=make_anim(300),
            on_click=on_click,
        )

    glow_top = ft.Container(
        width=260, height=260, left=-90, top=20, border_radius=130, animate=make_anim(600)
    )
    glow_bottom = ft.Container(
        width=300, height=300, right=-100, bottom=50, border_radius=150, animate=make_anim(600)
    )

    header_holder = ft.Container()
    dock_holder = ft.Container()

    # Анимированный контейнер для плавных переходов между вкладками
    view_switcher = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=260,
        reverse_duration=180,
        switch_in_curve=ft.AnimationCurve.EASE_OUT_CUBIC,
        switch_out_curve=ft.AnimationCurve.EASE_IN_CUBIC,
        expand=True,
    )

    # Главная колонка интерфейса
    main_body = ft.Column(
        expand=True,
        spacing=12,
        controls=[header_holder, view_switcher, dock_holder],
    )

    # Плавная анимированная шкала прогресса
    progress_track_width = 368
    progress_bar_fill = ft.Container(
        width=0,
        height=8,
        border_radius=4,
        animate=make_anim(500),
    )

    def sync_glows():
        theme = get_theme()
        is_abyss = settings.get("glass_mode") == "abyss"
        glow_top.bgcolor = "#04FFFFFF" if is_abyss else theme["glow1"]
        glow_bottom.bgcolor = "#03FFFFFF" if is_abyss else theme["glow2"]

    def select_program(prog_name):
        nonlocal current_program, active_view
        current_program = prog_name
        state["current_program"] = prog_name
        save_state(state)
        active_view = "workouts"
        rebuild_ui()

    def delete_current_program(e):
        nonlocal current_program
        if len(programs) <= 1:
            show_toast("Должна остаться хотя бы одна программа")
            return
        programs.pop(current_program, None)
        current_program = list(programs.keys())[0]
        state["current_program"] = current_program
        save_state(state)
        rebuild_ui()
        show_toast("Программа удалена")

    def switch_view(view_name):
        nonlocal active_view
        active_view = view_name
        rebuild_ui()

    def open_create_program_view(e=None):
        nonlocal active_view, builder_program_name, builder_selected_items, builder_cat_filter
        builder_program_name = ""
        builder_selected_items = []
        builder_cat_filter = "Все"
        active_view = "create_program"
        rebuild_ui()

    # Открытие настройки подходов с созданием временной копии (для кнопок ✓ и ✕)
    def open_exercise_detail(idx):
        nonlocal selected_ex_idx, active_view, detail_temp_ex
        prog_list = programs.get(current_program, [])
        if 0 <= idx < len(prog_list):
            selected_ex_idx = idx
            detail_temp_ex = copy.deepcopy(prog_list[idx])
            if "sets_data" not in detail_temp_ex or not detail_temp_ex["sets_data"]:
                detail_temp_ex["sets_data"] = [
                    {"weight": "50", "reps": "10", "done": False, "prev_weight": None, "prev_reps": None}
                    for _ in range(4)
                ]
            active_view = "detail"
            rebuild_ui()

    # Сохранение изменений упражнения по нажатию на ГАЛОЧКУ (✓)
    def save_detail_changes(e=None):
        nonlocal active_view, detail_temp_ex
        prog_list = programs.get(current_program, [])
        if detail_temp_ex is not None and selected_ex_idx is not None and selected_ex_idx < len(prog_list):
            sets_list = detail_temp_ex.get("sets_data", [])
            detail_temp_ex["done"] = len(sets_list) > 0 and all(s.get("done", False) for s in sets_list)
            prog_list[selected_ex_idx] = detail_temp_ex
            save_state(state)
            show_toast("Подходы и веса сохранены")
        detail_temp_ex = None
        active_view = "workouts"
        rebuild_ui()

    # Отмена изменений упражнения по нажатию на КРЕСТИК (✕)
    def discard_detail_changes(e=None):
        nonlocal active_view, detail_temp_ex
        detail_temp_ex = None
        active_view = "workouts"
        rebuild_ui()
        show_toast("Изменения отменены")

    def add_from_catalog(item):
        if not current_program:
            return
        w = item.get("default_w", "40")
        new_ex = make_ex_entry(
            item["name"],
            item.get("svg", "bench"),
            item.get("tip", "Выполняйте движение подконтрольно."),
            w,
        )
        programs[current_program].append(new_ex)
        save_state(state)
        open_exercise_detail(len(programs[current_program]) - 1)

    # Диалог создания своего тренажера
    custom_name_input = ft.TextField(
        label="Название упражнения / тренажера",
        border_color="#26FFFFFF",
        focused_border_color="#FFFFFF",
        text_style=ft.TextStyle(color="#FFFFFF"),
    )
    custom_weight_input = ft.TextField(
        label="Рабочий вес (кг)",
        value="40",
        border_color="#26FFFFFF",
        focused_border_color="#FFFFFF",
        text_style=ft.TextStyle(color="#FFFFFF"),
    )
    custom_tip_input = ft.TextField(
        label="Заметка по технике",
        value="Подконтрольное выполнение в полной амплитуде.",
        border_color="#26FFFFFF",
        focused_border_color="#FFFFFF",
        text_style=ft.TextStyle(color="#FFFFFF"),
    )

    def close_custom_dialog(e=None):
        custom_dialog.open = False
        page.update()

    def save_custom_exercise(e):
        name_val = (custom_name_input.value or "").strip()
        if name_val:
            w_val = format_weight(custom_weight_input.value or "40")
            tip_val = (custom_tip_input.value or "").strip() or "Подконтрольное выполнение."
            custom_name_input.value = ""
            close_custom_dialog()
            new_item = {
                "name": name_val,
                "svg": "bench",
                "tip": tip_val,
                "default_w": w_val,
            }
            if active_view == "create_program":
                builder_selected_items.append(new_item)
                rebuild_ui()
            else:
                add_from_catalog(new_item)

    custom_dialog = ft.AlertDialog(
        bgcolor="#08080C",
        title=ft.Text("СВОЁ УПРАЖНЕНИЕ", size=16, weight=ft.FontWeight.W_800, color="#FFFFFF"),
        content=ft.Column(
            tight=True,
            spacing=12,
            controls=[custom_name_input, custom_weight_input, custom_tip_input],
        ),
        actions=[
            ft.Container(
                content=ft.Text("Отмена", color="#8AFFFFFF", weight=ft.FontWeight.W_700),
                padding=make_padding(14, 10, 14, 10),
                border_radius=12,
                on_click=close_custom_dialog,
            ),
            ft.Container(
                content=ft.Text("ДОБАВИТЬ", color="#000000", weight=ft.FontWeight.W_900),
                bgcolor="#FFFFFF",
                padding=make_padding(18, 10, 18, 10),
                border_radius=12,
                on_click=save_custom_exercise,
            ),
        ],
    )
    page.overlay.append(custom_dialog)

    def open_custom_dialog(e):
        custom_dialog.open = True
        page.update()

    def toggle_exercise_done(idx):
        ex = programs[current_program][idx]
        new_state = not ex.get("done", False)
        ex["done"] = new_state
        for s in ex.get("sets_data", []):
            s["done"] = new_state
        save_state(state)
        rebuild_ui()

    def delete_exercise(idx):
        programs[current_program].pop(idx)
        save_state(state)
        rebuild_ui()

    def start_workout_timer(e):
        nonlocal workout_active, workout_start_ts
        if not workout_active:
            workout_active = True
            workout_start_ts = time.time()
            timer_text_control.value = "00:00"
            rebuild_ui()
            show_toast("Тренировка началась! Секундомер запущен.")

    # Завершение тренировки: сохранение силовых + запись в историю аккаунта
    def finish_workout(e):
        nonlocal workout_active, workout_start_ts
        prog_exercises = programs.get(current_program, [])
        if not prog_exercises:
            return

        now_dt = datetime.datetime.now()
        short_date = now_dt.strftime("%d.%m")
        full_date = now_dt.strftime("%d.%m.%Y в %H:%M")

        elapsed_sec = int(time.time() - workout_start_ts) if workout_active else 0
        duration_str = format_duration(elapsed_sec) if workout_active else "Без таймера"

        workout_active = False
        workout_start_ts = 0.0
        timer_text_control.value = "00:00"

        done_sets_total = 0
        for ex in prog_exercises:
            sets_data = ex.get("sets_data", [])
            for s in sets_data:
                if s.get("done", False):
                    done_sets_total += 1
                s["prev_weight"] = format_weight(s.get("weight", "0"))
                s["prev_reps"] = str(safe_int(s.get("reps", "10"), 10))
                s["done"] = False
            ex["last_date"] = short_date
            ex["done"] = False

        # Обновляем статистику в Аккаунте
        account["completed_count"] = int(account.get("completed_count", 0)) + 1
        if "history" not in account:
            account["history"] = []
        account["history"].insert(
            0,
            {
                "date": full_date,
                "program": current_program,
                "duration": duration_str,
                "exercises_count": len(prog_exercises),
                "sets_done": done_sets_total,
            },
        )

        save_state(state)
        rebuild_ui()
        show_toast(f"Тренировка сохранена! Всего тренировок: {account['completed_count']}")

    def change_theme(theme_name):
        settings["theme"] = theme_name
        save_state(state)
        rebuild_ui()

    def change_glass_mode(mode_name):
        settings["glass_mode"] = mode_name
        save_state(state)
        rebuild_ui()

    def change_font_choice(font_key):
        settings["font_choice"] = font_key
        apply_page_font()
        save_state(state)
        rebuild_ui()

    # =========================================================================
    # ЭКРАН 1: ГЛАВНЫЙ ЭКРАН ПРОГРАММ И ТРЕНИРОВКИ
    # =========================================================================
    def build_workouts_view():
        theme = get_theme()
        accent = theme["accent"]

        # Горизонтальная лента программ + кнопка "+ СОЗДАТЬ ПРОГРАММУ"
        prog_tabs = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=8)
        for p_name in programs.keys():
            is_sel = p_name == current_program
            prog_tabs.controls.append(
                ft.Container(
                    on_click=lambda e, pn=p_name: select_program(pn),
                    animate=make_anim(280),
                    padding=make_padding(16, 10, 16, 10),
                    border_radius=16,
                    bgcolor=accent if is_sel else "#10FFFFFF",
                    border=make_border(1.2, accent if is_sel else "#22FFFFFF"),
                    content=ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(
                                ft.Icons.BOLT_ROUNDED if is_sel else ft.Icons.FOLDER_OUTLINED,
                                size=15,
                                color="#000000" if is_sel else accent,
                            ),
                            ft.Text(
                                p_name.upper(),
                                size=11,
                                weight=fw("title"),
                                color="#000000" if is_sel else "#FFFFFF",
                            ),
                        ],
                    ),
                )
            )

        # Кнопка создания новой программы
        prog_tabs.controls.append(
            ft.Container(
                on_click=open_create_program_view,
                animate=make_anim(280),
                padding=make_padding(14, 10, 14, 10),
                border_radius=16,
                bgcolor="#16FFFFFF",
                border=make_border(1.2, accent),
                content=ft.Row(
                    spacing=5,
                    controls=[
                        ft.Icon(ft.Icons.ADD_CIRCLE_ROUNDED, size=15, color=accent),
                        ft.Text(
                            "СОЗДАТЬ ПРОГРАММУ",
                            size=11,
                            weight=fw("title"),
                            color=accent,
                        ),
                    ],
                ),
            )
        )

        prog_exercises = programs.get(current_program, [])
        total_ex = len(prog_exercises)
        done_ex_count = sum(1 for ex in prog_exercises if ex.get("done", False))

        total_sets_all = sum(len(ex.get("sets_data", [])) for ex in prog_exercises)
        done_sets_all = sum(
            sum(1 for s in ex.get("sets_data", []) if s.get("done", False))
            for ex in prog_exercises
        )
        progress = done_sets_all / total_sets_all if total_sets_all > 0 else 0
        pct = int(progress * 100)

        # Обновляем ширину плавной полосы прогресса
        progress_bar_fill.width = max(0, int(progress_track_width * progress))
        progress_bar_fill.bgcolor = accent

        # Панель таймера тренировки и компактная кнопка «Закончить» у правого края
        if not workout_active:
            session_controls = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Container(
                        on_click=start_workout_timer,
                        padding=make_padding(14, 8, 14, 8),
                        border_radius=14,
                        bgcolor=accent,
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color="#000000", size=18),
                                ft.Text("НАЧАТЬ ТРЕНИРОВКУ", size=11, weight=fw("hero"), color="#000000"),
                            ],
                        ),
                    ),
                    ft.Container(
                        on_click=finish_workout,
                        padding=make_padding(11, 7, 11, 7),
                        border_radius=12,
                        bgcolor="#14FFFFFF",
                        border=make_border(1, "#28FFFFFF"),
                        content=ft.Row(
                            spacing=4,
                            controls=[
                                ft.Icon(ft.Icons.FLAG_ROUNDED, color=accent, size=14),
                                ft.Text("Закончить", size=10, weight=fw("title"), color=accent),
                            ],
                        ),
                    ),
                ],
            )
        else:
            timer_text_control.color = accent
            session_controls = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Container(
                        padding=make_padding(12, 6, 12, 6),
                        border_radius=14,
                        bgcolor=theme["badge_bg"],
                        border=make_border(1, accent),
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.TIMER_ROUNDED, color=accent, size=16),
                                ft.Text("ВРЕМЯ:", size=10, weight=fw("title"), color="#B0FFFFFF"),
                                timer_text_control,
                            ],
                        ),
                    ),
                    # Небольшая аккуратная кнопка "Закончить" у правого края
                    ft.Container(
                        on_click=finish_workout,
                        padding=make_padding(12, 7, 12, 7),
                        border_radius=12,
                        bgcolor=accent,
                        content=ft.Row(
                            spacing=4,
                            controls=[
                                ft.Icon(ft.Icons.CHECK_ROUNDED, color="#000000", size=14),
                                ft.Text("Закончить", size=10, weight=fw("hero"), color="#000000"),
                            ],
                        ),
                    ),
                ],
            )

        progress_card = ios26_glass(
            padding=15,
            radius=22,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        f"ПРОГРАММА: {current_program.upper()}",
                                        size=10,
                                        weight=fw("title"),
                                        color="#75FFFFFF",
                                    ),
                                    ft.Text(
                                        f"ПОДХОДЫ: {done_sets_all}/{total_sets_all} • УПР: {done_ex_count}/{total_ex} ({pct}%)",
                                        size=13,
                                        weight=fw("hero"),
                                        color=accent,
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=4,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.ADD_ROUNDED,
                                        icon_size=18,
                                        icon_color=accent,
                                        tooltip="Добавить тренажер в эту программу",
                                        on_click=lambda e: switch_view("catalog"),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                        icon_size=17,
                                        icon_color="#50FFFFFF",
                                        tooltip="Удалить программу",
                                        on_click=delete_current_program,
                                    )
                                    if len(programs) > 1
                                    else ft.Container(),
                                ],
                            ),
                        ],
                    ),
                    # Анимированная полоса прогресса
                    ft.Container(
                        width=progress_track_width,
                        height=8,
                        border_radius=4,
                        bgcolor="#14FFFFFF",
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Row(spacing=0, controls=[progress_bar_fill]),
                    ),
                    session_controls,
                ],
            ),
        )

        ex_list = ft.Column(spacing=10, scroll=ft.ScrollMode.HIDDEN, expand=True)

        if total_ex == 0:
            ex_list.controls.append(
                ios26_glass(
                    padding=28,
                    radius=24,
                    on_click=lambda e: switch_view("catalog"),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, color=accent, size=38),
                            ft.Text(
                                "В ПРОГРАММЕ ПОКА НЕТ УПРАЖНЕНИЙ",
                                size=14,
                                weight=fw("hero"),
                                color="#FFFFFF",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Нажмите сюда, чтобы добавить тренажеры из каталога",
                                size=12,
                                weight=fw("body"),
                                color="#80FFFFFF",
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                )
            )

        for idx, ex in enumerate(prog_exercises):
            is_done = ex.get("done", False)
            sets_data = ex.get("sets_data", [])
            sets_count = len(sets_data)
            done_sets = sum(1 for s in sets_data if s.get("done", False))
            max_w = max([safe_float(s.get("weight", 0)) for s in sets_data], default=0.0)
            w_str = format_weight(max_w)
            reps_preview = "/".join(str(safe_int(s.get("reps", 10))) for s in sets_data[:4])

            prev_weights = [
                safe_float(s.get("prev_weight"))
                for s in sets_data
                if s.get("prev_weight") is not None
            ]
            has_prev = len(prev_weights) > 0
            prev_max_w = format_weight(max(prev_weights)) if has_prev else None
            prev_reps_preview = (
                "/".join(
                    str(s.get("prev_reps", "10"))
                    for s in sets_data[:4]
                    if s.get("prev_reps") is not None
                )
                if has_prev
                else ""
            )
            last_date_lbl = ex.get("last_date") or ""
            svg_key = ex.get("svg") or CATALOG_MAP.get(ex["name"], {}).get("svg", "bench")

            check_circle = ft.Container(
                width=28,
                height=28,
                border_radius=9,
                animate=make_anim(240),
                bgcolor=accent if is_done else "#08FFFFFF",
                border=make_border(1.5, accent if is_done else "#38FFFFFF"),
                alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
                on_click=lambda e, i=idx: toggle_exercise_done(i),
                content=ft.Icon(
                    ft.Icons.CHECK_ROUNDED,
                    size=17,
                    color="#000000" if is_done else "transparent",
                ),
            )

            thumb = ft.Container(
                width=64,
                height=44,
                border_radius=10,
                bgcolor="#050507",
                border=make_border(1, "#22FFFFFF"),
                on_click=lambda e, i=idx: open_exercise_detail(i),
                content=render_svg(svg_key, width=60, height=40),
            )

            info_controls = [
                ft.Text(
                    ex["name"],
                    size=14,
                    weight=fw("title"),
                    color="#55FFFFFF" if is_done else "#FFFFFF",
                    style=ft.TextStyle(
                        decoration=ft.TextDecoration.LINE_THROUGH if is_done else None
                    ),
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Container(
                            padding=make_padding(8, 3, 8, 3),
                            border_radius=8,
                            bgcolor=theme["badge_bg"],
                            content=ft.Text(
                                f"{done_sets}/{sets_count} ПОДХ • {reps_preview}",
                                size=10,
                                weight=fw("title"),
                                color=accent,
                            ),
                        ),
                        ft.Container(
                            padding=make_padding(8, 3, 8, 3),
                            border_radius=8,
                            bgcolor="#14FFFFFF",
                            content=ft.Text(
                                f"{w_str} КГ",
                                size=10,
                                weight=fw("title"),
                                color=theme["secondary"],
                            ),
                        ),
                    ],
                ),
            ]

            if has_prev:
                date_part = f" ({last_date_lbl})" if last_date_lbl else ""
                info_controls.append(
                    ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.HISTORY_ROUNDED, size=12, color="#75FFFFFF"),
                            ft.Text(
                                f"Прошлый раз{date_part}: {prev_max_w} кг × {prev_reps_preview}",
                                size=10,
                                weight=fw("body"),
                                color="#85FFFFFF",
                            ),
                        ],
                    )
                )

            info_area = ft.Container(
                expand=True,
                on_click=lambda e, i=idx: open_exercise_detail(i),
                content=ft.Column(spacing=4, controls=info_controls),
            )

            card_row = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=10,
                controls=[
                    check_circle,
                    thumb,
                    info_area,
                    ft.IconButton(
                        icon=ft.Icons.CLOSE_ROUNDED,
                        icon_size=18,
                        icon_color="#45FFFFFF",
                        on_click=lambda e, i=idx: delete_exercise(i),
                    ),
                ],
            )

            ex_list.controls.append(
                ios26_glass(
                    content=card_row,
                    padding=12,
                    radius=20,
                    is_highlighted=is_done,
                )
            )

        return ft.Column(
            key="view_workouts",
            expand=True,
            spacing=12,
            controls=[prog_tabs, progress_card, ex_list],
        )

    # =========================================================================
    # ЭКРАН 2: КОНСТРУКТОР СОЗДАНИЯ НОВОЙ ПРОГРАММЫ
    # =========================================================================
    def build_create_program_view():
        theme = get_theme()
        accent = theme["accent"]

        def on_prog_name_change(e):
            nonlocal builder_program_name
            builder_program_name = e.control.value

        def toggle_builder_item(item):
            names = [x["name"] for x in builder_selected_items]
            if item["name"] in names:
                builder_selected_items[:] = [x for x in builder_selected_items if x["name"] != item["name"]]
            else:
                builder_selected_items.append(item)
            rebuild_ui()

        def set_builder_cat(cat_name):
            nonlocal builder_cat_filter
            builder_cat_filter = cat_name
            rebuild_ui()

        def save_created_program(e):
            nonlocal current_program, active_view
            p_title = (builder_program_name or "").strip()
            if not p_title:
                show_toast("Введите название программы!")
                return
            if not builder_selected_items:
                show_toast("Выберите хотя бы одно упражнение!")
                return

            programs[p_title] = [
                make_ex_entry(
                    it["name"],
                    it.get("svg", "bench"),
                    it.get("tip", "Выполняйте подконтрольно."),
                    it.get("default_w", "40"),
                )
                for it in builder_selected_items
            ]
            current_program = p_title
            state["current_program"] = p_title
            save_state(state)
            active_view = "workouts"
            rebuild_ui()
            show_toast(f"Программа «{p_title}» сохранена!")

        name_field = ft.TextField(
            value=builder_program_name,
            label="Название программы (например: Грудь + Бицепс)",
            border_color=accent,
            focused_border_color="#FFFFFF",
            border_radius=16,
            text_style=ft.TextStyle(size=14, weight=fw("title"), color="#FFFFFF"),
            on_change=on_prog_name_change,
        )

        categories = ["Все"] + [g["category"] for g in EXERCISE_CATALOG]
        filter_row = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=6)
        for cat_name in categories:
            is_sel = builder_cat_filter == cat_name
            filter_row.controls.append(
                ft.Container(
                    on_click=lambda e, c=cat_name: set_builder_cat(c),
                    padding=make_padding(14, 7, 14, 7),
                    border_radius=14,
                    bgcolor=accent if is_sel else "#10FFFFFF",
                    border=make_border(1, accent if is_sel else "#22FFFFFF"),
                    content=ft.Text(
                        cat_name.upper(),
                        size=10,
                        weight=fw("title"),
                        color="#000000" if is_sel else "#FFFFFF",
                    ),
                )
            )

        items_list = ft.Column(spacing=10, scroll=ft.ScrollMode.HIDDEN, expand=True)
        selected_names = {x["name"] for x in builder_selected_items}

        for group in EXERCISE_CATALOG:
            if builder_cat_filter != "Все" and group["category"] != builder_cat_filter:
                continue

            items_list.controls.append(
                ft.Text(group["category"].upper(), size=11, weight=fw("title"), color="#80FFFFFF")
            )

            for item in group["items"]:
                is_picked = item["name"] in selected_names
                items_list.controls.append(
                    ios26_glass(
                        padding=12,
                        radius=20,
                        is_highlighted=is_picked,
                        on_click=lambda e, it=item: toggle_builder_item(it),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=76,
                                    height=50,
                                    border_radius=12,
                                    bgcolor="#050507",
                                    border=make_border(1, "#24FFFFFF"),
                                    content=render_svg(item["svg"], width=72, height=46),
                                ),
                                ft.Column(
                                    expand=True,
                                    spacing=3,
                                    controls=[
                                        ft.Text(item["name"], size=13, weight=fw("title"), color="#FFFFFF"),
                                        ft.Text(item["tip"], size=10, weight=fw("body"), color="#75FFFFFF", max_lines=2),
                                    ],
                                ),
                                ft.Container(
                                    width=32,
                                    height=32,
                                    border_radius=10,
                                    bgcolor=accent if is_picked else "#14FFFFFF",
                                    alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
                                    content=ft.Icon(
                                        ft.Icons.CHECK_ROUNDED if is_picked else ft.Icons.ADD_ROUNDED,
                                        color="#000000" if is_picked else "#FFFFFF",
                                        size=18,
                                    ),
                                ),
                            ],
                        ),
                    )
                )

        save_btn = ft.Container(
            on_click=save_created_program,
            padding=make_padding(16, 14, 16, 14),
            border_radius=18,
            bgcolor=accent,
            alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color="#000000", size=20),
                    ft.Text(
                        f"СОХРАНИТЬ ПРОГРАММУ (ВЫБРАНО: {len(builder_selected_items)})",
                        size=12,
                        weight=fw("hero"),
                        color="#000000",
                    ),
                ],
            ),
        )

        return ft.Column(
            key="view_create_program",
            expand=True,
            spacing=10,
            controls=[name_field, filter_row, items_list, save_btn],
        )

    # =========================================================================
    # ЭКРАН 3: КАТАЛОГ ТРЕНАЖЕРОВ (ДОБАВЛЕНИЕ В ТЕКУЩУЮ ПРОГРАММУ)
    # =========================================================================
    def build_catalog_view():
        theme = get_theme()
        accent = theme["accent"]

        def select_cat(cat_name):
            nonlocal selected_cat_filter
            selected_cat_filter = cat_name
            rebuild_ui()

        cat_col = ft.Column(spacing=10, scroll=ft.ScrollMode.HIDDEN, expand=True)

        cat_col.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        f"ДОБАВИТЬ В: {current_program.upper()}",
                        size=11,
                        weight=fw("title"),
                        color=accent,
                    ),
                    ft.Container(
                        on_click=open_custom_dialog,
                        padding=make_padding(12, 6, 12, 6),
                        border_radius=12,
                        bgcolor="#16FFFFFF",
                        border=make_border(1, accent),
                        content=ft.Text(
                            "+ СВОЁ УПРАЖНЕНИЕ",
                            size=10,
                            weight=fw("title"),
                            color=accent,
                        ),
                    ),
                ],
            )
        )

        categories = ["Все"] + [g["category"] for g in EXERCISE_CATALOG]
        filter_row = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=6)
        for cat_name in categories:
            is_sel = selected_cat_filter == cat_name
            filter_row.controls.append(
                ft.Container(
                    on_click=lambda e, c=cat_name: select_cat(c),
                    padding=make_padding(14, 7, 14, 7),
                    border_radius=14,
                    bgcolor=accent if is_sel else "#10FFFFFF",
                    border=make_border(1, accent if is_sel else "#22FFFFFF"),
                    content=ft.Text(
                        cat_name.upper(),
                        size=10,
                        weight=fw("title"),
                        color="#000000" if is_sel else "#FFFFFF",
                    ),
                )
            )
        cat_col.controls.append(filter_row)

        for group in EXERCISE_CATALOG:
            if selected_cat_filter != "Все" and group["category"] != selected_cat_filter:
                continue

            cat_col.controls.append(
                ft.Container(
                    padding=make_padding(0, 6, 0, 2),
                    content=ft.Text(
                        group["category"].upper(),
                        size=12,
                        weight=fw("title"),
                        color="#80FFFFFF",
                    ),
                )
            )

            for item in group["items"]:
                item_card = ios26_glass(
                    padding=12,
                    radius=20,
                    on_click=lambda e, it=item: add_from_catalog(it),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=84,
                                height=54,
                                border_radius=12,
                                bgcolor="#050507",
                                border=make_border(1, "#24FFFFFF"),
                                content=render_svg(item["svg"], width=80, height=50),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=3,
                                controls=[
                                    ft.Text(item["name"], size=14, weight=fw("title"), color="#FFFFFF"),
                                    ft.Text(item["tip"], size=11, weight=fw("body"), color="#75FFFFFF", max_lines=2),
                                ],
                            ),
                            ft.Container(
                                width=34,
                                height=34,
                                border_radius=12,
                                bgcolor=accent,
                                alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
                                content=ft.Icon(ft.Icons.ADD_ROUNDED, color="#000000", size=20),
                            ),
                        ],
                    ),
                )
                cat_col.controls.append(item_card)

        return ft.Column(key="view_catalog", expand=True, controls=[cat_col])

    # =========================================================================
    # ЭКРАН 4: КРУПНОЕ И ПОНЯТНОЕ МЕНЮ НАСТРОЙКИ ПОДХОДОВ (С ГАЛОЧКОЙ И КРЕСТИКОМ)
    # =========================================================================
    def build_exercise_detail_view():
        theme = get_theme()
        accent = theme["accent"]

        if detail_temp_ex is None:
            switch_view("workouts")
            return ft.Container()

        ex = detail_temp_ex
        cat_info = CATALOG_MAP.get(ex["name"], {})
        svg_key = ex.get("svg") or cat_info.get("svg", "bench")
        tip_text = ex.get("tip") or cat_info.get("tip", "Выполняйте движение подконтрольно и без рывков.")
        last_date_lbl = ex.get("last_date")

        def change_set_weight(s_idx, delta):
            s = ex["sets_data"][s_idx]
            cur = safe_float(s.get("weight", "0"), 0.0)
            nv = max(0.0, cur + delta)
            s["weight"] = format_weight(nv)
            rebuild_ui()

        def on_weight_typed(e, s_idx):
            ex["sets_data"][s_idx]["weight"] = e.control.value

        def change_set_reps(s_idx, delta):
            s = ex["sets_data"][s_idx]
            cur = safe_int(s.get("reps", "10"), 10)
            nv = max(1, cur + delta)
            s["reps"] = str(nv)
            rebuild_ui()

        def on_reps_typed(e, s_idx):
            ex["sets_data"][s_idx]["reps"] = e.control.value

        def toggle_set_done(s_idx):
            ex["sets_data"][s_idx]["done"] = not ex["sets_data"][s_idx].get("done", False)
            rebuild_ui()

        def add_new_set(e):
            last_w = ex["sets_data"][-1]["weight"] if ex["sets_data"] else "50"
            last_r = ex["sets_data"][-1]["reps"] if ex["sets_data"] else "10"
            ex["sets_data"].append(
                {"weight": str(last_w), "reps": str(last_r), "done": False, "prev_weight": None, "prev_reps": None}
            )
            rebuild_ui()

        def remove_set(s_idx):
            if len(ex["sets_data"]) > 1:
                ex["sets_data"].pop(s_idx)
                rebuild_ui()

        detail_col = ft.Column(spacing=14, scroll=ft.ScrollMode.HIDDEN, expand=True)

        # Компактная карточка с иллюстрацией тренажера
        detail_col.controls.append(
            ios26_glass(
                padding=14,
                radius=22,
                content=ft.Row(
                    spacing=14,
                    controls=[
                        ft.Container(
                            width=105,
                            height=74,
                            border_radius=14,
                            bgcolor="#050507",
                            border=make_border(1, "#24FFFFFF"),
                            content=render_svg(svg_key, width=100, height=68),
                        ),
                        ft.Column(
                            expand=True,
                            spacing=4,
                            controls=[
                                ft.Text(ex["name"].upper(), size=15, weight=fw("hero"), color="#FFFFFF"),
                                ft.Text(tip_text, size=11, weight=fw("body"), color="#85FFFFFF"),
                            ],
                        ),
                    ],
                ),
            )
        )

        # Заголовок + крупная кнопка добавления подхода
        detail_col.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("РАБОЧИЕ ПОДХОДЫ", size=13, weight=fw("hero"), color="#FFFFFF"),
                    ft.Container(
                        on_click=add_new_set,
                        padding=make_padding(14, 8, 14, 8),
                        border_radius=14,
                        bgcolor=accent,
                        content=ft.Text("+ ДОБАВИТЬ ПОДХОД", size=11, weight=fw("hero"), color="#000000"),
                    ),
                ],
            )
        )

        # Крупные понятные карточки для каждого подхода
        for s_idx, s_data in enumerate(ex["sets_data"]):
            s_done = s_data.get("done", False)
            prev_w = s_data.get("prev_weight")
            prev_r = s_data.get("prev_reps")
            has_set_prev = prev_w is not None and prev_r is not None
            date_suffix = f" ({last_date_lbl})" if last_date_lbl else ""

            set_card = ios26_glass(
                padding=16,
                radius=22,
                is_highlighted=s_done,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        # Шапка подхода с крупным шрифтом
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Container(
                                            width=34,
                                            height=34,
                                            border_radius=10,
                                            bgcolor=accent if s_done else "#18FFFFFF",
                                            alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
                                            on_click=lambda e, i=s_idx: toggle_set_done(i),
                                            content=ft.Icon(
                                                ft.Icons.CHECK_ROUNDED,
                                                size=22,
                                                color="#000000" if s_done else "#70FFFFFF",
                                            ),
                                        ),
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text(
                                                    f"ПОДХОД #{s_idx + 1}",
                                                    size=16,
                                                    weight=fw("hero"),
                                                    color=accent if s_done else "#FFFFFF",
                                                ),
                                                ft.Text(
                                                    f"Прошлый раз{date_suffix}: {prev_w} кг × {prev_r}"
                                                    if has_set_prev
                                                    else "Впишите вес и повторения",
                                                    size=12,
                                                    weight=fw("body"),
                                                    color="#90FFFFFF",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Container(
                                            on_click=lambda e, i=s_idx: toggle_set_done(i),
                                            padding=make_padding(14, 8, 14, 8),
                                            border_radius=12,
                                            bgcolor=accent if s_done else "#18FFFFFF",
                                            content=ft.Text(
                                                "ВЫПОЛНЕН" if s_done else "ОТМЕТИТЬ",
                                                size=12,
                                                weight=fw("hero"),
                                                color="#000000" if s_done else "#FFFFFF",
                                            ),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                            icon_size=20,
                                            icon_color="#60FFFFFF",
                                            on_click=lambda e, i=s_idx: remove_set(i),
                                        )
                                        if len(ex["sets_data"]) > 1
                                        else ft.Container(),
                                    ],
                                ),
                            ],
                        ),
                        # Крупный блок ВЕСА (КГ)
                        ft.Container(
                            padding=make_padding(12, 8, 12, 8),
                            border_radius=16,
                            bgcolor="#0EFFFFFF",
                            border=make_border(1, "#24FFFFFF"),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("ВЕС СНАРЯДА (КГ)", size=13, weight=fw("title"), color="#B0FFFFFF"),
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Container(
                                                on_click=lambda e, i=s_idx: change_set_weight(i, -2.5),
                                                padding=make_padding(12, 10, 12, 10),
                                                border_radius=12,
                                                bgcolor="#1FFFFFFF",
                                                content=ft.Text("-2.5", size=14, weight=fw("hero"), color="#FFFFFF"),
                                            ),
                                            ft.TextField(
                                                value=str(s_data.get("weight", "50")),
                                                width=78,
                                                height=44,
                                                content_padding=make_padding(4, 6, 4, 6),
                                                text_align=ft.TextAlign.CENTER,
                                                border_color="#30FFFFFF",
                                                border_radius=12,
                                                text_style=ft.TextStyle(
                                                    size=20, weight=fw("hero"), color="#FFFFFF"
                                                ),
                                                on_change=lambda e, i=s_idx: on_weight_typed(e, i),
                                            ),
                                            ft.Container(
                                                on_click=lambda e, i=s_idx: change_set_weight(i, 2.5),
                                                padding=make_padding(12, 10, 12, 10),
                                                border_radius=12,
                                                bgcolor=accent,
                                                content=ft.Text("+2.5", size=14, weight=fw("hero"), color="#000000"),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        # Крупный блок ПОВТОРЕНИЙ
                        ft.Container(
                            padding=make_padding(12, 8, 12, 8),
                            border_radius=16,
                            bgcolor="#0EFFFFFF",
                            border=make_border(1, "#24FFFFFF"),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("ПОВТОРЕНИЯ (РАЗ)", size=13, weight=fw("title"), color="#B0FFFFFF"),
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Container(
                                                on_click=lambda e, i=s_idx: change_set_reps(i, -1),
                                                padding=make_padding(14, 10, 14, 10),
                                                border_radius=12,
                                                bgcolor="#1FFFFFFF",
                                                content=ft.Text("-1", size=14, weight=fw("hero"), color="#FFFFFF"),
                                            ),
                                            ft.TextField(
                                                value=str(s_data.get("reps", "10")),
                                                width=78,
                                                height=44,
                                                content_padding=make_padding(4, 6, 4, 6),
                                                text_align=ft.TextAlign.CENTER,
                                                border_color="#30FFFFFF",
                                                border_radius=12,
                                                text_style=ft.TextStyle(
                                                    size=20, weight=fw("hero"), color=accent
                                                ),
                                                on_change=lambda e, i=s_idx: on_reps_typed(e, i),
                                            ),
                                            ft.Container(
                                                on_click=lambda e, i=s_idx: change_set_reps(i, 1),
                                                padding=make_padding(14, 10, 14, 10),
                                                border_radius=12,
                                                bgcolor=accent,
                                                content=ft.Text("+1", size=14, weight=fw("hero"), color="#000000"),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            )
            detail_col.controls.append(set_card)

        return ft.Column(key="view_detail", expand=True, controls=[detail_col])

    # =========================================================================
    # ЭКРАН 5: ОТДЕЛЬНАЯ ВКЛАДКА «ТЕМЫ» (ЦВЕТА, СТЕКЛО, ШРИФТЫ)
    # =========================================================================
    def build_themes_view():
        theme = get_theme()
        accent = theme["accent"]
        current_theme_name = settings.get("theme", "Stealth Monochrome")
        current_glass_mode = settings.get("glass_mode", "ios26")
        current_font_choice = settings.get("font_choice", "Montserrat (Bold Sport)")

        themes_list = ft.Column(spacing=12, scroll=ft.ScrollMode.HIDDEN, expand=True)

        # 1. Цветовые темы
        themes_list.controls.append(
            ft.Text("ЦВЕТОВАЯ ПАЛИТРА OLED", size=12, weight=fw("title"), color="#75FFFFFF")
        )

        for t_name, t_vals in THEMES.items():
            is_sel = t_name == current_theme_name
            themes_list.controls.append(
                ios26_glass(
                    padding=14,
                    radius=20,
                    is_highlighted=is_sel,
                    on_click=lambda e, tn=t_name: change_theme(tn),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=14,
                                controls=[
                                    ft.Container(
                                        width=30,
                                        height=30,
                                        border_radius=15,
                                        bgcolor=t_vals["accent"],
                                        border=make_border(2, "#FFFFFF" if is_sel else "#30FFFFFF"),
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(t_name.upper(), size=13, weight=fw("title"), color="#FFFFFF"),
                                            ft.Text(t_vals.get("desc", ""), size=11, weight=fw("body"), color="#80FFFFFF"),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE_ROUNDED if is_sel else ft.Icons.CIRCLE_OUTLINED,
                                color=t_vals["accent"] if is_sel else "#40FFFFFF",
                                size=20,
                            ),
                        ],
                    ),
                )
            )

        # 2. Коллекция шрифтов с поддержкой русского языка
        themes_list.controls.append(
            ft.Container(
                padding=make_padding(0, 8, 0, 0),
                content=ft.Text("ШРИФТЫ И ТИПОГРАФИКА (КИРИЛЛИЦА)", size=12, weight=fw("title"), color="#75FFFFFF"),
            )
        )

        for f_key, f_info in FONT_FAMILIES.items():
            is_f_sel = current_font_choice == f_key
            themes_list.controls.append(
                ios26_glass(
                    padding=14,
                    radius=20,
                    is_highlighted=is_f_sel,
                    on_click=lambda e, fk=f_key: change_font_choice(fk),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=3,
                                controls=[
                                    ft.Text(
                                        f_key,
                                        size=14,
                                        font_family=f_info["family"],
                                        weight=f_info["title"],
                                        color="#FFFFFF",
                                    ),
                                    ft.Text(
                                        f_info["desc"],
                                        size=11,
                                        font_family=f_info["family"],
                                        weight=f_info["body"],
                                        color="#80FFFFFF",
                                    ),
                                ],
                            ),
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE_ROUNDED if is_f_sel else ft.Icons.CIRCLE_OUTLINED,
                                color=accent if is_f_sel else "#40FFFFFF",
                                size=20,
                            ),
                        ],
                    ),
                )
            )

        # 3. Оптика стекла
        themes_list.controls.append(
            ft.Container(
                padding=make_padding(0, 8, 0, 0),
                content=ft.Text("ОПТИКА СТЕКЛА (iOS 26)", size=12, weight=fw("title"), color="#75FFFFFF"),
            )
        )

        glass_modes = [
            ("ios26", "Liquid Glass iOS 26", "Глубокое преломление + зеркальный блик грани"),
            ("abyss", "Pitch Black Abyss", "Экстремально темное стекло 98.5% OLED Black"),
        ]

        for mode_key, title, subtitle in glass_modes:
            is_active = current_glass_mode == mode_key
            themes_list.controls.append(
                ios26_glass(
                    padding=14,
                    radius=20,
                    is_highlighted=is_active,
                    on_click=lambda e, m=mode_key: change_glass_mode(m),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=3,
                                controls=[
                                    ft.Text(title, size=14, weight=fw("title"), color="#FFFFFF"),
                                    ft.Text(subtitle, size=11, weight=fw("body"), color="#80FFFFFF"),
                                ],
                            ),
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE_ROUNDED if is_active else ft.Icons.CIRCLE_OUTLINED,
                                color=accent if is_active else "#40FFFFFF",
                                size=20,
                            ),
                        ],
                    ),
                )
            )

        return ft.Column(key="view_themes", expand=True, controls=[themes_list])

    # =========================================================================
    # ЭКРАН 6: ВКЛАДКА «АККАУНТ» (ИМЯ, СЧЕТЧИК ТРЕНИРОВОК, ЖУРНАЛ ПО ДАТАМ)
    # =========================================================================
    def build_account_view():
        theme = get_theme()
        accent = theme["accent"]

        def on_user_name_change(e):
            account["name"] = e.control.value
            save_state(state)

        user_name = account.get("name", "Атлет")
        completed_count = int(account.get("completed_count", 0))
        history_list = account.get("history", [])

        acc_col = ft.Column(spacing=14, scroll=ft.ScrollMode.HIDDEN, expand=True)

        # Карточка профиля
        acc_col.controls.append(
            ios26_glass(
                padding=18,
                radius=24,
                content=ft.Column(
                    spacing=14,
                    controls=[
                        ft.Row(
                            spacing=14,
                            controls=[
                                ft.Container(
                                    width=56,
                                    height=56,
                                    border_radius=28,
                                    bgcolor=theme["badge_bg"],
                                    border=make_border(1.5, accent),
                                    alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
                                    content=ft.Icon(ft.Icons.PERSON_ROUNDED, color=accent, size=30),
                                ),
                                ft.Column(
                                    expand=True,
                                    spacing=4,
                                    controls=[
                                        ft.Text("ПРОФИЛЬ АТЛЕТА", size=10, weight=fw("title"), color=accent),
                                        ft.TextField(
                                            value=user_name,
                                            label="Ваше имя",
                                            border_color="#28FFFFFF",
                                            focused_border_color=accent,
                                            border_radius=12,
                                            height=48,
                                            text_style=ft.TextStyle(size=16, weight=fw("hero"), color="#FFFFFF"),
                                            on_change=on_user_name_change,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # Статистика тренировок
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    padding=14,
                                    border_radius=18,
                                    bgcolor="#10FFFFFF",
                                    border=make_border(1, "#22FFFFFF"),
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=4,
                                        controls=[
                                            ft.Text(
                                                str(completed_count),
                                                size=28,
                                                weight=fw("hero"),
                                                color=accent,
                                            ),
                                            ft.Text(
                                                "ЗАВЕРШЕНО ТРЕНИРОВОК",
                                                size=10,
                                                weight=fw("title"),
                                                color="#80FFFFFF",
                                                text_align=ft.TextAlign.CENTER,
                                            ),
                                        ],
                                    ),
                                ),
                                ft.Container(
                                    expand=True,
                                    padding=14,
                                    border_radius=18,
                                    bgcolor="#10FFFFFF",
                                    border=make_border(1, "#22FFFFFF"),
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=4,
                                        controls=[
                                            ft.Text(
                                                str(len(programs)),
                                                size=28,
                                                weight=fw("hero"),
                                                color="#FFFFFF",
                                            ),
                                            ft.Text(
                                                "АКТИВНЫХ ПРОГРАММ",
                                                size=10,
                                                weight=fw("title"),
                                                color="#80FFFFFF",
                                                text_align=ft.TextAlign.CENTER,
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            )
        )

        # Журнал дат проведенных тренировок
        acc_col.controls.append(
            ft.Text("ИСТОРИЯ ТРЕНИРОВОК ПО ДНЯМ", size=12, weight=fw("title"), color="#80FFFFFF")
        )

        if not history_list:
            acc_col.controls.append(
                ios26_glass(
                    padding=24,
                    radius=22,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, color="#50FFFFFF", size=34),
                            ft.Text(
                                "История пока пуста",
                                size=14,
                                weight=fw("title"),
                                color="#FFFFFF",
                            ),
                            ft.Text(
                                "Когда вы нажмете «Закончить» на главном экране, здесь появится дата, время и программа тренировки.",
                                size=11,
                                weight=fw("body"),
                                color="#75FFFFFF",
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                )
            )
        else:
            for item in history_list:
                acc_col.controls.append(
                    ios26_glass(
                        padding=14,
                        radius=20,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=12,
                                    controls=[
                                        ft.Container(
                                            width=40,
                                            height=40,
                                            border_radius=12,
                                            bgcolor=theme["badge_bg"],
                                            alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
                                            content=ft.Icon(
                                                ft.Icons.EVENT_AVAILABLE_ROUNDED,
                                                color=accent,
                                                size=20,
                                            ),
                                        ),
                                        ft.Column(
                                            spacing=3,
                                            controls=[
                                                ft.Text(
                                                    item.get("program", "Тренировка").upper(),
                                                    size=13,
                                                    weight=fw("title"),
                                                    color="#FFFFFF",
                                                ),
                                                ft.Text(
                                                    f"Дата: {item.get('date', '')}",
                                                    size=11,
                                                    weight=fw("body"),
                                                    color="#85FFFFFF",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    spacing=3,
                                    controls=[
                                        ft.Container(
                                            padding=make_padding(8, 3, 8, 3),
                                            border_radius=8,
                                            bgcolor="#16FFFFFF",
                                            content=ft.Text(
                                                f"⏱ {item.get('duration', '00:00')}",
                                                size=10,
                                                weight=fw("title"),
                                                color=accent,
                                            ),
                                        ),
                                        ft.Text(
                                            f"Упр: {item.get('exercises_count', 0)} • Подх: {item.get('sets_done', 0)}",
                                            size=10,
                                            weight=fw("body"),
                                            color="#70FFFFFF",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    )
                )

        return ft.Column(key="view_account", expand=True, controls=[acc_col])

    # =========================================================================
    # СБОРКА ШАПКИ, ДОКА И ПЛАВНОЕ ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК
    # =========================================================================
    def rebuild_ui():
        sync_glows()
        theme = get_theme()
        accent = theme["accent"]

        titles = {
            "workouts": "OLED GYM",
            "create_program": "НОВАЯ ПРОГРАММА",
            "catalog": "КАТАЛОГ",
            "detail": "ПОДХОДЫ",
            "themes": "ТЕМЫ И ШРИФТЫ",
            "account": "АККАУНТ",
        }

        has_custom_icon = os.path.exists(os.path.join("assets", "icon.png"))
        title_row_controls = []
        if has_custom_icon:
            title_row_controls.append(
                ft.Container(
                    width=36,
                    height=36,
                    border_radius=10,
                    bgcolor="#000000",
                    border=make_border(1, "#26FFFFFF"),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(src="icon.png", width=36, height=36),
                )
            )

        title_row_controls.append(
            ft.Column(
                spacing=2,
                controls=[
                    ft.Text(
                        titles.get(active_view, "OLED GYM"),
                        size=24,
                        weight=fw("hero"),
                        color="#FFFFFF",
                    ),
                    ft.Text(
                        f"{account.get('name', 'Атлет').upper()} • {settings.get('theme', '').upper()}",
                        size=10,
                        weight=fw("title"),
                        color=theme["secondary"],
                    ),
                ],
            )
        )

        # Правая часть шапки: в режиме "detail" показываем ГАЛОЧКУ (✓) и КРЕСТИК (✕)
        right_header_controls = []
        if active_view == "detail":
            right_header_controls = [
                # КРЕСТИК — отменить и не сохранять изменения
                ios26_glass(
                    padding=8,
                    radius=14,
                    on_click=discard_detail_changes,
                    content=ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.CLOSE_ROUNDED, color="#F43F5E", size=20),
                            ft.Text("ОТМЕНА", size=10, weight=fw("hero"), color="#F43F5E"),
                        ],
                    ),
                ),
                # ГАЛОЧКА — подтвердить и сохранить подходы
                ft.Container(
                    on_click=save_detail_changes,
                    padding=make_padding(12, 8, 12, 8),
                    border_radius=14,
                    bgcolor=accent,
                    content=ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_ROUNDED, color="#000000", size=20),
                            ft.Text("СОХРАНИТЬ", size=10, weight=fw("hero"), color="#000000"),
                        ],
                    ),
                ),
            ]
        elif active_view in ("catalog", "create_program"):
            right_header_controls = [
                ios26_glass(
                    padding=8,
                    radius=14,
                    on_click=lambda e: switch_view("workouts"),
                    content=ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.CLOSE_ROUNDED, color="#FFFFFF", size=18),
                            ft.Text("ЗАКРЫТЬ", size=10, weight=fw("title"), color="#FFFFFF"),
                        ],
                    ),
                )
            ]

        header_holder.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=10, controls=title_row_controls),
                ft.Row(spacing=8, controls=right_header_controls),
            ],
        )

        # Нижний док на 3 вкладки: ТРЕНИРОВКИ | ТЕМЫ | АККАУНТ
        def dock_btn(view_key, icon_data, label):
            is_act = active_view == view_key or (
                view_key == "workouts" and active_view in ("detail", "catalog", "create_program")
            )
            return ft.Container(
                on_click=lambda e: switch_view(view_key),
                animate=make_anim(280),
                padding=make_padding(18, 10, 18, 10),
                border_radius=18,
                bgcolor=accent if is_act else "transparent",
                content=ft.Row(
                    spacing=6,
                    controls=[
                        ft.Icon(
                            icon_data,
                            size=17,
                            color="#000000" if is_act else "#85FFFFFF",
                        ),
                        ft.Text(
                            label,
                            size=11,
                            weight=fw("title"),
                            color="#000000" if is_act else "#85FFFFFF",
                        ),
                    ],
                ),
            )

        dock_holder.content = ios26_glass(
            padding=6,
            radius=26,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    dock_btn("workouts", ft.Icons.FITNESS_CENTER_ROUNDED, "ТРЕНИРОВКИ"),
                    dock_btn("themes", ft.Icons.PALETTE_ROUNDED, "ТЕМЫ"),
                    dock_btn("account", ft.Icons.PERSON_ROUNDED, "АККАУНТ"),
                ],
            ),
        )

        if active_view == "workouts":
            view_switcher.content = build_workouts_view()
        elif active_view == "create_program":
            view_switcher.content = build_create_program_view()
        elif active_view == "catalog":
            view_switcher.content = build_catalog_view()
        elif active_view == "detail":
            view_switcher.content = build_exercise_detail_view()
        elif active_view == "themes":
            view_switcher.content = build_themes_view()
        else:
            view_switcher.content = build_account_view()

        page.update()

    root_stack = ft.Stack(
        expand=True,
        controls=[
            glow_top,
            glow_bottom,
            ft.Container(
                expand=True,
                padding=make_padding(18, 38, 18, 16),
                content=main_body,
            ),
        ],
    )

    page.add(root_stack)
    rebuild_ui()


if hasattr(ft, "run"):
    ft.run(main, assets_dir="assets")
else:
    ft.app(target=main, assets_dir="assets")
