"""
SCAR Detail Page - View and edit SCAR details
"""

import streamlit as st
from datetime import datetime
from database import (
    get_scar_by_id, 
    update_scar, 
    submit_scar, 
    verify_scar,
    get_scar_activity
)

def format_date(date_str):
    """Format date string for display"""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return date_str

def format_datetime(date_str):
    """Format datetime string for display"""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return date_str

def show():
    """Display SCAR detail page"""
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    scar_id = st.session_state.get('selected_scar_id')
    
    if not scar_id:
        st.error("No SCAR selected")
        if st.button("← Back to SCARs"):
            st.session_state.page = "scars"
            st.rerun()
        return
    
    scar = get_scar_by_id(scar_id)
    if not scar:
        st.error("SCAR not found")
        if st.button("← Back to SCARs"):
            st.session_state.page = "scars"
            st.rerun()
        return
    
    # Check access for suppliers
    if not is_admin and scar.get('vendor_id') != user.get('vendor_id'):
        st.error("You don't have access to this SCAR")
        if st.button("← Back to SCARs"):
            st.session_state.page = "scars"
            st.rerun()
        return
    
    # Determine edit permissions
    can_edit_supplier_sections = (
        (is_admin or user['role'] == 'supplier') and 
        scar['status'] in ['new', 'open']
    )
    can_edit_admin_sections = is_admin
    can_submit = user['role'] == 'supplier' and scar['status'] == 'open'
    can_verify = is_admin and scar['status'] == 'submitted'
    
    # Header with back button
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("← Back to SCARs"):
            st.session_state.page = "scars"
            st.rerun()
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 1rem; margin: 1rem 0;">
        <h1 style="margin: 0;">{scar['scar_number']}</h1>
        <span class="badge badge-{scar['status']}" style="font-size: 0.9rem;">{scar['status'].upper()}</span>
        {f'<span class="badge badge-{scar["severity"]}" style="font-size: 0.9rem;">{scar["severity"].upper()}</span>' if scar.get('severity') else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Status messages
    if scar['status'] == 'closed':
        st.success("✅ This SCAR has been verified and closed.")
    elif scar['status'] == 'submitted':
        if is_admin:
            st.info("📋 Supplier response submitted. Please review and verify.")
        else:
            st.info("📤 Your response has been submitted and is awaiting review.")
    elif scar['status'] == 'open':
        if not is_admin:
            st.warning(f"⏳ Please submit your response by {format_date(scar.get('response_due_date'))}")
    
    # Create tabs for the form sections
    tabs = st.tabs([
        "📄 SCAR Details",
        "⚠️ Non-Conformity", 
        "🛡️ 3. Containment",
        "🔍 4. Root Cause",
        "🔧 5. Correction",
        "🛑 6. Prevention",
        "✅ 7. Verification"
    ])
    
    # Initialize form data in session state
    if 'scar_form_data' not in st.session_state or st.session_state.get('scar_form_id') != scar_id:
        st.session_state.scar_form_data = {
            'containment_isolate': scar.get('containment_isolate') or '',
            'containment_screen_sort': scar.get('containment_screen_sort') or '',
            'containment_prepared_by': scar.get('containment_prepared_by') or '',
            'containment_date': scar.get('containment_date') or '',
            'root_cause': scar.get('root_cause') or '',
            'root_cause_evidence': scar.get('root_cause_evidence') or '',
            'root_cause_approved_by': scar.get('root_cause_approved_by') or '',
            'root_cause_date': scar.get('root_cause_date') or '',
            'corrective_action': scar.get('corrective_action') or '',
            'correction_approved_by': scar.get('correction_approved_by') or '',
            'correction_date': scar.get('correction_date') or '',
            'preventive_action': scar.get('preventive_action') or '',
            'prevention_approved_by': scar.get('prevention_approved_by') or '',
            'prevention_date': scar.get('prevention_date') or '',
            'verification_acceptable': scar.get('verification_acceptable') or '',
            'effectiveness_check': scar.get('effectiveness_check') or '',
            'verified_by': scar.get('verified_by') or '',
            'verification_date': scar.get('verification_date') or '',
        }
        st.session_state.scar_form_id = scar_id
    
    # Tab 1: SCAR Details (read-only)
    with tabs[0]:
        st.markdown("### Section 1: SCAR Details")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("SCAR Number", value=scar['scar_number'], disabled=True)
            st.text_input("Date Issued", value=format_date(scar.get('date_issued')), disabled=True)
            st.text_input("Response Due Date", value=format_date(scar.get('response_due_date')), disabled=True)
            st.text_input("NCR #", value=scar.get('ncr_number') or '', disabled=True)
        
        with col2:
            st.text_input("Supplier Name", value=scar.get('vendor_name') or '', disabled=True)
            st.text_input("Supplier Contact", value=scar.get('contact_name') or '', disabled=True)
            st.text_input("Contact Email", value=scar.get('contact_email') or '', disabled=True)
            st.text_input("PO/SO #", value=scar.get('po_so_number') or '', disabled=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Part/SKU #", value=scar.get('part_sku_number') or '', disabled=True)
        with col2:
            st.text_input("Affected Quantity", value=str(scar.get('affected_quantity') or ''), disabled=True)
        with col3:
            st.text_input("Lot Number(s)", value=scar.get('lot_numbers') or '', disabled=True)
    
    # Tab 2: Non-Conformity (read-only)
    with tabs[1]:
        st.markdown("### Section 2: Non-Conformity Description")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Product Name/Description", value=scar.get('product_name') or '', disabled=True)
        with col2:
            st.text_input("Defect Type", value=scar.get('defect_type') or '', disabled=True)
        
        st.text_area("Detailed Description of Non-Conformity", 
                     value=scar.get('nonconformity_description') or '', 
                     disabled=True, 
                     height=150)
        
        severity = scar.get('severity', '').capitalize() if scar.get('severity') else 'Not specified'
        st.text_input("Severity", value=severity, disabled=True)
    
    # Tab 3: Containment (editable by supplier)
    with tabs[2]:
        st.markdown("### Section 3: Containment")
        st.caption("Describe immediate actions taken to contain the non-conformity.")
        
        with st.form("containment_form"):
            containment_isolate = st.text_area(
                "3.1 Isolate Affected Inventory",
                value=st.session_state.scar_form_data['containment_isolate'],
                height=100,
                disabled=not can_edit_supplier_sections,
                help="Describe how affected inventory was isolated to prevent further distribution"
            )
            
            containment_screen_sort = st.text_area(
                "3.2 Screen and Sort",
                value=st.session_state.scar_form_data['containment_screen_sort'],
                height=100,
                disabled=not can_edit_supplier_sections,
                help="Describe screening and sorting activities performed"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                containment_prepared_by = st.text_input(
                    "Prepared By",
                    value=st.session_state.scar_form_data['containment_prepared_by'],
                    disabled=not can_edit_supplier_sections
                )
            with col2:
                containment_date = st.text_input(
                    "Date (YYYY-MM-DD)",
                    value=st.session_state.scar_form_data['containment_date'],
                    disabled=not can_edit_supplier_sections
                )
            
            if can_edit_supplier_sections:
                if st.form_submit_button("💾 Save Containment", use_container_width=True):
                    update_data = {
                        'containment_isolate': containment_isolate,
                        'containment_screen_sort': containment_screen_sort,
                        'containment_prepared_by': containment_prepared_by,
                        'containment_date': containment_date,
                    }
                    update_scar(scar_id, update_data, user['id'])
                    st.session_state.scar_form_data.update(update_data)
                    st.success("Containment section saved!")
                    st.rerun()
    
    # Tab 4: Root Cause (editable by supplier)
    with tabs[3]:
        st.markdown("### Section 4: Root Cause Analysis")
        st.caption("Identify the root cause(s) of the non-conformity using the 5 Whys or similar methodology.")
        
        with st.form("root_cause_form"):
            root_cause = st.text_area(
                "4.1 Root Cause(s) of Defect - 5 Whys Analysis",
                value=st.session_state.scar_form_data['root_cause'],
                height=150,
                disabled=not can_edit_supplier_sections,
                help="1. Why did the defect occur?\n2. Why? (dig deeper)\n3. Why?\n4. Why?\n5. Why? (root cause)"
            )
            
            root_cause_evidence = st.text_area(
                "4.2 Evidence Supporting Root Cause",
                value=st.session_state.scar_form_data['root_cause_evidence'],
                height=100,
                disabled=not can_edit_supplier_sections,
                help="Provide data, documentation, or analysis supporting your root cause determination"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                root_cause_approved_by = st.text_input(
                    "RCA Approved By (Supplier Quality)",
                    value=st.session_state.scar_form_data['root_cause_approved_by'],
                    disabled=not can_edit_supplier_sections
                )
            with col2:
                root_cause_date = st.text_input(
                    "Date (YYYY-MM-DD)",
                    value=st.session_state.scar_form_data['root_cause_date'],
                    disabled=not can_edit_supplier_sections
                )
            
            if can_edit_supplier_sections:
                if st.form_submit_button("💾 Save Root Cause", use_container_width=True):
                    update_data = {
                        'root_cause': root_cause,
                        'root_cause_evidence': root_cause_evidence,
                        'root_cause_approved_by': root_cause_approved_by,
                        'root_cause_date': root_cause_date,
                    }
                    update_scar(scar_id, update_data, user['id'])
                    st.session_state.scar_form_data.update(update_data)
                    st.success("Root Cause section saved!")
                    st.rerun()
    
    # Tab 5: Correction (editable by supplier)
    with tabs[4]:
        st.markdown("### Section 5: Corrective Action")
        st.caption("Describe the corrective actions taken to address the root cause.")
        
        with st.form("correction_form"):
            corrective_action = st.text_area(
                "Corrective Action / Rationale",
                value=st.session_state.scar_form_data['corrective_action'],
                height=150,
                disabled=not can_edit_supplier_sections,
                help="Describe specific actions taken to correct the non-conformity and prevent recurrence"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                correction_approved_by = st.text_input(
                    "CA Approved By (Supplier)",
                    value=st.session_state.scar_form_data['correction_approved_by'],
                    disabled=not can_edit_supplier_sections
                )
            with col2:
                correction_date = st.text_input(
                    "Date (YYYY-MM-DD)",
                    value=st.session_state.scar_form_data['correction_date'],
                    disabled=not can_edit_supplier_sections
                )
            
            if can_edit_supplier_sections:
                if st.form_submit_button("💾 Save Corrective Action", use_container_width=True):
                    update_data = {
                        'corrective_action': corrective_action,
                        'correction_approved_by': correction_approved_by,
                        'correction_date': correction_date,
                    }
                    update_scar(scar_id, update_data, user['id'])
                    st.session_state.scar_form_data.update(update_data)
                    st.success("Corrective Action section saved!")
                    st.rerun()
    
    # Tab 6: Prevention (editable by supplier)
    with tabs[5]:
        st.markdown("### Section 6: Preventive Action")
        st.caption("Describe actions to prevent the non-conformity from recurring.")
        
        with st.form("prevention_form"):
            preventive_action = st.text_area(
                "Preventive Action / Responsible / Target Date",
                value=st.session_state.scar_form_data['preventive_action'],
                height=150,
                disabled=not can_edit_supplier_sections,
                help="List preventive actions, who is responsible, and target completion dates"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                prevention_approved_by = st.text_input(
                    "PA Approved By (Supplier Quality)",
                    value=st.session_state.scar_form_data['prevention_approved_by'],
                    disabled=not can_edit_supplier_sections
                )
            with col2:
                prevention_date = st.text_input(
                    "Date (YYYY-MM-DD)",
                    value=st.session_state.scar_form_data['prevention_date'],
                    disabled=not can_edit_supplier_sections
                )
            
            if can_edit_supplier_sections:
                if st.form_submit_button("💾 Save Preventive Action", use_container_width=True):
                    update_data = {
                        'preventive_action': preventive_action,
                        'prevention_approved_by': prevention_approved_by,
                        'prevention_date': prevention_date,
                    }
                    update_scar(scar_id, update_data, user['id'])
                    st.session_state.scar_form_data.update(update_data)
                    st.success("Preventive Action section saved!")
                    st.rerun()
    
    # Tab 7: Verification (admin only)
    with tabs[6]:
        st.markdown("### Section 7: Calyx Verification (Internal Quality Team)")
        
        if not is_admin:
            st.info("🔒 This section is only visible to Calyx Containers quality team.")
            
            if scar['status'] == 'closed':
                st.markdown("---")
                st.markdown("**Verification Result:**")
                if scar.get('verification_acceptable') == 'yes':
                    st.success("✅ Supplier response was accepted")
                else:
                    st.warning("Response was returned for revision")
                
                if scar.get('effectiveness_check'):
                    st.markdown(f"**Effectiveness Check:** {scar.get('effectiveness_check')}")
                if scar.get('verified_by'):
                    st.markdown(f"**Verified By:** {scar.get('verified_by')} on {format_date(scar.get('verification_date'))}")
        else:
            with st.form("verification_form"):
                verification_acceptable = st.radio(
                    "Supplier Response Acceptable?",
                    options=['', 'yes', 'no'],
                    format_func=lambda x: {'': 'Select...', 'yes': '✅ Yes - Accept Response', 'no': '❌ No - Return for Revision'}[x],
                    index=['', 'yes', 'no'].index(st.session_state.scar_form_data['verification_acceptable']) if st.session_state.scar_form_data['verification_acceptable'] in ['', 'yes', 'no'] else 0,
                    disabled=scar['status'] == 'closed'
                )
                
                effectiveness_check = st.text_area(
                    "Effectiveness Check",
                    value=st.session_state.scar_form_data['effectiveness_check'],
                    height=100,
                    disabled=scar['status'] == 'closed',
                    help="Document follow-up verification of corrective action effectiveness"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    verified_by = st.text_input(
                        "Verified By",
                        value=st.session_state.scar_form_data['verified_by'],
                        disabled=scar['status'] == 'closed'
                    )
                with col2:
                    verification_date = st.text_input(
                        "Date (YYYY-MM-DD)",
                        value=st.session_state.scar_form_data['verification_date'],
                        disabled=scar['status'] == 'closed'
                    )
                
                if scar['status'] != 'closed':
                    if st.form_submit_button("💾 Save Verification", use_container_width=True):
                        update_data = {
                            'verification_acceptable': verification_acceptable,
                            'effectiveness_check': effectiveness_check,
                            'verified_by': verified_by,
                            'verification_date': verification_date,
                        }
                        update_scar(scar_id, update_data, user['id'])
                        st.session_state.scar_form_data.update(update_data)
                        st.success("Verification section saved!")
                        st.rerun()
    
    # Action buttons
    st.markdown("---")
    st.markdown("### Actions")
    
    col1, col2, col3 = st.columns(3)
    
    # Submit button for suppliers
    if can_submit:
        with col1:
            if st.button("📤 Submit Response", type="primary", use_container_width=True):
                # Check required fields
                form_data = st.session_state.scar_form_data
                missing_fields = []
                
                if not form_data.get('containment_isolate'):
                    missing_fields.append("Containment - Isolate Affected Inventory")
                if not form_data.get('root_cause'):
                    missing_fields.append("Root Cause Analysis")
                if not form_data.get('corrective_action'):
                    missing_fields.append("Corrective Action")
                if not form_data.get('preventive_action'):
                    missing_fields.append("Preventive Action")
                
                if missing_fields:
                    st.error(f"Please complete the following sections before submitting:\n- " + "\n- ".join(missing_fields))
                else:
                    st.session_state.show_submit_confirm = True
    
    # Verify button for admin
    if can_verify:
        with col1:
            if st.button("✅ Verify & Close", type="primary", use_container_width=True):
                st.session_state.show_verify_confirm = True
        with col2:
            if st.button("↩️ Return to Supplier", use_container_width=True):
                st.session_state.show_return_confirm = True
    
    # Reopen button for closed SCARs (admin only)
    if is_admin and scar['status'] == 'closed':
        with col1:
            if st.button("🔄 Reopen SCAR", use_container_width=True):
                st.session_state.show_reopen_confirm = True
    
    # Confirmation dialogs
    if st.session_state.get('show_submit_confirm'):
        st.warning("⚠️ Are you sure you want to submit this response? You won't be able to make changes after submission.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Submit", type="primary"):
                submit_scar(scar_id, user['id'])
                st.session_state.show_submit_confirm = False
                st.success("Response submitted successfully!")
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.show_submit_confirm = False
                st.rerun()
    
    if st.session_state.get('show_verify_confirm'):
        st.info("✅ Confirm verification and close this SCAR?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Verify & Close", type="primary"):
                update_scar(scar_id, st.session_state.scar_form_data, user['id'])
                verify_scar(scar_id, user['id'], acceptable=True)
                st.session_state.show_verify_confirm = False
                st.success("SCAR verified and closed!")
                st.rerun()
        with col2:
            if st.button("Cancel", key="cancel_verify"):
                st.session_state.show_verify_confirm = False
                st.rerun()
    
    if st.session_state.get('show_return_confirm'):
        st.warning("↩️ Return this SCAR to the supplier for revision?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Return", type="primary"):
                verify_scar(scar_id, user['id'], acceptable=False)
                st.session_state.show_return_confirm = False
                st.success("SCAR returned to supplier!")
                st.rerun()
        with col2:
            if st.button("Cancel", key="cancel_return"):
                st.session_state.show_return_confirm = False
                st.rerun()
    
    if st.session_state.get('show_reopen_confirm'):
        st.warning("🔄 Reopen this SCAR?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Reopen", type="primary"):
                verify_scar(scar_id, user['id'], acceptable=False, reopen=True)
                st.session_state.show_reopen_confirm = False
                st.success("SCAR reopened!")
                st.rerun()
        with col2:
            if st.button("Cancel", key="cancel_reopen"):
                st.session_state.show_reopen_confirm = False
                st.rerun()
    
    # Activity log
    st.markdown("---")
    with st.expander("📜 Activity Log"):
        activities = get_scar_activity(scar_id)
        if activities:
            for activity in activities:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{activity.get('user_name', 'System')}** - {activity['action']}")
                    if activity.get('details'):
                        st.caption(activity['details'])
                with col2:
                    st.caption(format_datetime(activity['created_at']))
                st.markdown("---")
        else:
            st.info("No activity recorded yet.")
