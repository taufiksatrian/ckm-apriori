import io
import time
import pandas as pd
import streamlit as st
import utils
import streamlit.components.v1 as components

# Inisialisasi variabel di session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'preprocessed_df' not in st.session_state:
    st.session_state.preprocessed_df = None
if 'selected_combination' not in st.session_state:
    st.session_state.selected_combination = "Balanced choice. Support: 0.015, Confidence: 0.25"
if 'my_basket_sets' not in st.session_state:
    st.session_state.my_basket_sets = None
if 'rules' not in st.session_state:
    st.session_state.rules = None
if 'formatted_rules' not in st.session_state:
    st.session_state.formatted_rules = None
if 'product_recommendations' not in st.session_state:
    st.session_state.product_recommendations = None
if 'promo_recommendations' not in st.session_state:
    st.session_state.promo_recommendations = None

st.set_page_config(
    page_title="Customer Knowledge Management",
    page_icon="🍗",
    layout="wide"
)

st.header("Customer Knowledge Management")
st.logo("logo.png")
# Sidebar-based navbar for navigation
navbar_option = st.sidebar.radio(
    "#### Navigation:",
    ["Upload and Preprocess Data", "Analysis Data", "Association Rule with Apriori", "Product Recommendation", "Promo Recommendation"]
)
REQUIRED_COLUMNS = ['orderId', 'categoryName', 'itemName', 'price', 'qty', 'orderTime']

# Section: Sidebar for Date Filter
if st.session_state.preprocessed_df is not None:
    preprocessed_df = st.session_state.preprocessed_df
    
    # Get min and max dates from the preprocessed data
    min_date = pd.to_datetime(preprocessed_df['orderTime'].min())
    max_date = pd.to_datetime(preprocessed_df['orderTime'].max())

    # Sidebar Date Range Input
    st.sidebar.markdown("#### Filter")
    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date,
                                    help="Select Date Range for filter data to use.")

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

    if navbar_option == "Analysis Data":
        st.sidebar.markdown("#### Analysis Data Filters")
        time_period = st.sidebar.selectbox(
            "Select Time Period",
            options=["D (Daily)", "W (Weekly)", "M (Monthly)", "Y (Yearly)"],
            index=0,
            help="Select Time Period for filter data to use."
        )

        time_period_map = {"D (Daily)": "D", "W (Weekly)": "W", "M (Monthly)": "M", "Y (Yearly)": "Y"}
        selected_time_period = time_period_map[time_period]

# Section 1: Upload and preprocess data
if navbar_option == "Upload and Preprocess Data":
    with st.expander("Upload and Preprocess Data", expanded=True):
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"],
                                        help="Only CSV files are allowed. Required columns: orderId, categoryName, itemName, price, qty, orderTime.")

        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file

            df = pd.read_csv(uploaded_file)
            # Save the dataframe to session state
            st.session_state.df = df
            st.markdown("#### Uploaded Data Summary")
            tab1, tab2 = st.columns(2, gap='medium')
            with tab1:
                st.write("Uploaded Data Table:")
                st.dataframe(df)

            with tab2:
                st.write("Uploaded Data Info:")
                
                num_rows = df.shape[0]
                num_columns = df.shape[1]
                unique_orders = df['orderId'].nunique() if 'orderId' in df.columns else "N/A"
                unique_items = df['itemName'].nunique() if 'itemName' in df.columns else "N/A"
                unique_categories = df['categoryName'].nunique() if 'categoryName' in df.columns else "N/A"
                min_time = df['orderTime'].min() if 'orderTime' in df.columns else "N/A"
                max_time = df['orderTime'].max() if 'orderTime' in df.columns else "N/A"

                # If orderTime exists, show date range
                if min_time != "N/A" and max_time != "N/A":
                    st.markdown(f"""
                        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                            <strong>Date Range of Orders:</strong> {min_time} to {max_time}
                        </div>
                        """, unsafe_allow_html=True)            
                
                # Create a clean summary using metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Number of Rows", value=num_rows)
                    st.metric(label="Number of Unique Categories", value=unique_categories)

                with col2:
                    st.metric(label="Number of Columns", value=num_columns)
                    st.metric(label="Number of Unique Items", value=unique_items)

                with col3:
                    st.metric(label="Number of Unique Orders", value=unique_orders)
                    
                st.write("Data Types of Columns")
                data_types_str = " | ".join([f"**{col}**: {dtype}" for col, dtype in df.dtypes.items()])
                data_types_str = " | ".join([f"<strong>{col}</strong>: {dtype}" for col, dtype in df.dtypes.items()])

                st.markdown(f"""
                    <p style="margin-top: 0px; line-height: 1.5;">
                        {data_types_str}
                    </p>
                    """, unsafe_allow_html=True)

                # Summary Statistics for numeric columns
                st.write("Summary Statistics for Numeric Columns")
                stats = df[['qty', 'price']].describe()
                sums = df[['qty', 'price']].sum()
                st.markdown(f"""
                    - **Quantity (Min, Max, Sum):** {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}
                    - **Price (Min, Max, Sum):** {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}
                    """)

                # Check for missing values
                missing_values = df.isnull().sum()
                if missing_values.any():
                    st.write("Missing Values:")
                    
                    # Display missing values in a cleaner format
                    for column, value in missing_values[missing_values > 0].items():
                        st.write(f"- **{column}:** {value} missing values")

            st.markdown("---")
            st.markdown("#### Preprocessed Data Summary")
            preprocessed_df = utils.preprocess_data(df)
            st.session_state.preprocessed_df = preprocessed_df

            tab1, tab2 = st.columns(2, gap='medium')
            with tab1:
                st.write("Preprocessed Data Table:")
                st.dataframe(preprocessed_df)

            with tab2:
                st.write("Preprocessed Data Info:")
                
                num_rows = preprocessed_df.shape[0]
                num_columns = preprocessed_df.shape[1]
                unique_orders = preprocessed_df['orderId'].nunique() if 'orderId' in preprocessed_df.columns else "N/A"
                unique_items = preprocessed_df['itemName'].nunique() if 'itemName' in preprocessed_df.columns else "N/A"
                unique_categories = preprocessed_df['categoryName'].nunique() if 'categoryName' in preprocessed_df.columns else "N/A"
                min_time = preprocessed_df['orderTime'].min() if 'orderTime' in preprocessed_df.columns else "N/A"
                max_time = preprocessed_df['orderTime'].max() if 'orderTime' in preprocessed_df.columns else "N/A"

                # If orderTime exists, show date range
                if min_time != "N/A" and max_time != "N/A":
                    st.markdown(f"""
                        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                            <strong>Date Range of Orders:</strong> {min_time} to {max_time}
                        </div>
                        """, unsafe_allow_html=True)            
                
                # Create a clean summary using metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Number of Rows", value=num_rows)
                    st.metric(label="Number of Unique Categories", value=unique_categories)

                with col2:
                    st.metric(label="Number of Columns", value=num_columns)
                    st.metric(label="Number of Unique Items", value=unique_items)

                with col3:
                    st.metric(label="Number of Unique Orders", value=unique_orders)
                    
                st.write("Data Types of Columns")
                data_types_str = " | ".join([f"**{col}**: {dtype}" for col, dtype in preprocessed_df.dtypes.items()])
                data_types_str = " | ".join([f"<strong>{col}</strong>: {dtype}" for col, dtype in preprocessed_df.dtypes.items()])

                st.markdown(f"""
                    <p style="margin-top: 0px; line-height: 1.5;">
                        {data_types_str}
                    </p>
                    """, unsafe_allow_html=True)

                # Summary Statistics for numeric columns
                st.write("Summary Statistics for Numeric Columns")
                stats = preprocessed_df[['qty', 'price']].describe()
                sums = preprocessed_df[['qty', 'price']].sum()
                st.markdown(f"""
                    - **Quantity (Min, Max, Sum):** {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}
                    - **Price (Min, Max, Sum):** {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}
                    """)

                # Check for missing values
                missing_values = preprocessed_df.isnull().sum()
                if missing_values.any():
                    st.write("Missing Values:")
                    
                    # Display missing values in a cleaner format
                    for column, value in missing_values[missing_values > 0].items():
                        st.write(f"- **{column}:** {value} missing values")

            # Get min and max dates for date range selection
            # min_date = pd.to_datetime(preprocessed_df['orderTime'].min())
            # max_date = pd.to_datetime(preprocessed_df['orderTime'].max())

            # # Add date input with min and max dates
            # date_range = st.date_input("Select Date Range", [min_date, max_date])

            # # Convert date_range tuple to a list to modify
            # start_date = pd.to_datetime(date_range[0])
            # end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

            # # Filter the dataframe based on the adjusted date range
            # filtered_df = preprocessed_df[(preprocessed_df['orderTime'] >= start_date) & (preprocessed_df['orderTime'] <= end_date)]
            if st.session_state.filtered_df is not None:
                filtered_df = st.session_state.filtered_df
                min_time = filtered_df['orderTime'].min()
                max_time = filtered_df['orderTime'].max()
                
                
                st.markdown("---")
                st.markdown("#### Filtered Data Summary")
                st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                        <strong>Date Range of Orders:</strong> {min_time.strftime('%Y-%m-%d %H:%M:%S')} to {max_time.strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                    """, unsafe_allow_html=True)

                tab1, tab2 = st.columns(2, gap='medium')
                with tab1:
                    st.write("Filtered Data Table:")
                    st.dataframe(filtered_df)

                with tab2:
                    st.write("Filtered Data Info:")         
                    
                    num_rows = filtered_df.shape[0]
                    num_columns = filtered_df.shape[1]
                    unique_orders = filtered_df['orderId'].nunique()
                    unique_items = filtered_df['itemName'].nunique()
                    unique_categories = filtered_df['categoryName'].nunique()
                    
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(label="Number of Rows", value=num_rows)
                        st.metric(label="Number of Unique Categories", value=unique_categories)

                    with col2:
                        st.metric(label="Number of Columns", value=num_columns)
                        st.metric(label="Number of Unique Items", value=unique_items)

                    with col3:
                        st.metric(label="Number of Unique Orders", value=unique_orders)
                        # st.metric(label="Total Sales", value=f"{filtered_df['price'].sum():,.2f}")

                    st.write("Summary Statistics for Numeric Columns")
                    stats = preprocessed_df[['qty', 'price']].describe()
                    sums = preprocessed_df[['qty', 'price']].sum()
                    st.markdown(f"""
                        - **Quantity (Min, Max, Sum):** {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}
                        - **Price (Min, Max, Sum):** {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}
                        """)
                    
                    missing_values = filtered_df.isnull().sum()
                    if missing_values.any():
                        st.write("Missing Values:")
                        for column, value in missing_values[missing_values > 0].items():
                            st.write(f"- **{column}:** {value} missing values")

        elif st.session_state.df is not None:
            df = st.session_state.df 
            st.markdown("#### Uploaded Data Summary")
            tab1, tab2 = st.columns(2, gap='medium')
            with tab1:
                st.write("Uploaded Data Table:")
                st.dataframe(df)

            with tab2:
                st.write("Info Uploaded Data:")
                
                num_rows = df.shape[0]
                num_columns = df.shape[1]
                unique_orders = df['orderId'].nunique() if 'orderId' in df.columns else "N/A"
                unique_items = df['itemName'].nunique() if 'itemName' in df.columns else "N/A"
                unique_categories = df['categoryName'].nunique() if 'categoryName' in df.columns else "N/A"
                min_time = df['orderTime'].min() if 'orderTime' in df.columns else "N/A"
                max_time = df['orderTime'].max() if 'orderTime' in df.columns else "N/A"

                # If orderTime exists, show date range
                if min_time != "N/A" and max_time != "N/A":
                    st.markdown(f"""
                        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                            <strong>Date Range of Orders:</strong> {min_time} to {max_time}
                        </div>
                        """, unsafe_allow_html=True)            
                
                # Create a clean summary using metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Number of Rows", value=num_rows)
                    st.metric(label="Number of Unique Categories", value=unique_categories)

                with col2:
                    st.metric(label="Number of Columns", value=num_columns)
                    st.metric(label="Number of Unique Items", value=unique_items)

                with col3:
                    st.metric(label="Number of Unique Orders", value=unique_orders)
                    
                st.write("Data Types of Columns")
                data_types_str = " | ".join([f"**{col}**: {dtype}" for col, dtype in df.dtypes.items()])
                data_types_str = " | ".join([f"<strong>{col}</strong>: {dtype}" for col, dtype in df.dtypes.items()])

                st.markdown(f"""
                    <p style="margin-top: 0px; line-height: 1.5;">
                        {data_types_str}
                    </p>
                    """, unsafe_allow_html=True)

                # Summary Statistics for numeric columns
                st.write("Summary Statistics for Numeric Columns")
                stats = df[['qty', 'price']].describe()
                sums = df[['qty', 'price']].sum()
                st.markdown(f"""
                    - **Quantity (Min, Max, Sum):** {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}
                    - **Price (Min, Max, Sum):** {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}
                    """)

                # Check for missing values
                missing_values = df.isnull().sum()
                if missing_values.any():
                    st.write("Missing Values:")
                    
                    # Display missing values in a cleaner format
                    for column, value in missing_values[missing_values > 0].items():
                        st.write(f"- **{column}:** {value} missing values")

            st.markdown("---")
            st.markdown("#### Preprocessed Data Summary")
            preprocessed_df = utils.preprocess_data(df)
            st.session_state.preprocessed_df = preprocessed_df

            tab1, tab2 = st.columns(2, gap='medium')
            with tab1:
                st.write("Preprocessed Data Table:")
                st.dataframe(preprocessed_df)

            with tab2:
                st.write("Preprocessed Data Info:")
                
                num_rows = preprocessed_df.shape[0]
                num_columns = preprocessed_df.shape[1]
                unique_orders = preprocessed_df['orderId'].nunique() if 'orderId' in preprocessed_df.columns else "N/A"
                unique_items = preprocessed_df['itemName'].nunique() if 'itemName' in preprocessed_df.columns else "N/A"
                unique_categories = preprocessed_df['categoryName'].nunique() if 'categoryName' in preprocessed_df.columns else "N/A"
                min_time = preprocessed_df['orderTime'].min() if 'orderTime' in preprocessed_df.columns else "N/A"
                max_time = preprocessed_df['orderTime'].max() if 'orderTime' in preprocessed_df.columns else "N/A"

                # If orderTime exists, show date range
                if min_time != "N/A" and max_time != "N/A":
                    st.markdown(f"""
                        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                            <strong>Date Range of Orders:</strong> {min_time} to {max_time}
                        </div>
                        """, unsafe_allow_html=True)            
                
                # Create a clean summary using metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Number of Rows", value=num_rows)
                    st.metric(label="Number of Unique Categories", value=unique_categories)

                with col2:
                    st.metric(label="Number of Columns", value=num_columns)
                    st.metric(label="Number of Unique Items", value=unique_items)

                with col3:
                    st.metric(label="Number of Unique Orders", value=unique_orders)
                    
                st.write("Data Types of Columns")
                data_types_str = " | ".join([f"**{col}**: {dtype}" for col, dtype in preprocessed_df.dtypes.items()])
                data_types_str = " | ".join([f"<strong>{col}</strong>: {dtype}" for col, dtype in preprocessed_df.dtypes.items()])

                st.markdown(f"""
                    <p style="margin-top: 0px; line-height: 1.5;">
                        {data_types_str}
                    </p>
                    """, unsafe_allow_html=True)

                # Summary Statistics for numeric columns
                st.write("Summary Statistics for Numeric Columns")
                stats = preprocessed_df[['qty', 'price']].describe()
                sums = preprocessed_df[['qty', 'price']].sum()
                st.markdown(f"""
                    - **Quantity (Min, Max, Sum):** {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}
                    - **Price (Min, Max, Sum):** {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}
                    """)

                # Check for missing values
                missing_values = preprocessed_df.isnull().sum()
                if missing_values.any():
                    st.write("Missing Values:")
                    
                    # Display missing values in a cleaner format
                    for column, value in missing_values[missing_values > 0].items():
                        st.write(f"- **{column}:** {value} missing values")

            # Get min and max dates for date range selection
            # min_date = pd.to_datetime(preprocessed_df['orderTime'].min())
            # max_date = pd.to_datetime(preprocessed_df['orderTime'].max())

            # # Add date input with min and max dates
            # date_range = st.date_input("Select Date Range", [min_date, max_date])

            # # Convert date_range tuple to a list to modify
            # start_date = pd.to_datetime(date_range[0])
            # end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

            # # Filter the dataframe based on the adjusted date range
            # filtered_df = preprocessed_df[(preprocessed_df['orderTime'] >= start_date) & (preprocessed_df['orderTime'] <= end_date)]
            if st.session_state.filtered_df is not None:
                filtered_df = st.session_state.filtered_df

                st.markdown("---")
                st.markdown("#### Filtered Data Summary")
                min_time = filtered_df['orderTime'].min()
                max_time = filtered_df['orderTime'].max()

                # Display date range
                st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                        <strong>Date Range of Orders:</strong> {min_time.strftime('%Y-%m-%d %H:%M:%S')} to {max_time.strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                    """, unsafe_allow_html=True)
                tab1, tab2 = st.columns(2, gap='medium')
                with tab1:
                    st.write("Filtered Data Table:")
                    st.dataframe(filtered_df)

                with tab2:
                    st.write("Filtered Data Info:")         
                    
                    num_rows = filtered_df.shape[0]
                    num_columns = filtered_df.shape[1]
                    unique_orders = filtered_df['orderId'].nunique()
                    unique_items = filtered_df['itemName'].nunique()
                    unique_categories = filtered_df['categoryName'].nunique()
                    

                    # Display the summary in the second column
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(label="Number of Rows", value=num_rows)
                        st.metric(label="Number of Unique Categories", value=unique_categories)

                    with col2:
                        st.metric(label="Number of Columns", value=num_columns)
                        st.metric(label="Number of Unique Items", value=unique_items)

                    with col3:
                        st.metric(label="Number of Unique Orders", value=unique_orders)
                        # st.metric(label="Total Sales", value=f"{filtered_df['price'].sum():,.2f}")

                    st.write("Summary Statistics for Numeric Columns")
                    stats = preprocessed_df[['qty', 'price']].describe()
                    sums = preprocessed_df[['qty', 'price']].sum()
                    st.markdown(f"""
                        - **Quantity (Min, Max, Sum):** {stats['qty']['min']:.2f}, {stats['qty']['max']:.2f}, {sums['qty']:.2f}
                        - **Price (Min, Max, Sum):** {stats['price']['min']:.2f}, {stats['price']['max']:.2f}, {sums['price']:.2f}
                        """)
                    
                    missing_values = filtered_df.isnull().sum()
                    if missing_values.any():
                        st.write("Missing Values:")
                        for column, value in missing_values[missing_values > 0].items():
                            st.write(f"- **{column}:** {value} missing values")

# Section 2: Analysis Data
elif navbar_option == "Analysis Data":
    with st.expander("Analysis Data", expanded=True):
        if st.session_state.filtered_df is not None:
            
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
            st.warning("Silakan unggah data terlebih dahulu di bagian 'Mengunggah Data'.")

# Section 3: Association Rule with Apriori
elif navbar_option == "Association Rule with Apriori":
    with st.expander("Association Rule with Apriori", expanded=True):
        
        st.markdown("#### Run Apriori Algorithm")
        st.markdown("""
        The Apriori algorithm will generate association rules from the transactions. Choose a recommended combination of minimum support and confidence below:
        """)

        # Predefined combinations of min_support, min_confidence, and explanations
        combinations = {
            "Recommended for broad analysis. Support: 0.010, Confidence: 0.25": {
                "values": (0.010, 0.25),
                "explanation": """
                    This combination captures the **broadest set of items**. With 1% support, it includes even low-frequency items, while a confidence of 25% balances the number and strength of the rules.
                """
            },
            "Strong but diverse rules. Support: 0.010, Confidence: 0.30": {
                "values": (0.010, 0.30),
                "explanation": """
                    **Wider scope** with strong associations. Support of 1% ensures broad item coverage, and confidence of 30% focuses on reliable associations.
                """
            },
            "High confidence, broad scope. Support: 0.010, Confidence: 0.35": {
                "values": (0.010, 0.35),
                "explanation": """
                    This combination offers **high confidence (35%)** for frequently occurring items (1% support), prioritizing very strong associations.
                """
            },
            "Balanced choice. Support: 0.015, Confidence: 0.25": {
                "values": (0.015, 0.25),
                "explanation": """
                    A balanced choice with **slightly higher support (1.5%)** and **moderate confidence (25%)**. Ideal for capturing frequently bought but not too rare items.
                """
            },
            "Middle ground, reliable rules. Support: 0.015, Confidence: 0.30": {
                "values": (0.015, 0.30),
                "explanation": """
                    A solid **middle ground**. With 1.5% support and 30% confidence, it's ideal for uncovering reliable associations without excluding too many items.
                """
            },
            "High confidence, frequent items. Support: 0.015, Confidence: 0.35": {
                "values": (0.015, 0.35),
                "explanation": """
                    Focuses on frequent items with **high confidence** (35%), ensuring the strongest rules for the most frequent combinations.
                """
            },
            "Focused on frequent items. Support: 0.020, Confidence: 0.25": {
                "values": (0.020, 0.25),
                "explanation": """
                    Focused on **more popular products** with 2% support, allowing some flexibility with a confidence of 25% to generate more rules.
                """
            },
            "Narrower focus, reliable rules. Support: 0.020, Confidence: 0.30": {
                "values": (0.020, 0.30),
                "explanation": """
                    For a **tighter analysis**, 2% support ensures that only frequent items are included, and 30% confidence makes sure the rules are reliable.
                """
            },
            "Strongest associations. Support: 0.020, Confidence: 0.35": {
                "values": (0.020, 0.35),
                "explanation": """
                    **Recommended for discovering the strongest associations**. A support of 2% ensures frequent items are included, and a confidence of 35% focuses on very reliable associations.
                """
            }
        }
        
        # Dropdown to select pre-configured combination of min_support and min_confidence
        selected_combination = st.selectbox(
            "Select a recommended combination",
            options=list(combinations.keys()),
            index=list(combinations.keys()).index(st.session_state.selected_combination)  # Restore previous selection
        )

        st.session_state.selected_combination = selected_combination

        # Extract the selected values and explanation
        min_support, min_confidence = combinations[selected_combination]["values"]
        explanation = combinations[selected_combination]["explanation"]

        # Explanation for support and confidence
        st.markdown(f"""
        You have selected:
        - **Minimum Support**: `{min_support:.3f}` - This means an itemset must appear in at least {min_support * 100:.1f}% of all transactions.
        - **Minimum Confidence**: `{min_confidence:.2f}` - This means the association rules must have a confidence of at least {min_confidence * 100:.0f}% to be accepted.
        """)

        # Display the explanation for the selected combination
        st.markdown(f"**Explanation:** {explanation}")

        # Run the Apriori algorithm when the button is clicked
        if st.session_state.filtered_df is not None and st.button("Run Apriori"):
            my_basket_sets = utils.create_basket_sets(st.session_state.filtered_df)
            st.session_state.my_basket_sets = my_basket_sets

            rules = utils.calculate_apriori(my_basket_sets, support=min_support, min_confidence=min_confidence)
            st.session_state.rules = rules

            formatted_rules = utils.display_association_rules(rules)
            st.session_state.formatted_rules = formatted_rules

            st.toast('Market Basket Analysis has been completed successfully!', icon='✅')
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

        # Display association rules if available
        if st.session_state.formatted_rules is not None:
            st.markdown(f"""
            #### Apriori Results
            - **Number of Transactions Analyzed**: `{st.session_state.my_basket_sets.shape[0]}`
            - **Number of Items Considered**: `{st.session_state.my_basket_sets.shape[1]}`
            - **Number of Association Rules Generated**: `{len(st.session_state.rules)}`
            """)

            st.write("Results Apriori Data Table:")
            st.dataframe(st.session_state.formatted_rules)

            tab1, tab2 = st.columns(2, gap='medium')
            with tab1:
                st.write("Results Apriori Visualization with Graph:")
                html_content = utils.generate_pyvis_graph(st.session_state.rules)
                components.html(html_content, height=650)

            with tab2:
                st.write("Results Apriori Visualization with Graph:")
                st.sidebar.markdown("#### Apriori Visualization Filters")
    
                # Sidebar for metric selection
                metric = st.sidebar.selectbox(
                    "Select Metric for Ranking Rules", 
                    options=['confidence', 'lift', 'support'], 
                    index=0,  # Default to 'confidence'
                    help="Choose which metric to rank the association rules."
                )
                
                # Sidebar for the number of top rules to display
                top_n = st.sidebar.slider(
                    "Number of Top Rules to Display", 
                    min_value=5, max_value=100, value=10, 
                    help="Adjust the number of top association rules to display."
                )
                # metric = st.selectbox("Select Metric for Ranking Rules", options=['confidence', 'lift', 'support'])
                # top_n = st.slider("Number of Top Rules to Display", min_value=5, max_value=100, value=10)
                bar_chart_fig = utils.plot_top_association_rules(st.session_state.rules, metric=metric, top_n=top_n)
                st.plotly_chart(bar_chart_fig)

# Section 4: Product Recommendation
elif navbar_option == "Product Recommendation":
    with st.expander("Product Recommendation", expanded=True):
        if st.session_state.rules is not None:
            product_to_recommend = st.text_input("Enter Product for Recommendation:", key="product_input")
            if st.button("Run Product Recommendation"):
                if product_to_recommend:
                    product_recommendations = utils.product_recommendation(st.session_state.rules, st.session_state.filtered_df, product_to_recommend)
                    st.session_state.product_recommendations = product_recommendations
                    for product in product_recommendations:
                        st.write(product)
                else:
                    st.warning("Please enter a product for recommendation.")
        else:
            st.warning("Silakan unggah data terlebih dahulu di bagian 'Analisis Apriori'.")

# Section 5: Promo Recommendation
elif navbar_option == "Promo Recommendation":
    with st.expander("Promo Recommendation", expanded=True):
        if st.session_state.rules is not None:
            promo_to_recommend = st.text_input("Enter Product for Promo Recommendation:", key="promo_input")
            if st.button("Run Promo Recommendation"):
                if promo_to_recommend:
                    promo_recommendations = utils.promo_recommendation(st.session_state.rules, st.session_state.filtered_df, promo_to_recommend)
                    st.session_state.promo_recommendations = promo_recommendations
                    st.write("Promotional Recommendations:")
                    promo_recommendations_df = pd.DataFrame(promo_recommendations)
                    st.dataframe(promo_recommendations_df)
                else:
                    st.warning("Please enter a product for promo recommendation.")
        else:
            st.warning("Silakan unggah data terlebih dahulu di bagian 'Analisis Apriori'.")
