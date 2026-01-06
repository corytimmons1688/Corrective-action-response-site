"""
SCAR Management System - Streamlit Application
Calyx Containers Quality Management System
Single-file version for Streamlit Cloud compatibility
"""

import streamlit as st
import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

st.set_page_config(
    page_title="SCAR Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --calyx-red: #DC2626;
        --calyx-red-dark: #B91C1C;
    }
    
    .main-header {
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .main-header h1 { margin: 0; font-size: 1.75rem; font-weight: 700; }
    .main-header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.95rem; }
    
    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 { color: #6B7280; font-size: 0.875rem; font-weight: 500; margin: 0 0 0.5rem 0; }
    .metric-card .value { font-size: 2rem; font-weight: 700; color: #111827; }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .badge-open { background: #FEF3C7; color: #92400E; }
    .badge-submitted { background: #DBEAFE; color: #1E40AF; }
    .badge-closed { background: #D1FAE5; color: #065F46; }
    .badge-new { background: #E5E7EB; color: #374151; }
    
    .badge-minor { background: #D1FAE5; color: #065F46; }
    .badge-major { background: #FEF3C7; color: #92400E; }
    .badge-critical { background: #FEE2E2; color: #991B1B; }
    
    .badge-pending { background: #FEF3C7; color: #92400E; }
    .badge-approved { background: #D1FAE5; color: #065F46; }
    .badge-rejected { background: #FEE2E2; color: #991B1B; }
    
    section[data-testid="stSidebar"] { background-color: #1F2937; }
    section[data-testid="stSidebar"] .stMarkdown { color: white; }
    
    .stButton > button { border-radius: 8px; font-weight: 500; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div { border-radius: 8px; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Database Functions
# =============================================================================

DATABASE_PATH = Path(__file__).parent / "data" / "scar.db"

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return get_password_hash(password) == hashed

@contextmanager
def get_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                address TEXT,
                phone TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendor_contacts (
                id TEXT PRIMARY KEY,
                vendor_id TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                is_primary INTEGER DEFAULT 0,
                FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'supplier')),
                vendor_id TEXT,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scars (
                id TEXT PRIMARY KEY,
                scar_number TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new', 'open', 'submitted', 'closed')),
                date_issued TEXT,
                response_due_date TEXT,
                vendor_id TEXT,
                vendor_contact_id TEXT,
                ncr_number TEXT,
                po_so_number TEXT,
                part_sku_number TEXT,
                affected_quantity INTEGER,
                lot_numbers TEXT,
                product_name TEXT,
                defect_type TEXT,
                nonconformity_description TEXT,
                severity TEXT CHECK(severity IN ('minor', 'major', 'critical')),
                containment_isolate TEXT,
                containment_screen_sort TEXT,
                containment_prepared_by TEXT,
                containment_date TEXT,
                root_cause TEXT,
                root_cause_evidence TEXT,
                root_cause_approved_by TEXT,
                root_cause_date TEXT,
                corrective_action TEXT,
                correction_approved_by TEXT,
                correction_date TEXT,
                preventive_action TEXT,
                prevention_approved_by TEXT,
                prevention_date TEXT,
                verification_acceptable TEXT,
                effectiveness_check TEXT,
                verified_by TEXT,
                verification_date TEXT,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL,
                FOREIGN KEY (vendor_contact_id) REFERENCES vendor_contacts(id) ON DELETE SET NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scar_activity (
                id TEXT PRIMARY KEY,
                scar_id TEXT NOT NULL,
                user_id TEXT,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scar_id) REFERENCES scars(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM vendors")
        if cursor.fetchone()[0] == 0:
            seed_database(cursor)

def seed_database(cursor):
    vendors = [
        (str(uuid.uuid4()), "Pacific Glass Co.", "123 Harbor Blvd, Long Beach, CA 90802", "(562) 555-0100"),
        (str(uuid.uuid4()), "Western Packaging Inc.", "456 Industrial Way, Phoenix, AZ 85001", "(602) 555-0200"),
        (str(uuid.uuid4()), "Mountain View Plastics", "789 Tech Park Dr, Denver, CO 80202", "(303) 555-0300"),
        (str(uuid.uuid4()), "Coastal Container Corp.", "321 Seaside Ave, San Diego, CA 92101", "(619) 555-0400"),
    ]
    cursor.executemany("INSERT INTO vendors (id, name, address, phone) VALUES (?, ?, ?, ?)", vendors)
    
    contacts = [
        (str(uuid.uuid4()), vendors[0][0], "John Smith", "jsmith@pacificglass.com", "(562) 555-0101", 1),
        (str(uuid.uuid4()), vendors[0][0], "Sarah Johnson", "sjohnson@pacificglass.com", "(562) 555-0102", 0),
        (str(uuid.uuid4()), vendors[1][0], "Mike Wilson", "mwilson@westernpkg.com", "(602) 555-0201", 1),
        (str(uuid.uuid4()), vendors[2][0], "Emily Chen", "echen@mvplastics.com", "(303) 555-0301", 1),
        (str(uuid.uuid4()), vendors[3][0], "Robert Garcia", "rgarcia@coastalcontainer.com", "(619) 555-0401", 1),
    ]
    cursor.executemany("INSERT INTO vendor_contacts (id, vendor_id, name, email, phone, is_primary) VALUES (?, ?, ?, ?, ?, ?)", contacts)
    
    admin_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO users (id, email, password, name, role, status) VALUES (?, ?, ?, ?, ?, ?)",
        (admin_id, "admin@calyxcontainers.com", get_password_hash("admin123"), "Admin User", "admin", "approved")
    )
    
    supplier_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO users (id, email, password, name, role, vendor_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (supplier_id, "jsmith@pacificglass.com", get_password_hash("supplier123"), "John Smith", "supplier", vendors[0][0], "approved")
    )
    
    today = datetime.now()
    scars = [
        {
            "id": str(uuid.uuid4()),
            "scar_number": "SCAR-2026-001",
            "status": "open",
            "date_issued": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "response_due_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "vendor_id": vendors[0][0],
            "vendor_contact_id": contacts[0][0],
            "ncr_number": "NCR-2026-0042",
            "po_so_number": "PO-78234",
            "part_sku_number": "GLS-500ML-CLR",
            "affected_quantity": 500,
            "lot_numbers": "LOT-2026-A123, LOT-2026-A124",
            "product_name": "500ml Clear Glass Jar",
            "defect_type": "Dimensional",
            "nonconformity_description": "Jar height exceeds specification by 2mm. Affects lid fitment and seal integrity.",
            "severity": "major",
            "created_by": admin_id,
        },
        {
            "id": str(uuid.uuid4()),
            "scar_number": "SCAR-2026-002",
            "status": "submitted",
            "date_issued": (today - timedelta(days=15)).strftime("%Y-%m-%d"),
            "response_due_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            "vendor_id": vendors[1][0],
            "vendor_contact_id": contacts[2][0],
            "ncr_number": "NCR-2026-0038",
            "po_so_number": "PO-77891",
            "part_sku_number": "BOX-1OZ-WHT",
            "affected_quantity": 1000,
            "lot_numbers": "LOT-2026-B456",
            "product_name": "1oz White Cardboard Box",
            "defect_type": "Visual",
            "nonconformity_description": "Color inconsistency across batch. Some boxes show yellowish tint.",
            "severity": "minor",
            "containment_isolate": "All affected boxes isolated in Warehouse B, Section 3.",
            "containment_screen_sort": "100% visual inspection completed. 127 boxes with visible discoloration separated.",
            "containment_prepared_by": "Mike Wilson",
            "containment_date": (today - timedelta(days=10)).strftime("%Y-%m-%d"),
            "root_cause": "1. Why yellow tint? Ink formulation variance.\n2. Why variance? Supplier changed pigment source.\n3. Why changed? Cost reduction initiative.\n4. Why not communicated? Process gap in change management.\n5. Why gap? No formal change notification procedure.",
            "root_cause_evidence": "Lab analysis confirmed different pigment composition.",
            "root_cause_approved_by": "Quality Manager - Western Pkg",
            "root_cause_date": (today - timedelta(days=8)).strftime("%Y-%m-%d"),
            "corrective_action": "Reverted to original pigment supplier. Implemented incoming inspection for color consistency.",
            "correction_approved_by": "Mike Wilson",
            "correction_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "preventive_action": "1. Established formal change notification procedure.\n2. Added color consistency check to incoming QC protocol.",
            "prevention_approved_by": "Quality Manager - Western Pkg",
            "prevention_date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "created_by": admin_id,
        },
        {
            "id": str(uuid.uuid4()),
            "scar_number": "SCAR-2026-003",
            "status": "closed",
            "date_issued": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
            "response_due_date": (today - timedelta(days=16)).strftime("%Y-%m-%d"),
            "vendor_id": vendors[2][0],
            "vendor_contact_id": contacts[3][0],
            "ncr_number": "NCR-2026-0029",
            "po_so_number": "PO-76543",
            "part_sku_number": "CAP-CR-28MM",
            "affected_quantity": 2500,
            "lot_numbers": "LOT-2025-C789",
            "product_name": "28mm Child-Resistant Cap",
            "defect_type": "Functional",
            "nonconformity_description": "Child-resistant mechanism fails testing.",
            "severity": "critical",
            "containment_isolate": "Entire lot quarantined.",
            "containment_screen_sort": "Functional testing on 250 sample units. 23% failure rate confirmed.",
            "containment_prepared_by": "Emily Chen",
            "containment_date": (today - timedelta(days=28)).strftime("%Y-%m-%d"),
            "root_cause": "1. Why mechanism fails? Locking tab height insufficient.\n2. Why insufficient? Mold wear detected.",
            "root_cause_evidence": "Mold inspection photos showing 0.3mm wear on locking tab cavity.",
            "root_cause_approved_by": "Emily Chen - Quality Director",
            "root_cause_date": (today - timedelta(days=25)).strftime("%Y-%m-%d"),
            "corrective_action": "Mold refurbished and recertified.",
            "correction_approved_by": "Plant Manager - MVP",
            "correction_date": (today - timedelta(days=22)).strftime("%Y-%m-%d"),
            "preventive_action": "Implemented predictive maintenance program with shot-count triggers.",
            "prevention_approved_by": "Emily Chen - Quality Director",
            "prevention_date": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "verification_acceptable": "yes",
            "effectiveness_check": "Follow-up audit completed. New maintenance program operational.",
            "verified_by": "Calyx QA Team",
            "verification_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "created_by": admin_id,
        },
    ]
    
    for scar in scars:
        columns = ", ".join(scar.keys())
        placeholders = ", ".join(["?" for _ in scar])
        cursor.execute(f"INSERT INTO scars ({columns}) VALUES ({placeholders})", list(scar.values()))

# Database query functions
def get_user_by_email(email: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, v.name as vendor_name 
            FROM users u LEFT JOIN vendors v ON u.vendor_id = v.id 
            WHERE u.email = ?
        """, (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, v.name as vendor_name 
            FROM users u LEFT JOIN vendors v ON u.vendor_id = v.id 
            WHERE u.id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_user(email: str, password: str, name: str, role: str, vendor_id: str = None):
    user_id = str(uuid.uuid4())
    status = "approved" if role == "admin" else "pending"
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, email, password, name, role, vendor_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, email, get_password_hash(password), name, role, vendor_id, status)
        )
    return get_user_by_id(user_id)

def get_all_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, v.name as vendor_name 
            FROM users u LEFT JOIN vendors v ON u.vendor_id = v.id 
            ORDER BY u.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def update_user(user_id: str, **kwargs):
    allowed = ['name', 'email', 'role', 'vendor_id', 'status']
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return get_user_by_id(user_id)
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [user_id]
    with get_db() as conn:
        conn.cursor().execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
    return get_user_by_id(user_id)

def update_user_password(user_id: str, new_password: str):
    with get_db() as conn:
        conn.cursor().execute("UPDATE users SET password = ? WHERE id = ?", (get_password_hash(new_password), user_id))

def delete_user(user_id: str):
    with get_db() as conn:
        conn.cursor().execute("DELETE FROM users WHERE id = ?", (user_id,))

def get_pending_users_count():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'pending'")
        return cursor.fetchone()[0]

def get_all_vendors():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

def get_vendor_by_id(vendor_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_vendor(name: str, address: str = None, phone: str = None):
    vendor_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.cursor().execute("INSERT INTO vendors (id, name, address, phone) VALUES (?, ?, ?, ?)", (vendor_id, name, address, phone))
    return get_vendor_by_id(vendor_id)

def update_vendor(vendor_id: str, **kwargs):
    allowed = ['name', 'address', 'phone']
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return get_vendor_by_id(vendor_id)
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [vendor_id]
    with get_db() as conn:
        conn.cursor().execute(f"UPDATE vendors SET {set_clause} WHERE id = ?", values)
    return get_vendor_by_id(vendor_id)

def delete_vendor(vendor_id: str):
    with get_db() as conn:
        conn.cursor().execute("DELETE FROM vendors WHERE id = ?", (vendor_id,))

def get_vendor_contacts(vendor_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendor_contacts WHERE vendor_id = ? ORDER BY is_primary DESC, name", (vendor_id,))
        return [dict(row) for row in cursor.fetchall()]

def create_vendor_contact(vendor_id: str, name: str, email: str, phone: str = None, is_primary: bool = False):
    contact_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vendor_contacts (id, vendor_id, name, email, phone, is_primary) VALUES (?, ?, ?, ?, ?, ?)",
            (contact_id, vendor_id, name, email, phone, 1 if is_primary else 0)
        )
        cursor.execute("SELECT * FROM vendor_contacts WHERE id = ?", (contact_id,))
        return dict(cursor.fetchone())

def delete_vendor_contact(contact_id: str):
    with get_db() as conn:
        conn.cursor().execute("DELETE FROM vendor_contacts WHERE id = ?", (contact_id,))

def get_next_scar_number():
    year = datetime.now().year
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT scar_number FROM scars WHERE scar_number LIKE ? ORDER BY scar_number DESC LIMIT 1", (f"SCAR-{year}-%",))
        row = cursor.fetchone()
        if row:
            last_num = int(row[0].split("-")[-1])
            return f"SCAR-{year}-{last_num + 1:03d}"
        return f"SCAR-{year}-001"

def create_scar(data: dict, created_by: str):
    scar_id = str(uuid.uuid4())
    scar_number = get_next_scar_number()
    data['id'] = scar_id
    data['scar_number'] = scar_number
    data['status'] = 'open'
    data['created_by'] = created_by
    data['created_at'] = datetime.now().isoformat()
    data['updated_at'] = datetime.now().isoformat()
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO scars ({columns}) VALUES ({placeholders})", list(data.values()))
        cursor.execute(
            "INSERT INTO scar_activity (id, scar_id, user_id, action, details) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), scar_id, created_by, "created", f"SCAR {scar_number} created")
        )
    return get_scar_by_id(scar_id)

def get_scar_by_id(scar_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, v.name as vendor_name, vc.name as contact_name, vc.email as contact_email
            FROM scars s
            LEFT JOIN vendors v ON s.vendor_id = v.id
            LEFT JOIN vendor_contacts vc ON s.vendor_contact_id = vc.id
            WHERE s.id = ?
        """, (scar_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_all_scars(vendor_id: str = None, status: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
            SELECT s.*, v.name as vendor_name, vc.name as contact_name, vc.email as contact_email
            FROM scars s
            LEFT JOIN vendors v ON s.vendor_id = v.id
            LEFT JOIN vendor_contacts vc ON s.vendor_contact_id = vc.id
            WHERE 1=1
        """
        params = []
        if vendor_id:
            query += " AND s.vendor_id = ?"
            params.append(vendor_id)
        if status:
            query += " AND s.status = ?"
            params.append(status)
        query += " ORDER BY s.created_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def update_scar(scar_id: str, data: dict, user_id: str = None):
    data['updated_at'] = datetime.now().isoformat()
    for key in ['id', 'scar_number', 'created_by', 'created_at']:
        data.pop(key, None)
    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    values = list(data.values()) + [scar_id]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE scars SET {set_clause} WHERE id = ?", values)
        if user_id:
            cursor.execute(
                "INSERT INTO scar_activity (id, scar_id, user_id, action, details) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), scar_id, user_id, "updated", "SCAR updated")
            )
    return get_scar_by_id(scar_id)

def submit_scar(scar_id: str, user_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE scars SET status = 'submitted', updated_at = ? WHERE id = ?", (datetime.now().isoformat(), scar_id))
        cursor.execute(
            "INSERT INTO scar_activity (id, scar_id, user_id, action, details) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), scar_id, user_id, "submitted", "Supplier response submitted")
        )
    return get_scar_by_id(scar_id)

def verify_scar(scar_id: str, user_id: str, acceptable: bool, reopen: bool = False):
    new_status = "open" if reopen else ("closed" if acceptable else "open")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE scars SET status = ?, updated_at = ? WHERE id = ?", (new_status, datetime.now().isoformat(), scar_id))
        action = "reopened" if reopen else ("closed" if acceptable else "returned")
        details = "SCAR reopened" if reopen else ("SCAR verified and closed" if acceptable else "SCAR returned to supplier")
        cursor.execute(
            "INSERT INTO scar_activity (id, scar_id, user_id, action, details) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), scar_id, user_id, action, details)
        )
    return get_scar_by_id(scar_id)

def get_scar_activity(scar_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, u.name as user_name
            FROM scar_activity a LEFT JOIN users u ON a.user_id = u.id
            WHERE a.scar_id = ?
            ORDER BY a.created_at DESC
        """, (scar_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_scar_stats(vendor_id: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        base = "SELECT COUNT(*) FROM scars WHERE 1=1"
        params = []
        if vendor_id:
            base += " AND vendor_id = ?"
            params = [vendor_id]
        cursor.execute(base, params)
        total = cursor.fetchone()[0]
        stats = {"total": total}
        for status in ['new', 'open', 'submitted', 'closed']:
            cursor.execute(base + " AND status = ?", params + [status])
            stats[status] = cursor.fetchone()[0]
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(base + " AND status IN ('new', 'open') AND response_due_date < ?", params + [today])
        stats['overdue'] = cursor.fetchone()[0]
        return stats

# =============================================================================
# Helper Functions
# =============================================================================

def format_date(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return date_str

def format_datetime(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return date_str

# =============================================================================
# Session State Initialization
# =============================================================================

init_database()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"

# =============================================================================
# Authentication
# =============================================================================

def login(email: str, password: str) -> bool:
    user = get_user_by_email(email)
    if user and verify_password(password, user['password']):
        if user['status'] != 'approved':
            st.error("Your account is pending approval.")
            return False
        st.session_state.authenticated = True
        st.session_state.user = user
        return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

# =============================================================================
# Pages
# =============================================================================

def show_login_page():
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
                if st.form_submit_button("Sign In", use_container_width=True):
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
                reg_name = st.text_input("Full Name")
                reg_email = st.text_input("Email Address")
                reg_vendor = st.selectbox("Select Your Company", options=[""] + [v['id'] for v in vendors],
                    format_func=lambda x: "Select..." if x == "" else next((v['name'] for v in vendors if v['id'] == x), x))
                reg_password = st.text_input("Password", type="password")
                reg_confirm = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Register", use_container_width=True):
                    if not all([reg_name, reg_email, reg_vendor, reg_password]):
                        st.error("Please fill in all fields")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match")
                    elif get_user_by_email(reg_email):
                        st.error("Account already exists")
                    else:
                        create_user(reg_email, reg_password, reg_name, "supplier", reg_vendor)
                        st.success("Registration successful! Awaiting admin approval.")

def show_sidebar():
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    
    with st.sidebar:
        st.markdown("""
        <div style="display: flex; align-items: center; padding: 1rem 0; border-bottom: 1px solid #374151; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; justify-content: center; 
                        width: 40px; height: 40px; background: #DC2626; border-radius: 8px;">
                <span style="color: white; font-weight: bold;">CC</span>
            </div>
            <div style="margin-left: 12px;">
                <div style="color: white; font-weight: 600;">SCAR System</div>
                <div style="color: #9CA3AF; font-size: 0.75rem;">Calyx Containers</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Navigation")
        
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        
        if st.button("📋 SCARs", use_container_width=True):
            st.session_state.page = "scars"
            st.rerun()
        
        if is_admin:
            pending = get_pending_users_count()
            label = f"⚙️ Settings" + (f" ({pending})" if pending > 0 else "")
            if st.button(label, use_container_width=True):
                st.session_state.page = "settings"
                st.rerun()
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="padding: 1rem; background: #374151; border-radius: 8px;">
            <div style="color: white; font-weight: 500;">{user['name']}</div>
            <div style="color: #9CA3AF; font-size: 0.75rem;">{user['email']}</div>
            <div style="color: #9CA3AF; font-size: 0.75rem;">{'Admin' if is_admin else user.get('vendor_name', 'Supplier')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👤 Profile", use_container_width=True):
                st.session_state.page = "profile"
                st.rerun()
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                logout()

def show_dashboard():
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    vendor_id = None if is_admin else user.get('vendor_id')
    
    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome back, {user['name'].split()[0]} 👋</h1>
        <p>{'SCAR Management Overview' if is_admin else f"SCARs for {user.get('vendor_name', 'your organization')}"}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if is_admin:
        if st.button("➕ Create SCAR", type="primary"):
            st.session_state.page = "scar_create"
            st.rerun()
    
    stats = get_scar_stats(vendor_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>📂 Open</h3><div class="value">{stats.get("open", 0)}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>📤 Submitted</h3><div class="value">{stats.get("submitted", 0)}</div></div>', unsafe_allow_html=True)
    with col3:
        color = "#DC2626" if stats.get("overdue", 0) > 0 else "#111827"
        st.markdown(f'<div class="metric-card"><h3>⚠️ Overdue</h3><div class="value" style="color:{color};">{stats.get("overdue", 0)}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><h3>✅ Closed</h3><div class="value">{stats.get("closed", 0)}</div></div>', unsafe_allow_html=True)
    
    st.markdown("### Recent SCARs")
    scars = get_all_scars(vendor_id=vendor_id)[:5]
    
    if not scars:
        st.info("No SCARs found.")
    else:
        for scar in scars:
            col1, col2, col3 = st.columns([2, 4, 1])
            with col1:
                st.markdown(f"**{scar['scar_number']}**")
                st.markdown(f'<span class="badge badge-{scar["status"]}">{scar["status"].upper()}</span>', unsafe_allow_html=True)
            with col2:
                st.markdown(f"{scar.get('product_name') or 'No description'}")
                st.caption(f"Vendor: {scar.get('vendor_name', 'Unassigned')}" if is_admin else f"Due: {format_date(scar.get('response_due_date'))}")
            with col3:
                if st.button("View", key=f"dash_{scar['id']}"):
                    st.session_state.selected_scar_id = scar['id']
                    st.session_state.page = "scar_detail"
                    st.rerun()
            st.markdown("---")

def show_scars_list():
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    vendor_id = None if is_admin else user.get('vendor_id')
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 📋 SCARs")
    with col2:
        if is_admin and st.button("➕ Create SCAR", type="primary"):
            st.session_state.page = "scar_create"
            st.rerun()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Open", "Submitted", "Closed"])
    with col2:
        if is_admin:
            vendors = get_all_vendors()
            vendor_filter = st.selectbox("Vendor", ["All"] + [v['name'] for v in vendors])
            if vendor_filter != "All":
                vendor_id = next((v['id'] for v in vendors if v['name'] == vendor_filter), None)
    with col3:
        search = st.text_input("🔍 Search")
    
    status = None if status_filter == "All" else status_filter.lower()
    scars = get_all_scars(vendor_id=vendor_id, status=status)
    
    if search:
        search_lower = search.lower()
        scars = [s for s in scars if search_lower in s.get('scar_number', '').lower() or 
                 search_lower in (s.get('product_name') or '').lower()]
    
    st.caption(f"Showing {len(scars)} SCAR(s)")
    
    for scar in scars:
        col1, col2, col3, col4 = st.columns([1.5, 3, 2, 1])
        with col1:
            st.markdown(f"**{scar['scar_number']}**")
            st.markdown(f'<span class="badge badge-{scar["status"]}">{scar["status"].upper()}</span>', unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{scar.get('product_name') or 'No product'}**")
            st.caption(scar.get('vendor_name', 'Unassigned') if is_admin else f"Due: {format_date(scar.get('response_due_date'))}")
        with col3:
            if scar.get('severity'):
                st.markdown(f'<span class="badge badge-{scar["severity"]}">{scar["severity"].upper()}</span>', unsafe_allow_html=True)
        with col4:
            if st.button("View", key=f"list_{scar['id']}"):
                st.session_state.selected_scar_id = scar['id']
                st.session_state.page = "scar_detail"
                st.rerun()
        st.markdown("---")

def show_scar_detail():
    user = st.session_state.user
    is_admin = user['role'] == 'admin'
    scar_id = st.session_state.get('selected_scar_id')
    
    if not scar_id:
        st.error("No SCAR selected")
        if st.button("← Back"):
            st.session_state.page = "scars"
            st.rerun()
        return
    
    scar = get_scar_by_id(scar_id)
    if not scar:
        st.error("SCAR not found")
        return
    
    if not is_admin and scar.get('vendor_id') != user.get('vendor_id'):
        st.error("Access denied")
        return
    
    can_edit = (is_admin or user['role'] == 'supplier') and scar['status'] in ['new', 'open']
    can_submit = user['role'] == 'supplier' and scar['status'] == 'open'
    can_verify = is_admin and scar['status'] == 'submitted'
    
    if st.button("← Back to SCARs"):
        st.session_state.page = "scars"
        st.rerun()
    
    st.markdown(f"# {scar['scar_number']}")
    st.markdown(f'<span class="badge badge-{scar["status"]}">{scar["status"].upper()}</span>', unsafe_allow_html=True)
    
    tabs = st.tabs(["Details", "Non-Conformity", "Containment", "Root Cause", "Correction", "Prevention", "Verification"])
    
    # Tab 1: Details
    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("SCAR Number", scar['scar_number'], disabled=True)
            st.text_input("Date Issued", format_date(scar.get('date_issued')), disabled=True)
            st.text_input("Due Date", format_date(scar.get('response_due_date')), disabled=True)
        with col2:
            st.text_input("Vendor", scar.get('vendor_name', ''), disabled=True)
            st.text_input("Contact", scar.get('contact_name', ''), disabled=True)
            st.text_input("NCR #", scar.get('ncr_number', ''), disabled=True)
    
    # Tab 2: Non-Conformity
    with tabs[1]:
        st.text_input("Product", scar.get('product_name', ''), disabled=True)
        st.text_input("Defect Type", scar.get('defect_type', ''), disabled=True)
        st.text_area("Description", scar.get('nonconformity_description', ''), disabled=True)
        st.text_input("Severity", (scar.get('severity') or '').capitalize(), disabled=True)
    
    # Tab 3: Containment
    with tabs[2]:
        with st.form("containment"):
            isolate = st.text_area("Isolate Affected Inventory", scar.get('containment_isolate', ''), disabled=not can_edit)
            screen = st.text_area("Screen and Sort", scar.get('containment_screen_sort', ''), disabled=not can_edit)
            col1, col2 = st.columns(2)
            with col1:
                prep_by = st.text_input("Prepared By", scar.get('containment_prepared_by', ''), disabled=not can_edit)
            with col2:
                prep_date = st.text_input("Date", scar.get('containment_date', ''), disabled=not can_edit)
            if can_edit and st.form_submit_button("Save"):
                update_scar(scar_id, {'containment_isolate': isolate, 'containment_screen_sort': screen,
                    'containment_prepared_by': prep_by, 'containment_date': prep_date}, user['id'])
                st.success("Saved!")
                st.rerun()
    
    # Tab 4: Root Cause
    with tabs[3]:
        with st.form("root_cause"):
            rc = st.text_area("Root Cause (5 Whys)", scar.get('root_cause', ''), disabled=not can_edit, height=150)
            evidence = st.text_area("Evidence", scar.get('root_cause_evidence', ''), disabled=not can_edit)
            col1, col2 = st.columns(2)
            with col1:
                rc_by = st.text_input("Approved By", scar.get('root_cause_approved_by', ''), disabled=not can_edit)
            with col2:
                rc_date = st.text_input("Date", scar.get('root_cause_date', ''), disabled=not can_edit)
            if can_edit and st.form_submit_button("Save"):
                update_scar(scar_id, {'root_cause': rc, 'root_cause_evidence': evidence,
                    'root_cause_approved_by': rc_by, 'root_cause_date': rc_date}, user['id'])
                st.success("Saved!")
                st.rerun()
    
    # Tab 5: Correction
    with tabs[4]:
        with st.form("correction"):
            ca = st.text_area("Corrective Action", scar.get('corrective_action', ''), disabled=not can_edit, height=150)
            col1, col2 = st.columns(2)
            with col1:
                ca_by = st.text_input("Approved By", scar.get('correction_approved_by', ''), disabled=not can_edit)
            with col2:
                ca_date = st.text_input("Date", scar.get('correction_date', ''), disabled=not can_edit)
            if can_edit and st.form_submit_button("Save"):
                update_scar(scar_id, {'corrective_action': ca, 'correction_approved_by': ca_by,
                    'correction_date': ca_date}, user['id'])
                st.success("Saved!")
                st.rerun()
    
    # Tab 6: Prevention
    with tabs[5]:
        with st.form("prevention"):
            pa = st.text_area("Preventive Action", scar.get('preventive_action', ''), disabled=not can_edit, height=150)
            col1, col2 = st.columns(2)
            with col1:
                pa_by = st.text_input("Approved By", scar.get('prevention_approved_by', ''), disabled=not can_edit)
            with col2:
                pa_date = st.text_input("Date", scar.get('prevention_date', ''), disabled=not can_edit)
            if can_edit and st.form_submit_button("Save"):
                update_scar(scar_id, {'preventive_action': pa, 'prevention_approved_by': pa_by,
                    'prevention_date': pa_date}, user['id'])
                st.success("Saved!")
                st.rerun()
    
    # Tab 7: Verification
    with tabs[6]:
        if not is_admin:
            st.info("This section is for Calyx QA team only.")
            if scar['status'] == 'closed' and scar.get('verification_acceptable') == 'yes':
                st.success("✅ Response accepted")
        else:
            with st.form("verification"):
                acceptable = st.radio("Response Acceptable?", ['', 'yes', 'no'],
                    format_func=lambda x: {'': 'Select...', 'yes': '✅ Yes', 'no': '❌ No'}[x],
                    index=['', 'yes', 'no'].index(scar.get('verification_acceptable') or ''),
                    disabled=scar['status'] == 'closed')
                eff = st.text_area("Effectiveness Check", scar.get('effectiveness_check', ''), disabled=scar['status'] == 'closed')
                col1, col2 = st.columns(2)
                with col1:
                    ver_by = st.text_input("Verified By", scar.get('verified_by', ''), disabled=scar['status'] == 'closed')
                with col2:
                    ver_date = st.text_input("Date", scar.get('verification_date', ''), disabled=scar['status'] == 'closed')
                if scar['status'] != 'closed' and st.form_submit_button("Save"):
                    update_scar(scar_id, {'verification_acceptable': acceptable, 'effectiveness_check': eff,
                        'verified_by': ver_by, 'verification_date': ver_date}, user['id'])
                    st.success("Saved!")
                    st.rerun()
    
    # Actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    if can_submit:
        with col1:
            if st.button("📤 Submit Response", type="primary"):
                submit_scar(scar_id, user['id'])
                st.success("Submitted!")
                st.rerun()
    
    if can_verify:
        with col1:
            if st.button("✅ Verify & Close", type="primary"):
                verify_scar(scar_id, user['id'], acceptable=True)
                st.success("Closed!")
                st.rerun()
        with col2:
            if st.button("↩️ Return to Supplier"):
                verify_scar(scar_id, user['id'], acceptable=False)
                st.success("Returned!")
                st.rerun()
    
    if is_admin and scar['status'] == 'closed':
        with col1:
            if st.button("🔄 Reopen"):
                verify_scar(scar_id, user['id'], acceptable=False, reopen=True)
                st.success("Reopened!")
                st.rerun()

def show_scar_create():
    user = st.session_state.user
    if user['role'] != 'admin':
        st.error("Access denied")
        return
    
    if st.button("← Back"):
        st.session_state.page = "scars"
        st.rerun()
    
    st.markdown("# ➕ Create SCAR")
    
    vendors = get_all_vendors()
    
    with st.form("create_scar"):
        col1, col2 = st.columns(2)
        with col1:
            date_issued = st.date_input("Date Issued", datetime.now().date())
            due_date = st.date_input("Due Date", (datetime.now() + timedelta(days=14)).date())
            ncr = st.text_input("NCR #")
        with col2:
            vendor_id = st.selectbox("Vendor", [""] + [v['id'] for v in vendors],
                format_func=lambda x: "Select..." if x == "" else next((v['name'] for v in vendors if v['id'] == x), x))
            contacts = get_vendor_contacts(vendor_id) if vendor_id else []
            contact_id = st.selectbox("Contact", [""] + [c['id'] for c in contacts],
                format_func=lambda x: "Select..." if x == "" else next((c['name'] for c in contacts if c['id'] == x), x),
                disabled=not vendor_id)
            po = st.text_input("PO/SO #")
        
        product = st.text_input("Product Name")
        defect = st.selectbox("Defect Type", ["", "Dimensional", "Visual", "Functional", "Labeling", "Packaging", "Other"])
        desc = st.text_area("Description", height=100)
        severity = st.radio("Severity", ["minor", "major", "critical"], horizontal=True,
            format_func=lambda x: {"minor": "🟢 Minor", "major": "🟡 Major", "critical": "🔴 Critical"}[x])
        
        if st.form_submit_button("Create SCAR", type="primary"):
            if not all([vendor_id, contact_id, product, defect, desc]):
                st.error("Please fill required fields")
            else:
                scar = create_scar({
                    'date_issued': date_issued.isoformat(),
                    'response_due_date': due_date.isoformat(),
                    'vendor_id': vendor_id,
                    'vendor_contact_id': contact_id,
                    'ncr_number': ncr,
                    'po_so_number': po,
                    'product_name': product,
                    'defect_type': defect,
                    'nonconformity_description': desc,
                    'severity': severity,
                }, user['id'])
                st.success(f"Created {scar['scar_number']}!")
                st.session_state.selected_scar_id = scar['id']
                st.session_state.page = "scar_detail"
                st.rerun()

def show_settings():
    user = st.session_state.user
    if user['role'] != 'admin':
        st.error("Access denied")
        return
    
    st.markdown("# ⚙️ Settings")
    
    tab1, tab2 = st.tabs(["👥 Users", "🏢 Vendors"])
    
    with tab1:
        users = get_all_users()
        vendors = get_all_vendors()
        pending = [u for u in users if u['status'] == 'pending']
        
        # Add User Form
        with st.expander("➕ Add User"):
            with st.form("add_user"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Full Name *")
                    new_email = st.text_input("Email *")
                    new_password = st.text_input("Password *", type="password")
                with col2:
                    new_role = st.selectbox("Role *", ["supplier", "admin"], 
                        format_func=lambda x: "🔑 Administrator" if x == "admin" else "📦 Supplier")
                    new_vendor = st.selectbox("Vendor (for suppliers)", 
                        options=[""] + [v['id'] for v in vendors],
                        format_func=lambda x: "Select vendor..." if x == "" else next((v['name'] for v in vendors if v['id'] == x), x))
                    new_status = st.selectbox("Status", ["approved", "pending"],
                        format_func=lambda x: "✅ Approved" if x == "approved" else "⏳ Pending")
                
                if st.form_submit_button("Create User", use_container_width=True):
                    if not all([new_name, new_email, new_password]):
                        st.error("Please fill in name, email, and password")
                    elif new_role == "supplier" and not new_vendor:
                        st.error("Please select a vendor for supplier accounts")
                    elif get_user_by_email(new_email):
                        st.error("A user with this email already exists")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        new_user = create_user(new_email, new_password, new_name, new_role, 
                            new_vendor if new_role == "supplier" else None)
                        if new_status == "approved":
                            update_user(new_user['id'], status='approved')
                        st.success(f"User '{new_name}' created successfully!")
                        st.rerun()
        
        # Pending Approvals
        if pending:
            st.markdown("### ⏳ Pending Approvals")
            for p in pending:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{p['name']}** ({p['email']})")
                    st.caption(f"Vendor: {p.get('vendor_name', 'N/A')}")
                with col2:
                    if st.button("✅ Approve", key=f"approve_{p['id']}"):
                        update_user(p['id'], status='approved')
                        st.rerun()
                with col3:
                    if st.button("❌ Reject", key=f"reject_{p['id']}"):
                        update_user(p['id'], status='rejected')
                        st.rerun()
            st.markdown("---")
        
        st.markdown("### All Users")
        for u in users:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{u['name']}** ({u['email']})")
            with col2:
                role_label = '🔑 Admin' if u['role'] == 'admin' else f"📦 {u.get('vendor_name', 'Supplier')}"
                status_icon = {'approved': '✅', 'pending': '⏳', 'rejected': '❌'}.get(u['status'], '⚪')
                st.caption(f"{role_label} - {status_icon} {u['status']}")
            with col3:
                if u['id'] != user['id'] and st.button("🗑️", key=f"del_user_{u['id']}"):
                    delete_user(u['id'])
                    st.rerun()
    
    with tab2:
        with st.expander("➕ Add Vendor"):
            with st.form("add_vendor"):
                name = st.text_input("Name")
                addr = st.text_input("Address")
                phone = st.text_input("Phone")
                if st.form_submit_button("Add"):
                    if name:
                        create_vendor(name, addr, phone)
                        st.rerun()
        
        for v in get_all_vendors():
            with st.expander(f"🏢 {v['name']}"):
                st.caption(f"Address: {v.get('address', 'N/A')} | Phone: {v.get('phone', 'N/A')}")
                contacts = get_vendor_contacts(v['id'])
                if contacts:
                    for c in contacts:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"• {c['name']} ({c['email']})")
                        with col2:
                            if st.button("🗑️", key=f"del_contact_{c['id']}"):
                                delete_vendor_contact(c['id'])
                                st.rerun()
                
                with st.form(f"add_contact_{v['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        c_name = st.text_input("Name", key=f"cn_{v['id']}")
                    with col2:
                        c_email = st.text_input("Email", key=f"ce_{v['id']}")
                    if st.form_submit_button("Add Contact"):
                        if c_name and c_email:
                            create_vendor_contact(v['id'], c_name, c_email)
                            st.rerun()

def show_profile():
    user = st.session_state.user
    st.markdown("# 👤 Profile")
    
    st.markdown(f"**Name:** {user['name']}")
    st.markdown(f"**Email:** {user['email']}")
    st.markdown(f"**Role:** {'Administrator' if user['role'] == 'admin' else 'Supplier'}")
    
    st.markdown("---")
    st.markdown("### Change Password")
    
    with st.form("change_password"):
        current = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Update"):
            if not all([current, new_pw, confirm]):
                st.error("Fill all fields")
            elif new_pw != confirm:
                st.error("Passwords don't match")
            else:
                u = get_user_by_id(user['id'])
                if not verify_password(current, u['password']):
                    st.error("Wrong current password")
                else:
                    update_user_password(user['id'], new_pw)
                    st.success("Password updated!")

# =============================================================================
# Main Router
# =============================================================================

def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_sidebar()
        page = st.session_state.page
        
        if page == "dashboard":
            show_dashboard()
        elif page == "scars":
            show_scars_list()
        elif page == "scar_detail":
            show_scar_detail()
        elif page == "scar_create":
            show_scar_create()
        elif page == "settings":
            show_settings()
        elif page == "profile":
            show_profile()
        else:
            show_dashboard()

if __name__ == "__main__":
    main()
