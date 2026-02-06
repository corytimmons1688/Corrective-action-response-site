"""
Database module for SCAR Management System
Supabase-backed version - replaces SQLite with Supabase PostgreSQL + Storage
"""

import hashlib
import os
from datetime import datetime
from supabase import create_client, Client

# =============================================================================
# Supabase Client Initialization
# =============================================================================

# Try Streamlit secrets first, then fall back to environment variables
def _get_config(key: str) -> str:
    """Get config value from Streamlit secrets or environment variables.
    Supports both flat and nested TOML formats:
        SUPABASE_URL = "..."          (flat / top-level)
        [supabase]
        SUPABASE_URL = "..."          (nested under [supabase])
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            # 1. Check top-level keys first
            if key in st.secrets:
                return st.secrets[key]
            # 2. Check nested under [supabase] section
            if "supabase" in st.secrets and key in st.secrets["supabase"]:
                return st.secrets["supabase"][key]
    except Exception:
        pass
    return os.environ.get(key, "")


_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Get or create Supabase client singleton.
    Reads config lazily so Streamlit secrets are available at call time."""
    global _supabase_client
    if _supabase_client is None:
        url = _get_config("SUPABASE_URL")
        key = _get_config("SUPABASE_KEY")
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY environment variables must be set. "
                "Add them to your Streamlit secrets or .env file."
            )
        _supabase_client = create_client(url, key)
    return _supabase_client


def get_password_hash(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return get_password_hash(password) == hashed


def init_database():
    """
    Verify Supabase connection is working.
    Tables are created via the SQL migration file - this just validates connectivity.
    """
    try:
        sb = get_supabase()
        sb.table("vendors").select("id").limit(1).execute()
    except Exception as e:
        raise ConnectionError(f"Could not connect to Supabase: {e}")


# =============================================================================
# User Operations
# =============================================================================

def get_user_by_email(email: str) -> dict | None:
    """Get user by email with vendor info"""
    sb = get_supabase()
    result = (
        sb.table("users")
        .select("*, vendors(name)")
        .eq("email", email)
        .maybe_single()
        .execute()
    )
    if result.data:
        row = result.data
        row["vendor_name"] = row.pop("vendors", {}).get("name") if row.get("vendors") else None
        return row
    return None


def get_user_by_id(user_id: str) -> dict | None:
    """Get user by ID with vendor info"""
    sb = get_supabase()
    result = (
        sb.table("users")
        .select("*, vendors(name)")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if result.data:
        row = result.data
        row["vendor_name"] = row.pop("vendors", {}).get("name") if row.get("vendors") else None
        return row
    return None


def create_user(email: str, password: str, name: str, role: str, vendor_id: str = None) -> dict:
    """Create a new user. If assigned to a vendor, also add as vendor contact."""
    sb = get_supabase()
    status = "approved" if role == "admin" else "pending"

    data = {
        "email": email,
        "password": get_password_hash(password),
        "name": name,
        "role": role,
        "vendor_id": vendor_id,
        "status": status,
    }

    result = sb.table("users").insert(data).execute()

    # Auto-add as vendor contact if assigned to a vendor
    if vendor_id:
        # Check if contact with this email already exists for this vendor
        existing = (
            sb.table("vendor_contacts")
            .select("id")
            .eq("vendor_id", vendor_id)
            .eq("email", email)
            .execute()
        )
        if not existing.data:
            create_vendor_contact(vendor_id, name, email)

    return get_user_by_id(result.data[0]["id"])


def get_all_users() -> list:
    """Get all users with vendor info"""
    sb = get_supabase()
    result = (
        sb.table("users")
        .select("*, vendors(name)")
        .order("created_at", desc=True)
        .execute()
    )
    users = []
    for row in result.data:
        row["vendor_name"] = row.pop("vendors", {}).get("name") if row.get("vendors") else None
        users.append(row)
    return users


def update_user(user_id: str, **kwargs) -> dict:
    """Update user fields. If vendor_id changes, also add as vendor contact."""
    allowed_fields = ["name", "email", "role", "vendor_id", "status"]
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return get_user_by_id(user_id)

    sb = get_supabase()
    sb.table("users").update(updates).eq("id", user_id).execute()

    # If vendor_id was set, ensure user is a vendor contact
    new_vendor_id = updates.get("vendor_id")
    if new_vendor_id:
        user = get_user_by_id(user_id)
        existing = (
            sb.table("vendor_contacts")
            .select("id")
            .eq("vendor_id", new_vendor_id)
            .eq("email", user["email"])
            .execute()
        )
        if not existing.data:
            create_vendor_contact(new_vendor_id, user["name"], user["email"])

    return get_user_by_id(user_id)


def update_user_password(user_id: str, new_password: str):
    """Update user password"""
    sb = get_supabase()
    sb.table("users").update({"password": get_password_hash(new_password)}).eq("id", user_id).execute()


def delete_user(user_id: str):
    """Delete a user"""
    sb = get_supabase()
    sb.table("users").delete().eq("id", user_id).execute()


def get_pending_users_count() -> int:
    """Get count of pending user approvals"""
    sb = get_supabase()
    result = sb.table("users").select("id", count="exact").eq("status", "pending").execute()
    return result.count or 0


# =============================================================================
# Vendor Operations
# =============================================================================

def get_all_vendors() -> list:
    """Get all vendors"""
    sb = get_supabase()
    result = sb.table("vendors").select("*").order("name").execute()
    return result.data


def get_vendor_by_id(vendor_id: str) -> dict | None:
    """Get vendor by ID"""
    sb = get_supabase()
    result = sb.table("vendors").select("*").eq("id", vendor_id).maybe_single().execute()
    return result.data


def create_vendor(name: str, address: str = None, phone: str = None) -> dict:
    """Create a new vendor"""
    sb = get_supabase()
    data = {"name": name, "address": address, "phone": phone}
    result = sb.table("vendors").insert(data).execute()
    return result.data[0]


def update_vendor(vendor_id: str, **kwargs) -> dict:
    """Update vendor fields"""
    allowed_fields = ["name", "address", "phone"]
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return get_vendor_by_id(vendor_id)

    sb = get_supabase()
    sb.table("vendors").update(updates).eq("id", vendor_id).execute()
    return get_vendor_by_id(vendor_id)


def delete_vendor(vendor_id: str):
    """Delete a vendor (cascades to contacts)"""
    sb = get_supabase()
    sb.table("vendors").delete().eq("id", vendor_id).execute()


def get_vendor_contacts(vendor_id: str) -> list:
    """Get all contacts for a vendor"""
    sb = get_supabase()
    result = (
        sb.table("vendor_contacts")
        .select("*")
        .eq("vendor_id", vendor_id)
        .order("is_primary", desc=True)
        .order("name")
        .execute()
    )
    return result.data


def create_vendor_contact(
    vendor_id: str, name: str, email: str, phone: str = None, is_primary: bool = False
) -> dict:
    """Create a vendor contact"""
    sb = get_supabase()
    data = {
        "vendor_id": vendor_id,
        "name": name,
        "email": email,
        "phone": phone,
        "is_primary": is_primary,
    }
    result = sb.table("vendor_contacts").insert(data).execute()
    return result.data[0]


def update_vendor_contact(contact_id: str, **kwargs) -> dict | None:
    """Update vendor contact"""
    allowed_fields = ["name", "email", "phone", "is_primary"]
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return None

    sb = get_supabase()
    result = sb.table("vendor_contacts").update(updates).eq("id", contact_id).execute()
    return result.data[0] if result.data else None


def delete_vendor_contact(contact_id: str):
    """Delete a vendor contact"""
    sb = get_supabase()
    sb.table("vendor_contacts").delete().eq("id", contact_id).execute()


# =============================================================================
# SCAR Operations
# =============================================================================

def get_next_scar_number() -> str:
    """Generate next SCAR number using the DB function"""
    sb = get_supabase()
    result = sb.rpc("get_next_scar_number").execute()
    return result.data


def create_scar(data: dict, created_by: str) -> dict:
    """Create a new SCAR"""
    scar_number = get_next_scar_number()

    data["scar_number"] = scar_number
    data["status"] = "open"
    data["created_by"] = created_by

    # Remove any None-value keys to let DB defaults apply
    data = {k: v for k, v in data.items() if v is not None}

    sb = get_supabase()
    result = sb.table("scars").insert(data).execute()
    scar_id = result.data[0]["id"]

    # Log activity
    sb.table("scar_activity").insert(
        {
            "scar_id": scar_id,
            "user_id": created_by,
            "action": "created",
            "details": f"SCAR {scar_number} created",
        }
    ).execute()

    return get_scar_by_id(scar_id)


def get_scar_by_id(scar_id: str) -> dict | None:
    """Get SCAR by ID with vendor info"""
    sb = get_supabase()
    result = (
        sb.table("scars")
        .select("*, vendors(name), vendor_contacts(name, email)")
        .eq("id", scar_id)
        .maybe_single()
        .execute()
    )
    if result.data:
        row = result.data
        row["vendor_name"] = row.pop("vendors", {}).get("name") if row.get("vendors") else None
        contact = row.pop("vendor_contacts", {}) or {}
        row["contact_name"] = contact.get("name")
        row["contact_email"] = contact.get("email")
        return row
    return None


def get_all_scars(vendor_id: str = None, status: str = None) -> list:
    """Get all SCARs, optionally filtered by vendor and/or status"""
    sb = get_supabase()
    query = sb.table("scars").select(
        "*, vendors(name), vendor_contacts(name, email)"
    )

    if vendor_id:
        query = query.eq("vendor_id", vendor_id)
    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).execute()

    scars = []
    for row in result.data:
        row["vendor_name"] = row.pop("vendors", {}).get("name") if row.get("vendors") else None
        contact = row.pop("vendor_contacts", {}) or {}
        row["contact_name"] = contact.get("name")
        row["contact_email"] = contact.get("email")
        scars.append(row)
    return scars


def update_scar(scar_id: str, data: dict, user_id: str = None) -> dict:
    """Update SCAR fields"""
    protected = {"id", "scar_number", "created_by", "created_at", "updated_at"}
    updates = {k: v for k, v in data.items() if k not in protected}

    if not updates:
        return get_scar_by_id(scar_id)

    # Sanitize DATE columns — PostgreSQL rejects empty strings for DATE fields
    date_fields = {
        "date_issued", "response_due_date", "containment_date",
        "root_cause_date", "correction_date", "prevention_date",
        "verification_date",
    }
    for field in date_fields:
        if field in updates and not updates[field]:
            updates[field] = None

    sb = get_supabase()
    sb.table("scars").update(updates).eq("id", scar_id).execute()

    if user_id:
        sb.table("scar_activity").insert(
            {
                "scar_id": scar_id,
                "user_id": user_id,
                "action": "updated",
                "details": "SCAR updated",
            }
        ).execute()

    return get_scar_by_id(scar_id)


def submit_scar(scar_id: str, user_id: str) -> dict:
    """Submit SCAR response (supplier action)"""
    sb = get_supabase()
    sb.table("scars").update({"status": "submitted"}).eq("id", scar_id).execute()

    sb.table("scar_activity").insert(
        {
            "scar_id": scar_id,
            "user_id": user_id,
            "action": "submitted",
            "details": "Supplier response submitted",
        }
    ).execute()

    return get_scar_by_id(scar_id)


def verify_scar(scar_id: str, user_id: str, acceptable: bool, reopen: bool = False) -> dict:
    """Verify SCAR (admin action)"""
    new_status = "open" if reopen else ("closed" if acceptable else "open")

    sb = get_supabase()
    sb.table("scars").update({"status": new_status}).eq("id", scar_id).execute()

    action = "reopened" if reopen else ("closed" if acceptable else "returned")
    details = (
        "SCAR reopened for revision"
        if reopen
        else (
            "SCAR verified and closed"
            if acceptable
            else "SCAR returned to supplier for revision"
        )
    )

    sb.table("scar_activity").insert(
        {
            "scar_id": scar_id,
            "user_id": user_id,
            "action": action,
            "details": details,
        }
    ).execute()

    return get_scar_by_id(scar_id)


def get_scar_activity(scar_id: str) -> list:
    """Get activity log for a SCAR"""
    sb = get_supabase()
    result = (
        sb.table("scar_activity")
        .select("*, users(name)")
        .eq("scar_id", scar_id)
        .order("created_at", desc=True)
        .execute()
    )
    activities = []
    for row in result.data:
        row["user_name"] = row.pop("users", {}).get("name") if row.get("users") else None
        activities.append(row)
    return activities


def get_scar_stats(vendor_id: str = None) -> dict:
    """Get SCAR statistics"""
    sb = get_supabase()

    def count_query(extra_filters: dict = None):
        q = sb.table("scars").select("id", count="exact")
        if vendor_id:
            q = q.eq("vendor_id", vendor_id)
        if extra_filters:
            for k, v in extra_filters.items():
                q = q.eq(k, v)
        return q.execute().count or 0

    stats = {
        "total": count_query(),
        "new": count_query({"status": "new"}),
        "open": count_query({"status": "open"}),
        "submitted": count_query({"status": "submitted"}),
        "closed": count_query({"status": "closed"}),
    }

    # Overdue: open/new SCARs past their due date
    today = datetime.now().strftime("%Y-%m-%d")
    q = (
        sb.table("scars")
        .select("id", count="exact")
        .in_("status", ["new", "open"])
        .lt("response_due_date", today)
    )
    if vendor_id:
        q = q.eq("vendor_id", vendor_id)
    stats["overdue"] = q.execute().count or 0

    return stats


# =============================================================================
# Attachment / File Operations
# =============================================================================

STORAGE_BUCKET = "scar-attachments"

LOGO_FILE = "Calyx Containers Primary Logo-01_Black (1).png"


def get_logo_url(expires_in: int = 86400) -> str:
    """Get a signed URL for the Calyx logo from Supabase storage.
    Tries the scar-attachments bucket first. Returns empty string on failure."""
    sb = get_supabase()
    try:
        result = sb.storage.from_(STORAGE_BUCKET).create_signed_url(LOGO_FILE, expires_in)
        if isinstance(result, dict) and result.get("signedURL"):
            return result["signedURL"]
    except Exception:
        pass
    return ""


def upload_attachment(
    scar_id: str,
    user_id: str,
    file_name: str,
    file_bytes: bytes,
    file_type: str,
    category: str = "general",
    description: str = None,
) -> dict:
    """
    Upload a file to Supabase Storage and record metadata in scar_attachments.

    Args:
        scar_id: The SCAR this file belongs to
        user_id: Who uploaded it
        file_name: Original file name
        file_bytes: Raw file content
        file_type: MIME type (e.g. 'image/png', 'application/pdf')
        category: One of 'evidence', 'containment', 'root_cause', 'corrective',
                  'preventive', 'verification', 'general'
        description: Optional text description

    Returns:
        The scar_attachments row (dict)
    """
    sb = get_supabase()

    # Build unique storage path
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = file_name.replace(" ", "_")
    storage_path = f"scars/{scar_id}/{timestamp}_{safe_name}"

    # Upload to Supabase Storage
    sb.storage.from_(STORAGE_BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": file_type},
    )

    # Record metadata
    meta = {
        "scar_id": scar_id,
        "uploaded_by": user_id,
        "file_name": file_name,
        "file_type": file_type,
        "file_size": len(file_bytes),
        "storage_path": storage_path,
        "category": category,
        "description": description,
    }
    result = sb.table("scar_attachments").insert(meta).execute()

    # Log activity
    sb.table("scar_activity").insert(
        {
            "scar_id": scar_id,
            "user_id": user_id,
            "action": "attachment_added",
            "details": f"File uploaded: {file_name} ({category})",
        }
    ).execute()

    return result.data[0]


def get_scar_attachments(scar_id: str) -> list:
    """Get all attachments for a SCAR"""
    sb = get_supabase()
    result = (
        sb.table("scar_attachments")
        .select("*, users(name)")
        .eq("scar_id", scar_id)
        .order("created_at", desc=True)
        .execute()
    )
    attachments = []
    for row in result.data:
        row["uploaded_by_name"] = row.pop("users", {}).get("name") if row.get("users") else None
        attachments.append(row)
    return attachments


def get_attachment_download_url(storage_path: str, expires_in: int = 3600) -> str:
    """
    Generate a signed download URL for a stored file.

    Args:
        storage_path: The path in Supabase Storage
        expires_in: URL validity in seconds (default 1 hour)

    Returns:
        Signed URL string
    """
    sb = get_supabase()
    result = sb.storage.from_(STORAGE_BUCKET).create_signed_url(storage_path, expires_in)
    return result.get("signedURL", "")


def delete_attachment(attachment_id: str, scar_id: str = None, user_id: str = None):
    """Delete an attachment (both storage file and metadata row)."""
    sb = get_supabase()

    result = sb.table("scar_attachments").select("*").eq("id", attachment_id).maybe_single().execute()
    if not result.data:
        return

    attachment = result.data
    storage_path = attachment["storage_path"]

    # Remove from storage
    try:
        sb.storage.from_(STORAGE_BUCKET).remove([storage_path])
    except Exception:
        pass

    # Remove metadata row
    sb.table("scar_attachments").delete().eq("id", attachment_id).execute()

    # Log activity
    if scar_id and user_id:
        sb.table("scar_activity").insert(
            {
                "scar_id": scar_id,
                "user_id": user_id,
                "action": "attachment_removed",
                "details": f"File removed: {attachment['file_name']}",
            }
        ).execute()
