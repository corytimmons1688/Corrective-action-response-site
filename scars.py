"""
SCARs List Page - View and filter all SCARs
"""

import streamlit as st
from datetime import datetime
from database import get_all_scars, get_all_vendors

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
    """Display SCARs list page"""
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    vendor_id = None if is_admin else user.get('vendor_id')
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 📋 SCARs")
        st.caption("Supplier Corrective Action Reports")
    with col2:
        if is_admin:
            if st.button("➕ Create SCAR", type="primary", use_container_width=True):
                st.session_state.page = "scar_create"
                st.rerun()
    
    # Filters
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        # Status filter using tabs
        status_filter = st.session_state.get('scar_filter', 'all')
        status_options = ["All", "Open", "Submitted", "Closed"]
        selected_status = st.selectbox(
            "Status",
            options=status_options,
            index=status_options.index(status_filter.capitalize()) if status_filter.capitalize() in status_options else 0
        )
        status_filter = None if selected_status == "All" else selected_status.lower()
    
    with col2:
        if is_admin:
            vendors = get_all_vendors()
            vendor_options = [{"id": "", "name": "All Vendors"}] + vendors
            selected_vendor = st.selectbox(
                "Vendor",
                options=[v['id'] for v in vendor_options],
                format_func=lambda x: next((v['name'] for v in vendor_options if v['id'] == x), "All Vendors")
            )
            if selected_vendor:
                vendor_id = selected_vendor
            else:
                vendor_id = None
    
    with col3:
        search = st.text_input("🔍 Search", placeholder="Search by SCAR number, product...")
    
    # Get SCARs
    scars = get_all_scars(vendor_id=vendor_id, status=status_filter)
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        scars = [s for s in scars if 
                 search_lower in s.get('scar_number', '').lower() or
                 search_lower in (s.get('product_name') or '').lower() or
                 search_lower in (s.get('vendor_name') or '').lower() or
                 search_lower in (s.get('defect_type') or '').lower()]
    
    st.markdown("---")
    
    # Results count
    st.caption(f"Showing {len(scars)} SCAR{'s' if len(scars) != 1 else ''}")
    
    if not scars:
        st.info("No SCARs found matching your criteria.")
        return
    
    # SCARs table
    for scar in scars:
        is_overdue = False
        if scar.get('response_due_date') and scar['status'] in ['new', 'open']:
            try:
                due_date = datetime.fromisoformat(scar['response_due_date'])
                is_overdue = due_date < datetime.now()
            except:
                pass
        
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1.5, 2.5, 1.5, 1.5, 1])
            
            with col1:
                st.markdown(f"**{scar['scar_number']}**")
                status_class = f"badge-{scar['status']}"
                st.markdown(f'<span class="badge {status_class}">{scar["status"].upper()}</span>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{scar.get('product_name') or 'No product specified'}**")
                st.caption(f"{scar.get('defect_type') or 'No defect type'}")
                if is_admin:
                    st.caption(f"📍 {scar.get('vendor_name', 'Unassigned')}")
            
            with col3:
                if scar.get('severity'):
                    severity_class = f"badge-{scar['severity']}"
                    st.markdown(f'<span class="badge {severity_class}">{scar["severity"].upper()}</span>', unsafe_allow_html=True)
                st.caption(f"Issued: {format_date(scar.get('date_issued'))}")
            
            with col4:
                due_text = format_date(scar.get('response_due_date'))
                if is_overdue:
                    st.markdown(f"**⚠️ OVERDUE**")
                    st.caption(f"Due: {due_text}")
                else:
                    st.caption(f"Due: {due_text}")
            
            with col5:
                if st.button("View", key=f"view_{scar['id']}", use_container_width=True):
                    st.session_state.selected_scar_id = scar['id']
                    st.session_state.page = "scar_detail"
                    st.rerun()
            
            st.markdown("---")
