import logging
import re
import os
import requests
import random
import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def setup_logging(level=logging.INFO):
    """Configura el sistema de logs para el scraping y otras herramientas."""
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=level,
        datefmt="%H:%M:%S"
    )
    logging.info("✅ Logging configurado correctamente.")

def clean_text(text: str) -> str:
    """Limpia texto HTML o strings con notas, corchetes, paréntesis, etc."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ---------------------------
# Tool: Hora actual
# ---------------------------
def get_current_time() -> str:
    """Devuelve la hora y fecha actual en formato legible."""
    now = datetime.datetime.now()
    return f"La hora actual es {now.strftime('%H:%M:%S')} del {now.strftime('%d/%m/%Y')}."

# ---------------------------
# Tool: OpenWeather (clima real)
# ---------------------------
def get_weather(city: str) -> str:
    """Obtiene el clima actual de una ciudad usando OpenWeather API."""
    if not OPENWEATHER_API_KEY:
        return "❌ Falta la variable de entorno OPENWEATHER_API_KEY."

    city = city.strip()
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={OPENWEATHER_API_KEY}&lang=es&units=metric"
        )
        r = requests.get(url, timeout=8)
        data = r.json()

        if data.get("cod") != 200:
            return f"⚠️ No se pudo obtener el clima para '{city}': {data.get('message', 'Error desconocido')}."

        weather = data["weather"][0]
        main = data["main"]

        description = weather["description"].capitalize()
        temp = main["temp"]
        feels_like = main.get("feels_like", temp)
        humidity = main.get("humidity", "N/A")

        # Emoji según el tipo de clima
        desc_l = description.lower()
        if "lluv" in desc_l:
            emoji = "🌧️"
        elif "nublado" in desc_l or "nubes" in desc_l:
            emoji = "☁️"
        elif "sol" in desc_l or "despejado" in desc_l:
            emoji = "☀️"
        elif "nieve" in desc_l:
            emoji = "❄️"
        elif "torment" in desc_l:
            emoji = "⛈️"
        else:
            emoji = "🌤️"

        return (
            f"{emoji} Clima en {city}:\n"
            f"- {description}\n"
            f"- Temperatura: {temp}°C (sensación: {feels_like}°C)\n"
            f"- Humedad: {humidity}%"
        )
    except Exception as e:
        return f"⚠️ Error al obtener datos del clima: {e}"

# ---------------------------
# Tool: Dato curioso
# ---------------------------
def generate_fun_fact() -> str:
    """Devuelve un dato curioso aleatorio sobre los Juegos Olímpicos."""
    facts = [
        "Los primeros Juegos Olímpicos modernos se celebraron en Atenas en 1896.",
        "El logo olímpico con los cinco anillos representa los cinco continentes unidos.",
        "En 1900, las mujeres participaron por primera vez en los Juegos Olímpicos.",
        "Los Juegos de Tokio 2020 se celebraron en 2021 debido a la pandemia.",
        "Michael Phelps tiene el récord de más medallas olímpicas: 28 en total.",
        "El fuego olímpico se inspira en las antiguas ceremonias de Olimpia, Grecia.",
        "Solo cinco países han participado en todos los Juegos Olímpicos modernos.",
        "En los Juegos de 1900, el croquet fue deporte olímpico.",
        "Los primeros Juegos Olímpicos de invierno se celebraron en 1924 en Chamonix, Francia.",
        "En 1960, Roma fue la primera sede olímpica televisada en directo.",
        "Los anillos fueron diseñados en 1913 por Pierre de Coubertin.",
        "En París 1900 hubo deportes inusuales como el croquet y el tiro a las palomas vivas.",
        "Usain Bolt ganó oro en 100 m y 200 m en tres Juegos consecutivos.",
        "En Roma 1960 se usó por primera vez foto-finish.",
        "En Tokio 2020 las medallas se fabricaron con materiales reciclados de dispositivos electrónicos."
    ]
    return random.choice(facts)

# ---------------------------
# Helper: Alias de países
# ---------------------------
COUNTRY_ALIASES = {
    # 🌍 América
    "eeuu": "United States", "ee. uu.": "United States", "estados unidos": "United States", "usa": "United States",
    "canadá": "Canada", "canada": "Canada",
    "méxico": "Mexico", "mexico": "Mexico",
    "cuba": "Cuba", "puerto rico": "Puerto Rico",
    "república dominicana": "Dominican Republic", "dominicana": "Dominican Republic",
    "guatemala": "Guatemala", "honduras": "Honduras", "el salvador": "El Salvador", "nicaragua": "Nicaragua",
    "costa rica": "Costa Rica", "panamá": "Panama", "panama": "Panama",
    "colombia": "Colombia", "venezuela": "Venezuela", "ecuador": "Ecuador", "perú": "Peru", "peru": "Peru",
    "bolivia": "Bolivia", "paraguay": "Paraguay", "uruguay": "Uruguay", "argentina": "Argentina", "chile": "Chile",
    "brasil": "Brazil", "brasilia": "Brazil",

    # 🌍 Europa Occidental
    "españa": "Spain", "espana": "Spain",
    "portugal": "Portugal", "francia": "France", "alemania": "Germany", "suiza": "Switzerland",
    "bélgica": "Belgium", "belgica": "Belgium", "luxemburgo": "Luxembourg",
    "reino unido": "Great Britain", "gran bretaña": "Great Britain", "inglaterra": "Great Britain", "uk": "Great Britain",
    "irlanda": "Ireland", "italia": "Italy", "san marino": "San Marino", "mónaco": "Monaco", "monaco": "Monaco",

    # 🌍 Europa del Este
    "rusia": "ROC", "federación rusa": "ROC", "rusia olímpica": "ROC", "urss": "ROC", "roc": "ROC",
    "ucrania": "Ukraine", "bielorrusia": "Belarus", "polonia": "Poland", "república checa": "Czech Republic",
    "chequia": "Czech Republic", "eslovaquia": "Slovakia", "hungría": "Hungary", "hungria": "Hungary",
    "rumanía": "Romania", "rumania": "Romania", "bulgaria": "Bulgaria", "serbia": "Serbia",
    "croacia": "Croatia", "bosnia": "Bosnia and Herzegovina", "eslovenia": "Slovenia", "macedonia": "North Macedonia",
    "kosovo": "Kosovo", "albania": "Albania", "moldavia": "Moldova", "georgia": "Georgia", "armenia": "Armenia",

    # 🌍 Europa del Norte
    "suecia": "Sweden", "noruega": "Norway", "dinamarca": "Denmark", "finlandia": "Finland", "islandia": "Iceland",
    "letonia": "Latvia", "lituania": "Lithuania", "estonia": "Estonia",

    # 🌍 África
    "sudáfrica": "South Africa", "sudafrica": "South Africa",
    "nigeria": "Nigeria", "kenia": "Kenya", "etiopía": "Ethiopia", "etiopia": "Ethiopia",
    "egipto": "Egypt", "marruecos": "Morocco", "argelia": "Algeria", "túnez": "Tunisia", "tunez": "Tunisia",
    "ghana": "Ghana", "camerún": "Cameroon", "camerun": "Cameroon", "senegal": "Senegal", "uganda": "Uganda",
    "zimbabue": "Zimbabwe", "botsuana": "Botswana", "mozambique": "Mozambique",
    "angola": "Angola", "zambia": "Zambia", "malí": "Mali", "mali": "Mali", "etiopia": "Ethiopia",

    # 🌍 Asia Occidental y Central
    "turquía": "Turkey", "turquia": "Turkey", "chipre": "Cyprus", "israel": "Israel", "jordania": "Jordan",
    "líbanon": "Lebanon", "libano": "Lebanon", "siria": "Syria", "irak": "Iraq", "iraq": "Iraq",
    "irán": "Iran", "iran": "Iran", "arabia saudita": "Saudi Arabia", "qatar": "Qatar",
    "emiratos árabes unidos": "United Arab Emirates", "emiratos arabes unidos": "United Arab Emirates",
    "kuwait": "Kuwait", "bahrein": "Bahrain", "oman": "Oman", "yemen": "Yemen",
    "kazajistán": "Kazakhstan", "kazajistan": "Kazakhstan", "uzbekistán": "Uzbekistan", "uzbekistan": "Uzbekistan",
    "kirguistán": "Kyrgyzstan", "kirguistan": "Kyrgyzstan", "tayikistán": "Tajikistan", "tayikistan": "Tajikistan",

    # 🌍 Asia Oriental
    "china": "China", "hong kong": "Hong Kong", "macao": "Macau", "taiwán": "Chinese Taipei", "taiwan": "Chinese Taipei",
    "corea del sur": "South Korea", "corea del norte": "North Korea", "japón": "Japan", "japon": "Japan",
    "mongolia": "Mongolia",

    # 🌍 Asia Meridional y Sudeste Asiático
    "india": "India", "pakistán": "Pakistan", "pakistan": "Pakistan",
    "bangladés": "Bangladesh", "bangladesh": "Bangladesh", "nepal": "Nepal", "bután": "Bhutan", "maldivas": "Maldives",
    "sri lanka": "Sri Lanka", "myanmar": "Myanmar", "birmania": "Myanmar",
    "tailandia": "Thailand", "vietnam": "Vietnam", "laos": "Laos", "camboya": "Cambodia", "malasia": "Malaysia",
    "singapur": "Singapore", "indonesia": "Indonesia", "filipinas": "Philippines", "timor oriental": "Timor-Leste",

    # 🌍 Oceanía
    "australia": "Australia", "nueva zelanda": "New Zealand", "nueva zelandia": "New Zealand",
    "fiyi": "Fiji", "samoa": "Samoa", "tonga": "Tonga", "papúa nueva guinea": "Papua New Guinea",
    "papua nueva guinea": "Papua New Guinea", "islas cook": "Cook Islands",
    "islas salomón": "Solomon Islands", "micronesia": "Micronesia", "palau": "Palau",
    "kiribati": "Kiribati", "vanuatu": "Vanuatu", "nauru": "Nauru", "tuvalu": "Tuvalu",

    # 🌍 Otros / Territorios especiales
    "palestina": "Palestine", "hong-kong": "Hong Kong", "china taipei": "Chinese Taipei",
    "corea": "South Korea", "macedonia del norte": "North Macedonia",
}

def normalize_country(name: str) -> str:
    """Normaliza nombre de país usando aliases; si no hay alias devuelve title-case del original."""
    if not isinstance(name, str):
        return name
    key = name.strip().lower()
    return COUNTRY_ALIASES.get(key, name.strip().title())

# ---------------------------
# Tool: Comparar dos países (usa CSV)
# ---------------------------
def compare_countries(country1: str, country2: str, year: int) -> str:
    """
    Compara el rendimiento de dos países en un año.
    Retorna resumen con medallas y ranking de ambos y resumen del ganador.
    """
    csv_path = "./olympic_medals_2000_2024.csv"
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return "⚠️ No se encontró el archivo de datos olímpicos (olympic_medals_2000_2024.csv)."

    # Normalizar año y países
    try:
        year = int(year)
    except Exception:
        return "⚠️ Año inválido."

    c1 = normalize_country(country1)
    c2 = normalize_country(country2)

    subset = df[(df["year"] == year) & (df["country"].isin([c1, c2]))]

    if subset.empty or len(subset) < 2:
        return f"⚠️ No se encontraron datos de ambos países ({c1}, {c2}) en {year}."

    rows = subset.sort_values(by="rank", ascending=True)
    lines = []
    for _, row in rows.iterrows():
        lines.append(
            f"🏳️ **{row['country']}** — Oro: {int(row['gold'])}, Plata: {int(row['silver'])}, "
            f"Bronce: {int(row['bronze'])}, Total: {int(row['total'])} (Ranking: {int(row['rank'])})"
        )

    top = rows.iloc[0]
    summary = f"\n🏆 En {year}, **{top['country']}** obtuvo el mejor resultado."
    return "\n".join(lines) + summary
