import streamlit as st

st.set_page_config(
    page_title="CKM UMKM Purbalingga",
    page_icon="🍗", 
    layout="wide",  
)

max_width_str = f"max-width: 1200px; margin: 0 auto; padding: 1rem;"

st.markdown(f"""
    <style>
    /* General Styling */
    body {{
        background-color: #f4f4f4;  /* Light grey background */
    }}
    .main {{
        background-color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}
    .appview-container .main .block-container{{{max_width_str}}} /* Center the content and set max width */
    
    /* Header and Subheader Styling */
    .header {{
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: #046ccc;  /* Primary color */
        margin-bottom: 0rem;
    }}
    .sub-header {{
        text-align: center;
        font-size: 2.0rem;
        margin-bottom: 0rem;
    }}
    
    /* Section Styling for Pengantar, Tujuan, Manfaat */
    .research-section {{
        margin: 1.2rem 0;  /* Reduced margin between sections */
        padding: 1rem 1.5rem;  /* Reduced padding for sections */
        margin-bottom: 2.5rem;
        background-color: #e2eaf3;  /* Light secondary color */
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    .research-section h3 {{
        font-size: 1.5rem;
        color: #046ccc;
        margin-bottom: 0rem;
    }}
    .research-section p {{
        line-height: 1.5;
        color: #333;
        margin-bottom: 0.5rem;  /* Reduced margin under paragraphs */
    }}

    /* Horizontal Timeline Styling */
    .timeline-horizontal {{
        display: flex;
        justify-content: space-evenly;
        align-items: center;
        position: relative;
        margin: 2rem 0;
        padding: 0;
    }}
    
    .timeline-horizontal::before {{
        content: '';
        position: absolute;
        top: 10px;
        left: 0;
        right: 0;
        height: 2px;
        background: #046ccc;
        z-index: 1;
    }}
    
    .timeline-item {{
        position: relative;
        width: 22%;
        text-align: center;
        z-index: 2;
    }}
    
    .timeline-item h3 {{
        font-size: 1.3rem;
        color: #046ccc;
        margin-top: 1rem;
    }}
    
    .timeline-item p {{
        line-height: 1.4;
        color: #333;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;  /* Reduced margin under paragraphs */
    }}
    
    .timeline-item::before {{
        content: '';
        position: absolute;
        top: 0px;
        left: 50%;
        transform: translateX(-50%);
        width: 16px;
        height: 16px;
        background-color: white;
        border: 4px solid #046ccc;
        border-radius: 50%;
        z-index: 3;
    }}

    /* Footer */
    .footer {{
        text-align: center;
        margin-top: 4rem;
        font-size: 0.9rem;
        color: #888;
    }}
    </style>
    """, unsafe_allow_html=True)

st.logo("logo.png") 

navbar_option = st.sidebar.radio(
    "#### Navigasi:",
    ["Pengantar", "Tahapan Pengolahan dan Penerapan Algoritma Apriori dalam CKM"]
)

if navbar_option == "Pengantar":
    st.markdown(f"""
    <script>
    window.location.href = '#pengantar';
    </script>
    """, unsafe_allow_html=True)
elif navbar_option == "Tahapan Pengolahan dan Penerapan Algoritma Apriori dalam CKM":
    st.markdown(f"""
    <script>
    window.location.href = '#tahapan-pengolahan-dan-penerapan-algoritma-apriori-dalam-ckm';
    </script>
    """, unsafe_allow_html=True)

# Header Section
st.markdown("""
<h2 class='sub-header'>Implementasi Customer Knowledge Management Menggunakan Metode Apriori Berbasis Framework Streamlit
""", unsafe_allow_html=True)

# Boody Section
st.markdown("""
<div class='research-section'>
    <h3>Pengantar</h3>
    <p>Penelitian ini mengusung penerapan Customer Knowledge Management (CKM) di UMKM Kabupaten Purbalingga, dengan fokus pada UMKM Dkriuk Fried Chicken sebagai sampel penelitian. CKM menjadi penting dalam memanfaatkan big data untuk menghasilkan wawasan yang dapat diterapkan dalam strategi bisnis. Model data mining yang digunakan adalah Algoritma Apriori, yang bertujuan untuk mengidentifikasi pola pembelian dan memberikan rekomendasi produk.</p>
    <Penelitian>Penelitian ini bertujuan untuk memanfaatkan big data dengan implementasi model CKM dan algoritma Apriori pada UMKM Dkriuk Purbalingga. Model ini akan menghasilkan pola pembelian pelanggan yang dapat digunakan untuk memberikan rekomendasi produk, strategi pemasaran, serta identifikasi produk terlaris. Penelitian ini diharapkan memberikan kontribusi yang signifikan bagi UMKM Dkriuk Purbalingga pasca-pandemi Covid-19, dengan memberikan wawasan berbasis data tentang kebutuhan pelanggan yang dapat menunjang keberhasilan usaha.</p>
</div>

<div class='research-section'>
    <h3>Tahapan Pengolahan dan Penerapan Algoritma Apriori dalam CKM</h3>
</div>      

<div class="timeline-horizontal">
<div class="timeline-item">
    <h3>1. Mengunggah Data</h3>
    <p>Data transaksi diunggah untuk dianalisis dengan menggunakan metode CKM dan algoritma Apriori.</p>
</div>

<div class="timeline-item">
    <h3>2. Preprocessing Data</h3>
    <p>Pembersihan dan pengolahan data untuk memastikan data siap digunakan dalam analisis lebih lanjut.</p>
</div>

<div class="timeline-item">
    <h3>3. Analisis Data</h3>
    <p>Data dianalisis untuk memahami pola pembelian dan perilaku konsumen yang paling relevan.</p>
</div>

<div class="timeline-item">
    <h3>4. Analisis Apriori</h3>
    <p>Mengidentifikasi hubungan antara produk yang sering dibeli bersama dengan algoritma Apriori.</p>
</div>

<div class="timeline-item">
    <h3>5. Penerapan</h3>
    <p>Menerapkan hasil analisis untuk memberikan rekomendasi produk dan strategi promosi yang tepat.</p>
</div>
</div>
""", unsafe_allow_html=True)

# Footer Section
st.markdown("""
    <div class='footer'>
        © 2024 CKM UMKM Purbalingga - Semua Hak Dilindungi
    </div>
""", unsafe_allow_html=True)
