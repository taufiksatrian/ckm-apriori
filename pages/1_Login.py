import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configure the page settings
st.set_page_config(
    page_title="Login - CKM UMKM Purbalingga",
    page_icon="🔐", 
    layout="centered"
)

# Function to set the custom CSS for the page
def set_page_style():
    st.markdown("""
        <style>
        body {
            background-color: #f0f2f6;
        }
        .main-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 15vh;
        }
        .login-container {
            width: 100%;
            max-width: 400px;
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .login-header {
            font-size: 1.75rem;
            color: #046ccc;
            font-weight: bold;
            margin-bottom: 1.5rem;
        }
        .input-box {
            width: 100%;
            padding: 0.75rem;
            margin-bottom: 1rem;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #f7f9fc;
            font-size: 1rem;
        }
        .login-button {
            width: 100%;
            padding: 0.75rem;
            background-color: #046ccc;
            color: white;
            font-size: 1rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .login-button:hover {
            background-color: #035bb5;
        }
        .forgot-password {
            margin-top: 1rem;
            color: #666;
            font-size: 0.875rem;
        }
        .forgot-password:hover {
            text-decoration: underline;
            cursor: pointer;
        }
        .footer {
            text-align: center;
            margin-top: 12rem;
            font-size: 0.875rem;
            color: #888;
        }
        </style>
    """, unsafe_allow_html=True)

# Function to load Google Sheets credentials
def load_gspread_credentials():
    creds_info = st.secrets["gcp_service_account"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

# Function to verify login credentials against Google Sheets data
def verify_login(sheet, username, password):
    user_data = sheet.get_all_records()  
    for row in user_data:
        if (row["Email"] == username or row["Username"] == username) and row["Password"] == password:
            return True
    return False

# Function to display the login form and handle submission
def display_login_form(sheet):
    with st.container():
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)

        with st.form(key="login_form", clear_on_submit=True):
            st.markdown("<h2 class='login-header'>Login</h2>", unsafe_allow_html=True)

            username = st.text_input(
                "Email or Username", 
                placeholder="Enter your email or username", 
                key="username", 
                help="Please enter your registered email or username."
            )

            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your password", 
                key="password", 
                help="Please enter your password."
            )

            submit_button = st.form_submit_button(label="Login", help="Click to login")

            if submit_button:
                if verify_login(sheet, username, password):
                    st.session_state["logged_in"] = True
                    st.success("Login successful! Redirecting...")
                    st.switch_page("pages/Customer_Knowledge_Management.py")
                else:
                    st.error("Invalid username or password!")

            st.markdown("""
                <a class='daftar' href='#'>Daftar!</a>
                <a class='lupa-password' href='#'>Lupa Password?</a>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Function to display the footer
def display_footer():
    st.markdown("""
        <div class='footer'>
            © 2024 CKM UMKM Purbalingga - Semua Hak Dilindungi
        </div>
    """, unsafe_allow_html=True)

# Main function to run the login application
def run_login_app():
    # Set page style
    set_page_style()

    # Load credentials and authorize gspread
    client = load_gspread_credentials()

    # Open the Google Sheet by its name
    sheet = client.open("ckm").sheet1

    # Display the login form
    display_login_form(sheet)

    # Display the footer
    display_footer()

# Run the application
run_login_app()
