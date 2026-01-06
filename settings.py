"""
Settings Page - User and Vendor Management (admin only)
"""

import streamlit as st
from database import (
    get_all_users,
    get_all_vendors,
    update_user,
    delete_user,
    update_user_password,
    create_user,
    create_vendor,
    update_vendor,
    delete_vendor,
    get_vendor_contacts,
    create_vendor_contact,
    update_vendor_contact,
    delete_vendor_contact,
    get_password_hash
)

def show():
    """Display settings page"""
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    
    # Check admin access
    if not is_admin:
        st.error("Access denied. Only administrators can access settings.")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    st.markdown("# ⚙️ Settings")
    st.caption("Manage users, vendors, and system configuration")
    
    # Tabs for different settings sections
    tab1, tab2 = st.tabs(["👥 User Management", "🏢 Vendor Management"])
    
    # User Management Tab
    with tab1:
        show_user_management()
    
    # Vendor Management Tab
    with tab2:
        show_vendor_management()


def show_user_management():
    """Display user management section"""
    st.markdown("### User Management")
    
    # Get all users and vendors
    users = get_all_users()
    vendors = get_all_vendors()
    
    # Filter controls
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "Pending", "Approved", "Rejected"],
            key="user_status_filter"
        )
    with col2:
        role_filter = st.selectbox(
            "Filter by Role",
            options=["All", "Admin", "Supplier"],
            key="user_role_filter"
        )
    with col3:
        search = st.text_input("🔍 Search users", placeholder="Name or email...", key="user_search")
    
    # Apply filters
    filtered_users = users
    if status_filter != "All":
        filtered_users = [u for u in filtered_users if u['status'] == status_filter.lower()]
    if role_filter != "All":
        filtered_users = [u for u in filtered_users if u['role'] == role_filter.lower()]
    if search:
        search_lower = search.lower()
        filtered_users = [u for u in filtered_users if 
                         search_lower in u['name'].lower() or 
                         search_lower in u['email'].lower()]
    
    # Pending approvals section
    pending_users = [u for u in users if u['status'] == 'pending']
    if pending_users:
        st.markdown("---")
        st.markdown(f"### ⏳ Pending Approvals ({len(pending_users)})")
        
        for pending_user in pending_users:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{pending_user['name']}**")
                    st.caption(pending_user['email'])
                
                with col2:
                    st.caption(f"Company: {pending_user.get('vendor_name', 'Not assigned')}")
                
                with col3:
                    if st.button("✅ Approve", key=f"approve_{pending_user['id']}", use_container_width=True):
                        update_user(pending_user['id'], status='approved')
                        st.success(f"User {pending_user['name']} approved!")
                        st.rerun()
                
                with col4:
                    if st.button("❌ Reject", key=f"reject_{pending_user['id']}", use_container_width=True):
                        update_user(pending_user['id'], status='rejected')
                        st.warning(f"User {pending_user['name']} rejected.")
                        st.rerun()
                
                st.markdown("---")
    
    # Add new admin user
    st.markdown("---")
    with st.expander("➕ Add Administrator"):
        with st.form("add_admin_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_admin_name = st.text_input("Name *")
                new_admin_email = st.text_input("Email *")
            with col2:
                new_admin_password = st.text_input("Password *", type="password")
                new_admin_password_confirm = st.text_input("Confirm Password *", type="password")
            
            if st.form_submit_button("Create Admin", use_container_width=True):
                if not all([new_admin_name, new_admin_email, new_admin_password]):
                    st.error("Please fill in all fields")
                elif new_admin_password != new_admin_password_confirm:
                    st.error("Passwords do not match")
                elif len(new_admin_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    try:
                        create_user(new_admin_email, new_admin_password, new_admin_name, "admin")
                        st.success(f"Admin user {new_admin_name} created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create user: {str(e)}")
    
    # All users list
    st.markdown("---")
    st.markdown(f"### All Users ({len(filtered_users)})")
    
    if not filtered_users:
        st.info("No users found matching your criteria.")
    else:
        for u in filtered_users:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2.5, 2, 1.5, 1.5, 1.5])
                
                with col1:
                    st.markdown(f"**{u['name']}**")
                    st.caption(u['email'])
                
                with col2:
                    role_badge = "🔑 Admin" if u['role'] == 'admin' else "📦 Supplier"
                    st.markdown(role_badge)
                    if u.get('vendor_name'):
                        st.caption(u['vendor_name'])
                
                with col3:
                    status_colors = {
                        'pending': '🟡',
                        'approved': '🟢',
                        'rejected': '🔴'
                    }
                    st.markdown(f"{status_colors.get(u['status'], '⚪')} {u['status'].capitalize()}")
                
                with col4:
                    if st.button("✏️ Edit", key=f"edit_user_{u['id']}", use_container_width=True):
                        st.session_state.editing_user = u['id']
                
                with col5:
                    # Don't allow deleting yourself
                    if u['id'] != st.session_state.user['id']:
                        if st.button("🗑️", key=f"delete_user_{u['id']}", use_container_width=True):
                            st.session_state.deleting_user = u['id']
                
                # Edit form
                if st.session_state.get('editing_user') == u['id']:
                    with st.form(f"edit_user_form_{u['id']}"):
                        st.markdown("##### Edit User")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_name = st.text_input("Name", value=u['name'])
                            edit_email = st.text_input("Email", value=u['email'])
                        with col2:
                            edit_role = st.selectbox(
                                "Role",
                                options=['admin', 'supplier'],
                                index=0 if u['role'] == 'admin' else 1
                            )
                            edit_vendor = st.selectbox(
                                "Vendor",
                                options=[""] + [v['id'] for v in vendors],
                                format_func=lambda x: "No vendor" if x == "" else next((v['name'] for v in vendors if v['id'] == x), x),
                                index=0 if not u.get('vendor_id') else ([v['id'] for v in vendors].index(u['vendor_id']) + 1 if u.get('vendor_id') in [v['id'] for v in vendors] else 0)
                            )
                        
                        edit_status = st.selectbox(
                            "Status",
                            options=['pending', 'approved', 'rejected'],
                            index=['pending', 'approved', 'rejected'].index(u['status'])
                        )
                        
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            new_password = st.text_input("New Password (leave blank to keep current)", type="password")
                        with col2:
                            if st.form_submit_button("Save", type="primary"):
                                update_user(u['id'], 
                                           name=edit_name, 
                                           email=edit_email, 
                                           role=edit_role, 
                                           vendor_id=edit_vendor or None,
                                           status=edit_status)
                                if new_password:
                                    update_user_password(u['id'], new_password)
                                st.session_state.editing_user = None
                                st.success("User updated!")
                                st.rerun()
                        with col3:
                            if st.form_submit_button("Cancel"):
                                st.session_state.editing_user = None
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get('deleting_user') == u['id']:
                    st.warning(f"⚠️ Are you sure you want to delete {u['name']}?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Yes, Delete", key=f"confirm_delete_user_{u['id']}", type="primary"):
                            delete_user(u['id'])
                            st.session_state.deleting_user = None
                            st.success("User deleted!")
                            st.rerun()
                    with col2:
                        if st.button("Cancel", key=f"cancel_delete_user_{u['id']}"):
                            st.session_state.deleting_user = None
                            st.rerun()
                
                st.markdown("---")


def show_vendor_management():
    """Display vendor management section"""
    st.markdown("### Vendor Management")
    
    vendors = get_all_vendors()
    
    # Add new vendor
    with st.expander("➕ Add New Vendor"):
        with st.form("add_vendor_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_vendor_name = st.text_input("Vendor Name *")
                new_vendor_phone = st.text_input("Phone")
            with col2:
                new_vendor_address = st.text_area("Address", height=100)
            
            if st.form_submit_button("Create Vendor", use_container_width=True):
                if not new_vendor_name:
                    st.error("Vendor name is required")
                else:
                    try:
                        create_vendor(new_vendor_name, new_vendor_address, new_vendor_phone)
                        st.success(f"Vendor '{new_vendor_name}' created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create vendor: {str(e)}")
    
    st.markdown("---")
    
    # Vendors list
    if not vendors:
        st.info("No vendors found. Add your first vendor above.")
    else:
        for vendor in vendors:
            with st.expander(f"🏢 {vendor['name']}"):
                # Vendor details
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Address:** {vendor.get('address') or 'Not specified'}")
                with col2:
                    st.markdown(f"**Phone:** {vendor.get('phone') or 'Not specified'}")
                
                # Edit vendor
                with st.form(f"edit_vendor_{vendor['id']}"):
                    st.markdown("##### Edit Vendor Details")
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("Name", value=vendor['name'], key=f"vendor_name_{vendor['id']}")
                        edit_phone = st.text_input("Phone", value=vendor.get('phone') or '', key=f"vendor_phone_{vendor['id']}")
                    with col2:
                        edit_address = st.text_area("Address", value=vendor.get('address') or '', key=f"vendor_address_{vendor['id']}", height=100)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Vendor"):
                            update_vendor(vendor['id'], name=edit_name, address=edit_address, phone=edit_phone)
                            st.success("Vendor updated!")
                            st.rerun()
                    with col2:
                        if st.form_submit_button("🗑️ Delete Vendor", type="secondary"):
                            st.session_state[f'confirm_delete_vendor_{vendor["id"]}'] = True
                
                # Delete confirmation
                if st.session_state.get(f'confirm_delete_vendor_{vendor["id"]}'):
                    st.warning("⚠️ Deleting a vendor will also remove all associated contacts. Continue?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Yes, Delete", key=f"do_delete_vendor_{vendor['id']}"):
                            delete_vendor(vendor['id'])
                            st.session_state[f'confirm_delete_vendor_{vendor["id"]}'] = False
                            st.success("Vendor deleted!")
                            st.rerun()
                    with col2:
                        if st.button("Cancel", key=f"cancel_delete_vendor_{vendor['id']}"):
                            st.session_state[f'confirm_delete_vendor_{vendor["id"]}'] = False
                            st.rerun()
                
                # Contacts section
                st.markdown("---")
                st.markdown("##### Contacts")
                
                contacts = get_vendor_contacts(vendor['id'])
                
                if contacts:
                    for contact in contacts:
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        with col1:
                            primary_badge = " ⭐" if contact.get('is_primary') else ""
                            st.markdown(f"**{contact['name']}**{primary_badge}")
                        with col2:
                            st.caption(contact['email'])
                        with col3:
                            st.caption(contact.get('phone') or 'No phone')
                        with col4:
                            if st.button("🗑️", key=f"delete_contact_{contact['id']}"):
                                delete_vendor_contact(contact['id'])
                                st.rerun()
                else:
                    st.caption("No contacts for this vendor.")
                
                # Add contact form
                st.markdown("---")
                with st.form(f"add_contact_{vendor['id']}"):
                    st.markdown("**Add Contact**")
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    with col1:
                        contact_name = st.text_input("Name *", key=f"contact_name_{vendor['id']}")
                    with col2:
                        contact_email = st.text_input("Email *", key=f"contact_email_{vendor['id']}")
                    with col3:
                        contact_phone = st.text_input("Phone", key=f"contact_phone_{vendor['id']}")
                    with col4:
                        contact_primary = st.checkbox("Primary", key=f"contact_primary_{vendor['id']}")
                    
                    if st.form_submit_button("Add Contact"):
                        if not contact_name or not contact_email:
                            st.error("Name and email are required")
                        else:
                            create_vendor_contact(vendor['id'], contact_name, contact_email, contact_phone, contact_primary)
                            st.success("Contact added!")
                            st.rerun()
