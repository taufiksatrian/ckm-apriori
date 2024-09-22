import time
import pandas as pd
import streamlit as st
import utils
import streamlit.components.v1 as components
from google.cloud import bigquery
from google.oauth2.service_account import Credentials

# Initialize BigQuery client
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# BigQuery configuration
DATASET_ID = "ckm-apriori.dkriuk"  # Replace with your dataset ID in BigQuery
TABLE_ID = f"{DATASET_ID}.dkriuk-2023"

# Initialize session state variables
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'selected_file_name' not in st.session_state:
    st.session_state.selected_file_name = None
if 'selected_data' not in st.session_state:
    st.session_state.selected_data = None
if 'confirm_data' not in st.session_state:
    st.session_state.confirm_data = False 
if 'preprocessed_df' not in st.session_state:
    st.session_state.preprocessed_df = None
if 'date_range' not in st.session_state:
    st.session_state.date_range = None
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'my_basket_sets' not in st.session_state:
    st.session_state.my_basket_sets = None
if 'rules' not in st.session_state:
    st.session_state.rules = None
if 'formatted_rules' not in st.session_state:
    st.session_state.formatted_rules = None
if 'selected_combination' not in st.session_state:
    st.session_state.selected_combination = "Pilihan seimbang. Support: 0.015, Confidence: 0.25"
if 'sort_by' not in st.session_state:
    st.session_state.sort_by = "Confidence"
if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

st.set_page_config(
    page_title="Customer Knowledge Management - CKM UMKM Purbalingga",
    page_icon="🍗",
    layout="wide"
)
st.logo("logo.png") 
st.header("Customer Knowledge Management")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("You must log in to access this page.")
    st.stop()

# Sidebar navigasi
navbar_option = st.sidebar.radio(
    "Navigasi:",
    ["Mengunggah Data", "Preprocessing Data", "Analisis Data", "Analisis Apriori", "Penerapan"]
)

REQUIRED_COLUMNS = ['orderId', 'categoryName', 'itemName', 'price', 'qty', 'orderTime']

# Section 1: Mengunggah Data
if navbar_option == "Mengunggah Data":
    with st.expander("Mengunggah Data", expanded=True):
        # File uploader for CSV
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"], help="Pilih file CSV yang ingin diunggah.")
        
        if uploaded_file is not None:
            # Convert the uploaded CSV file into a Pandas DataFrame
            df = pd.read_csv(uploaded_file)
            
            if 'orderTime' in df.columns:
                df['orderTime'] = pd.to_datetime(df['orderTime'], errors='coerce')
            
            df['fileName'] = uploaded_file.name
            st.session_state.uploaded_file = uploaded_file
            st.session_state.df = df
            
            st.markdown(f"#### Data yang diunggah dari file: **{uploaded_file.name}**")
            tab1, tab2 = st.columns(2, gap='medium')
            with tab1:
                st.write("Tabel Data yang Diunggah:")
                st.dataframe(df)
                if st.button("Konfirmasi Pengunggahan", type="primary"):
                    st.session_state.confirm_data = True

            with tab2:
                st.write("Info Data yang Diupload:")
                
                num_rows = df.shape[0]
                num_columns = df.shape[1]
                unique_orders = df['orderId'].nunique() if 'orderId' in df.columns else "N/A"
                unique_items = df['itemName'].nunique() if 'itemName' in df.columns else "N/A"
                unique_categories = df['categoryName'].nunique() if 'categoryName' in df.columns else "N/A"
                min_time = df['orderTime'].min() if 'orderTime' in df.columns else "N/A"
                max_time = df['orderTime'].max() if 'orderTime' in df.columns else "N/A"
                
                if min_time != "N/A" and max_time != "N/A":
                    st.markdown(f"""
                        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                            <strong>Rentang Tanggal Pesanan:</strong> {min_time} to {max_time}
                        </div>
                        """, unsafe_allow_html=True)            
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Jumlah Baris", value=num_rows)
                    st.metric(label="Jumlah Kategori Unik", value=unique_categories)

                with col2:
                    st.metric(label="Jumlah Kolom", value=num_columns)
                    st.metric(label="Jumlah Item Unik", value=unique_items)

                with col3:
                    st.metric(label="Jumlah Pesanan Unik", value=unique_orders)
                    
                data_types_str = " | ".join([f"<strong>{col}</strong>: {dtype}" for col, dtype in df.dtypes.items()])

                st.markdown(f"""
                    <p style="margin-bottom: 0px;">
                        Tipe Data Kolom
                    </p>
                    <p style="margin-top: 0px;">
                        {data_types_str}
                    </p>
                    """, unsafe_allow_html=True)
                
                stats = df[['qty', 'price']].describe()
                sums = df[['qty', 'price']].sum()
                st.markdown(f"""
                    <p style="margin-bottom: 0px;">Statistik Ringkasan untuk Kolom Numerik</p>
                    <ul style="margin-top: 0px;">
                        <li><strong>Quantity (Min, Max, Sum):</strong> {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}</li>
                        <li><strong>Price (Min, Max, Sum):</strong> {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}</li>
                    </ul>
                    """, unsafe_allow_html=True)

                missing_values = df.isnull().sum()
                if missing_values.any():
                    st.markdown("<p style='margin-bottom: 0px;'>Nilai yang Hilang</p>", unsafe_allow_html=True)
                    
                    missing_values_str = "\n".join([f"<li><strong>{column}</strong>: {value} nilai hilang</li>" for column, value in missing_values[missing_values > 0].items()])
                    
                    st.markdown(f"""
                    <ul style="margin-top: 0px;">
                        {missing_values_str}
                    </ul>
                    """, unsafe_allow_html=True)

        # Fetch available datasets from BigQuery based on fileName
        st.markdown("#### Pilih File yang Sudah Diunggah Sebelumnya:")
        query = f"SELECT DISTINCT fileName FROM `{TABLE_ID}`"
        df_previous_uploads = client.query(query).to_dataframe()

        if df_previous_uploads['fileName'].unique().tolist() and st.session_state.selected_file_name is not None and st.session_state.selected_file_name != 'Pilih file sebelumnya':  
            selected_file_name = st.selectbox(
                "Pilih file sebelumnya untuk digunakan:",
                options=df_previous_uploads['fileName'].unique().tolist(),
                index=0  
            )
            st.session_state.selected_file_name = selected_file_name
        else: 
            selected_file_name = st.selectbox(
                "Pilih file sebelumnya untuk digunakan:",
                options=['Pilih file sebelumnya'] + df_previous_uploads['fileName'].unique().tolist(),
                index=0  
            )
            st.session_state.selected_file_name = selected_file_name


        if st.session_state.selected_file_name != 'Pilih file sebelumnya': 
            query = f"SELECT * FROM `{TABLE_ID}` WHERE fileName = '{st.session_state.selected_file_name}'"
            selected_data = client.query(query).to_dataframe()

            if selected_data is not None:
                st.markdown(f"#### Data dari file: **{st.session_state.selected_file_name}**")
                tab1, tab2 = st.columns(2, gap='medium')
                with tab1:
                    st.write("Tabel Data")
                    selected_data.loc[:, selected_data.columns != 'fileName']
                    if st.button("Konfirmasi Data untuk Diproses", type="primary"):
                        st.session_state.confirm_data = True 
                        if st.session_state.confirm_data is True:
                            st.session_state.selected_data = selected_data

                with tab2:
                    st.write("Info Data")

                    num_rows = selected_data.shape[0]
                    num_columns = selected_data.shape[1]
                    unique_orders = selected_data['orderId'].nunique() if 'orderId' in selected_data.columns else "N/A"
                    unique_items = selected_data['itemName'].nunique() if 'itemName' in selected_data.columns else "N/A"
                    unique_categories = selected_data['categoryName'].nunique() if 'categoryName' in selected_data.columns else "N/A"
                    min_time = selected_data['orderTime'].min() if 'orderTime' in selected_data.columns else "N/A"
                    max_time = selected_data['orderTime'].max() if 'orderTime' in selected_data.columns else "N/A"

                    if min_time != "N/A" and max_time != "N/A":
                        st.markdown(f"""
                            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                                <strong>Rentang Tanggal Pesanan:</strong> {min_time} to {max_time}
                            </div>
                            """, unsafe_allow_html=True)            
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="Jumlah Baris", value=num_rows)
                        st.metric(label="Jumlah Kategori Unik", value=unique_categories)

                    with col2:
                        st.metric(label="Jumlah Kolom", value=num_columns)
                        st.metric(label="Jumlah Item Unik", value=unique_items)

                    with col3:
                        st.metric(label="Jumlah Pesanan Unik", value=unique_orders)
                        
                    data_types_str = " | ".join([f"<strong>{col}</strong>: {dtype}" for col, dtype in selected_data.dtypes.items()])

                    st.markdown(f"""
                        <p style="margin-bottom: 0px;">
                            Tipe Data Kolom
                        </p>
                        <p style="margin-top: 0px;">
                            {data_types_str}
                        </p>
                        """, unsafe_allow_html=True)
                    
                    stats = selected_data[['qty', 'price']].describe()
                    sums = selected_data[['qty', 'price']].sum()
                    st.markdown(f"""
                        <p style="margin-bottom: 0px;">Statistik Ringkasan untuk Kolom Numerik</p>
                        <ul style="margin-top: 0px;">
                            <li><strong>Quantity (Min, Max, Sum):</strong> {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}</li>
                            <li><strong>Price (Min, Max, Sum):</strong> {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}</li>
                        </ul>
                        """, unsafe_allow_html=True)

                    missing_values = selected_data.isnull().sum()
                    if missing_values.any():
                        st.markdown("<p style='margin-bottom: 0px;'>Nilai yang Hilang</p>", unsafe_allow_html=True)
                        
                        missing_values_str = "\n".join([f"<li><strong>{column}</strong>: {value} nilai hilang</li>" for column, value in missing_values[missing_values > 0].items()])
                        
                        st.markdown(f"""
                        <ul style="margin-top: 0px;">
                            {missing_values_str}
                        </ul>
                        """, unsafe_allow_html=True)

# Section 2: Preprocessing Data
elif navbar_option == "Preprocessing Data":
    with st.expander("Preprocessing Data", expanded=True):
        # Preprocessing can only proceed if the data has been confirmed
        if st.session_state.confirm_data:
            # Use uploaded or selected data for preprocessing
            if st.session_state.df is not None or st.session_state.selected_data is not None:
                df_to_preprocess = st.session_state.df if st.session_state.df is not None else st.session_state.selected_data

                # Preprocessing step: Ensure columns are available
                missing_columns = [col for col in REQUIRED_COLUMNS if col not in df_to_preprocess.columns]
                if missing_columns:
                    st.error(f"Kolom berikut tidak ada di data yang diunggah: {', '.join(missing_columns)}")
                else:
                    st.markdown(f"#### Data dari file **{st.session_state.selected_file_name}** siap untuk diproses")
                    tab1, tab2 = st.columns(2, gap='medium')
                    with tab1:
                        st.write("Tabel Data")
                        st.dataframe(df_to_preprocess.loc[:, df_to_preprocess.columns != 'fileName'])

                    with tab2:
                        st.write("Info Data")

                        num_rows = df_to_preprocess.shape[0]
                        num_columns = df_to_preprocess.shape[1]
                        unique_orders = df_to_preprocess['orderId'].nunique() if 'orderId' in df_to_preprocess.columns else "N/A"
                        unique_items = df_to_preprocess['itemName'].nunique() if 'itemName' in df_to_preprocess.columns else "N/A"
                        unique_categories = df_to_preprocess['categoryName'].nunique() if 'categoryName' in df_to_preprocess.columns else "N/A"
                        min_time = df_to_preprocess['orderTime'].min() if 'orderTime' in df_to_preprocess.columns else "N/A"
                        max_time = df_to_preprocess['orderTime'].max() if 'orderTime' in df_to_preprocess.columns else "N/A"

                        if min_time != "N/A" and max_time != "N/A":
                            st.markdown(f"""
                                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                                    <strong>Rentang Tanggal Pesanan:</strong> {min_time} to {max_time}
                                </div>
                                """, unsafe_allow_html=True)            
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Jumlah Baris", value=num_rows)
                            st.metric(label="Jumlah Kategori Unik", value=unique_categories)

                        with col2:
                            st.metric(label="Jumlah Kolom", value=num_columns)
                            st.metric(label="Jumlah Item Unik", value=unique_items)

                        with col3:
                            st.metric(label="Jumlah Pesanan Unik", value=unique_orders)
                            
                        data_types_str = " | ".join([f"<strong>{col}</strong>: {dtype}" for col, dtype in df_to_preprocess.dtypes.items()])

                        st.markdown(f"""
                            <p style="margin-bottom: 0px;">
                                Tipe Data Kolom
                            </p>
                            <p style="margin-top: 0px;">
                                {data_types_str}
                            </p>
                            """, unsafe_allow_html=True)
                        
                        stats = df_to_preprocess[['qty', 'price']].describe()
                        sums = df_to_preprocess[['qty', 'price']].sum()
                        st.markdown(f"""
                            <p style="margin-bottom: 0px;">Statistik Ringkasan untuk Kolom Numerik</p>
                            <ul style="margin-top: 0px;">
                                <li><strong>Quantity (Min, Max, Sum):</strong> {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}</li>
                                <li><strong>Price (Min, Max, Sum):</strong> {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}</li>
                            </ul>
                            """, unsafe_allow_html=True)

                        missing_values = df_to_preprocess.isnull().sum()
                        if missing_values.any():
                            st.markdown("<p style='margin-bottom: 0px;'>Nilai yang Hilang</p>", unsafe_allow_html=True)
                            
                            missing_values_str = "\n".join([f"<li><strong>{column}</strong>: {value} nilai hilang</li>" for column, value in missing_values[missing_values > 0].items()])
                            
                            st.markdown(f"""
                            <ul style="margin-top: 0px;">
                                {missing_values_str}
                            </ul>
                            """, unsafe_allow_html=True)

                    preprocessed_df = utils.preprocess_data(df_to_preprocess)
                    st.session_state.preprocessed_df = preprocessed_df

                    st.markdown(f"#### Setelah preprocessing data {st.session_state.selected_file_name} siap digunakan untuk analisis")
                    tab1, tab2 = st.columns(2, gap='medium')
                    with tab1:
                        st.write("Tabel Data")
                        st.dataframe(preprocessed_df)

                    with tab2:
                        st.write("Info Data")

                        num_rows = preprocessed_df.shape[0]
                        num_columns = preprocessed_df.shape[1]
                        unique_orders = preprocessed_df['orderId'].nunique() if 'orderId' in preprocessed_df.columns else "N/A"
                        unique_items = preprocessed_df['itemName'].nunique() if 'itemName' in preprocessed_df.columns else "N/A"
                        unique_categories = preprocessed_df['categoryName'].nunique() if 'categoryName' in preprocessed_df.columns else "N/A"
                        min_time = preprocessed_df['orderTime'].min() if 'orderTime' in preprocessed_df.columns else "N/A"
                        max_time = preprocessed_df['orderTime'].max() if 'orderTime' in preprocessed_df.columns else "N/A"

                        if min_time != "N/A" and max_time != "N/A":
                            st.markdown(f"""
                                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                                    <strong>Rentang Tanggal Pesanan:</strong> {min_time} to {max_time}
                                </div>
                                """, unsafe_allow_html=True)            
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Jumlah Baris", value=num_rows)
                            st.metric(label="Jumlah Kategori Unik", value=unique_categories)

                        with col2:
                            st.metric(label="Jumlah Kolom", value=num_columns)
                            st.metric(label="Jumlah Item Unik", value=unique_items)

                        with col3:
                            st.metric(label="Jumlah Pesanan Unik", value=unique_orders)
                            
                        data_types_str = " | ".join([f"<strong>{col}</strong>: {dtype}" for col, dtype in preprocessed_df.dtypes.items()])

                        st.markdown(f"""
                            <p style="margin-bottom: 0px;">
                                Tipe Data Kolom
                            </p>
                            <p style="margin-top: 0px;">
                                {data_types_str}
                            </p>
                            """, unsafe_allow_html=True)
                        
                        stats = preprocessed_df[['qty', 'price']].describe()
                        sums = preprocessed_df[['qty', 'price']].sum()
                        st.markdown(f"""
                            <p style="margin-bottom: 0px;">Statistik Ringkasan untuk Kolom Numerik</p>
                            <ul style="margin-top: 0px;">
                                <li><strong>Quantity (Min, Max, Sum):</strong> {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}</li>
                                <li><strong>Price (Min, Max, Sum):</strong> {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}</li>
                            </ul>
                            """, unsafe_allow_html=True)

                        missing_values = preprocessed_df.isnull().sum()
                        if missing_values.any():
                            st.markdown("<p style='margin-bottom: 0px;'>Nilai yang Hilang</p>", unsafe_allow_html=True)
                            
                            missing_values_str = "\n".join([f"<li><strong>{column}</strong>: {value} nilai hilang</li>" for column, value in missing_values[missing_values > 0].items()])
                            
                            st.markdown(f"""
                            <ul style="margin-top: 0px;">
                                {missing_values_str}
                            </ul>
                            """, unsafe_allow_html=True)

                # Sidebar filter only appears after preprocessing
                if st.session_state.preprocessed_df is not None:
                    preprocessed_df = st.session_state.preprocessed_df
                    
                    # Get min and max dates from the preprocessed data
                    min_date = pd.to_datetime(preprocessed_df['orderTime'].min())
                    max_date = pd.to_datetime(preprocessed_df['orderTime'].max())

                    # Sidebar Date Range Input
                    st.sidebar.markdown("#### Filter")
                    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date,
                                                    help="Select Date Range for filter data to use.")
                    
                    st.session_state.date_range = date_range

                    # Ensure that both start and end dates are selected
                    if isinstance(date_range, tuple) and len(date_range) == 2:
                        # Both start and end date selected
                        start_date = pd.to_datetime(date_range[0])
                        end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                    else:
                        # Only one date selected, so set end_date to be the same as start_date
                        start_date = pd.to_datetime(date_range[0])
                        end_date = start_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

                    # Filter the dataframe based on the selected date range
                    filtered_df = preprocessed_df[(preprocessed_df['orderTime'] >= start_date) & (preprocessed_df['orderTime'] <= end_date)]
                    st.session_state.filtered_df = filtered_df

                    st.markdown(f"#### Setelah difilter {st.session_state.selected_file_name} siap digunakan untuk analisis")
                    tab1, tab2 = st.columns(2, gap='medium')
                    with tab1:
                        st.write("Tabel Data")
                        st.dataframe(filtered_df)

                    with tab2:
                        st.write("Info Data")

                        num_rows = filtered_df.shape[0]
                        num_columns = filtered_df.shape[1]
                        unique_orders = filtered_df['orderId'].nunique() if 'orderId' in filtered_df.columns else "N/A"
                        unique_items = filtered_df['itemName'].nunique() if 'itemName' in filtered_df.columns else "N/A"
                        unique_categories = filtered_df['categoryName'].nunique() if 'categoryName' in filtered_df.columns else "N/A"
                        min_time = filtered_df['orderTime'].min() if 'orderTime' in filtered_df.columns else "N/A"
                        max_time = filtered_df['orderTime'].max() if 'orderTime' in filtered_df.columns else "N/A"

                        if min_time != "N/A" and max_time != "N/A":
                            st.markdown(f"""
                                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                                    <strong>Rentang Tanggal Pesanan:</strong> {min_time} to {max_time}
                                </div>
                                """, unsafe_allow_html=True)            
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Jumlah Baris", value=num_rows)
                            st.metric(label="Jumlah Kategori Unik", value=unique_categories)

                        with col2:
                            st.metric(label="Jumlah Kolom", value=num_columns)
                            st.metric(label="Jumlah Item Unik", value=unique_items)

                        with col3:
                            st.metric(label="Jumlah Pesanan Unik", value=unique_orders)
                            
                        data_types_str = " | ".join([f"<strong>{col}</strong>: {dtype}" for col, dtype in filtered_df.dtypes.items()])

                        st.markdown(f"""
                            <p style="margin-bottom: 0px;">
                                Tipe Data Kolom
                            </p>
                            <p style="margin-top: 0px;">
                                {data_types_str}
                            </p>
                            """, unsafe_allow_html=True)
                        
                        stats = filtered_df[['qty', 'price']].describe()
                        sums = filtered_df[['qty', 'price']].sum()
                        st.markdown(f"""
                            <p style="margin-bottom: 0px;">Statistik Ringkasan untuk Kolom Numerik</p>
                            <ul style="margin-top: 0px;">
                                <li><strong>Quantity (Min, Max, Sum):</strong> {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}</li>
                                <li><strong>Price (Min, Max, Sum):</strong> {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}</li>
                            </ul>
                            """, unsafe_allow_html=True)

                        missing_values = filtered_df.isnull().sum()
                        if missing_values.any():
                            st.markdown("<p style='margin-bottom: 0px;'>Nilai yang Hilang</p>", unsafe_allow_html=True)
                            
                            missing_values_str = "\n".join([f"<li><strong>{column}</strong>: {value} nilai hilang</li>" for column, value in missing_values[missing_values > 0].items()])
                            
                            st.markdown(f"""
                            <ul style="margin-top: 0px;">
                                {missing_values_str}
                            </ul>
                            """, unsafe_allow_html=True)
        else:
            st.warning("Silakan unggah dan konfirmasi data terlebih dahulu di bagian 'Mengunggah Data'.")

# Section 3: Analisis Data
elif navbar_option == "Analisis Data":
    with st.expander("Analisis Data", expanded=True):
        if st.session_state.filtered_df is not None:
            filtered_df = st.session_state.filtered_df
            preprocessed_df = st.session_state.preprocessed_df
            mins_date = pd.to_datetime(preprocessed_df['orderTime'].min())
            maxs_date = pd.to_datetime(preprocessed_df['orderTime'].max())

            if st.session_state.date_range is None:
                min_date = pd.to_datetime(preprocessed_df['orderTime'].min())
                max_date = pd.to_datetime(preprocessed_df['orderTime'].max())
                st.session_state.date_range = [min_date, max_date]
            else:
                if len(st.session_state.date_range) == 2:
                    min_date = st.session_state.date_range[0]
                    max_date = st.session_state.date_range[1]
                else:
                    min_date = pd.to_datetime(preprocessed_df['orderTime'].min())
                    max_date = pd.to_datetime(preprocessed_df['orderTime'].max())
                    st.session_state.date_range = [min_date, max_date]

            # Sidebar Date Range Input for further filtering
            st.sidebar.markdown("#### Filter Tanggal (Analisis Apriori)")
            date_range = st.sidebar.date_input(
                "Select Date Range", [min_date, max_date], min_value=mins_date, max_value=maxs_date,
                help="Pilih rentang tanggal untuk memfilter data analisis.")
            
            st.session_state.date_range = [min_date, max_date]

            # Ensure that both start and end dates are selected
            if isinstance(date_range, tuple) and len(date_range) == 2:
                # Both start and end date selected
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            else:
                # Only one date selected, so set end_date to be the same as start_date
                start_date = pd.to_datetime(date_range[0])
                end_date = start_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

            # Filter the dataframe based on the selected date range in Analysis Data
            filtered_df = preprocessed_df[(preprocessed_df['orderTime'] >= start_date) & (preprocessed_df['orderTime'] <= end_date)]
            st.session_state.filtered_df = filtered_df

            st.sidebar.markdown("#### Analysis Data Filters")
            time_period = st.sidebar.selectbox(
                "Select Time Period",
                options=["D (Daily)", "W (Weekly)", "M (Monthly)", "Y (Yearly)"],
                index=0,
                help="Select Time Period for filter data to use."
            )

            time_period_map = {"D (Daily)": "D", "W (Weekly)": "W", "M (Monthly)": "M", "Y (Yearly)": "Y"}
            selected_time_period = time_period_map[time_period]

            fig1 = utils.plot_total_transactions(st.session_state.filtered_df, time_period=selected_time_period)
            st.plotly_chart(fig1)

            tab1, tab2 = st.columns(2, gap='medium')

            with tab1:
                fig1 = utils.plot_monthly_total_transaction(st.session_state.filtered_df)
                st.plotly_chart(fig1)

            with tab2:
                fig2 = utils.plot_weekly_total_transaction(st.session_state.filtered_df)
                st.plotly_chart(fig2)

            tab1, tab2 = st.columns(2, gap='medium')

            with tab1:
                fig1 = utils.plot_daily_total_transaction(st.session_state.filtered_df)
                st.plotly_chart(fig1)

            with tab2:
                fig2 = utils.plot_hourly_total_transaction(st.session_state.filtered_df)
                st.plotly_chart(fig2)

            tab1, tab2 = st.columns(2, gap='medium')

            with tab1:
                fig1 = utils.plot_top_items(st.session_state.filtered_df)
                st.plotly_chart(fig1)

            with tab2:
                fig2 = utils.plot_least_sold_items(st.session_state.filtered_df)
                st.plotly_chart(fig2)
        else:
            st.warning("Silakan unggah dan konfirmasi data terlebih dahulu di bagian 'Mengunggah Data'.")

# Bagian 4: Analisis Apriori
elif navbar_option == "Analisis Apriori":
    with st.expander("Analisis Apriori", expanded=True):
        if st.session_state.filtered_df is not None:
            filtered_df = st.session_state.filtered_df
            preprocessed_df = st.session_state.preprocessed_df
            mins_date = pd.to_datetime(preprocessed_df['orderTime'].min())
            maxs_date = pd.to_datetime(preprocessed_df['orderTime'].max())

            if st.session_state.date_range is None:
                min_date = pd.to_datetime(preprocessed_df['orderTime'].min())
                max_date = pd.to_datetime(preprocessed_df['orderTime'].max())
                st.session_state.date_range = [min_date, max_date]
            else:
                if len(st.session_state.date_range) == 2:
                    min_date = st.session_state.date_range[0]
                    max_date = st.session_state.date_range[1]
                    st.session_state.date_range = [min_date, max_date]

            # Sidebar Date Range Input for further filtering
            st.sidebar.markdown("#### Filter Tanggal (Analisis Apriori)")
            date_range = st.sidebar.date_input(
                "Select Date Range", [min_date, max_date], min_value=mins_date, max_value=maxs_date,
                help="Pilih rentang tanggal untuk memfilter data analisis.")
            

            # Ensure that both start and end dates are selected
            if isinstance(date_range, tuple) and len(date_range) == 2:
                # Both start and end date selected
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            else:
                # Only one date selected, so set end_date to be the same as start_date
                start_date = pd.to_datetime(date_range[0])
                end_date = start_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

            # Filter the dataframe based on the selected date range in Analysis Data
            filtered_df = preprocessed_df[(preprocessed_df['orderTime'] >= start_date) & (preprocessed_df['orderTime'] <= end_date)]
            st.session_state.filtered_df = filtered_df
        
        st.markdown("#### Jalankan Algoritma Apriori")
        st.markdown("""
        Algoritma Apriori akan menghasilkan aturan asosiasi dari transaksi. Pilih kombinasi minimum support dan confidence yang direkomendasikan di bawah ini:
        """)

        # Kombinasi yang sudah ditentukan sebelumnya untuk min_support, min_confidence, dan penjelasan
        combinations = {
            "Direkomendasikan untuk analisis luas. Support: 0.010, Confidence: 0.25": {
                "values": (0.010, 0.25),
                "explanation": """
                    Kombinasi ini menangkap **set item paling luas**. Dengan support 1%, kombinasi ini mencakup bahkan item yang jarang muncul, sedangkan confidence 25% menyeimbangkan jumlah dan kekuatan aturan.
                """
            },
            "Aturan kuat namun beragam. Support: 0.010, Confidence: 0.30": {
                "values": (0.010, 0.30),
                "explanation": """
                    **Cakupan yang lebih luas** dengan asosiasi yang kuat. Support 1% memastikan cakupan item yang luas, dan confidence 30% berfokus pada asosiasi yang dapat diandalkan.
                """
            },
            "Kepercayaan tinggi, cakupan luas. Support: 0.010, Confidence: 0.35": {
                "values": (0.010, 0.35),
                "explanation": """
                    Kombinasi ini menawarkan **confidence tinggi (35%)** untuk item yang sering muncul (1% support), memprioritaskan asosiasi yang sangat kuat.
                """
            },
            "Pilihan seimbang. Support: 0.015, Confidence: 0.25": {
                "values": (0.015, 0.25),
                "explanation": """
                    Pilihan yang seimbang dengan **support sedikit lebih tinggi (1.5%)** dan **confidence moderat (25%)**. Ideal untuk menangkap item yang sering dibeli tetapi tidak terlalu jarang.
                """
            },
            "Titik tengah, aturan yang dapat diandalkan. Support: 0.015, Confidence: 0.30": {
                "values": (0.015, 0.30),
                "explanation": """
                    **Titik tengah yang kuat**. Dengan support 1.5% dan confidence 30%, kombinasi ini ideal untuk menemukan asosiasi yang andal tanpa mengecualikan terlalu banyak item.
                """
            },
            "Kepercayaan tinggi, item yang sering muncul. Support: 0.015, Confidence: 0.35": {
                "values": (0.015, 0.35),
                "explanation": """
                    Fokus pada item yang sering muncul dengan **kepercayaan tinggi (35%)**, memastikan aturan yang paling kuat untuk kombinasi item yang sering.
                """
            },
            "Fokus pada item populer. Support: 0.020, Confidence: 0.25": {
                "values": (0.020, 0.25),
                "explanation": """
                    Berfokus pada **produk yang lebih populer** dengan support 2%, memberikan fleksibilitas dengan confidence 25% untuk menghasilkan lebih banyak aturan.
                """
            },
            "Fokus lebih sempit, aturan yang andal. Support: 0.020, Confidence: 0.30": {
                "values": (0.020, 0.30),
                "explanation": """
                    Untuk **analisis yang lebih ketat**, support 2% memastikan hanya item yang sering dimasukkan, dan confidence 30% memastikan aturannya andal.
                """
            },
            "Asosiasi yang paling kuat. Support: 0.020, Confidence: 0.35": {
                "values": (0.020, 0.35),
                "explanation": """
                    **Direkomendasikan untuk menemukan asosiasi yang paling kuat**. Support 2% memastikan item yang sering muncul disertakan, dan confidence 35% berfokus pada asosiasi yang sangat andal.
                """
            }
        }
        
        # Dropdown untuk memilih kombinasi pre-configured min_support dan min_confidence
        selected_combination = st.selectbox(
            "Pilih kombinasi yang direkomendasikan",
            options=list(combinations.keys()),
            index=list(combinations.keys()).index(st.session_state.selected_combination)  # Mengembalikan pilihan sebelumnya
        )

        st.session_state.selected_combination = selected_combination

        # Mengambil nilai yang dipilih dan penjelasannya
        min_support, min_confidence = combinations[selected_combination]["values"]
        explanation = combinations[selected_combination]["explanation"]

        # Penjelasan untuk support dan confidence
        st.markdown(f"""
        Anda telah memilih:
        - **Minimum Support**: `{min_support:.3f}` - Ini berarti itemset harus muncul di setidaknya {min_support * 100:.1f}% dari semua transaksi.
        - **Minimum Confidence**: `{min_confidence:.2f}` - Ini berarti aturan asosiasi harus memiliki confidence minimal {min_confidence * 100:.0f}% agar diterima.
        """)

        # Menampilkan penjelasan untuk kombinasi yang dipilih
        st.markdown(f"**Penjelasan:** {explanation}")

        # Jalankan algoritma Apriori saat tombol diklik
        if st.session_state.filtered_df is not None and st.button("Jalankan Apriori", type="primary"):
            my_basket_sets = utils.create_basket_sets(st.session_state.filtered_df)
            st.session_state.my_basket_sets = my_basket_sets

            rules = utils.calculate_apriori(my_basket_sets, support=min_support, min_confidence=min_confidence)
            st.session_state.rules = rules

            formatted_rules = utils.display_association_rules(rules)
            st.session_state.formatted_rules = formatted_rules

            st.toast('Analisis Market Basket telah selesai!', icon='✅')
            time.sleep(0.001)

            st.markdown(
                """
                <style>
                .stAlert {
                    position: fixed;
                    top: 1rem;
                    right: 1rem;
                    width: auto;
                    z-index: 9999;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("Silakan unggah dan konfirmasi data terlebih dahulu di bagian 'Mengunggah Data'.")

        # Tampilkan aturan asosiasi jika tersedia
        if st.session_state.formatted_rules is not None:
            st.markdown(f"""
            #### Hasil Apriori
            - **Jumlah Transaksi yang Dianalisis**: `{st.session_state.my_basket_sets.shape[0]}`
            - **Jumlah Item yang Dipertimbangkan**: `{st.session_state.my_basket_sets.shape[1]}`
            - **Jumlah Aturan Asosiasi yang Dihasilkan**: `{len(st.session_state.rules)}`
            """)

            st.write("Tabel Hasil Apriori:")
            st.dataframe(st.session_state.formatted_rules)

            tab1, tab2 = st.columns(2, gap='medium')
            with tab1:
                st.write("Visualisasi Hasil Apriori dengan Graph:")
                html_content = utils.generate_pyvis_graph(st.session_state.rules)
                components.html(html_content, height=650)

            with tab2:
                st.write("Visualisasi Hasil Apriori dengan Grafik")
                st.sidebar.markdown("#### Filter Visualisasi Apriori")
    
                # Sidebar untuk pemilihan metrik
                metric = st.sidebar.selectbox(
                    "Pilih Metrik untuk Mengurutkan Aturan", 
                    options=['confidence', 'lift', 'support'], 
                    index=0,  # Default ke 'confidence'
                    help="Pilih metrik untuk mengurutkan aturan asosiasi."
                )
                
                # Sidebar untuk memilih jumlah aturan teratas yang ditampilkan
                top_n = st.sidebar.slider(
                    "Jumlah Aturan Teratas untuk Ditampilkan", 
                    min_value=5, max_value=100, value=10, 
                    help="Atur jumlah aturan asosiasi teratas yang akan ditampilkan."
                )
                bar_chart_fig = utils.plot_top_association_rules(st.session_state.rules, metric=metric, top_n=top_n)
                st.plotly_chart(bar_chart_fig)

# Section 5: Penerapan
elif navbar_option == "Penerapan":
    st.sidebar.markdown("#### Sort dan Filter")
    st.session_state.sort_by = st.sidebar.selectbox(
        "Sort produk berdasarkan:", 
        options=["Produk sering dibeli bersama (Confidence)", "Produk paling banyak dibeli (Support)"],
        index=0 if st.session_state.sort_by == "Produk sering dibeli bersama (Confidence)" else 1,
        help="Silahkan pilih urutkan berdasarkan pilihan ini."
    )

    if st.session_state.sort_by == "Produk sering dibeli bersama (Confidence)":
        st.session_state.sort_column = 'confidence'
    else:
        st.session_state.sort_column = 'support'

    selected_tags = st.sidebar.multiselect(
        "Filter berdasarkan tag:",
        options=["Hubungan Kuat", "Populer", "Relevan"],
        default=[],
        help="Pilih tag untuk memfilter hasil rekomendasi"
    )

    with st.expander("Rekomendasi Produk", expanded=True):
        if st.session_state.rules is not None:
            st.markdown("#### Pilih Produk untuk Rekomendasi Produk")

            rules_sorted = st.session_state.formatted_rules.sort_values(by=st.session_state.sort_column, ascending=False)

            antecedents_products = rules_sorted['antecedents'].apply(
                lambda x: [item.strip() for item in x.split(',')]
            ).explode().unique().tolist()

            # Pilih produk dari 'antecedents' yang akan digunakan untuk rekomendasi
            product_to_recommend = st.selectbox(
                "Pilih produk untuk mencari rekomendasi:",
                antecedents_products,
                key="product_input",
                placeholder="Cari produk",
                help="Cari produk yang ingin Anda lihat rekomendasinya"
            )

            if st.button("Cari Rekomendasi Produk", type="primary"):
                if product_to_recommend:
                    # Dapatkan rekomendasi produk
                    product_recommendations = utils.product_recommendation(
                        rules=st.session_state.formatted_rules, 
                        item=product_to_recommend, 
                        sort_by=st.session_state.sort_column
                    )
                    
                    if product_recommendations:
                        st.success(f"Berikut adalah produk yang direkomendasikan berdasarkan produk '{product_to_recommend}':")
                        st.markdown("<ul>", unsafe_allow_html=True)
                        
                        # Tampilkan rekomendasi produk beserta tag
                        for rec in product_recommendations:
                            confidence_percent = f"{rec['confidence'] * 100:.2f}%"
                            support_percent = f"{rec['support'] * 100:.2f}%"

                            tags = []
                            if rec['confidence'] >= 0.3:
                                tags.append("Hubungan Kuat")
                            if rec['support'] >= 0.03:
                                tags.append("Populer")
                            if not tags:
                                tags.append("Relevan")

                            if selected_tags and not any(tag in selected_tags for tag in tags):
                                continue

                            st.markdown(f"""
                                <div style="background-color: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 5px;">
                                    <h5>{rec['product'].capitalize()}</h5>
                                    <p>Tingkat Keterkaitan <strong>{confidence_percent}</strong> | Kemunculan <strong>{support_percent}</strong></p>
                                    {"".join([f'<span style="background-color: #d4edda; color: #155724; padding: 5px; margin-right: 5px; border-radius: 3px;">{tag}</span>' for tag in tags])}
                                </div>
                            """, unsafe_allow_html=True)


                    else:
                        st.warning(f"Tidak ada rekomendasi produk yang ditemukan untuk '{product_to_recommend}'. Coba dengan nama produk lain.")
                else:
                    st.error("Silakan masukkan nama produk untuk melihat rekomendasi.")
        else:
            st.warning("Silakan jalankan analisis asosiasi terlebih dahulu di bagian 'Analisis Apriori'.")

    
    with st.expander("Rekomendasi Promo", expanded=True):
        if st.session_state.rules is not None:
            st.markdown("#### Pilih Produk untuk Rekomendasi Promo")

            rules_sorted = st.session_state.formatted_rules.sort_values(by=st.session_state.sort_column, ascending=False)

            # Ambil produk dari antecedents dan consequents yang sudah disortir
            product_list = pd.concat([
                rules_sorted['antecedents'].apply(lambda x: [item.strip() for item in x.split(',')]).explode(),
                rules_sorted['consequents'].apply(lambda x: [item.strip() for item in x.split(',')]).explode()
            ]).unique().tolist()

            # Pilih produk dari 'antecedents' yang akan digunakan untuk rekomendasi
            promo_to_recommend = st.selectbox(
                "Pilih produk untuk rekomendasi promo:",
                product_list,
                key="promo_input",
                placeholder="Cari produk",
                help="Cari produk yang ingin Anda buat rekomendasinya"
            )

            if st.button("Cari Rekomendasi Promo", type="primary"):
                if promo_to_recommend:
                    # Panggil fungsi untuk mendapatkan rekomendasi promosi
                    promo_recommendations = utils.promo_recommendation(st.session_state.rules, promo_to_recommend, sort_by=st.session_state.sort_column)
                    st.session_state.promo_recommendations = promo_recommendations
                    
                    if promo_recommendations:
                        st.success(f"Rekomendasi promo untuk produk '{promo_to_recommend}':")

                        # Tampilkan hasil dengan styling yang lebih baik
                        for promo in promo_recommendations:
                            confidence_percent = f"{promo['confidence'] * 100:.2f}%"
                            support_percent = f"{promo['support'] * 100:.2f}%"
                            
                            # Tentukan tag berdasarkan confidence dan support
                            tags = []
                            if promo['confidence'] >= 0.3:
                                tags.append("Hubungan Kuat")
                            if promo['support'] >= 0.03:
                                tags.append("Populer")
                            if not tags:
                                tags.append("Relevan")

                            # Tampilkan hasil dengan layout yang lebih menarik
                            st.markdown(f"""
                                <div style="background-color: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 5px;">
                                    <h5>{promo['Paket Promo'].capitalize()}</h5>
                                    <p>Tingkat keterkaitan: <strong>{confidence_percent}</strong> | Kemunculan: <strong>{support_percent}</strong></p>
                                    {"".join([f'<span style="background-color: #d4edda; color: #155724; padding: 5px; margin-right: 5px; border-radius: 3px;">{tag}</span>' for tag in tags])}
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Tidak ada rekomendasi promo untuk produk ini.")
                else:
                    st.warning("Silakan pilih produk terlebih dahulu.")
        else:
            st.warning("Silahkan jalankan analisis asosiasi terlebih dahulu di bagian 'Analisis Apriori'.")

st.sidebar.markdown("---")  
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.success("You have been logged out.")
    st.switch_page("pages/1_Login.py")