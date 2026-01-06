"""
SCAR Create Page - Create new SCAR (admin only)
"""

import streamlit as st
from datetime import datetime, timedelta
from database import (
    get_all_vendors,
    get_vendor_contacts,
    create_scar
)

def show():
    """Display SCAR creation page"""
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    
    # Check admin access
    if not is_admin:
        st.error("Access denied. Only administrators can create SCARs.")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    # Header
    if st.button("← Back to SCARs"):
        st.session_state.page = "scars"
        st.rerun()
    
    st.markdown("# ➕ Create New SCAR")
    st.caption("Fill out the SCAR details and non-conformity description to create a new Supplier Corrective Action Report.")
    
    st.markdown("---")
    
    # Get vendors for dropdown
    vendors = get_all_vendors()
    
    # Initialize form state
    if 'new_scar_vendor_id' not in st.session_state:
        st.session_state.new_scar_vendor_id = None
    
    with st.form("create_scar_form"):
        st.markdown("### Section 1: SCAR Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date_issued = st.date_input(
                "Date Issued *",
                value=datetime.now().date()
            )
            
            response_due_date = st.date_input(
                "Response Due Date *",
                value=(datetime.now() + timedelta(days=14)).date()
            )
            
            ncr_number = st.text_input(
                "NCR # (Non-Conformance Report)",
                placeholder="e.g., NCR-2026-0001"
            )
            
            po_so_number = st.text_input(
                "PO/SO #",
                placeholder="e.g., PO-12345"
            )
        
        with col2:
            vendor_id = st.selectbox(
                "Supplier/Vendor *",
                options=[""] + [v['id'] for v in vendors],
                format_func=lambda x: "Select a vendor..." if x == "" else next((v['name'] for v in vendors if v['id'] == x), x),
                key="vendor_select"
            )
            
            # Get contacts for selected vendor
            contacts = []
            if vendor_id:
                contacts = get_vendor_contacts(vendor_id)
            
            vendor_contact_id = st.selectbox(
                "Supplier Contact *",
                options=[""] + [c['id'] for c in contacts],
                format_func=lambda x: "Select a contact..." if x == "" else next((f"{c['name']} ({c['email']})" for c in contacts if c['id'] == x), x),
                disabled=not vendor_id
            )
            
            part_sku_number = st.text_input(
                "Part/SKU #",
                placeholder="e.g., SKU-12345"
            )
            
            affected_quantity = st.number_input(
                "Affected Quantity",
                min_value=0,
                value=0
            )
        
        lot_numbers = st.text_input(
            "Lot Number(s)",
            placeholder="e.g., LOT-2026-A001, LOT-2026-A002"
        )
        
        st.markdown("---")
        st.markdown("### Section 2: Non-Conformity Description")
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input(
                "Product Name/Description *",
                placeholder="e.g., 500ml Clear Glass Jar"
            )
        
        with col2:
            defect_type = st.selectbox(
                "Defect Type *",
                options=["", "Dimensional", "Visual", "Functional", "Labeling", "Packaging", "Contamination", "Documentation", "Other"]
            )
        
        nonconformity_description = st.text_area(
            "Detailed Description of Non-Conformity *",
            height=150,
            placeholder="Provide a detailed description of the non-conformity, including:\n- What was found\n- Where it was discovered\n- Impact on product quality/safety\n- Any relevant measurements or observations"
        )
        
        severity = st.radio(
            "Severity *",
            options=["minor", "major", "critical"],
            format_func=lambda x: {
                "minor": "🟢 Minor - Does not affect product functionality or safety",
                "major": "🟡 Major - Affects product functionality but not safety",
                "critical": "🔴 Critical - Affects product safety or regulatory compliance"
            }[x],
            horizontal=True
        )
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button("📋 Create SCAR", type="primary", use_container_width=True)
        
        if submitted:
            # Validate required fields
            errors = []
            
            if not vendor_id:
                errors.append("Please select a vendor")
            if not vendor_contact_id:
                errors.append("Please select a vendor contact")
            if not product_name:
                errors.append("Please enter a product name")
            if not defect_type:
                errors.append("Please select a defect type")
            if not nonconformity_description:
                errors.append("Please provide a non-conformity description")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create SCAR
                scar_data = {
                    'date_issued': date_issued.isoformat(),
                    'response_due_date': response_due_date.isoformat(),
                    'vendor_id': vendor_id,
                    'vendor_contact_id': vendor_contact_id,
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
                    new_scar = create_scar(scar_data, user['id'])
                    st.success(f"✅ SCAR {new_scar['scar_number']} created successfully!")
                    
                    # Redirect to the new SCAR
                    st.session_state.selected_scar_id = new_scar['id']
                    st.session_state.page = "scar_detail"
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create SCAR: {str(e)}")
    
    # Help text
    with st.expander("ℹ️ Help: Creating a SCAR"):
        st.markdown("""
        **What is a SCAR?**
        
        A Supplier Corrective Action Report (SCAR) is a formal document used to communicate quality issues 
        to suppliers and track their response and corrective actions.
        
        **Severity Levels:**
        
        - **Minor**: Cosmetic defects or minor deviations that don't affect product function or safety
        - **Major**: Defects that affect product functionality but don't pose safety risks
        - **Critical**: Defects that affect product safety or regulatory compliance
        
        **After Creation:**
        
        Once created, the SCAR will be assigned to the selected vendor. The vendor contact will be notified 
        and can log in to view and respond to the SCAR. The supplier must complete the Containment, Root Cause, 
        Correction, and Prevention sections before submitting their response.
        """)
