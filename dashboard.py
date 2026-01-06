"""
Dashboard Page - Overview of SCAR statistics and recent activity
"""

import streamlit as st
from datetime import datetime
from database import get_scar_stats, get_all_scars

def format_date(date_str):
    """Format date string for display"""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return date_str

def show():
    """Display dashboard page"""
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    vendor_id = None if is_admin else user.get('vendor_id')
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome back, {user['name'].split()[0]} 👋</h1>
        <p>{'Overview of your SCAR management system' if is_admin else f"SCARs for {user.get('vendor_name', 'your organization')}"}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons for admin
    if is_admin:
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("➕ Create SCAR", type="primary", use_container_width=True):
                st.session_state.page = "scar_create"
                st.rerun()
    
    # Stats
    stats = get_scar_stats(vendor_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📂 Open SCARs</h3>
            <div class="value">{stats.get('open', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📤 Awaiting Review</h3>
            <div class="value">{stats.get('submitted', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚠️ Overdue</h3>
            <div class="value" style="color: {'#DC2626' if stats.get('overdue', 0) > 0 else '#111827'};">{stats.get('overdue', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅ Closed</h3>
            <div class="value">{stats.get('closed', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent SCARs
    st.markdown("### Recent SCARs")
    
    scars = get_all_scars(vendor_id=vendor_id)[:5]
    
    if not scars:
        st.info("No SCARs found. " + ("Create your first SCAR to get started." if is_admin else "No SCARs have been assigned to your organization."))
    else:
        for scar in scars:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                
                with col1:
                    st.markdown(f"**{scar['scar_number']}**")
                    status_class = f"badge-{scar['status']}"
                    st.markdown(f'<span class="badge {status_class}">{scar["status"].upper()}</span>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"{scar.get('product_name') or scar.get('defect_type') or 'No description'}")
                    if is_admin:
                        st.caption(f"Vendor: {scar.get('vendor_name', 'Unassigned')}")
                    else:
                        st.caption(f"Due: {format_date(scar.get('response_due_date'))}")
                
                with col3:
                    if scar.get('severity'):
                        severity_class = f"badge-{scar['severity']}"
                        st.markdown(f'<span class="badge {severity_class}">{scar["severity"].upper()}</span>', unsafe_allow_html=True)
                
                with col4:
                    if st.button("View →", key=f"view_{scar['id']}", use_container_width=True):
                        st.session_state.selected_scar_id = scar['id']
                        st.session_state.page = "scar_detail"
                        st.rerun()
                
                st.markdown("---")
    
    # Quick action for suppliers with open SCARs
    if not is_admin and stats.get('open', 0) > 0:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%); 
                    padding: 1.5rem; border-radius: 10px; border: 1px solid #FECACA;">
            <div style="display: flex; align-items: start; gap: 1rem;">
                <div style="font-size: 2rem;">📋</div>
                <div>
                    <h4 style="margin: 0; color: #991B1B;">You have {stats['open']} open SCAR{'s' if stats['open'] != 1 else ''} requiring attention</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #7F1D1D;">Please review and submit your responses before the due dates.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Open SCARs →"):
            st.session_state.scar_filter = "open"
            st.session_state.page = "scars"
            st.rerun()
