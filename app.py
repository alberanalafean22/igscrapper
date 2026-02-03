import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import quote_plus
import io

# ===================== CONFIG =====================
st.set_page_config(
    page_title="IG Profiler - BPS1372",
    page_icon="📸",
    layout="wide"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
/* Global */
body {
    background-color: #0e1117;
    color: #fafafa;
    font-family: 'Inter', sans-serif;
}

/* Title Header (Tanpa Logo) */
.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
    background: -webkit-linear-gradient(#833ab4, #fd1d1d, #fcb045);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle {
    font-size: 16px;
    color: #9aa0a6;
    margin-bottom: 30px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #020617);
    border-right: 1px solid #1f2937;
}

/* Button */
.stButton > button {
    background: linear-gradient(90deg, #833ab4, #fd1d1d);
    color: white;
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    border: none;
    width: 100%;
}

/* Footer */
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #020617;
    color: #9ca3af;
    text-align: center;
    padding: 8px;
    font-size: 13px;
    border-top: 1px solid #1f2937;
    z-index: 100;
}
</style>
""", unsafe_allow_html=True)

# ===================== FUNGSI SCRAPING =====================
def scrape_instagram_profiles(keyword, pages=1):
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    search_query = f"site:instagram.com {keyword}"
    
    for page in range(0, pages):
        start = page * 10
        url = f"https://www.google.com/search?q={quote_plus(search_query)}&start={start}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for g in soup.find_all('div', class_='tF2Cxc'):
                title = g.find('h3').text if g.find('h3') else "N/A"
                url_ig = g.find('a')['href'] if g.find('a') else ""
                snippet = g.find('div', class_='VwiC3b').text if g.find('div', class_='VwiC3b') else ""
                
                if "instagram.com/" in url_ig and "/p/" not in url_ig:
                    results.append({
                        "Nama Profil": title.split(" (@")[0],
                        "Username IG": url_ig.rstrip('/').split('/')[-1],
                        "Link URL IG": url_ig,
                        "Bio / Deskripsi": snippet,
                        "Keyword Terkait": keyword
                    })
            time.sleep(2)
        except:
            continue
            
    return results

# ===================== SIDEBAR =====================
with st.sidebar:
    st.header("⚙️ Pengaturan")
    keyword = st.text_input("Keyword", placeholder="Contoh: UMKM Solok")
    jml_halaman = st.number_input("Jumlah Halaman", min_value=1, max_value=10, value=2)
    start_button = st.button("🚀 Mulai Scraping")
    st.markdown("---")
    st.info("Aplikasi akan mencari profil Instagram publik yang terindeks secara global.")

# ===================== MAIN UI =====================
st.markdown('<div class="main-title">IG Data Discovery</div>', unsafe_allow_html=True)
st.markdown("""
<div class='subtitle'>
Scraping informasi profil Instagram (Username, Bio, dan Link) berdasarkan keyword untuk kebutuhan pendataan.
</div>
""", unsafe_allow_html=True)

# ===================== PROCESS =====================
if start_button:
    if not keyword:
        st.warning("⚠️ Mohon isi keyword terlebih dahulu.")
    else:
        status = st.empty()
        status.info(f"🔍 Mencari data untuk: **{keyword}**...")
        
        data_ig = scrape_instagram_profiles(keyword, jml_halaman)
        
        if data_ig:
            df = pd.DataFrame(data_ig)
            status.success(f"✅ Berhasil menemukan {len(df)} profil.")
            
            st.dataframe(df, use_container_width=True)

            # Export Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data Instagram')
            
            st.download_button(
                label="📥 Download Data Profil (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"IG_Scraping_{keyword}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            status.warning("⚠️ Tidak ditemukan hasil yang cocok. Coba keyword yang lebih umum.")

# ===================== FOOTER =====================
st.markdown("""
<div class="footer">
© Data Scraper Tool - 2026
</div>
""", unsafe_allow_html=True)
