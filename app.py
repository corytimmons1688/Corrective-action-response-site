"""
SCAR Management System for Calyx Containers
Brand-aligned version with grid-based layouts
"""

import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import json
import os

# ============================================================================
# CALYX BRAND CONFIGURATION
# ============================================================================

CALYX_COLORS = {
    "primary": "#0033A1",      # Calyx Blue
    "primary_light": "#004FFF", # Flash Blue (accessible)
    "white": "#FFFFFF",
    "black": "#000000",
    "cloud_blue": "#D9F1FD",
    "powder_blue": "#DBE6FF",
    "mist_blue": "#202945",
    "ocean_blue": "#001F60",
    "gray_90": "#1A1A1A",
    "gray_60": "#666666",
    "gray_30": "#B3B3B3",
    "gray_10": "#E5E5E5",
    "gray_5": "#F1F2F2",
}

# ============================================================================
# CALYX BRAND STYLES
# ============================================================================

def get_calyx_styles():
    return f"""
    <style>
        /* Import clean geometric font similar to Kentos R1 */
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&display=swap');
        
        /* Root Variables - Calyx Brand Colors */
        :root {{
            --calyx-primary: {CALYX_COLORS['primary']};
            --calyx-primary-light: {CALYX_COLORS['primary_light']};
            --calyx-white: {CALYX_COLORS['white']};
            --calyx-black: {CALYX_COLORS['black']};
            --calyx-cloud-blue: {CALYX_COLORS['cloud_blue']};
            --calyx-powder-blue: {CALYX_COLORS['powder_blue']};
            --calyx-mist-blue: {CALYX_COLORS['mist_blue']};
            --calyx-ocean-blue: {CALYX_COLORS['ocean_blue']};
            --calyx-gray-90: {CALYX_COLORS['gray_90']};
            --calyx-gray-60: {CALYX_COLORS['gray_60']};
            --calyx-gray-30: {CALYX_COLORS['gray_30']};
            --calyx-gray-10: {CALYX_COLORS['gray_10']};
            --calyx-gray-5: {CALYX_COLORS['gray_5']};
        }}
        
        /* Global Typography */
        html, body, [class*="css"] {{
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* Main container */
        .main .block-container {{
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        
        /* Header styling */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
            color: var(--calyx-gray-90);
            letter-spacing: 0.02em;
        }}
        
        h1 {{
            color: var(--calyx-primary);
            font-weight: 400;
            font-size: 2rem;
            margin-bottom: 1.5rem;
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, var(--calyx-primary) 0%, var(--calyx-ocean-blue) 100%);
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: var(--calyx-white);
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {{
            color: var(--calyx-white) !important;
        }}
        
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: rgba(255,255,255,0.8) !important;
        }}
        
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
            color: rgba(255,255,255,0.8) !important;
        }}
        
        [data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.2);
        }}
        
        /* Button styling */
        .stButton > button {{
            background-color: var(--calyx-primary);
            color: var(--calyx-white) !important;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1.5rem;
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
            letter-spacing: 0.02em;
            transition: background-color 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background-color: var(--calyx-primary-light);
            color: var(--calyx-white) !important;
        }}
        
        /* Sidebar button styling - ensure text is visible */
        [data-testid="stSidebar"] .stButton > button {{
            background-color: var(--calyx-white);
            color: var(--calyx-primary) !important;
            border: 1px solid rgba(255,255,255,0.3);
            text-align: left;
        }}
        
        [data-testid="stSidebar"] .stButton > button:hover {{
            background-color: var(--calyx-powder-blue);
            color: var(--calyx-primary) !important;
            border-color: var(--calyx-white);
        }}
        
        [data-testid="stSidebar"] .stButton > button span,
        [data-testid="stSidebar"] .stButton > button p,
        [data-testid="stSidebar"] .stButton > button div {{
            color: var(--calyx-primary) !important;
        }}
        
        [data-testid="stSidebar"] .stButton button[data-testid="baseButton-secondary"],
        [data-testid="stSidebar"] .stButton button[kind="secondary"] {{
            background-color: var(--calyx-white);
            color: var(--calyx-primary) !important;
        }}
        
        /* Secondary button */
        .stButton > button[kind="secondary"] {{
            background-color: var(--calyx-white);
            color: var(--calyx-primary);
            border: 1px solid var(--calyx-primary);
        }}
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {{
            border: 1px solid var(--calyx-gray-10);
            border-radius: 4px;
            font-family: 'DM Sans', sans-serif;
        }}
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--calyx-primary);
            box-shadow: 0 0 0 1px var(--calyx-primary);
        }}
        
        /* Grid Table Styles */
        .calyx-grid {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'DM Sans', sans-serif;
            background: var(--calyx-white);
            border: 1px solid var(--calyx-gray-10);
        }}
        
        .calyx-grid thead {{
            background: var(--calyx-primary);
        }}
        
        .calyx-grid th {{
            color: var(--calyx-white);
            font-weight: 500;
            padding: 12px 16px;
            text-align: left;
            font-size: 0.875rem;
            letter-spacing: 0.02em;
            border-bottom: 2px solid var(--calyx-ocean-blue);
        }}
        
        .calyx-grid td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--calyx-gray-10);
            font-size: 0.875rem;
            color: var(--calyx-gray-90);
        }}
        
        .calyx-grid tr:hover {{
            background: var(--calyx-gray-5);
        }}
        
        .calyx-grid tr:last-child td {{
            border-bottom: none;
        }}
        
        /* Status badges */
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 2px;
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        
        .status-open {{
            background: var(--calyx-powder-blue);
            color: var(--calyx-primary);
        }}
        
        .status-pending {{
            background: #FFF3CD;
            color: #856404;
        }}
        
        .status-closed {{
            background: #D4EDDA;
            color: #155724;
        }}
        
        .status-approved {{
            background: var(--calyx-cloud-blue);
            color: var(--calyx-ocean-blue);
        }}
        
        /* Role badges */
        .role-admin {{
            background: var(--calyx-primary);
            color: var(--calyx-white);
        }}
        
        .role-supplier {{
            background: var(--calyx-gray-60);
            color: var(--calyx-white);
        }}
        
        /* Card styling - more angular, less bubbly */
        .calyx-card {{
            background: var(--calyx-white);
            border: 1px solid var(--calyx-gray-10);
            padding: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .calyx-card-header {{
            border-bottom: 2px solid var(--calyx-primary);
            padding-bottom: 0.75rem;
            margin-bottom: 1rem;
        }}
        
        .calyx-card-title {{
            color: var(--calyx-gray-90);
            font-weight: 500;
            font-size: 1rem;
            margin: 0;
        }}
        
        /* Stats card */
        .calyx-stat {{
            background: var(--calyx-white);
            border: 1px solid var(--calyx-gray-10);
            border-left: 4px solid var(--calyx-primary);
            padding: 1rem 1.25rem;
        }}
        
        .calyx-stat-value {{
            font-size: 2rem;
            font-weight: 500;
            color: var(--calyx-primary);
            line-height: 1;
        }}
        
        .calyx-stat-label {{
            font-size: 0.875rem;
            color: var(--calyx-gray-60);
            margin-top: 0.25rem;
        }}
        
        /* Action links */
        .calyx-action {{
            color: var(--calyx-primary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.875rem;
        }}
        
        .calyx-action:hover {{
            color: var(--calyx-primary-light);
            text-decoration: underline;
        }}
        
        /* Logo area */
        .calyx-logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 1rem 0;
            margin-bottom: 1rem;
        }}
        
        .calyx-logo-mark {{
            width: 40px;
            height: 40px;
        }}
        
        .calyx-logo-text {{
            font-family: 'DM Sans', sans-serif;
            font-weight: 400;
            font-size: 1.25rem;
            letter-spacing: 0.15em;
            color: var(--calyx-white);
        }}
        
        .calyx-logo-subtitle {{
            font-size: 0.625rem;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: rgba(255,255,255,0.8);
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0;
            border-bottom: 2px solid var(--calyx-gray-10);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 0;
            padding: 0.75rem 1.5rem;
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
            color: var(--calyx-gray-60);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: var(--calyx-white);
            color: var(--calyx-primary);
            border-bottom: 2px solid var(--calyx-primary);
        }}
        
        /* Form sections */
        .form-section {{
            background: var(--calyx-gray-5);
            border-left: 3px solid var(--calyx-primary);
            padding: 1rem 1.25rem;
            margin: 1rem 0;
        }}
        
        .form-section-title {{
            font-weight: 500;
            color: var(--calyx-gray-90);
            margin-bottom: 0.5rem;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
            color: var(--calyx-gray-90);
            background: var(--calyx-white);
            border: 1px solid var(--calyx-gray-10);
        }}
        
        /* Alert/Info boxes */
        .stAlert {{
            border-radius: 0;
        }}
        
        /* Metric styling */
        [data-testid="stMetricValue"] {{
            color: var(--calyx-primary);
        }}
        
        /* Hide default streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--calyx-gray-5);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--calyx-gray-30);
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--calyx-gray-60);
        }}
    </style>
    """

# ============================================================================
# DATABASE SETUP
# ============================================================================

DB_PATH = "scar_system.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'supplier',
            vendor_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors(id)
        )
    ''')
    
    # Vendors table
    c.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            contact_name TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            address TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # SCARs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scar_number TEXT UNIQUE NOT NULL,
            vendor_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Open',
            priority TEXT DEFAULT 'Medium',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date DATE,
            
            -- Section 1: SCAR Details
            product_name TEXT,
            part_number TEXT,
            lot_number TEXT,
            quantity_affected INTEGER,
            
            -- Section 2: Non-Conformity Description
            nc_description TEXT,
            nc_category TEXT,
            detection_method TEXT,
            
            -- Section 3: Containment Actions
            containment_actions TEXT,
            containment_date DATE,
            containment_responsible TEXT,
            
            -- Section 4: Root Cause Analysis
            root_cause TEXT,
            rca_method TEXT,
            rca_completed_date DATE,
            
            -- Section 5: Corrective Action
            corrective_action TEXT,
            ca_responsible TEXT,
            ca_target_date DATE,
            ca_completion_date DATE,
            
            -- Section 6: Preventive Action
            preventive_action TEXT,
            pa_responsible TEXT,
            pa_target_date DATE,
            
            -- Section 7: Verification
            verification_method TEXT,
            verification_result TEXT,
            verification_date DATE,
            verified_by TEXT,
            
            closed_at TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Activity log table
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scar_id INTEGER,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scar_id) REFERENCES scars(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    
    # Create default admin if not exists
    admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
    try:
        c.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, role, status)
            VALUES (?, ?, ?, ?)
        ''', ("admin", admin_hash, "admin", "approved"))
        conn.commit()
    except:
        pass
    
    # Create demo vendor if not exists
    try:
        c.execute('''
            INSERT OR IGNORE INTO vendors (name, code, contact_name, contact_email, status)
            VALUES (?, ?, ?, ?, ?)
        ''', ("Demo Supplier Inc.", "DEMO-001", "John Smith", "john@demosupplier.com", "active"))
        conn.commit()
        
        # Create demo supplier user
        supplier_hash = hashlib.sha256("supplier123".encode()).hexdigest()
        c.execute("SELECT id FROM vendors WHERE code = 'DEMO-001'")
        vendor = c.fetchone()
        if vendor:
            c.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, role, vendor_id, status)
                VALUES (?, ?, ?, ?, ?)
            ''', ("supplier", supplier_hash, "supplier", vendor['id'], "approved"))
            conn.commit()
    except:
        pass
    
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================================================
# AUTHENTICATION
# ============================================================================

def authenticate(username, password):
    conn = get_db()
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute('''
        SELECT u.*, v.name as vendor_name, v.code as vendor_code
        FROM users u
        LEFT JOIN vendors v ON u.vendor_id = v.id
        WHERE u.username = ? AND u.password_hash = ?
    ''', (username, password_hash))
    user = c.fetchone()
    conn.close()
    return user

def check_login():
    if 'user' not in st.session_state or st.session_state.user is None:
        return False
    return True

def require_login():
    if not check_login():
        st.warning("Please log in to access this page.")
        st.stop()

def require_admin():
    require_login()
    if st.session_state.user['role'] != 'admin':
        st.error("Access denied. Admin privileges required.")
        st.stop()

# ============================================================================
# LOGO COMPONENT
# ============================================================================

def render_logo_text():
    """Simple text-based logo for sidebar"""
    return "CALYX CONTAINERS"

# ============================================================================
# GRID TABLE COMPONENT
# ============================================================================

def render_grid_table(headers, rows, row_key=None):
    """Render a clean grid-based table following Calyx brand guidelines"""
    html = '<table class="calyx-grid"><thead><tr>'
    for header in headers:
        html += f'<th>{header}</th>'
    html += '</tr></thead><tbody>'
    
    for row in rows:
        html += '<tr>'
        for cell in row:
            html += f'<td>{cell}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    return html

def get_status_badge(status):
    """Generate status badge HTML"""
    status_lower = status.lower()
    if status_lower == 'open':
        return f'<span class="status-badge status-open">{status}</span>'
    elif status_lower in ['pending', 'in progress']:
        return f'<span class="status-badge status-pending">{status}</span>'
    elif status_lower in ['closed', 'completed']:
        return f'<span class="status-badge status-closed">{status}</span>'
    elif status_lower == 'approved':
        return f'<span class="status-badge status-approved">{status}</span>'
    else:
        return f'<span class="status-badge">{status}</span>'

def get_role_badge(role):
    """Generate role badge HTML"""
    if role == 'admin':
        return f'<span class="status-badge role-admin">{role.upper()}</span>'
    else:
        return f'<span class="status-badge role-supplier">{role.upper()}</span>'

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    with st.sidebar:
        # Logo using Streamlit native markdown
        st.markdown("## ◇ CALYX")
        st.caption("CONTAINERS")
        
        st.divider()
        
        if check_login():
            user = st.session_state.user
            st.markdown(f"**User:** {user['username']}")
            st.markdown(f"**Role:** {user['role'].title()}")
            if user.get('vendor_name'):
                st.markdown(f"**Vendor:** {user['vendor_name']}")
            
            st.divider()
            
            # Navigation
            st.markdown("### Navigation")
            
            if user['role'] == 'admin':
                if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
                    st.session_state.page = "dashboard"
                    st.rerun()
                if st.button("📋 SCARs", key="nav_scars", use_container_width=True):
                    st.session_state.page = "scars"
                    st.rerun()
                if st.button("🏢 Vendors", key="nav_vendors", use_container_width=True):
                    st.session_state.page = "vendors"
                    st.rerun()
                if st.button("👥 Users", key="nav_users", use_container_width=True):
                    st.session_state.page = "users"
                    st.rerun()
            else:
                if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
                    st.session_state.page = "dashboard"
                    st.rerun()
                if st.button("📋 My SCARs", key="nav_scars", use_container_width=True):
                    st.session_state.page = "scars"
                    st.rerun()
            
            st.divider()
            
            if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = "login"
                st.rerun()
        else:
            st.markdown("### SCAR Management")
            st.markdown("Please log in to continue.")

# ============================================================================
# LOGIN PAGE
# ============================================================================

def login_page():
    st.markdown("# SCAR Management System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Sign In")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        if user['status'] != 'approved':
                            st.error("Your account is pending approval.")
                        else:
                            st.session_state.user = dict(user)
                            st.session_state.page = "dashboard"
                            st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.warning("Please enter username and password")
        
        # Demo credentials info
        st.divider()
        st.caption("Demo Credentials")
        st.info("**Admin:** admin / admin123\n\n**Supplier:** supplier / supplier123")

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

def dashboard_page():
    require_login()
    user = st.session_state.user
    
    st.markdown("# Dashboard")
    st.markdown("---")
    
    conn = get_db()
    c = conn.cursor()
    
    # Get statistics based on role
    if user['role'] == 'admin':
        c.execute("SELECT COUNT(*) FROM scars")
        total_scars = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM scars WHERE status = 'Open'")
        open_scars = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM scars WHERE status = 'Closed'")
        closed_scars = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM vendors WHERE status = 'active'")
        active_vendors = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE status = 'pending'")
        pending_users = c.fetchone()[0]
    else:
        vendor_id = user['vendor_id']
        c.execute("SELECT COUNT(*) FROM scars WHERE vendor_id = ?", (vendor_id,))
        total_scars = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM scars WHERE vendor_id = ? AND status = 'Open'", (vendor_id,))
        open_scars = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM scars WHERE vendor_id = ? AND status = 'Closed'", (vendor_id,))
        closed_scars = c.fetchone()[0]
        
        active_vendors = None
        pending_users = None
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total SCARs", total_scars)
    
    with col2:
        st.metric("Open SCARs", open_scars)
    
    with col3:
        st.metric("Closed SCARs", closed_scars)
    
    if user['role'] == 'admin':
        with col4:
            st.metric("Active Vendors", active_vendors)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent SCARs
    st.markdown("### Recent SCARs")
    
    if user['role'] == 'admin':
        c.execute('''
            SELECT s.*, v.name as vendor_name, v.code as vendor_code
            FROM scars s
            LEFT JOIN vendors v ON s.vendor_id = v.id
            ORDER BY s.created_at DESC
            LIMIT 10
        ''')
    else:
        c.execute('''
            SELECT s.*, v.name as vendor_name, v.code as vendor_code
            FROM scars s
            LEFT JOIN vendors v ON s.vendor_id = v.id
            WHERE s.vendor_id = ?
            ORDER BY s.created_at DESC
            LIMIT 10
        ''', (user['vendor_id'],))
    
    scars = c.fetchall()
    conn.close()
    
    if scars:
        headers = ["SCAR #", "Vendor", "Product", "Status", "Priority", "Created"]
        rows = []
        for scar in scars:
            rows.append([
                scar['scar_number'],
                scar['vendor_name'] or '-',
                scar['product_name'] or '-',
                get_status_badge(scar['status']),
                scar['priority'],
                scar['created_at'][:10] if scar['created_at'] else '-'
            ])
        
        st.markdown(render_grid_table(headers, rows), unsafe_allow_html=True)
    else:
        st.info("No SCARs found.")
    
    # Pending users alert for admin
    if user['role'] == 'admin' and pending_users > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(f"⚠️ {pending_users} user(s) pending approval. Go to Users to review.")

# ============================================================================
# SCARS PAGE
# ============================================================================

def scars_page():
    require_login()
    user = st.session_state.user
    
    st.markdown("# SCAR Management")
    st.markdown("---")
    
    # Create new SCAR (admin only)
    if user['role'] == 'admin':
        with st.expander("➕ Create New SCAR", expanded=False):
            create_scar_form()
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Status", ["All", "Open", "In Progress", "Closed"])
    
    with col2:
        priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
    
    conn = get_db()
    c = conn.cursor()
    
    # Build query
    query = '''
        SELECT s.*, v.name as vendor_name, v.code as vendor_code
        FROM scars s
        LEFT JOIN vendors v ON s.vendor_id = v.id
        WHERE 1=1
    '''
    params = []
    
    if user['role'] != 'admin':
        query += " AND s.vendor_id = ?"
        params.append(user['vendor_id'])
    
    if status_filter != "All":
        query += " AND s.status = ?"
        params.append(status_filter)
    
    if priority_filter != "All":
        query += " AND s.priority = ?"
        params.append(priority_filter)
    
    query += " ORDER BY s.created_at DESC"
    
    c.execute(query, params)
    scars = c.fetchall()
    conn.close()
    
    st.markdown(f"### SCARs ({len(scars)} total)")
    
    if scars:
        headers = ["SCAR #", "Vendor", "Product", "Status", "Priority", "Due Date", "Actions"]
        rows = []
        
        for scar in scars:
            action_btn = f'<span class="calyx-action" style="cursor: pointer;">View Details</span>'
            rows.append([
                scar['scar_number'],
                f"{scar['vendor_code']} - {scar['vendor_name']}" if scar['vendor_name'] else '-',
                scar['product_name'] or '-',
                get_status_badge(scar['status']),
                scar['priority'],
                scar['due_date'] or '-',
                action_btn
            ])
        
        st.markdown(render_grid_table(headers, rows), unsafe_allow_html=True)
        
        # SCAR details expansion
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### SCAR Details")
        
        scar_numbers = [s['scar_number'] for s in scars]
        selected_scar = st.selectbox("Select SCAR to view/edit:", ["Select..."] + scar_numbers)
        
        if selected_scar != "Select...":
            scar_detail_view(selected_scar)
    else:
        st.info("No SCARs found matching the criteria.")

def create_scar_form():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, code FROM vendors WHERE status = 'active' ORDER BY name")
    vendors = c.fetchall()
    conn.close()
    
    if not vendors:
        st.warning("No active vendors. Please add a vendor first.")
        return
    
    with st.form("new_scar_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            vendor_options = {f"{v['code']} - {v['name']}": v['id'] for v in vendors}
            selected_vendor = st.selectbox("Vendor *", options=list(vendor_options.keys()))
            product_name = st.text_input("Product Name *")
            part_number = st.text_input("Part Number")
        
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            due_date = st.date_input("Due Date")
            lot_number = st.text_input("Lot Number")
        
        nc_description = st.text_area("Non-Conformity Description *")
        
        submitted = st.form_submit_button("Create SCAR", use_container_width=True)
        
        if submitted:
            if selected_vendor and product_name and nc_description:
                vendor_id = vendor_options[selected_vendor]
                scar_number = f"SCAR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                conn = get_db()
                c = conn.cursor()
                c.execute('''
                    INSERT INTO scars (scar_number, vendor_id, product_name, part_number, 
                                      lot_number, priority, due_date, nc_description, 
                                      created_by, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')
                ''', (scar_number, vendor_id, product_name, part_number, lot_number, 
                      priority, due_date, nc_description, st.session_state.user['id']))
                
                # Log activity
                c.execute('''
                    INSERT INTO activity_log (scar_id, user_id, action, details)
                    VALUES (?, ?, ?, ?)
                ''', (c.lastrowid, st.session_state.user['id'], 'Created', f'SCAR {scar_number} created'))
                
                conn.commit()
                conn.close()
                
                st.success(f"SCAR {scar_number} created successfully!")
                st.rerun()
            else:
                st.error("Please fill in all required fields.")

def scar_detail_view(scar_number):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT s.*, v.name as vendor_name, v.code as vendor_code
        FROM scars s
        LEFT JOIN vendors v ON s.vendor_id = v.id
        WHERE s.scar_number = ?
    ''', (scar_number,))
    scar = c.fetchone()
    
    if not scar:
        st.error("SCAR not found")
        return
    
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    
    # SCAR Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(scar['scar_number'])
        st.caption(f"{scar['vendor_code']} - {scar['vendor_name']}")
    with col2:
        status_color = "🟢" if scar['status'] == 'Closed' else "🟡" if scar['status'] == 'In Progress' else "🔵"
        st.markdown(f"**Status:** {status_color} {scar['status']}")
    
    # Tabs for different sections
    tabs = st.tabs([
        "1. Details", 
        "2. Non-Conformity", 
        "3. Containment", 
        "4. Root Cause",
        "5. Corrective Action",
        "6. Preventive Action",
        "7. Verification",
        "Activity Log"
    ])
    
    # Tab 1: Details
    with tabs[0]:
        with st.form("scar_details_form"):
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("Product Name", value=scar['product_name'] or '')
                part_number = st.text_input("Part Number", value=scar['part_number'] or '')
                lot_number = st.text_input("Lot Number", value=scar['lot_number'] or '')
            with col2:
                quantity_affected = st.number_input("Quantity Affected", value=scar['quantity_affected'] or 0)
                priority = st.selectbox("Priority", ["Low", "Medium", "High"], 
                                       index=["Low", "Medium", "High"].index(scar['priority']))
                status = st.selectbox("Status", ["Open", "In Progress", "Closed"],
                                     index=["Open", "In Progress", "Closed"].index(scar['status']) if scar['status'] in ["Open", "In Progress", "Closed"] else 0,
                                     disabled=not is_admin)
            
            if st.form_submit_button("Update Details", use_container_width=True):
                c.execute('''
                    UPDATE scars SET product_name=?, part_number=?, lot_number=?, 
                                    quantity_affected=?, priority=?, status=?
                    WHERE id=?
                ''', (product_name, part_number, lot_number, quantity_affected, priority, status, scar['id']))
                conn.commit()
                st.success("Details updated!")
                st.rerun()
    
    # Tab 2: Non-Conformity
    with tabs[1]:
        with st.form("nc_form"):
            nc_description = st.text_area("Non-Conformity Description", 
                                         value=scar['nc_description'] or '', height=150)
            nc_category = st.selectbox("Category", 
                                      ["", "Dimensional", "Material", "Functional", "Documentation", "Other"],
                                      index=["", "Dimensional", "Material", "Functional", "Documentation", "Other"].index(scar['nc_category']) if scar['nc_category'] else 0)
            detection_method = st.text_input("Detection Method", value=scar['detection_method'] or '')
            
            if st.form_submit_button("Update Non-Conformity", use_container_width=True):
                c.execute('''
                    UPDATE scars SET nc_description=?, nc_category=?, detection_method=?
                    WHERE id=?
                ''', (nc_description, nc_category, detection_method, scar['id']))
                conn.commit()
                st.success("Non-conformity details updated!")
                st.rerun()
    
    # Tab 3: Containment
    with tabs[2]:
        with st.form("containment_form"):
            containment_actions = st.text_area("Containment Actions", 
                                              value=scar['containment_actions'] or '', height=150)
            col1, col2 = st.columns(2)
            with col1:
                containment_date = st.date_input("Containment Date", 
                                                value=datetime.strptime(scar['containment_date'], '%Y-%m-%d').date() if scar['containment_date'] else None)
            with col2:
                containment_responsible = st.text_input("Responsible Party", 
                                                       value=scar['containment_responsible'] or '')
            
            if st.form_submit_button("Update Containment", use_container_width=True):
                c.execute('''
                    UPDATE scars SET containment_actions=?, containment_date=?, containment_responsible=?
                    WHERE id=?
                ''', (containment_actions, containment_date, containment_responsible, scar['id']))
                conn.commit()
                st.success("Containment actions updated!")
                st.rerun()
    
    # Tab 4: Root Cause
    with tabs[3]:
        with st.form("rca_form"):
            root_cause = st.text_area("Root Cause Analysis", 
                                     value=scar['root_cause'] or '', height=150)
            col1, col2 = st.columns(2)
            with col1:
                rca_method = st.selectbox("Analysis Method", 
                                         ["", "5 Whys", "Fishbone/Ishikawa", "FMEA", "8D", "Other"],
                                         index=["", "5 Whys", "Fishbone/Ishikawa", "FMEA", "8D", "Other"].index(scar['rca_method']) if scar['rca_method'] else 0)
            with col2:
                rca_completed_date = st.date_input("RCA Completed Date",
                                                   value=datetime.strptime(scar['rca_completed_date'], '%Y-%m-%d').date() if scar['rca_completed_date'] else None)
            
            if st.form_submit_button("Update Root Cause", use_container_width=True):
                c.execute('''
                    UPDATE scars SET root_cause=?, rca_method=?, rca_completed_date=?
                    WHERE id=?
                ''', (root_cause, rca_method, rca_completed_date, scar['id']))
                conn.commit()
                st.success("Root cause analysis updated!")
                st.rerun()
    
    # Tab 5: Corrective Action
    with tabs[4]:
        with st.form("ca_form"):
            corrective_action = st.text_area("Corrective Action", 
                                            value=scar['corrective_action'] or '', height=150)
            col1, col2 = st.columns(2)
            with col1:
                ca_responsible = st.text_input("Responsible Party", value=scar['ca_responsible'] or '')
                ca_target_date = st.date_input("Target Date",
                                               value=datetime.strptime(scar['ca_target_date'], '%Y-%m-%d').date() if scar['ca_target_date'] else None)
            with col2:
                ca_completion_date = st.date_input("Completion Date",
                                                   value=datetime.strptime(scar['ca_completion_date'], '%Y-%m-%d').date() if scar['ca_completion_date'] else None)
            
            if st.form_submit_button("Update Corrective Action", use_container_width=True):
                c.execute('''
                    UPDATE scars SET corrective_action=?, ca_responsible=?, ca_target_date=?, ca_completion_date=?
                    WHERE id=?
                ''', (corrective_action, ca_responsible, ca_target_date, ca_completion_date, scar['id']))
                conn.commit()
                st.success("Corrective action updated!")
                st.rerun()
    
    # Tab 6: Preventive Action
    with tabs[5]:
        with st.form("pa_form"):
            preventive_action = st.text_area("Preventive Action", 
                                            value=scar['preventive_action'] or '', height=150)
            col1, col2 = st.columns(2)
            with col1:
                pa_responsible = st.text_input("Responsible Party", value=scar['pa_responsible'] or '')
            with col2:
                pa_target_date = st.date_input("Target Date",
                                               value=datetime.strptime(scar['pa_target_date'], '%Y-%m-%d').date() if scar['pa_target_date'] else None)
            
            if st.form_submit_button("Update Preventive Action", use_container_width=True):
                c.execute('''
                    UPDATE scars SET preventive_action=?, pa_responsible=?, pa_target_date=?
                    WHERE id=?
                ''', (preventive_action, pa_responsible, pa_target_date, scar['id']))
                conn.commit()
                st.success("Preventive action updated!")
                st.rerun()
    
    # Tab 7: Verification
    with tabs[6]:
        with st.form("verification_form"):
            verification_method = st.text_area("Verification Method", 
                                              value=scar['verification_method'] or '', height=100)
            verification_result = st.selectbox("Result", 
                                              ["", "Effective", "Not Effective", "Pending"],
                                              index=["", "Effective", "Not Effective", "Pending"].index(scar['verification_result']) if scar['verification_result'] else 0,
                                              disabled=not is_admin)
            col1, col2 = st.columns(2)
            with col1:
                verification_date = st.date_input("Verification Date",
                                                  value=datetime.strptime(scar['verification_date'], '%Y-%m-%d').date() if scar['verification_date'] else None,
                                                  disabled=not is_admin)
            with col2:
                verified_by = st.text_input("Verified By", value=scar['verified_by'] or '', disabled=not is_admin)
            
            if st.form_submit_button("Update Verification", use_container_width=True, disabled=not is_admin):
                c.execute('''
                    UPDATE scars SET verification_method=?, verification_result=?, 
                                    verification_date=?, verified_by=?
                    WHERE id=?
                ''', (verification_method, verification_result, verification_date, verified_by, scar['id']))
                conn.commit()
                st.success("Verification updated!")
                st.rerun()
    
    # Tab 8: Activity Log
    with tabs[7]:
        c.execute('''
            SELECT al.*, u.username
            FROM activity_log al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE al.scar_id = ?
            ORDER BY al.created_at DESC
        ''', (scar['id'],))
        activities = c.fetchall()
        
        if activities:
            headers = ["Date/Time", "User", "Action", "Details"]
            rows = []
            for act in activities:
                rows.append([
                    act['created_at'],
                    act['username'] or 'System',
                    act['action'],
                    act['details'] or '-'
                ])
            st.markdown(render_grid_table(headers, rows), unsafe_allow_html=True)
        else:
            st.info("No activity recorded yet.")
    
    conn.close()

# ============================================================================
# VENDORS PAGE
# ============================================================================

def vendors_page():
    require_admin()
    
    st.markdown("# Vendor Management")
    st.markdown("---")
    
    # Create new vendor
    with st.expander("➕ Add New Vendor", expanded=False):
        with st.form("new_vendor_form"):
            col1, col2 = st.columns(2)
            with col1:
                vendor_name = st.text_input("Vendor Name *")
                vendor_code = st.text_input("Vendor Code *")
                contact_name = st.text_input("Contact Name")
            with col2:
                contact_email = st.text_input("Contact Email")
                contact_phone = st.text_input("Contact Phone")
                status = st.selectbox("Status", ["active", "inactive"])
            
            address = st.text_area("Address", height=80)
            
            if st.form_submit_button("Add Vendor", use_container_width=True):
                if vendor_name and vendor_code:
                    conn = get_db()
                    c = conn.cursor()
                    try:
                        c.execute('''
                            INSERT INTO vendors (name, code, contact_name, contact_email, 
                                               contact_phone, address, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (vendor_name, vendor_code, contact_name, contact_email, 
                              contact_phone, address, status))
                        conn.commit()
                        st.success(f"Vendor '{vendor_name}' added successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Vendor code already exists.")
                    finally:
                        conn.close()
                else:
                    st.error("Please fill in required fields.")
    
    # Vendor list
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT v.*, 
               (SELECT COUNT(*) FROM scars WHERE vendor_id = v.id) as scar_count
        FROM vendors v
        ORDER BY v.name
    ''')
    vendors = c.fetchall()
    conn.close()
    
    st.markdown(f"### Vendors ({len(vendors)} total)")
    
    if vendors:
        headers = ["Code", "Name", "Contact", "Email", "Phone", "Status", "SCARs"]
        rows = []
        for vendor in vendors:
            status_badge = '<span class="status-badge status-closed">ACTIVE</span>' if vendor['status'] == 'active' else '<span class="status-badge status-pending">INACTIVE</span>'
            rows.append([
                vendor['code'],
                vendor['name'],
                vendor['contact_name'] or '-',
                vendor['contact_email'] or '-',
                vendor['contact_phone'] or '-',
                status_badge,
                str(vendor['scar_count'])
            ])
        
        st.markdown(render_grid_table(headers, rows), unsafe_allow_html=True)
        
        # Edit vendor
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Edit Vendor")
        
        vendor_options = {f"{v['code']} - {v['name']}": v['id'] for v in vendors}
        selected_vendor = st.selectbox("Select vendor to edit:", ["Select..."] + list(vendor_options.keys()))
        
        if selected_vendor != "Select...":
            vendor_id = vendor_options[selected_vendor]
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,))
            vendor = c.fetchone()
            conn.close()
            
            if vendor:
                with st.form("edit_vendor_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("Vendor Name", value=vendor['name'])
                        edit_contact = st.text_input("Contact Name", value=vendor['contact_name'] or '')
                        edit_email = st.text_input("Contact Email", value=vendor['contact_email'] or '')
                    with col2:
                        edit_phone = st.text_input("Contact Phone", value=vendor['contact_phone'] or '')
                        edit_status = st.selectbox("Status", ["active", "inactive"],
                                                   index=0 if vendor['status'] == 'active' else 1)
                    
                    edit_address = st.text_area("Address", value=vendor['address'] or '')
                    
                    if st.form_submit_button("Update Vendor", use_container_width=True):
                        conn = get_db()
                        c = conn.cursor()
                        c.execute('''
                            UPDATE vendors SET name=?, contact_name=?, contact_email=?,
                                              contact_phone=?, address=?, status=?
                            WHERE id=?
                        ''', (edit_name, edit_contact, edit_email, edit_phone, edit_address, edit_status, vendor_id))
                        conn.commit()
                        conn.close()
                        st.success("Vendor updated!")
                        st.rerun()
    else:
        st.info("No vendors found. Add a vendor to get started.")

# ============================================================================
# USERS PAGE
# ============================================================================

def users_page():
    require_admin()
    
    st.markdown("# User Management")
    st.markdown("---")
    
    conn = get_db()
    c = conn.cursor()
    
    # Pending approvals alert
    c.execute("SELECT COUNT(*) FROM users WHERE status = 'pending'")
    pending_count = c.fetchone()[0]
    
    if pending_count > 0:
        st.warning(f"⚠️ {pending_count} user(s) pending approval")
    
    # Create new user
    with st.expander("➕ Add New User", expanded=False):
        c.execute("SELECT id, name, code FROM vendors WHERE status = 'active' ORDER BY name")
        vendors = c.fetchall()
        
        with st.form("new_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username *")
                new_password = st.text_input("Password *", type="password")
            with col2:
                new_role = st.selectbox("Role", ["supplier", "admin"])
                if new_role == "supplier" and vendors:
                    vendor_options = {"None": None}
                    vendor_options.update({f"{v['code']} - {v['name']}": v['id'] for v in vendors})
                    new_vendor = st.selectbox("Assign to Vendor", options=list(vendor_options.keys()))
                else:
                    new_vendor = None
            
            new_status = st.selectbox("Status", ["approved", "pending"])
            
            if st.form_submit_button("Create User", use_container_width=True):
                if new_username and new_password:
                    try:
                        vendor_id = vendor_options.get(new_vendor) if new_vendor else None
                        c.execute('''
                            INSERT INTO users (username, password_hash, role, vendor_id, status)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (new_username, hash_password(new_password), new_role, vendor_id, new_status))
                        conn.commit()
                        st.success(f"User '{new_username}' created!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")
                else:
                    st.error("Please fill in required fields.")
    
    # User list
    c.execute('''
        SELECT u.*, v.name as vendor_name, v.code as vendor_code
        FROM users u
        LEFT JOIN vendors v ON u.vendor_id = v.id
        ORDER BY u.created_at DESC
    ''')
    users = c.fetchall()
    conn.close()
    
    st.markdown(f"### Users ({len(users)} total)")
    
    if users:
        headers = ["Username", "Role", "Vendor", "Status", "Created"]
        rows = []
        for user in users:
            vendor_info = f"{user['vendor_code']} - {user['vendor_name']}" if user['vendor_name'] else '-'
            status_badge = get_status_badge('approved' if user['status'] == 'approved' else 'pending')
            rows.append([
                user['username'],
                get_role_badge(user['role']),
                vendor_info,
                status_badge,
                user['created_at'][:10] if user['created_at'] else '-'
            ])
        
        st.markdown(render_grid_table(headers, rows), unsafe_allow_html=True)
        
        # User management actions
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### User Actions")
        
        user_options = {u['username']: u['id'] for u in users if u['username'] != 'admin'}
        selected_user = st.selectbox("Select user:", ["Select..."] + list(user_options.keys()))
        
        if selected_user != "Select...":
            user_id = user_options[selected_user]
            
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = c.fetchone()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if user['status'] == 'pending':
                    if st.button("✓ Approve User", use_container_width=True):
                        c.execute("UPDATE users SET status = 'approved' WHERE id = ?", (user_id,))
                        conn.commit()
                        st.success("User approved!")
                        st.rerun()
                else:
                    st.info("User is already approved")
            
            with col2:
                if st.button("🔑 Reset Password", use_container_width=True):
                    new_pw = "password123"
                    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", 
                             (hash_password(new_pw), user_id))
                    conn.commit()
                    st.success(f"Password reset to: {new_pw}")
            
            with col3:
                if st.button("🗑️ Delete User", use_container_width=True, type="secondary"):
                    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
                    conn.commit()
                    st.success("User deleted!")
                    st.rerun()
            
            conn.close()
    else:
        st.info("No users found.")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    st.set_page_config(
        page_title="Calyx Containers | SCAR Management",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply Calyx brand styles
    st.markdown(get_calyx_styles(), unsafe_allow_html=True)
    
    # Initialize database
    init_db()
    
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    
    # Render sidebar
    render_sidebar()
    
    # Route to appropriate page
    if not check_login():
        login_page()
    else:
        page = st.session_state.page
        
        if page == "dashboard":
            dashboard_page()
        elif page == "scars":
            scars_page()
        elif page == "vendors":
            vendors_page()
        elif page == "users":
            users_page()
        else:
            dashboard_page()

if __name__ == "__main__":
    main()
