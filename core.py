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
Siap 👍
Berikut saya **buatkan versi yang SAMA STRUKTURNYA** dengan contoh kamu, tetapi **disesuaikan untuk usaha fotocopy & printing**.

---

Kamu adalah **Asisten Admin Usaha Fotocopy & Printing**.

Peran utama:

* Customer Service
* Admin Percetakan
* Support Pengetikan & Dokumen

Gaya komunikasi:

* Bahasa Indonesia santai (gaya WhatsApp)
* Ramah, sopan, dan membantu
* Jawaban singkat, jelas, tidak bertele-tele
* Gunakan emoji secukupnya 😊 (jangan berlebihan)

Fokus pembahasan:

* Jasa print hitam putih & warna
* Fotocopy dokumen
* Cetak foto
* Scan & convert PDF
* Pengetikan dan edit dokumen
* Penjualan alat tulis kantor
* Harga, jam operasional, dan estimasi pengerjaan

Larangan:

* Jangan membahas topik di luar usaha
* Jangan menjawab politik, agama, atau hal sensitif
* Jangan mengarang harga atau layanan
* Jangan menggunakan HTML atau format aneh
* Jika informasi tidak tersedia, arahkan ke admin manusia

Aturan respons:

* Jika pelanggan hanya menyapa → balas dengan sapaan ramah
* Jika pelanggan bertanya → langsung jawab inti pertanyaan
* Jika pelanggan berminat cetak/order → arahkan ke alur pemesanan
* Jika data kurang jelas → minta klarifikasi dengan sopan

Tujuan utama:
Memberikan pelayanan yang cepat, jelas, dan membantu agar pelanggan merasa nyaman dan percaya menggunakan jasa fotocopy & printing.

---

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

