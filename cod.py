import json
import os
import flet as ft

DATA_FILE = "oled_workout_v4.json"

# Встроенные векторные SVG-схемы для всех типов тренажеров и упражнений
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
}

# Полный каталог упражнений и тренажеров по категориям
EXERCISE_CATALOG = [
    {
        "category": "Грузоблочные тренажеры",
        "items": [
            {"name": "Верхняя тяга", "svg": "lat", "tip": "Тяните рукоять к верху груди, сводя и опуская лопатки.", "default_w": "60"},
            {"name": "Горизонтальная тяга блока", "svg": "row", "tip": "Держите спину прямой, тяните рукоять к поясу.", "default_w": "55"},
            {"name": "Жим от груди в тренажере сидя", "svg": "chest_machine", "tip": "Прижмите лопатки к спинке, выжимайте рукояти плавно без рывков.", "default_w": "50"},
            {"name": "Тренажер «Бабочка» (Пек-дек)", "svg": "fly", "tip": "Локти чуть согнуты, сводите руки перед грудью с паузой 1 сек.", "default_w": "45"},
            {"name": "Разгибание ног сидя", "svg": "leg_ext", "tip": "Плавно разгибайте колени до пикового сокращения квадрицепса.", "default_w": "50"},
            {"name": "Сгибание ног сидя / лежа", "svg": "leg_curl", "tip": "Прижимайте таз к скамье, сгибайте голень без отрыва бедер.", "default_w": "40"},
        ],
    },
    {
        "category": "Тренажеры со свободными весами и рамы",
        "items": [
            {"name": "Жим ногами", "svg": "leg_press", "tip": "Не отрывайте поясницу от спинки и не выпрямляйте колени до щелчка.", "default_w": "120"},
            {"name": "Машина Смита", "svg": "smith", "tip": "Контролируйте траекторию грифа, держите кор в жестком тонусе.", "default_w": "60"},
            {"name": "Гиперэкстензия", "svg": "hyper", "tip": "Поднимайте корпус до прямой линии с ногами без переразгибания.", "default_w": "10"},
            {"name": "Тренажер для икр", "svg": "calves", "tip": "Максимальная растяжка внизу и пауза на носках в верхней точке.", "default_w": "50"},
            {"name": "Жим лежа", "svg": "bench", "tip": "Лопатки сведены, жесткий упор ногами, опускайте гриф на низ груди.", "default_w": "70"},
            {"name": "Жим гантелями на наклонной скамье", "svg": "incline_db", "tip": "Угол скамьи 30°, опускайте гантели глубоко вдоль линии ключиц.", "default_w": "24"},
            {"name": "Скручивание", "svg": "crunch", "tip": "Скручивайте грудной отдел к тазу на выдохе, не тяните шею руками.", "default_w": "0"},
            {"name": "Разгибание рук", "svg": "tricep", "tip": "Локти прижаты к корпусу, разгибайте предплечья до конца.", "default_w": "25"},
            {"name": "Отжимание на брусьях в тренажере", "svg": "dips", "tip": "Опускайтесь до прямого угла в локтях, контролируя плечевой пояс.", "default_w": "40"},
            {"name": "Сгибание рук на скамье Скотта", "svg": "scott", "tip": "Плечи плотно лежат на пюпитре, поднимайте вес без раскачки.", "default_w": "30"},
            {"name": "Сгибание рук молот", "svg": "hammer", "tip": "Нейтральный хват (ладони друг к другу), локти неподвижны.", "default_w": "16"},
            {"name": "Жим от плеч (гантели)", "svg": "shoulder_press", "tip": "Выжимайте гантели строго вверх без прогиба в пояснице.", "default_w": "20"},
            {"name": "Махи в стороны (гантели)", "svg": "lat_raise", "tip": "Поднимайте локти до уровня плеч, слегка наклонив корпус вперед.", "default_w": "10"},
        ],
    },
]

CATALOG_MAP = {
    item["name"]: item
    for group in EXERCISE_CATALOG
    for item in group["items"]
}

THEMES = {
    "Stealth Monochrome": {
        "accent": "#FFFFFF",
        "secondary": "#A1A1AA",
        "glow1": "#0DFFFFFF",
        "glow2": "#08FFFFFF",
        "badge_bg": "#18FFFFFF",
    },
    "Obsidian Phantom": {
        "accent": "#D4D4D8",
        "secondary": "#71717A",
        "glow1": "#09FFFFFF",
        "glow2": "#05FFFFFF",
        "badge_bg": "#12FFFFFF",
    },
    "Carbon Titanium": {
        "accent": "#E2E8F0",
        "secondary": "#94A3B8",
        "glow1": "#0ECBD5E1",
        "glow2": "#0864748B",
        "badge_bg": "#16E2E8F0",
    },
    "Ghost Silver": {
        "accent": "#F4F4F5",
        "secondary": "#A1A1AA",
        "glow1": "#12E4E4E7",
        "glow2": "#0871717A",
        "badge_bg": "#1AF4F4F5",
    },
    "Eclipse Crimson": {
        "accent": "#F43F5E",
        "secondary": "#A1A1AA",
        "glow1": "#10F43F5E",
        "glow2": "#06FFFFFF",
        "badge_bg": "#16F43F5E",
    },
}

DAYS_ORDER = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]

DAYS_FULL = {
    "ПН": "Понедельник",
    "ВТ": "Вторник",
    "СР": "Среда",
    "ЧТ": "Четверг",
    "ПТ": "Пятница",
    "СБ": "Суббота",
    "ВС": "Воскресенье",
}


def load_state():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "workouts" in data and "settings" in data:
                    for d in DAYS_ORDER:
                        if d not in data["workouts"]:
                            data["workouts"][d] = []
                    return data
        except Exception:
            pass
    return {
        "settings": {
            "theme": "Stealth Monochrome",
            "glass_mode": "ios26",
        },
        "workouts": {d: [] for d in DAYS_ORDER},
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


def make_anim(duration=280):
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
    page.title = "OLED"
    page.bgcolor = "#000000"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 440
    page.window.height = 880

    state = load_state()
    workout_data = state["workouts"]
    settings = state["settings"]

    current_day = "ПН"
    active_view = "workouts"  # "workouts", "catalog", "detail", "settings"
    selected_ex_idx = None

    def get_theme():
        t_name = settings.get("theme", "Stealth Monochrome")
        return THEMES.get(t_name, THEMES["Stealth Monochrome"])

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
            animate=make_anim(260),
            on_click=on_click,
        )

    glow_top = ft.Container(
        width=260, height=260, left=-90, top=20, border_radius=130, animate=make_anim(500)
    )
    glow_bottom = ft.Container(
        width=300, height=300, right=-100, bottom=50, border_radius=150, animate=make_anim(500)
    )

    main_body = ft.Column(expand=True, spacing=12)

    def sync_glows():
        theme = get_theme()
        is_abyss = settings.get("glass_mode") == "abyss"
        glow_top.bgcolor = "#04FFFFFF" if is_abyss else theme["glow1"]
        glow_bottom.bgcolor = "#03FFFFFF" if is_abyss else theme["glow2"]

    def select_day(day):
        nonlocal current_day, active_view
        current_day = day
        active_view = "workouts"
        rebuild_ui()

    def switch_view(view_name):
        nonlocal active_view
        active_view = view_name
        rebuild_ui()

    def open_exercise_detail(idx):
        nonlocal selected_ex_idx, active_view
        selected_ex_idx = idx
        active_view = "detail"
        rebuild_ui()

    def add_from_catalog(item):
        w = item.get("default_w", "40")
        new_ex = {
            "name": item["name"],
            "svg": item["svg"],
            "done": False,
            "sets_data": [
                {"weight": str(w), "reps": "10", "done": False},
                {"weight": str(w), "reps": "10", "done": False},
                {"weight": str(w), "reps": "10", "done": False},
                {"weight": str(w), "reps": "10", "done": False},
            ],
        }
        workout_data[current_day].append(new_ex)
        save_state(state)
        open_exercise_detail(len(workout_data[current_day]) - 1)

    def toggle_exercise_done(day, idx):
        ex = workout_data[day][idx]
        new_state = not ex.get("done", False)
        ex["done"] = new_state
        for s in ex.get("sets_data", []):
            s["done"] = new_state
        save_state(state)
        rebuild_ui()

    def delete_exercise(day, idx):
        workout_data[day].pop(idx)
        save_state(state)
        rebuild_ui()

    def reset_day_progress(e):
        for ex in workout_data[current_day]:
            ex["done"] = False
            for s in ex.get("sets_data", []):
                s["done"] = False
        save_state(state)
        rebuild_ui()

    def change_theme(theme_name):
        settings["theme"] = theme_name
        save_state(state)
        rebuild_ui()

    def change_glass_mode(mode_name):
        settings["glass_mode"] = mode_name
        save_state(state)
        rebuild_ui()

    # Экран 1: Главный экран дня недели
    def build_workouts_view():
        theme = get_theme()
        accent = theme["accent"]

        day_tabs = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=6)
        for day in DAYS_ORDER:
            is_sel = day == current_day
            has_ex = len(workout_data.get(day, [])) > 0
            day_tabs.controls.append(
                ft.Container(
                    on_click=lambda e, d=day: select_day(d),
                    animate=make_anim(240),
                    width=48,
                    height=46,
                    border_radius=15,
                    bgcolor=accent if is_sel else ("#12FFFFFF" if has_ex else "#06FFFFFF"),
                    border=make_border(1.2, accent if is_sel else "#22FFFFFF"),
                    alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text(
                                day,
                                size=12,
                                weight=ft.FontWeight.W_900,
                                color="#000000" if is_sel else "#FFFFFF",
                            ),
                            ft.Container(
                                width=4,
                                height=4,
                                border_radius=2,
                                bgcolor="#000000" if is_sel else (accent if has_ex else "transparent"),
                            ),
                        ],
                    ),
                )
            )

        day_exercises = workout_data.get(current_day, [])
        total = len(day_exercises)
        done_count = sum(1 for ex in day_exercises if ex.get("done", False))
        progress = done_count / total if total > 0 else 0
        pct = int(progress * 100)

        progress_card = ios26_glass(
            padding=15,
            radius=22,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        f"{DAYS_FULL.get(current_day, current_day).upper()} • ПРОГРАММА",
                                        size=11,
                                        weight=ft.FontWeight.W_900,
                                        color="#75FFFFFF",
                                    ),
                                    ft.Text(
                                        f"ВЫПОЛНЕНО: {done_count} ИЗ {total} ({pct}%)",
                                        size=14,
                                        weight=ft.FontWeight.W_900,
                                        color=accent,
                                    ),
                                ],
                            ),
                            ft.Container(
                                on_click=reset_day_progress,
                                padding=make_padding(12, 6, 12, 6),
                                border_radius=12,
                                bgcolor="#14FFFFFF",
                                border=make_border(1, "#24FFFFFF"),
                                content=ft.Text("СБРОС", size=11, weight=ft.FontWeight.W_900, color=accent),
                            ),
                        ],
                    ),
                    ft.ProgressBar(
                        value=progress,
                        color=accent,
                        bgcolor="#14FFFFFF",
                        height=6,
                        border_radius=3,
                    ),
                ],
            ),
        )

        ex_list = ft.Column(spacing=10, scroll=ft.ScrollMode.HIDDEN, expand=True)

        if total == 0:
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
                                f"{DAYS_FULL.get(current_day, '').upper()} — ПУСТО",
                                size=15,
                                weight=ft.FontWeight.W_900,
                                color="#FFFFFF",
                            ),
                            ft.Text(
                                "Нажмите сюда или на «+», чтобы выбрать тренажеры и упражнения из списка с картинками",
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color="#80FFFFFF",
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                )
            )

        for idx, ex in enumerate(day_exercises):
            is_done = ex.get("done", False)
            sets_data = ex.get("sets_data", [])
            sets_count = len(sets_data)
            done_sets = sum(1 for s in sets_data if s.get("done", False))
            max_w = max([float(str(s.get("weight", 0)).replace(",", ".") or 0) for s in sets_data], default=0)
            w_str = str(int(max_w) if max_w.is_integer() else max_w)
            reps_preview = "/".join(str(s.get("reps", 10)) for s in sets_data[:4])

            svg_key = ex.get("svg") or CATALOG_MAP.get(ex["name"], {}).get("svg", "bench")

            check_circle = ft.Container(
                width=28,
                height=28,
                border_radius=9,
                animate=make_anim(240),
                bgcolor=accent if is_done else "#08FFFFFF",
                border=make_border(1.5, accent if is_done else "#38FFFFFF"),
                alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
                on_click=lambda e, d=current_day, i=idx: toggle_exercise_done(d, i),
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

            info_area = ft.Container(
                expand=True,
                on_click=lambda e, i=idx: open_exercise_detail(i),
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text(
                            ex["name"],
                            size=14,
                            weight=ft.FontWeight.W_900,
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
                                        weight=ft.FontWeight.W_900,
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
                                        weight=ft.FontWeight.W_900,
                                        color=theme["secondary"],
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
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
                        on_click=lambda e, d=current_day, i=idx: delete_exercise(d, i),
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

        return [day_tabs, progress_card, ex_list]

    # Экран 2: Каталог тренажеров и упражнений с картинками (открывается по "+")
    def build_catalog_view():
        theme = get_theme()
        accent = theme["accent"]

        cat_col = ft.Column(spacing=12, scroll=ft.ScrollMode.HIDDEN, expand=True)

        cat_col.controls.append(
            ft.Text(
                f"ВЫБЕРИТЕ ТРЕНАЖЕР ДЛЯ ДНЯ: {DAYS_FULL.get(current_day, current_day).upper()}",
                size=11,
                weight=ft.FontWeight.W_900,
                color=accent,
            )
        )

        for group in EXERCISE_CATALOG:
            cat_col.controls.append(
                ft.Container(
                    padding=make_padding(0, 6, 0, 2),
                    content=ft.Text(
                        group["category"].upper(),
                        size=12,
                        weight=ft.FontWeight.W_900,
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
                                    ft.Text(
                                        item["name"],
                                        size=14,
                                        weight=ft.FontWeight.W_900,
                                        color="#FFFFFF",
                                    ),
                                    ft.Text(
                                        item["tip"],
                                        size=11,
                                        weight=ft.FontWeight.W_600,
                                        color="#75FFFFFF",
                                        max_lines=2,
                                    ),
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

        return [cat_col]

    # Экран 3: Настройка каждого подхода отдельно (вес + повторы на каждый подход)
    def build_exercise_detail_view():
        theme = get_theme()
        accent = theme["accent"]

        day_list = workout_data.get(current_day, [])
        if selected_ex_idx is None or selected_ex_idx >= len(day_list):
            switch_view("workouts")
            return []

        ex = day_list[selected_ex_idx]
        if "sets_data" not in ex or not ex["sets_data"]:
            ex["sets_data"] = [
                {"weight": "50", "reps": "10", "done": False} for _ in range(4)
            ]

        cat_info = CATALOG_MAP.get(ex["name"], {})
        svg_key = ex.get("svg") or cat_info.get("svg", "bench")
        tip_text = cat_info.get("tip", "Выполняйте движение подконтрольно и без рывков.")

        def sync_done_status():
            sets_list = ex["sets_data"]
            ex["done"] = len(sets_list) > 0 and all(s.get("done", False) for s in sets_list)
            save_state(state)

        def change_set_weight(s_idx, delta):
            s = ex["sets_data"][s_idx]
            try:
                cur = float(str(s.get("weight", "0")).replace(",", "."))
                nv = max(0.0, cur + delta)
                s["weight"] = str(int(nv) if nv.is_integer() else round(nv, 1))
            except Exception:
                s["weight"] = "20"
            save_state(state)
            rebuild_ui()

        def on_weight_typed(e, s_idx):
            ex["sets_data"][s_idx]["weight"] = e.control.value
            save_state(state)

        def change_set_reps(s_idx, delta):
            s = ex["sets_data"][s_idx]
            try:
                cur = int(str(s.get("reps", "10")).strip())
                nv = max(1, cur + delta)
                s["reps"] = str(nv)
            except Exception:
                s["reps"] = "10"
            save_state(state)
            rebuild_ui()

        def on_reps_typed(e, s_idx):
            ex["sets_data"][s_idx]["reps"] = e.control.value
            save_state(state)

        def toggle_set_done(s_idx):
            ex["sets_data"][s_idx]["done"] = not ex["sets_data"][s_idx].get("done", False)
            sync_done_status()
            rebuild_ui()

        def add_new_set(e):
            last_w = ex["sets_data"][-1]["weight"] if ex["sets_data"] else "50"
            last_r = ex["sets_data"][-1]["reps"] if ex["sets_data"] else "10"
            ex["sets_data"].append({"weight": str(last_w), "reps": str(last_r), "done": False})
            sync_done_status()
            rebuild_ui()

        def remove_set(s_idx):
            if len(ex["sets_data"]) > 1:
                ex["sets_data"].pop(s_idx)
                sync_done_status()
                rebuild_ui()

        detail_col = ft.Column(spacing=12, scroll=ft.ScrollMode.HIDDEN, expand=True)

        # Карточка с иллюстрацией и техникой
        detail_col.controls.append(
            ios26_glass(
                padding=14,
                radius=24,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("ТЕХНИКА ТРЕНАЖЕРА", size=10, weight=ft.FontWeight.W_900, color="#75FFFFFF"),
                                ft.Text(DAYS_FULL.get(current_day, current_day).upper(), size=10, weight=ft.FontWeight.W_900, color=accent),
                            ],
                        ),
                        render_svg(svg_key, width=240, height=125),
                        ft.Text(
                            ex["name"].upper(),
                            size=16,
                            weight=ft.FontWeight.W_900,
                            color="#FFFFFF",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            tip_text,
                            size=11,
                            weight=ft.FontWeight.W_600,
                            color="#90FFFFFF",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
            )
        )

        # Заголовок таблицы подходов
        detail_col.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("НАСТРОЙКА КАЖДОГО ПОДХОДА", size=11, weight=ft.FontWeight.W_900, color="#80FFFFFF"),
                    ft.Container(
                        on_click=add_new_set,
                        padding=make_padding(12, 6, 12, 6),
                        border_radius=12,
                        bgcolor=accent,
                        content=ft.Text("+ ДОБАВИТЬ ПОДХОД", size=10, weight=ft.FontWeight.W_900, color="#000000"),
                    ),
                ],
            )
        )

        # Список подходов с удобными кнопками настройки веса (КГ) и повторений (ПОВТ)
        for s_idx, s_data in enumerate(ex["sets_data"]):
            s_done = s_data.get("done", False)

            set_card = ios26_glass(
                padding=12,
                radius=20,
                is_highlighted=s_done,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Container(
                                            width=26,
                                            height=26,
                                            border_radius=8,
                                            bgcolor=accent if s_done else "#14FFFFFF",
                                            alignment=ft.Alignment(0, 0) if hasattr(ft, "Alignment") else None,
                                            on_click=lambda e, i=s_idx: toggle_set_done(i),
                                            content=ft.Icon(
                                                ft.Icons.CHECK_ROUNDED,
                                                size=16,
                                                color="#000000" if s_done else "#60FFFFFF",
                                            ),
                                        ),
                                        ft.Text(
                                            f"ПОДХОД #{s_idx + 1}",
                                            size=13,
                                            weight=ft.FontWeight.W_900,
                                            color=accent if s_done else "#FFFFFF",
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Container(
                                            on_click=lambda e, i=s_idx: toggle_set_done(i),
                                            padding=make_padding(10, 4, 10, 4),
                                            border_radius=8,
                                            bgcolor=accent if s_done else "#14FFFFFF",
                                            content=ft.Text(
                                                "ГОТОВО" if s_done else "ОТМЕТИТЬ",
                                                size=10,
                                                weight=ft.FontWeight.W_900,
                                                color="#000000" if s_done else "#FFFFFF",
                                            ),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                            icon_size=17,
                                            icon_color="#50FFFFFF",
                                            on_click=lambda e, i=s_idx: remove_set(i),
                                        )
                                        if len(ex["sets_data"]) > 1
                                        else ft.Container(),
                                    ],
                                ),
                            ],
                        ),
                        # Строка настройки КГ и ПОВТОРЕНИЙ (совместимая с Flet 1.0)
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                # Блок Веса (КГ)
                                ft.Container(
                                    padding=make_padding(6, 5, 6, 5),
                                    border_radius=14,
                                    bgcolor="#0DFFFFFF",
                                    border=make_border(1, "#20FFFFFF"),
                                    content=ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Container(
                                                on_click=lambda e, i=s_idx: change_set_weight(i, -2.5),
                                                padding=make_padding(8, 8, 8, 8),
                                                border_radius=10,
                                                bgcolor="#1AFFFFFF",
                                                content=ft.Text("-2.5", size=11, weight=ft.FontWeight.W_900, color="#FFFFFF"),
                                            ),
                                            ft.Column(
                                                spacing=0,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.TextField(
                                                        value=str(s_data.get("weight", "50")),
                                                        width=62,
                                                        height=34,
                                                        content_padding=make_padding(2, 2, 2, 2),
                                                        text_align=ft.TextAlign.CENTER,
                                                        border_color="transparent",
                                                        text_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_900, color="#FFFFFF"),
                                                        on_change=lambda e, i=s_idx: on_weight_typed(e, i),
                                                    ),
                                                    ft.Text("КГ", size=9, weight=ft.FontWeight.W_900, color="#65FFFFFF"),
                                                ],
                                            ),
                                            ft.Container(
                                                on_click=lambda e, i=s_idx: change_set_weight(i, 2.5),
                                                padding=make_padding(8, 8, 8, 8),
                                                border_radius=10,
                                                bgcolor=accent,
                                                content=ft.Text("+2.5", size=11, weight=ft.FontWeight.W_900, color="#000000"),
                                            ),
                                        ],
                                    ),
                                ),
                                # Блок Повторений (ПОВТ)
                                ft.Container(
                                    padding=make_padding(6, 5, 6, 5),
                                    border_radius=14,
                                    bgcolor="#0DFFFFFF",
                                    border=make_border(1, "#20FFFFFF"),
                                    content=ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Container(
                                                on_click=lambda e, i=s_idx: change_set_reps(i, -1),
                                                padding=make_padding(9, 8, 9, 8),
                                                border_radius=10,
                                                bgcolor="#1AFFFFFF",
                                                content=ft.Text("-1", size=11, weight=ft.FontWeight.W_900, color="#FFFFFF"),
                                            ),
                                            ft.Column(
                                                spacing=0,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.TextField(
                                                        value=str(s_data.get("reps", "10")),
                                                        width=56,
                                                        height=34,
                                                        content_padding=make_padding(2, 2, 2, 2),
                                                        text_align=ft.TextAlign.CENTER,
                                                        border_color="transparent",
                                                        text_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_900, color=accent),
                                                        on_change=lambda e, i=s_idx: on_reps_typed(e, i),
                                                    ),
                                                    ft.Text("ПОВТ", size=9, weight=ft.FontWeight.W_900, color="#65FFFFFF"),
                                                ],
                                            ),
                                            ft.Container(
                                                on_click=lambda e, i=s_idx: change_set_reps(i, 1),
                                                padding=make_padding(9, 8, 9, 8),
                                                border_radius=10,
                                                bgcolor=accent,
                                                content=ft.Text("+1", size=11, weight=ft.FontWeight.W_900, color="#000000"),
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            )
            detail_col.controls.append(set_card)

        return [detail_col]

    # Экран 4: Меню настроек
    def build_settings_view():
        theme = get_theme()
        accent = theme["accent"]
        current_theme_name = settings.get("theme", "Stealth Monochrome")
        current_glass_mode = settings.get("glass_mode", "ios26")

        settings_list = ft.Column(spacing=12, scroll=ft.ScrollMode.HIDDEN, expand=True)

        settings_list.controls.append(
            ft.Text("ОПТИКА СТЕКЛА (iOS 26)", size=12, weight=ft.FontWeight.W_900, color="#70FFFFFF")
        )

        glass_modes = [
            ("ios26", "Liquid Glass iOS 26", "Глубокое преломление + зеркальный блик грани"),
            ("abyss", "Pitch Black Abyss", "Экстремально темное стекло 98.5% OLED Black"),
        ]

        for mode_key, title, subtitle in glass_modes:
            is_active = current_glass_mode == mode_key
            settings_list.controls.append(
                ios26_glass(
                    padding=15,
                    radius=22,
                    is_highlighted=is_active,
                    on_click=lambda e, m=mode_key: change_glass_mode(m),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=3,
                                controls=[
                                    ft.Text(title, size=14, weight=ft.FontWeight.W_900, color="#FFFFFF"),
                                    ft.Text(subtitle, size=11, weight=ft.FontWeight.W_600, color="#80FFFFFF"),
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

        settings_list.controls.append(
            ft.Container(
                padding=make_padding(0, 6, 0, 0),
                content=ft.Text("СТЕЛС-ТЕМЫ (MONOCHROME SERIES)", size=12, weight=ft.FontWeight.W_900, color="#70FFFFFF"),
            )
        )

        for t_name, t_vals in THEMES.items():
            is_sel = t_name == current_theme_name
            settings_list.controls.append(
                ios26_glass(
                    padding=15,
                    radius=22,
                    is_highlighted=is_sel,
                    on_click=lambda e, tn=t_name: change_theme(tn),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=14,
                                controls=[
                                    ft.Container(
                                        width=26,
                                        height=26,
                                        border_radius=13,
                                        bgcolor=t_vals["accent"],
                                        border=make_border(2, "#FFFFFF" if is_sel else "#30FFFFFF"),
                                    ),
                                    ft.Text(
                                        t_name.upper(),
                                        size=13,
                                        weight=ft.FontWeight.W_900,
                                        color="#FFFFFF",
                                    ),
                                ],
                            ),
                            ft.Text(
                                "АКТИВНА" if is_sel else "ВЫБРАТЬ",
                                size=11,
                                weight=ft.FontWeight.W_900,
                                color=t_vals["accent"] if is_sel else "#55FFFFFF",
                            ),
                        ],
                    ),
                )
            )

        return [settings_list]

    def rebuild_ui():
        sync_glows()
        theme = get_theme()
        accent = theme["accent"]

        titles = {
            "workouts": "OLED",
            "catalog": "КАТАЛОГ",
            "detail": "ПОДХОДЫ",
            "settings": "НАСТРОЙКИ",
        }

        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            titles.get(active_view, "OLED"),
                            size=28,
                            weight=ft.FontWeight.W_900,
                            color="#FFFFFF",
                        ),
                        ft.Text(
                            f"{settings.get('theme', '').upper()}",
                            size=10,
                            weight=ft.FontWeight.W_800,
                            color=theme["secondary"],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        ios26_glass(
                            padding=4,
                            radius=16,
                            is_highlighted=(active_view == "catalog"),
                            content=ft.IconButton(
                                icon=ft.Icons.ADD_ROUNDED,
                                icon_color=accent,
                                on_click=lambda e: switch_view("catalog"),
                            ),
                        )
                        if active_view == "workouts"
                        else ft.Container(),
                        ios26_glass(
                            padding=4,
                            radius=16,
                            is_highlighted=(active_view != "workouts"),
                            content=ft.IconButton(
                                icon=ft.Icons.TUNE_ROUNDED
                                if active_view == "workouts"
                                else ft.Icons.ARROW_BACK_ROUNDED,
                                icon_color=accent,
                                on_click=lambda e: switch_view(
                                    "settings" if active_view == "workouts" else "workouts"
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        )

        # Нижний док только с разделом ТРЕНИРОВКИ
        bottom_dock = ios26_glass(
            padding=8,
            radius=26,
            on_click=lambda e: switch_view("workouts"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        animate=make_anim(250),
                        padding=make_padding(36, 10, 36, 10),
                        border_radius=18,
                        bgcolor=accent if active_view == "workouts" else "#14FFFFFF",
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(
                                    ft.Icons.FITNESS_CENTER_ROUNDED,
                                    size=18,
                                    color="#000000" if active_view == "workouts" else "#FFFFFF",
                                ),
                                ft.Text(
                                    "ТРЕНИРОВКИ",
                                    size=12,
                                    weight=ft.FontWeight.W_900,
                                    color="#000000" if active_view == "workouts" else "#FFFFFF",
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

        if active_view == "workouts":
            view_controls = build_workouts_view()
        elif active_view == "catalog":
            view_controls = build_catalog_view()
        elif active_view == "detail":
            view_controls = build_exercise_detail_view()
        else:
            view_controls = build_settings_view()

        main_body.controls = [header, *view_controls, bottom_dock]
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
    ft.run(main)
else:
    ft.app(target=main)