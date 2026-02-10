import streamlit as st
import google-generativeai as genai

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Guru Bahasa Universal AI", page_icon="🌎", layout="wide")

# --- KONFIGURASI API ---
try:
    # Mengambil API Key dari Streamlit Secrets
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API Key tidak ditemukan! Pastikan sudah terisi di .streamlit/secrets.toml")
    st.stop()

model = genai.GenerativeModel("gemini-2.5-flash")

# --- SISTEM PENYIMPANAN SESSION ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} 

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- FUNGSI BUAT JUDUL OTOMATIS ---
def generate_chat_title(user_input):
    try:
        # Meminta Gemini membuat judul singkat berdasarkan topik pertama
        prompt_judul = f"Berikan judul chat maksimal 3 kata untuk topik: {user_input}. Balas hanya dengan judulnya saja."
        response = model.generate_content(prompt_judul)
        return response.text.strip()
    except:
        return "Percakapan Baru"

# --- SIDEBAR: RIWAYAT CHAT ---
with st.sidebar:
    st.title("🌍 Global Language Tutor")
    st.markdown("Belajar bahasa apa saja di dunia.")
    
    if st.button("+ Mulai Sesi Baru", use_container_width=True):
        st.session_state.current_chat_id = None
        st.rerun()

    st.write("---")
    st.subheader("Riwayat Belajar")
    
    # Menampilkan daftar riwayat berdasarkan judul otomatis
    for chat_id in st.session_state.all_chats.keys():
        if st.button(f"📖 {chat_id}", key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# --- TAMPILAN UTAMA ---
st.title("🎓 Guru Bahasa Universal")
st.markdown("""
Selamat datang! Kamu bisa bertanya tentang bahasa apa pun di dunia. 
Guru AI akan membantu menerjemahkan, menjelaskan tata bahasa, hingga budaya di balik bahasa tersebut.
""")

# Menampilkan chat yang sedang aktif
if st.session_state.current_chat_id:
    messages = st.session_state.all_chats[st.session_state.current_chat_id]
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
else:
    st.info("Ayo mulai! Tanyakan kalimat dalam bahasa Jerman, Jepang, Arab, atau apa pun!")

# --- LOGIKA INPUT DAN AI ---
if prompt := st.chat_input("Tanya guru bahasa di sini..."):
    
    # 1. Jika sesi baru, buatkan judul otomatis
    if st.session_state.current_chat_id is None:
        with st.spinner("Membuat judul sesi..."):
            new_title = generate_chat_title(prompt)
            # Cek jika judul sudah ada agar tidak error
            if new_title in st.session_state.all_chats:
                new_title = f"{new_title} ({len(st.session_state.all_chats)})"
            
            st.session_state.all_chats[new_title] = []
            st.session_state.current_chat_id = new_title

    # 2. Simpan pesan user ke riwayat
    st.session_state.all_chats[st.session_state.current_chat_id].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Panggil Guru AI
    with st.chat_message("assistant"):
        with st.spinner("Guru sedang merespons..."):
            try:
                # Instruksi Sistem yang Luas (Universal)
                instruction = (
                    "Kamu adalah 'Guru Bahasa Universal'. Kamu menguasai seluruh bahasa di dunia. "
                    "Tugasmu: Menerjemahkan, menjelaskan grammar/tata bahasa, memberikan cara pengucapan (phonetic), "
                    "dan memberikan konteks budaya. Selalu bersikap ramah, edukatif, dan bantu siswa "
                    "sampai mereka benar-benar paham bahasa yang sedang ditanyakan."
                )
                
                # Mengambil konteks chat agar nyambung
                history = st.session_state.all_chats[st.session_state.current_chat_id]
                response = model.generate_content(f"{instruction}\n\nPercakapan sejauh ini:\n{history}\n\nPertanyaan Siswa: {prompt}")
                
                answer = response.text
                st.markdown(answer)
                
                # Simpan jawaban AI
                st.session_state.all_chats[st.session_state.current_chat_id].append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Sistem Guru sedang gangguan: {e}")
    
    # Refresh agar perubahan judul di sidebar terlihat
    st.rerun()
