"""
SCAR Management System for Calyx Containers
Supabase-backed version with grid-based layouts
"""

import streamlit as st
from datetime import datetime, timedelta, date
import os

# Import database functions (Supabase-backed)
from database import (
    init_database,
    get_password_hash,
    verify_password,
    get_user_by_email,
    get_user_by_id,
    get_all_users,
    create_user,
    update_user,
    update_user_password,
    delete_user,
    get_pending_users_count,
    get_all_vendors,
    get_vendor_by_id,
    create_vendor,
    update_vendor,
    delete_vendor,
    get_vendor_contacts,
    create_vendor_contact,
    delete_vendor_contact,
    get_all_scars,
    get_scar_by_id,
    create_scar,
    update_scar,
    submit_scar,
    verify_scar,
    get_scar_activity,
    get_scar_stats,
    get_next_scar_number,
    upload_attachment,
    get_scar_attachments,
    get_attachment_download_url,
    delete_attachment,
)

# Default passwords — if user logs in with one of these, force a change
DEFAULT_PASSWORDS = {"admin123", "supplier123", "password123"}

# ============================================================================
# CALYX BRAND CONFIGURATION
# ============================================================================

CALYX_COLORS = {
    "primary": "#0033A1",
    "primary_light": "#004FFF",
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
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

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

        html, body, [class*="css"] {{
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .main .block-container {{
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}

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

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, var(--calyx-primary) 0%, var(--calyx-ocean-blue) 100%);
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{ color: var(--calyx-white); }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {{
            color: var(--calyx-white) !important;
        }}
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
            color: rgba(255,255,255,0.8) !important;
        }}
        [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.2); }}

        /* Buttons */
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
        .stButton > button[kind="secondary"] {{
            background-color: var(--calyx-white);
            color: var(--calyx-primary);
            border: 1px solid var(--calyx-primary);
        }}

        /* Inputs */
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

        /* Grid Table */
        .calyx-grid {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'DM Sans', sans-serif;
            background: var(--calyx-white);
            border: 1px solid var(--calyx-gray-10);
        }}
        .calyx-grid thead {{ background: var(--calyx-primary); }}
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
        .calyx-grid tr:hover {{ background: var(--calyx-gray-5); }}
        .calyx-grid tr:last-child td {{ border-bottom: none; }}

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
        .status-open {{ background: var(--calyx-powder-blue); color: var(--calyx-primary); }}
        .status-pending {{ background: #FFF3CD; color: #856404; }}
        .status-closed {{ background: #D4EDDA; color: #155724; }}
        .status-approved {{ background: var(--calyx-cloud-blue); color: var(--calyx-ocean-blue); }}
        .status-submitted {{ background: #E8DAEF; color: #6C3483; }}
        .role-admin {{ background: var(--calyx-primary); color: var(--calyx-white); }}
        .role-supplier {{ background: var(--calyx-gray-60); color: var(--calyx-white); }}

        /* Cards & Stats */
        .calyx-card {{
            background: var(--calyx-white);
            border: 1px solid var(--calyx-gray-10);
            padding: 1.5rem;
            margin-bottom: 1rem;
        }}
        .calyx-stat {{
            background: var(--calyx-white);
            border: 1px solid var(--calyx-gray-10);
            border-left: 4px solid var(--calyx-primary);
            padding: 1rem 1.25rem;
        }}
        .calyx-stat-value {{
            font-size: 2rem; font-weight: 500;
            color: var(--calyx-primary); line-height: 1;
        }}
        .calyx-stat-label {{
            font-size: 0.875rem; color: var(--calyx-gray-60); margin-top: 0.25rem;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{ gap: 0; border-bottom: 2px solid var(--calyx-gray-10); }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 0; padding: 0.75rem 1.5rem;
            font-family: 'DM Sans', sans-serif; font-weight: 500; color: var(--calyx-gray-60);
        }}
        .stTabs [aria-selected="true"] {{
            background: var(--calyx-white); color: var(--calyx-primary);
            border-bottom: 2px solid var(--calyx-primary);
        }}

        /* Misc */
        .form-section {{
            background: var(--calyx-gray-5); border-left: 3px solid var(--calyx-primary);
            padding: 1rem 1.25rem; margin: 1rem 0;
        }}
        .stAlert {{ border-radius: 0; }}
        [data-testid="stMetricValue"] {{ color: var(--calyx-primary); }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--calyx-gray-5); }}
        ::-webkit-scrollbar-thumb {{ background: var(--calyx-gray-30); }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--calyx-gray-60); }}
    </style>
    """

# ============================================================================
# AUTHENTICATION
# ============================================================================

def authenticate(email, password):
    user = get_user_by_email(email)
    if user and verify_password(password, user['password']):
        return user
    return None

def check_login():
    return st.session_state.get('user') is not None

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
# UI HELPER COMPONENTS
# ============================================================================

def render_grid_table(headers, rows):
    html = '<table class="calyx-grid"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for row in rows:
        html += '<tr>'
        for cell in row:
            html += f'<td>{cell}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

def get_status_badge(status):
    s = status.lower()
    css = {
        'open': 'status-open', 'new': 'status-open',
        'pending': 'status-pending', 'in progress': 'status-pending',
        'closed': 'status-closed', 'completed': 'status-closed',
        'approved': 'status-approved',
        'submitted': 'status-submitted',
    }.get(s, '')
    return f'<span class="status-badge {css}">{status}</span>'

def get_role_badge(role):
    css = 'role-admin' if role == 'admin' else 'role-supplier'
    return f'<span class="status-badge {css}">{role.upper()}</span>'

def get_severity_badge(severity):
    colors = {
        'minor': ('🟢', '#D4EDDA', '#155724'),
        'major': ('🟡', '#FFF3CD', '#856404'),
        'critical': ('🔴', '#F8D7DA', '#721C24'),
    }
    icon, bg, fg = colors.get(severity, ('⚪', '#E5E5E5', '#666666'))
    return f'<span class="status-badge" style="background:{bg};color:{fg};">{icon} {severity.upper()}</span>'

def parse_date(date_str):
    """Parse a date string from DB into a Python date, or None."""
    if not date_str:
        return None
    try:
        if isinstance(date_str, date):
            return date_str
        if 'T' in str(date_str):
            return datetime.fromisoformat(str(date_str).replace('Z', '+00:00')).date()
        return datetime.strptime(str(date_str), '%Y-%m-%d').date()
    except Exception:
        return None

def format_date(date_str):
    if not date_str:
        return "N/A"
    d = parse_date(date_str)
    return d.strftime("%m/%d/%y") if d else str(date_str)[:10]

def format_datetime(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
        return dt.strftime("%m/%d/%y %I:%M %p")
    except Exception:
        return str(date_str)

def navigate_to_scar(scar_id):
    """Set session state to show a specific SCAR detail view."""
    st.session_state.selected_scar_id = scar_id
    st.session_state.page = "scars"

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    with st.sidebar:
        st.markdown("## ◇ CALYX")
        st.caption("CONTAINERS")
        st.divider()

        if check_login():
            user = st.session_state.user
            st.markdown(f"**User:** {user['name']}")
            st.markdown(f"**Role:** {user['role'].title()}")
            if user.get('vendor_name'):
                st.markdown(f"**Vendor:** {user['vendor_name']}")

            st.divider()
            st.markdown("### Navigation")

            if user['role'] == 'admin':
                if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
                    st.session_state.page = "dashboard"
                    st.session_state.selected_scar_id = None
                    st.rerun()
                if st.button("📋 SCARs", key="nav_scars", use_container_width=True):
                    st.session_state.page = "scars"
                    st.session_state.selected_scar_id = None
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
                    st.session_state.selected_scar_id = None
                    st.rerun()
                if st.button("📋 My SCARs", key="nav_scars", use_container_width=True):
                    st.session_state.page = "scars"
                    st.session_state.selected_scar_id = None
                    st.rerun()

            st.divider()

            if st.button("🔑 Change Password", key="nav_password", use_container_width=True):
                st.session_state.page = "change_password"
                st.rerun()

            if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
                for k in ['user', 'force_password_change', 'selected_scar_id']:
                    st.session_state.pop(k, None)
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
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if email and password:
                    user = authenticate(email, password)
                    if user:
                        if user['status'] != 'approved':
                            st.error("Your account is pending approval.")
                        else:
                            st.session_state.user = user
                            # Force password change on default passwords
                            if password in DEFAULT_PASSWORDS:
                                st.session_state.force_password_change = True
                                st.session_state.page = "change_password"
                            else:
                                st.session_state.page = "dashboard"
                            st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.warning("Please enter email and password")

        st.divider()
        st.caption("Demo Credentials")
        st.info("**Admin:** admin@calyxcontainers.com / admin123\n\n**Supplier:** jsmith@pacificglass.com / supplier123")

# ============================================================================
# CHANGE PASSWORD PAGE
# ============================================================================

def change_password_page():
    require_login()
    user = st.session_state.user
    forced = st.session_state.get('force_password_change', False)

    st.markdown("# Change Password")
    st.markdown("---")

    if forced:
        st.warning("⚠️ You are using a default password. Please set a new password before continuing.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("change_password_form"):
            current_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")

            if st.form_submit_button("Update Password", use_container_width=True):
                if not current_pw or not new_pw or not confirm_pw:
                    st.error("Please fill in all fields.")
                elif not verify_password(current_pw, user['password']):
                    st.error("Current password is incorrect.")
                elif new_pw != confirm_pw:
                    st.error("New passwords do not match.")
                elif len(new_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_pw in DEFAULT_PASSWORDS:
                    st.error("Please choose a stronger password (not a default).")
                else:
                    update_user_password(user['id'], new_pw)
                    # Refresh user object
                    st.session_state.user = get_user_by_id(user['id'])
                    st.session_state.force_password_change = False
                    st.session_state.page = "dashboard"
                    st.success("✅ Password updated!")
                    st.rerun()

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

def dashboard_page():
    require_login()
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    vendor_id = None if is_admin else user.get('vendor_id')

    st.markdown("# Dashboard")
    st.markdown("---")

    stats = get_scar_stats(vendor_id)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total SCARs", stats.get('total', 0))
    with col2:
        st.metric("Open SCARs", stats.get('open', 0))
    with col3:
        st.metric("Closed SCARs", stats.get('closed', 0))
    if is_admin:
        with col4:
            st.metric("Awaiting Review", stats.get('submitted', 0))
    else:
        with col4:
            st.metric("Overdue", stats.get('overdue', 0))

    if stats.get('overdue', 0) > 0:
        st.warning(f"⚠️ {stats['overdue']} SCAR(s) are past their response due date!")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Recent SCARs")
    st.caption("Click a SCAR to view its details.")

    scars = get_all_scars(vendor_id=vendor_id)[:10]

    if scars:
        for scar in scars:
            scar_num = scar.get('scar_number', '-')
            vendor = scar.get('vendor_name') or '-'
            product = scar.get('product_name') or '-'
            status = scar.get('status', 'open').upper()
            severity = (scar.get('severity') or '-').upper()
            due = format_date(scar.get('response_due_date'))

            label = f"📋 {scar_num}  —  {vendor}  |  {product}  |  {status}  |  {severity}  |  Due: {due}"
            if st.button(label, key=f"dash_scar_{scar['id']}", use_container_width=True):
                navigate_to_scar(scar['id'])
                st.rerun()
    else:
        st.info("No SCARs found." + (" Create your first SCAR to get started." if is_admin else ""))

    if is_admin:
        pending = get_pending_users_count()
        if pending > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            st.warning(f"⚠️ {pending} user(s) pending approval. Go to Users to review.")

# ============================================================================
# SCARS PAGE
# ============================================================================

def scars_page():
    require_login()
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    vendor_id = None if is_admin else user.get('vendor_id')

    # If a specific SCAR was selected, show its detail view
    selected_id = st.session_state.get('selected_scar_id')
    if selected_id:
        if st.button("← Back to SCAR list"):
            st.session_state.selected_scar_id = None
            st.rerun()
        scar_detail_view(selected_id)
        return

    st.markdown("# SCAR Management")
    st.markdown("---")

    if is_admin:
        with st.expander("➕ Create New SCAR", expanded=False):
            create_scar_form()

    # Filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Open", "Submitted", "Closed"])
    with col2:
        severity_filter = st.selectbox("Severity", ["All", "Minor", "Major", "Critical"])
    with col3:
        search = st.text_input("🔍 Search", placeholder="SCAR number, product...")

    status_val = None if status_filter == "All" else status_filter.lower()
    scars = get_all_scars(vendor_id=vendor_id, status=status_val)

    if severity_filter != "All":
        scars = [s for s in scars if s.get('severity') == severity_filter.lower()]
    if search:
        q = search.lower()
        scars = [s for s in scars if
                 q in s.get('scar_number', '').lower() or
                 q in (s.get('product_name') or '').lower() or
                 q in (s.get('vendor_name') or '').lower() or
                 q in (s.get('defect_type') or '').lower()]

    st.markdown(f"### SCARs ({len(scars)} total)")

    if scars:
        # Column headers
        hdr = st.columns([1.5, 2, 2, 1.2, 1.2, 1.3, 1.2])
        hdr[0].markdown("**SCAR #**")
        hdr[1].markdown("**Vendor**")
        hdr[2].markdown("**Product**")
        hdr[3].markdown("**Status**")
        hdr[4].markdown("**Severity**")
        hdr[5].markdown("**Due Date**")
        hdr[6].markdown("**Action**")
        st.markdown("---")

        for scar in scars:
            cols = st.columns([1.5, 2, 2, 1.2, 1.2, 1.3, 1.2])
            cols[0].write(scar.get('scar_number', '-'))
            cols[1].write(scar.get('vendor_name') or '-')
            cols[2].write(scar.get('product_name') or '-')
            cols[3].markdown(get_status_badge(scar.get('status', 'open')), unsafe_allow_html=True)
            if scar.get('severity'):
                cols[4].markdown(get_severity_badge(scar['severity']), unsafe_allow_html=True)
            else:
                cols[4].write('-')
            cols[5].write(format_date(scar.get('response_due_date')))
            if cols[6].button("View", key=f"view_{scar['id']}"):
                navigate_to_scar(scar['id'])
                st.rerun()
    else:
        st.info("No SCARs found matching the criteria.")

# ============================================================================
# CREATE SCAR FORM
# ============================================================================

def create_scar_form():
    vendors = get_all_vendors()
    if not vendors:
        st.warning("No vendors found. Please add a vendor first.")
        return

    with st.form("new_scar_form"):
        st.markdown("### Section 1: SCAR Details")
        col1, col2 = st.columns(2)

        with col1:
            vendor_options = {v['name']: v['id'] for v in vendors}
            selected_vendor = st.selectbox("Vendor *", options=list(vendor_options.keys()))
            date_issued = st.date_input("Date Issued *", value=datetime.now().date())
            response_due_date = st.date_input("Response Due Date *",
                value=(datetime.now() + timedelta(days=14)).date())
            ncr_number = st.text_input("NCR #", placeholder="e.g., NCR-2026-0001")

        with col2:
            vendor_id = vendor_options.get(selected_vendor)
            contacts = get_vendor_contacts(vendor_id) if vendor_id else []
            if contacts:
                contact_options = {f"{c['name']} ({c['email']})": c['id'] for c in contacts}
                selected_contact = st.selectbox("Vendor Contact *", options=list(contact_options.keys()))
            else:
                st.text_input("Vendor Contact", value="No contacts — add in Vendors page", disabled=True)
                selected_contact = None
            po_so_number = st.text_input("PO/SO #", placeholder="e.g., PO-12345")
            part_sku_number = st.text_input("Part/SKU #", placeholder="e.g., SKU-12345")

        col1, col2, col3 = st.columns(3)
        with col1:
            affected_quantity = st.number_input("Affected Quantity", min_value=0, value=0)
        with col2:
            lot_numbers = st.text_input("Lot Number(s)", placeholder="e.g., LOT-2026-A001")

        st.markdown("---")
        st.markdown("### Section 2: Non-Conformity")

        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name *", placeholder="e.g., 500ml Clear Glass Jar")
        with col2:
            defect_type = st.selectbox("Defect Type *",
                ["", "Dimensional", "Visual", "Functional", "Labeling",
                 "Packaging", "Contamination", "Documentation", "Other"])

        nonconformity_description = st.text_area("Non-Conformity Description *", height=150,
            placeholder="Describe: what was found, where discovered, impact on quality/safety")

        severity = st.radio("Severity *", options=["minor", "major", "critical"],
            format_func=lambda x: {"minor": "🟢 Minor", "major": "🟡 Major", "critical": "🔴 Critical"}[x],
            horizontal=True)

        submitted = st.form_submit_button("📋 Create SCAR", use_container_width=True)

        if submitted:
            errors = []
            if not selected_vendor: errors.append("Select a vendor")
            if not selected_contact and contacts: errors.append("Select a vendor contact")
            if not product_name: errors.append("Enter a product name")
            if not defect_type: errors.append("Select a defect type")
            if not nonconformity_description: errors.append("Provide a non-conformity description")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                scar_data = {
                    'date_issued': date_issued.isoformat(),
                    'response_due_date': response_due_date.isoformat(),
                    'vendor_id': vendor_id,
                    'vendor_contact_id': contact_options[selected_contact] if selected_contact else None,
                    'ncr_number': ncr_number or None,
                    'po_so_number': po_so_number or None,
                    'part_sku_number': part_sku_number or None,
                    'affected_quantity': affected_quantity if affected_quantity > 0 else None,
                    'lot_numbers': lot_numbers or None,
                    'product_name': product_name,
                    'defect_type': defect_type,
                    'nonconformity_description': nonconformity_description,
                    'severity': severity,
                }
                try:
                    new_scar = create_scar(scar_data, st.session_state.user['id'])
                    st.success(f"✅ SCAR {new_scar['scar_number']} created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create SCAR: {str(e)}")

# ============================================================================
# SCAR DETAIL VIEW
# ============================================================================

def scar_detail_view(scar_id):
    scar = get_scar_by_id(scar_id)
    if not scar:
        st.error("SCAR not found")
        return

    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    can_edit = scar['status'] in ['new', 'open']
    can_submit = user['role'] == 'supplier' and scar['status'] == 'open'
    can_verify = is_admin and scar['status'] == 'submitted'

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(scar['scar_number'])
        st.caption(f"{scar.get('vendor_name', 'Unknown Vendor')} | {scar.get('product_name', '')}")
    with col2:
        icon = "🟢" if scar['status'] == 'closed' else "🟡" if scar['status'] == 'submitted' else "🔵"
        st.markdown(f"**Status:** {icon} {scar['status'].upper()}")
        if scar.get('severity'):
            st.markdown(f"**Severity:** {scar['severity'].upper()}")

    tabs = st.tabs([
        "1. Details", "2. Non-Conformity", "3. Containment", "4. Root Cause",
        "5. Corrective Action", "6. Preventive Action", "7. Verification",
        "📎 Attachments", "📜 Activity Log"
    ])

    # --- Tab 1: Details (read-only) ---
    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("SCAR Number", value=scar['scar_number'], disabled=True)
            st.text_input("Date Issued", value=format_date(scar.get('date_issued')), disabled=True)
            st.text_input("Response Due Date", value=format_date(scar.get('response_due_date')), disabled=True)
            st.text_input("NCR #", value=scar.get('ncr_number') or '', disabled=True)
        with col2:
            st.text_input("Supplier", value=scar.get('vendor_name') or '', disabled=True)
            st.text_input("Contact", value=scar.get('contact_name') or '', disabled=True)
            st.text_input("PO/SO #", value=scar.get('po_so_number') or '', disabled=True)
            st.text_input("Part/SKU #", value=scar.get('part_sku_number') or '', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Affected Quantity", value=str(scar.get('affected_quantity') or ''), disabled=True)
        with col2:
            st.text_input("Lot Number(s)", value=scar.get('lot_numbers') or '', disabled=True)

    # --- Tab 2: Non-Conformity (read-only) ---
    with tabs[1]:
        st.text_area("Non-Conformity Description",
            value=scar.get('nonconformity_description') or '', disabled=True, height=150)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Defect Type", value=scar.get('defect_type') or '', disabled=True)
        with col2:
            st.text_input("Severity", value=(scar.get('severity') or '').upper(), disabled=True)

    # --- Tab 3: Containment ---
    with tabs[2]:
        with st.form("containment_form"):
            containment_isolate = st.text_area("3.1 Isolate Affected Inventory",
                value=scar.get('containment_isolate') or '', height=100, disabled=not can_edit)
            containment_screen_sort = st.text_area("3.2 Screen and Sort",
                value=scar.get('containment_screen_sort') or '', height=100, disabled=not can_edit)
            col1, col2 = st.columns(2)
            with col1:
                containment_prepared_by = st.text_input("Prepared By",
                    value=scar.get('containment_prepared_by') or '', disabled=not can_edit)
            with col2:
                existing = parse_date(scar.get('containment_date'))
                containment_date = st.date_input("Date", value=existing,
                    disabled=not can_edit)
            if can_edit:
                if st.form_submit_button("💾 Save Containment", use_container_width=True):
                    update_scar(scar_id, {
                        'containment_isolate': containment_isolate,
                        'containment_screen_sort': containment_screen_sort,
                        'containment_prepared_by': containment_prepared_by,
                        'containment_date': containment_date.isoformat() if containment_date else None,
                    }, user['id'])
                    st.success("Containment section saved!")
                    st.rerun()

    # --- Tab 4: Root Cause ---
    with tabs[3]:
        with st.form("rca_form"):
            root_cause = st.text_area("4.1 Root Cause(s) — 5 Whys Analysis",
                value=scar.get('root_cause') or '', height=150, disabled=not can_edit)
            root_cause_evidence = st.text_area("4.2 Evidence Supporting Root Cause",
                value=scar.get('root_cause_evidence') or '', height=100, disabled=not can_edit)
            col1, col2 = st.columns(2)
            with col1:
                root_cause_approved_by = st.text_input("RCA Approved By",
                    value=scar.get('root_cause_approved_by') or '', disabled=not can_edit)
            with col2:
                existing = parse_date(scar.get('root_cause_date'))
                root_cause_date = st.date_input("Date", value=existing,
                    disabled=not can_edit)
            if can_edit:
                if st.form_submit_button("💾 Save Root Cause", use_container_width=True):
                    update_scar(scar_id, {
                        'root_cause': root_cause,
                        'root_cause_evidence': root_cause_evidence,
                        'root_cause_approved_by': root_cause_approved_by,
                        'root_cause_date': root_cause_date.isoformat() if root_cause_date else None,
                    }, user['id'])
                    st.success("Root Cause section saved!")
                    st.rerun()

    # --- Tab 5: Corrective Action ---
    with tabs[4]:
        with st.form("ca_form"):
            corrective_action = st.text_area("Corrective Action / Rationale",
                value=scar.get('corrective_action') or '', height=150, disabled=not can_edit)
            col1, col2 = st.columns(2)
            with col1:
                correction_approved_by = st.text_input("CA Approved By",
                    value=scar.get('correction_approved_by') or '', disabled=not can_edit)
            with col2:
                existing = parse_date(scar.get('correction_date'))
                correction_date = st.date_input("Date", value=existing,
                    disabled=not can_edit)
            if can_edit:
                if st.form_submit_button("💾 Save Corrective Action", use_container_width=True):
                    update_scar(scar_id, {
                        'corrective_action': corrective_action,
                        'correction_approved_by': correction_approved_by,
                        'correction_date': correction_date.isoformat() if correction_date else None,
                    }, user['id'])
                    st.success("Corrective Action section saved!")
                    st.rerun()

    # --- Tab 6: Preventive Action ---
    with tabs[5]:
        with st.form("pa_form"):
            preventive_action = st.text_area("Preventive Action / Responsible / Target Date",
                value=scar.get('preventive_action') or '', height=150, disabled=not can_edit)
            col1, col2 = st.columns(2)
            with col1:
                prevention_approved_by = st.text_input("PA Approved By",
                    value=scar.get('prevention_approved_by') or '', disabled=not can_edit)
            with col2:
                existing = parse_date(scar.get('prevention_date'))
                prevention_date = st.date_input("Date", value=existing,
                    disabled=not can_edit)
            if can_edit:
                if st.form_submit_button("💾 Save Preventive Action", use_container_width=True):
                    update_scar(scar_id, {
                        'preventive_action': preventive_action,
                        'prevention_approved_by': prevention_approved_by,
                        'prevention_date': prevention_date.isoformat() if prevention_date else None,
                    }, user['id'])
                    st.success("Preventive Action section saved!")
                    st.rerun()

    # --- Tab 7: Verification (admin only) ---
    with tabs[6]:
        if not is_admin:
            st.info("🔒 This section is only visible to the Calyx quality team.")
            if scar['status'] == 'closed' and scar.get('verification_acceptable') == 'yes':
                st.success("✅ Supplier response was accepted and verified.")
        else:
            with st.form("verification_form"):
                verification_acceptable = st.radio("Supplier Response Acceptable?",
                    options=['', 'yes', 'no'],
                    format_func=lambda x: {'': 'Select...', 'yes': '✅ Yes', 'no': '❌ No'}[x],
                    disabled=scar['status'] == 'closed')
                effectiveness_check = st.text_area("Effectiveness Check",
                    value=scar.get('effectiveness_check') or '', height=100,
                    disabled=scar['status'] == 'closed')
                col1, col2 = st.columns(2)
                with col1:
                    verified_by = st.text_input("Verified By",
                        value=scar.get('verified_by') or '', disabled=scar['status'] == 'closed')
                with col2:
                    existing = parse_date(scar.get('verification_date'))
                    verification_date = st.date_input("Date", value=existing,
                        disabled=scar['status'] == 'closed')
                if scar['status'] != 'closed':
                    if st.form_submit_button("💾 Save Verification", use_container_width=True):
                        update_scar(scar_id, {
                            'verification_acceptable': verification_acceptable,
                            'effectiveness_check': effectiveness_check,
                            'verified_by': verified_by,
                            'verification_date': verification_date.isoformat() if verification_date else None,
                        }, user['id'])
                        st.success("Verification section saved!")
                        st.rerun()

    # --- Tab 8: Attachments ---
    with tabs[7]:
        st.markdown("### 📎 Documents & Photos")
        if can_edit or is_admin:
            with st.form("upload_form"):
                uploaded_file = st.file_uploader("Upload a file",
                    type=["jpg", "jpeg", "png", "gif", "webp", "pdf",
                          "doc", "docx", "xls", "xlsx", "csv", "txt"],
                    help="Max 50MB. Images, PDFs, Word, Excel, CSV, or text files.")
                col1, col2 = st.columns(2)
                with col1:
                    category = st.selectbox("Category",
                        ["general", "evidence", "containment", "root_cause",
                         "corrective", "preventive", "verification"])
                with col2:
                    description = st.text_input("Description (optional)")
                if st.form_submit_button("📤 Upload", use_container_width=True):
                    if uploaded_file:
                        try:
                            file_bytes = uploaded_file.read()
                            upload_attachment(
                                scar_id=scar_id, user_id=user['id'],
                                file_name=uploaded_file.name, file_bytes=file_bytes,
                                file_type=uploaded_file.type, category=category,
                                description=description or None)
                            st.success(f"✅ {uploaded_file.name} uploaded!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Upload failed: {str(e)}")
                    else:
                        st.warning("Please select a file first.")

        attachments = get_scar_attachments(scar_id)
        if attachments:
            for att in attachments:
                col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
                with col1:
                    icon = "🖼️" if att.get('file_type', '').startswith('image/') else "📄"
                    st.markdown(f"**{icon} {att['file_name']}**")
                    if att.get('description'):
                        st.caption(att['description'])
                with col2:
                    st.caption(f"Category: {att['category']}")
                    st.caption(f"Size: {(att.get('file_size') or 0) / 1024:.0f} KB")
                with col3:
                    st.caption(f"By: {att.get('uploaded_by_name', 'Unknown')}")
                    st.caption(format_date(att.get('created_at')))
                with col4:
                    try:
                        url = get_attachment_download_url(att['storage_path'])
                        st.markdown(f"[⬇ Download]({url})")
                    except Exception:
                        st.caption("Link unavailable")
                    if is_admin:
                        if st.button("🗑️", key=f"del_att_{att['id']}"):
                            delete_attachment(att['id'], scar_id=scar_id, user_id=user['id'])
                            st.rerun()
                st.markdown("---")
        else:
            st.info("No files attached to this SCAR yet.")

    # --- Tab 9: Activity Log ---
    with tabs[8]:
        activities = get_scar_activity(scar_id)
        if activities:
            headers = ["Date/Time", "User", "Action", "Details"]
            rows = [[
                format_datetime(a.get('created_at')),
                a.get('user_name') or 'System',
                a.get('action', ''),
                a.get('details') or '-'
            ] for a in activities]
            st.markdown(render_grid_table(headers, rows), unsafe_allow_html=True)
        else:
            st.info("No activity recorded yet.")

    # --- Action buttons ---
    st.markdown("---")
    st.markdown("### Actions")
    col1, col2, col3 = st.columns(3)

    if can_submit:
        with col1:
            if st.button("📤 Submit Response", type="primary", use_container_width=True):
                # Validate all required sections are filled
                missing = []
                if not scar.get('containment_isolate'): missing.append("Containment (Isolate)")
                if not scar.get('containment_screen_sort'): missing.append("Containment (Screen & Sort)")
                if not scar.get('containment_prepared_by'): missing.append("Containment (Prepared By)")
                if not scar.get('containment_date'): missing.append("Containment (Date)")
                if not scar.get('root_cause'): missing.append("Root Cause")
                if not scar.get('root_cause_evidence'): missing.append("Root Cause Evidence")
                if not scar.get('root_cause_approved_by'): missing.append("Root Cause (Approved By)")
                if not scar.get('root_cause_date'): missing.append("Root Cause (Date)")
                if not scar.get('corrective_action'): missing.append("Corrective Action")
                if not scar.get('correction_approved_by'): missing.append("Corrective Action (Approved By)")
                if not scar.get('correction_date'): missing.append("Corrective Action (Date)")
                if not scar.get('preventive_action'): missing.append("Preventive Action")
                if not scar.get('prevention_approved_by'): missing.append("Preventive Action (Approved By)")
                if not scar.get('prevention_date'): missing.append("Preventive Action (Date)")

                if missing:
                    st.error(f"Complete these fields before submitting: {', '.join(missing)}")
                else:
                    submit_scar(scar_id, user['id'])
                    st.success("✅ Response submitted!")
                    st.rerun()

    if can_verify:
        with col1:
            if st.button("✅ Verify & Close", type="primary", use_container_width=True):
                verify_scar(scar_id, user['id'], acceptable=True)
                st.success("SCAR verified and closed!")
                st.rerun()
        with col2:
            if st.button("↩️ Return to Supplier", use_container_width=True):
                verify_scar(scar_id, user['id'], acceptable=False)
                st.success("SCAR returned to supplier.")
                st.rerun()

    if is_admin and scar['status'] == 'closed':
        with col1:
            if st.button("🔄 Reopen SCAR", use_container_width=True):
                verify_scar(scar_id, user['id'], acceptable=False, reopen=True)
                st.success("SCAR reopened!")
                st.rerun()

# ============================================================================
# VENDORS PAGE
# ============================================================================

def vendors_page():
    require_admin()
    st.markdown("# Vendor Management")
    st.markdown("---")

    with st.expander("➕ Add New Vendor", expanded=False):
        with st.form("new_vendor_form"):
            col1, col2 = st.columns(2)
            with col1:
                vendor_name = st.text_input("Vendor Name *")
                vendor_phone = st.text_input("Phone")
            with col2:
                vendor_address = st.text_area("Address", height=80)
            if st.form_submit_button("Add Vendor", use_container_width=True):
                if vendor_name:
                    try:
                        create_vendor(vendor_name, vendor_address, vendor_phone)
                        st.success(f"Vendor '{vendor_name}' added!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error("Vendor name is required.")

    vendors = get_all_vendors()
    st.markdown(f"### Vendors ({len(vendors)} total)")

    if vendors:
        headers = ["Name", "Phone", "Address", "Contacts"]
        rows = []
        for vendor in vendors:
            contacts = get_vendor_contacts(vendor['id'])
            primary = next((c['name'] for c in contacts if c.get('is_primary')), '-')
            count = len(contacts)
            rows.append([
                vendor['name'],
                vendor.get('phone') or '-',
                (vendor.get('address') or '-')[:50],
                f"{primary} (+{count - 1})" if count > 1 else primary,
            ])
        st.markdown(render_grid_table(headers, rows), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Edit Vendor")
        vendor_options = {v['name']: v['id'] for v in vendors}
        selected_vendor = st.selectbox("Select vendor to edit:", ["Select..."] + list(vendor_options.keys()))

        if selected_vendor != "Select...":
            vendor_id = vendor_options[selected_vendor]
            vendor = get_vendor_by_id(vendor_id)

            if vendor:
                with st.form("edit_vendor_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("Vendor Name", value=vendor['name'])
                        edit_phone = st.text_input("Phone", value=vendor.get('phone') or '')
                    with col2:
                        edit_address = st.text_area("Address", value=vendor.get('address') or '')
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Vendor", use_container_width=True):
                            update_vendor(vendor_id, name=edit_name, phone=edit_phone, address=edit_address)
                            st.success("Vendor updated!")
                            st.rerun()
                    with col2:
                        if st.form_submit_button("🗑️ Delete Vendor", type="secondary"):
                            delete_vendor(vendor_id)
                            st.success("Vendor deleted!")
                            st.rerun()

                st.markdown("#### Contacts")
                contacts = get_vendor_contacts(vendor_id)
                if contacts:
                    for c in contacts:
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        with col1:
                            badge = " ⭐" if c.get('is_primary') else ""
                            st.markdown(f"**{c['name']}**{badge}")
                        with col2:
                            st.caption(c['email'])
                        with col3:
                            st.caption(c.get('phone') or '-')
                        with col4:
                            if st.button("🗑️", key=f"del_contact_{c['id']}"):
                                delete_vendor_contact(c['id'])
                                st.rerun()

                with st.form(f"add_contact_{vendor_id}"):
                    st.markdown("**Add Contact**")
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    with col1:
                        contact_name = st.text_input("Name *")
                    with col2:
                        contact_email = st.text_input("Email *")
                    with col3:
                        contact_phone = st.text_input("Phone")
                    with col4:
                        contact_primary = st.checkbox("Primary")
                    if st.form_submit_button("Add Contact"):
                        if contact_name and contact_email:
                            create_vendor_contact(vendor_id, contact_name, contact_email,
                                                  contact_phone, contact_primary)
                            st.success("Contact added!")
                            st.rerun()
                        else:
                            st.error("Name and email are required.")
    else:
        st.info("No vendors found. Add a vendor to get started.")

# ============================================================================
# USERS PAGE
# ============================================================================

def users_page():
    require_admin()
    st.markdown("# User Management")
    st.markdown("---")

    pending_count = get_pending_users_count()
    if pending_count > 0:
        st.warning(f"⚠️ {pending_count} user(s) pending approval")

    with st.expander("➕ Add New User", expanded=False):
        vendors = get_all_vendors()
        with st.form("new_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name *")
                new_email = st.text_input("Email *")
                new_password = st.text_input("Password *", type="password")
            with col2:
                new_role = st.selectbox("Role", ["supplier", "admin"])
                if new_role == "supplier" and vendors:
                    vendor_options = {"None": None}
                    vendor_options.update({v['name']: v['id'] for v in vendors})
                    new_vendor = st.selectbox("Assign to Vendor", options=list(vendor_options.keys()))
                else:
                    new_vendor = None
            if st.form_submit_button("Create User", use_container_width=True):
                if new_name and new_email and new_password:
                    try:
                        vid = vendor_options.get(new_vendor) if new_vendor else None
                        create_user(new_email, new_password, new_name, new_role, vid)
                        st.success(f"User '{new_name}' created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error("Please fill in all required fields.")

    users = get_all_users()
    st.markdown(f"### Users ({len(users)} total)")

    if users:
        headers = ["Name", "Email", "Role", "Vendor", "Status", "Created"]
        rows = [[
            u['name'], u['email'], get_role_badge(u['role']),
            u.get('vendor_name') or '-', get_status_badge(u['status']),
            format_date(u.get('created_at')),
        ] for u in users]
        st.markdown(render_grid_table(headers, rows), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### User Actions")
        user_options = {f"{u['name']} ({u['email']})": u['id']
                        for u in users if u['id'] != st.session_state.user['id']}
        selected_user = st.selectbox("Select user:", ["Select..."] + list(user_options.keys()))

        if selected_user != "Select...":
            user_id = user_options[selected_user]
            target_user = get_user_by_id(user_id)

            if target_user:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if target_user['status'] in ('pending', 'rejected'):
                        if st.button("✓ Approve User", use_container_width=True):
                            update_user(user_id, status='approved')
                            st.success("User approved!")
                            st.rerun()
                    else:
                        st.info("User is already approved")
                with col2:
                    if st.button("🔑 Reset Password", use_container_width=True):
                        new_pw = "password123"
                        update_user_password(user_id, new_pw)
                        st.success(f"Password reset to: {new_pw}")
                with col3:
                    if st.button("🗑️ Delete User", use_container_width=True, type="secondary"):
                        delete_user(user_id)
                        st.success("User deleted!")
                        st.rerun()
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

    st.markdown(get_calyx_styles(), unsafe_allow_html=True)

    try:
        init_database()
    except Exception as e:
        st.error(f"⚠️ Database connection failed: {e}")
        st.info("Please check your SUPABASE_URL and SUPABASE_KEY in Settings → Secrets.")
        st.stop()

    # Initialize session state
    for key, default in [
        ('user', None), ('page', 'login'),
        ('force_password_change', False), ('selected_scar_id', None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    render_sidebar()

    if not check_login():
        login_page()
    elif st.session_state.force_password_change:
        # Block all other pages until password is changed
        change_password_page()
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
        elif page == "change_password":
            change_password_page()
        else:
            dashboard_page()

if __name__ == "__main__":
    main()
