"""
Profile Page - User profile and password management
"""

import streamlit as st
from database import update_user_password, verify_password, get_user_by_id

def show():
    """Display profile page"""
    user = st.session_state.user
    
    st.markdown("# 👤 Profile")
    st.caption("View your profile and change your password")
    
    st.markdown("---")
    
    # Profile information
    st.markdown("### Account Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #E5E7EB;">
            <h4 style="margin: 0 0 1rem 0; color: #374151;">Personal Details</h4>
            <p style="margin: 0.5rem 0;"><strong>Name:</strong> {user['name']}</p>
            <p style="margin: 0.5rem 0;"><strong>Email:</strong> {user['email']}</p>
            <p style="margin: 0.5rem 0;"><strong>Role:</strong> {'Administrator' if user['role'] == 'admin' else 'Supplier'}</p>
            <p style="margin: 0.5rem 0;"><strong>Status:</strong> <span class="badge badge-{user['status']}">{user['status'].upper()}</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if user['role'] == 'supplier' and user.get('vendor_name'):
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #E5E7EB;">
                <h4 style="margin: 0 0 1rem 0; color: #374151;">Organization</h4>
                <p style="margin: 0.5rem 0;"><strong>Vendor:</strong> {user.get('vendor_name', 'Not assigned')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #E5E7EB;">
                <h4 style="margin: 0 0 1rem 0; color: #374151;">Organization</h4>
                <p style="margin: 0.5rem 0; color: #6B7280;">{'Calyx Containers (Admin)' if user['role'] == 'admin' else 'Not assigned to a vendor'}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Change password
    st.markdown("### Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Update Password", use_container_width=True)
        
        if submitted:
            if not all([current_password, new_password, confirm_password]):
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                # Verify current password
                current_user = get_user_by_id(user['id'])
                if not verify_password(current_password, current_user['password']):
                    st.error("Current password is incorrect")
                else:
                    update_user_password(user['id'], new_password)
                    st.success("Password updated successfully!")
    
    st.markdown("---")
    
    # Account activity
    st.markdown("### Session Information")
    
    st.markdown(f"""
    <div style="background: #F9FAFB; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">
        <p style="margin: 0; color: #6B7280; font-size: 0.875rem;">
            You are currently logged in as <strong>{user['email']}</strong>.<br>
            Account created: {user.get('created_at', 'Unknown')[:10] if user.get('created_at') else 'Unknown'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
