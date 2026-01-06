"""
SCAR Management System - Streamlit Application
Calyx Containers Quality Management System
"""

import streamlit as st
from database import (
    init_database, 
    get_user_by_email, 
    verify_password, 
    create_user,
    get_all_vendors,
    get_pending_users_count
)

# Page configuration
st.set_page_config(
    page_title="SCAR Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --calyx-red: #DC2626;
        --calyx-red-dark: #B91C1C;
        --calyx-red-light: #FEE2E2;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 {
        color: #6B7280;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0 0 0.5rem 0;
    }
    
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .badge-open { background: #FEF3C7; color: #92400E; }
    .badge-submitted { background: #D1FAE5; color: #065F46; }
    .badge-closed { background: #E5E7EB; color: #374151; }
    .badge-new { background: #DBEAFE; color: #1E40AF; }
    
    .badge-minor { background: #D1FAE5; color: #065F46; }
    .badge-major { background: #FEF3C7; color: #92400E; }
    .badge-critical { background: #FEE2E2; color: #991B1B; }
    
    .badge-pending { background: #FEF3C7; color: #92400E; }
    .badge-approved { background: #D1FAE5; color: #065F46; }
    .badge-rejected { background: #FEE2E2; color: #991B1B; }
    
    /* Login page styling */
    .login-container {
        max-width: 400px;
        margin: 4rem auto;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        color: #DC2626;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1F2937;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 8px;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #374151;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_database()

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

def login(email: str, password: str) -> bool:
    """Authenticate user"""
    user = get_user_by_email(email)
    if user and verify_password(password, user['password']):
        if user['status'] != 'approved':
            st.error("Your account is pending approval. Please wait for an administrator to approve your account.")
            return False
        st.session_state.authenticated = True
        st.session_state.user = user
        return True
    return False

def logout():
    """Log out user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

def show_login_page():
    """Display login/registration page"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="display: inline-flex; align-items: center; justify-content: center; 
                        width: 60px; height: 60px; background: #DC2626; border-radius: 12px; margin-bottom: 1rem;">
                <span style="color: white; font-weight: bold; font-size: 1.5rem;">CC</span>
            </div>
            <h1 style="color: #DC2626; margin: 0;">SCAR Management System</h1>
            <p style="color: #6B7280; margin-top: 0.5rem;">Calyx Containers Quality Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    if email and password:
                        if login(email, password):
                            st.rerun()
                        else:
                            st.error("Invalid email or password")
                    else:
                        st.warning("Please enter both email and password")
            
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem; padding: 1rem; background: #F3F4F6; border-radius: 8px;">
                <p style="color: #6B7280; font-size: 0.875rem; margin: 0;">Demo Credentials</p>
                <p style="color: #374151; font-size: 0.875rem; margin: 0.25rem 0;">
                    <strong>Admin:</strong> admin@calyxcontainers.com / admin123
                </p>
                <p style="color: #374151; font-size: 0.875rem; margin: 0;">
                    <strong>Supplier:</strong> jsmith@pacificglass.com / supplier123
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with tab2:
            vendors = get_all_vendors()
            
            with st.form("register_form"):
                st.markdown("##### Create Supplier Account")
                
                reg_name = st.text_input("Full Name", placeholder="Enter your full name")
                reg_email = st.text_input("Email Address", placeholder="Enter your work email")
                reg_vendor = st.selectbox(
                    "Select Your Company",
                    options=[""] + [v['id'] for v in vendors],
                    format_func=lambda x: "Select a vendor..." if x == "" else next((v['name'] for v in vendors if v['id'] == x), x)
                )
                reg_password = st.text_input("Password", type="password", placeholder="Create a password")
                reg_password_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                register = st.form_submit_button("Register", use_container_width=True)
                
                if register:
                    if not all([reg_name, reg_email, reg_vendor, reg_password]):
                        st.error("Please fill in all fields")
                    elif reg_password != reg_password_confirm:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        existing = get_user_by_email(reg_email)
                        if existing:
                            st.error("An account with this email already exists")
                        else:
                            try:
                                create_user(reg_email, reg_password, reg_name, "supplier", reg_vendor)
                                st.success("Registration successful! Your account is pending approval. You will receive an email once approved.")
                            except Exception as e:
                                st.error(f"Registration failed: {str(e)}")
            
            st.info("📧 After registration, an administrator will review and approve your account.")

def show_sidebar():
    """Display sidebar navigation"""
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    
    with st.sidebar:
        # Logo and branding
        st.markdown("""
        <div style="display: flex; align-items: center; padding: 1rem 0; border-bottom: 1px solid #374151; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; justify-content: center; 
                        width: 40px; height: 40px; background: #DC2626; border-radius: 8px;">
                <span style="color: white; font-weight: bold; font-size: 1rem;">CC</span>
            </div>
            <div style="margin-left: 12px;">
                <div style="color: white; font-weight: 600; font-size: 1rem;">SCAR System</div>
                <div style="color: #9CA3AF; font-size: 0.75rem;">Calyx Containers</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### Navigation")
        
        if st.button("🏠 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        
        if st.button("📋 SCARs", use_container_width=True, key="nav_scars"):
            st.session_state.page = "scars"
            st.rerun()
        
        if is_admin:
            pending_count = get_pending_users_count()
            settings_label = f"⚙️ Settings" + (f" ({pending_count})" if pending_count > 0 else "")
            if st.button(settings_label, use_container_width=True, key="nav_settings"):
                st.session_state.page = "settings"
                st.rerun()
        
        st.markdown("---")
        
        # User info
        st.markdown(f"""
        <div style="padding: 1rem; background: #374151; border-radius: 8px; margin-top: 1rem;">
            <div style="color: white; font-weight: 500;">{user['name']}</div>
            <div style="color: #9CA3AF; font-size: 0.75rem;">{user['email']}</div>
            <div style="color: #9CA3AF; font-size: 0.75rem; margin-top: 0.25rem;">
                {'Administrator' if is_admin else user.get('vendor_name', 'Supplier')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👤 Profile", use_container_width=True, key="nav_profile"):
                st.session_state.page = "profile"
                st.rerun()
        with col2:
            if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
                logout()

def main():
    """Main application entry point"""
    
    # Initialize page state
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_sidebar()
        
        # Route to appropriate page
        page = st.session_state.page
        
        if page == "dashboard":
            from pages import dashboard
            dashboard.show()
        elif page == "scars":
            from pages import scars
            scars.show()
        elif page == "scar_detail":
            from pages import scar_detail
            scar_detail.show()
        elif page == "scar_create":
            from pages import scar_create
            scar_create.show()
        elif page == "settings":
            from pages import settings
            settings.show()
        elif page == "profile":
            from pages import profile
            profile.show()
        else:
            from pages import dashboard
            dashboard.show()

if __name__ == "__main__":
    main()
