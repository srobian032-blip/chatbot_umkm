import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# =============================
# PATH & KONFIGURASI
# =============================
BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "faq_toko.json"

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.3
)

# =============================
# HELPER: BERSIHKAN FORMAT
# =============================
def clean_text(text: str) -> str:
    if not text:
        return ""
    return (
        text
        .replace("<b>", "")
        .replace("</b>", "")
        .replace("*", "")
    )

# =============================
# FAQ DATABASE MATCHING
# =============================
def get_fallback_answer(user_message: str):
    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as f:
            faqs = json.load(f)

        text = user_message.lower()
        for faq in faqs:
            if any(kw in text for kw in faq.get("keywords", [])):
                return clean_text(faq.get("fakta_utama", ""))
    except Exception as e:
        print("FAQ Error:", e)

    return None

# =============================
# MAIN BOT LOGIC
# =============================
def get_bot_reply(user_message: str) -> str:
    if len(user_message.strip()) < 2:
        return "Halo Kak 😊 bisa dibantu apa?"

    # 1️⃣ Coba jawab dari database dulu
    faq_answer = get_fallback_answer(user_message)
    if faq_answer:
        return faq_answer

    salam = ["halo", "hai", "hi", "p", "assalamualaikum"]
    is_greeting = user_message.lower().strip() in salam

    try:
        logic_sapaan = (
            "Awali jawaban dengan sapaan ramah."
            if is_greeting
            else "Langsung ke jawaban tanpa sapaan."
        )

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                f"""
ROLE:
Kamu adalah **Customer Service & Admin Order UMKM Sulis Za Cake**.

Profil Usaha:
Sulis Za Cake bergerak di bidang **pembuatan kue custom dan produk kuliner rumahan**.

Peran utama kamu:
• Customer Service
• Admin Pemesanan Kue
• Konsultan Kue Custom

Gaya komunikasi:
• Bahasa Indonesia santai & ramah (gaya WhatsApp)
• Sopan, hangat, dan membantu
• Jawaban informatif, jelas, tidak bertele-tele
• Gunakan emoji secukupnya 🍰😊 (jangan berlebihan)

Fokus pembahasan:
• Kue ulang tahun custom
• Kue tart & dessert
• Snack & produk kuliner
• Ukuran, varian rasa, dan desain kue
• Harga & estimasi pengerjaan
• Cara pemesanan & pembayaran
• Jadwal produksi & pengambilan

Aturan penting:
• Jangan membahas topik di luar usaha
• Jangan menjawab politik, agama, atau hal sensitif
• Jangan mengarang harga, menu, atau janji waktu
• Jangan menggunakan HTML atau simbol aneh
• Jika informasi tidak ada di data → arahkan ke admin manusia

Aturan respons:
• Jika pelanggan hanya menyapa → balas dengan sapaan ramah
• Jika pelanggan bertanya → jawab langsung ke inti
• Jika pelanggan ingin pesan → jelaskan alur pemesanan
• Jika detail pesanan belum lengkap → minta klarifikasi dengan sopan
• Jika order custom → tanyakan ukuran, rasa, tema, tanggal

Tujuan utama:
Membantu pelanggan dengan cepat dan ramah agar mereka percaya dan nyaman memesan di **Sulis Za Cake**.

"""
            ),
            ("human", "{input}")
        ])

        chain = prompt | llm
        response = chain.invoke({"input": user_message})

        return clean_text(response.content)

    except Exception as e:
        print("AI Error:", e)
        return "Maaf kak, bisa dijelaskan lebih detail ya?"

