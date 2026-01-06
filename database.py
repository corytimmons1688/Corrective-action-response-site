"""
Database module for SCAR Management System
Handles all SQLite operations for users, vendors, and SCARs
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "data" / "scar.db"

def get_password_hash(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return get_password_hash(password) == hashed

@contextmanager
def get_db():
    """Context manager for database connections"""
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
    """Initialize database schema and seed data"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create vendors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                address TEXT,
                phone TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create vendor_contacts table
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
        
        # Create users table
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
        
        # Create SCARs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scars (
                id TEXT PRIMARY KEY,
                scar_number TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new', 'open', 'submitted', 'closed')),
                
                -- SCAR Details (Section 1)
                date_issued TEXT,
                response_due_date TEXT,
                vendor_id TEXT,
                vendor_contact_id TEXT,
                ncr_number TEXT,
                po_so_number TEXT,
                part_sku_number TEXT,
                affected_quantity INTEGER,
                lot_numbers TEXT,
                
                -- Non-Conformity (Section 2)
                product_name TEXT,
                defect_type TEXT,
                nonconformity_description TEXT,
                severity TEXT CHECK(severity IN ('minor', 'major', 'critical')),
                
                -- Containment (Section 3)
                containment_isolate TEXT,
                containment_screen_sort TEXT,
                containment_prepared_by TEXT,
                containment_date TEXT,
                
                -- Root Cause (Section 4)
                root_cause TEXT,
                root_cause_evidence TEXT,
                root_cause_approved_by TEXT,
                root_cause_date TEXT,
                
                -- Correction (Section 5)
                corrective_action TEXT,
                correction_approved_by TEXT,
                correction_date TEXT,
                
                -- Prevention (Section 6)
                preventive_action TEXT,
                prevention_approved_by TEXT,
                prevention_date TEXT,
                
                -- Verification (Section 7)
                verification_acceptable TEXT CHECK(verification_acceptable IN ('yes', 'no', '')),
                effectiveness_check TEXT,
                verified_by TEXT,
                verification_date TEXT,
                
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL,
                FOREIGN KEY (vendor_contact_id) REFERENCES vendor_contacts(id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Create activity log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scar_activity (
                id TEXT PRIMARY KEY,
                scar_id TEXT NOT NULL,
                user_id TEXT,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scar_id) REFERENCES scars(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM vendors")
        if cursor.fetchone()[0] == 0:
            seed_database(cursor)

def seed_database(cursor):
    """Seed database with initial data"""
    
    # Create vendors
    vendors = [
        (str(uuid.uuid4()), "Pacific Glass Co.", "123 Harbor Blvd, Long Beach, CA 90802", "(562) 555-0100"),
        (str(uuid.uuid4()), "Western Packaging Inc.", "456 Industrial Way, Phoenix, AZ 85001", "(602) 555-0200"),
        (str(uuid.uuid4()), "Mountain View Plastics", "789 Tech Park Dr, Denver, CO 80202", "(303) 555-0300"),
        (str(uuid.uuid4()), "Coastal Container Corp.", "321 Seaside Ave, San Diego, CA 92101", "(619) 555-0400"),
    ]
    cursor.executemany(
        "INSERT INTO vendors (id, name, address, phone) VALUES (?, ?, ?, ?)",
        vendors
    )
    
    # Create vendor contacts
    contacts = [
        (str(uuid.uuid4()), vendors[0][0], "John Smith", "jsmith@pacificglass.com", "(562) 555-0101", 1),
        (str(uuid.uuid4()), vendors[0][0], "Sarah Johnson", "sjohnson@pacificglass.com", "(562) 555-0102", 0),
        (str(uuid.uuid4()), vendors[1][0], "Mike Wilson", "mwilson@westernpkg.com", "(602) 555-0201", 1),
        (str(uuid.uuid4()), vendors[2][0], "Emily Chen", "echen@mvplastics.com", "(303) 555-0301", 1),
        (str(uuid.uuid4()), vendors[3][0], "Robert Garcia", "rgarcia@coastalcontainer.com", "(619) 555-0401", 1),
    ]
    cursor.executemany(
        "INSERT INTO vendor_contacts (id, vendor_id, name, email, phone, is_primary) VALUES (?, ?, ?, ?, ?, ?)",
        contacts
    )
    
    # Create admin user
    admin_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO users (id, email, password, name, role, status) VALUES (?, ?, ?, ?, ?, ?)",
        (admin_id, "admin@calyxcontainers.com", get_password_hash("admin123"), "Admin User", "admin", "approved")
    )
    
    # Create supplier user
    supplier_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO users (id, email, password, name, role, vendor_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (supplier_id, "jsmith@pacificglass.com", get_password_hash("supplier123"), "John Smith", "supplier", vendors[0][0], "approved")
    )
    
    # Create sample SCARs
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
            "root_cause_evidence": "Lab analysis confirmed different pigment composition. Supplier documentation shows vendor change on 2026-01-15.",
            "root_cause_approved_by": "Quality Manager - Western Pkg",
            "root_cause_date": (today - timedelta(days=8)).strftime("%Y-%m-%d"),
            "corrective_action": "Reverted to original pigment supplier. Implemented incoming inspection for color consistency.",
            "correction_approved_by": "Mike Wilson",
            "correction_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "preventive_action": "1. Established formal change notification procedure with 30-day advance notice requirement.\n2. Added color consistency check to incoming QC protocol.\n3. Quarterly supplier audits now include raw material sourcing review.",
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
            "nonconformity_description": "Child-resistant mechanism fails testing. Cap opens without proper push-and-turn motion.",
            "severity": "critical",
            "containment_isolate": "Entire lot quarantined. Customer shipments halted pending investigation.",
            "containment_screen_sort": "Functional testing on 250 sample units. 23% failure rate confirmed.",
            "containment_prepared_by": "Emily Chen",
            "containment_date": (today - timedelta(days=28)).strftime("%Y-%m-%d"),
            "root_cause": "1. Why mechanism fails? Locking tab height insufficient.\n2. Why insufficient? Mold wear detected.\n3. Why wear not caught? Maintenance schedule overdue.\n4. Why overdue? Resource constraints.\n5. Why constraints? Inadequate maintenance staffing.",
            "root_cause_evidence": "Mold inspection photos showing 0.3mm wear on locking tab cavity. Maintenance logs show 45-day overdue status.",
            "root_cause_approved_by": "Emily Chen - Quality Director",
            "root_cause_date": (today - timedelta(days=25)).strftime("%Y-%m-%d"),
            "corrective_action": "Mold refurbished and recertified. Added dedicated maintenance technician to CR cap production line.",
            "correction_approved_by": "Plant Manager - MVP",
            "correction_date": (today - timedelta(days=22)).strftime("%Y-%m-%d"),
            "preventive_action": "1. Implemented predictive maintenance program with shot-count triggers.\n2. Weekly dimensional checks on all CR components.\n3. Hired additional maintenance staff.\n4. Created maintenance dashboard for real-time monitoring.",
            "prevention_approved_by": "Emily Chen - Quality Director",
            "prevention_date": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "verification_acceptable": "yes",
            "effectiveness_check": "Follow-up audit completed. New maintenance program operational. 3 production runs passed all CR testing requirements.",
            "verified_by": "Calyx QA Team",
            "verification_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "created_by": admin_id,
        },
    ]
    
    for scar in scars:
        columns = ", ".join(scar.keys())
        placeholders = ", ".join(["?" for _ in scar])
        cursor.execute(
            f"INSERT INTO scars ({columns}) VALUES ({placeholders})",
            list(scar.values())
        )

# =============================================================================
# User Operations
# =============================================================================

def get_user_by_email(email: str) -> dict | None:
    """Get user by email"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, v.name as vendor_name 
            FROM users u 
            LEFT JOIN vendors v ON u.vendor_id = v.id 
            WHERE u.email = ?
        """, (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id: str) -> dict | None:
    """Get user by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, v.name as vendor_name 
            FROM users u 
            LEFT JOIN vendors v ON u.vendor_id = v.id 
            WHERE u.id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_user(email: str, password: str, name: str, role: str, vendor_id: str = None) -> dict:
    """Create a new user"""
    user_id = str(uuid.uuid4())
    status = "approved" if role == "admin" else "pending"
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, email, password, name, role, vendor_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, email, get_password_hash(password), name, role, vendor_id, status)
        )
    
    return get_user_by_id(user_id)

def get_all_users() -> list:
    """Get all users with vendor info"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, v.name as vendor_name 
            FROM users u 
            LEFT JOIN vendors v ON u.vendor_id = v.id 
            ORDER BY u.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def update_user(user_id: str, **kwargs) -> dict:
    """Update user fields"""
    allowed_fields = ['name', 'email', 'role', 'vendor_id', 'status']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return get_user_by_id(user_id)
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [user_id]
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
    
    return get_user_by_id(user_id)

def update_user_password(user_id: str, new_password: str):
    """Update user password"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (get_password_hash(new_password), user_id)
        )

def delete_user(user_id: str):
    """Delete a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

def get_pending_users_count() -> int:
    """Get count of pending user approvals"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'pending'")
        return cursor.fetchone()[0]

# =============================================================================
# Vendor Operations
# =============================================================================

def get_all_vendors() -> list:
    """Get all vendors"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

def get_vendor_by_id(vendor_id: str) -> dict | None:
    """Get vendor by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_vendor(name: str, address: str = None, phone: str = None) -> dict:
    """Create a new vendor"""
    vendor_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vendors (id, name, address, phone) VALUES (?, ?, ?, ?)",
            (vendor_id, name, address, phone)
        )
    return get_vendor_by_id(vendor_id)

def update_vendor(vendor_id: str, **kwargs) -> dict:
    """Update vendor fields"""
    allowed_fields = ['name', 'address', 'phone']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return get_vendor_by_id(vendor_id)
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [vendor_id]
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE vendors SET {set_clause} WHERE id = ?", values)
    
    return get_vendor_by_id(vendor_id)

def delete_vendor(vendor_id: str):
    """Delete a vendor"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vendors WHERE id = ?", (vendor_id,))

def get_vendor_contacts(vendor_id: str) -> list:
    """Get all contacts for a vendor"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM vendor_contacts WHERE vendor_id = ? ORDER BY is_primary DESC, name",
            (vendor_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def create_vendor_contact(vendor_id: str, name: str, email: str, phone: str = None, is_primary: bool = False) -> dict:
    """Create a vendor contact"""
    contact_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vendor_contacts (id, vendor_id, name, email, phone, is_primary) VALUES (?, ?, ?, ?, ?, ?)",
            (contact_id, vendor_id, name, email, phone, 1 if is_primary else 0)
        )
        cursor.execute("SELECT * FROM vendor_contacts WHERE id = ?", (contact_id,))
        return dict(cursor.fetchone())

def update_vendor_contact(contact_id: str, **kwargs) -> dict:
    """Update vendor contact"""
    allowed_fields = ['name', 'email', 'phone', 'is_primary']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if 'is_primary' in updates:
        updates['is_primary'] = 1 if updates['is_primary'] else 0
    
    if not updates:
        return None
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [contact_id]
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE vendor_contacts SET {set_clause} WHERE id = ?", values)
        cursor.execute("SELECT * FROM vendor_contacts WHERE id = ?", (contact_id,))
        return dict(cursor.fetchone())

def delete_vendor_contact(contact_id: str):
    """Delete a vendor contact"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vendor_contacts WHERE id = ?", (contact_id,))

# =============================================================================
# SCAR Operations
# =============================================================================

def get_next_scar_number() -> str:
    """Generate next SCAR number"""
    year = datetime.now().year
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT scar_number FROM scars WHERE scar_number LIKE ? ORDER BY scar_number DESC LIMIT 1",
            (f"SCAR-{year}-%",)
        )
        row = cursor.fetchone()
        if row:
            last_num = int(row[0].split("-")[-1])
            return f"SCAR-{year}-{last_num + 1:03d}"
        return f"SCAR-{year}-001"

def create_scar(data: dict, created_by: str) -> dict:
    """Create a new SCAR"""
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
        
        # Log activity
        cursor.execute(
            "INSERT INTO scar_activity (id, scar_id, user_id, action, details) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), scar_id, created_by, "created", f"SCAR {scar_number} created")
        )
    
    return get_scar_by_id(scar_id)

def get_scar_by_id(scar_id: str) -> dict | None:
    """Get SCAR by ID with vendor info"""
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

def get_all_scars(vendor_id: str = None, status: str = None) -> list:
    """Get all SCARs, optionally filtered by vendor and/or status"""
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

def update_scar(scar_id: str, data: dict, user_id: str = None) -> dict:
    """Update SCAR fields"""
    data['updated_at'] = datetime.now().isoformat()
    
    # Remove fields that shouldn't be updated
    data.pop('id', None)
    data.pop('scar_number', None)
    data.pop('created_by', None)
    data.pop('created_at', None)
    
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

def submit_scar(scar_id: str, user_id: str) -> dict:
    """Submit SCAR response (supplier action)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE scars SET status = 'submitted', updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), scar_id)
        )
        cursor.execute(
            "INSERT INTO scar_activity (id, scar_id, user_id, action, details) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), scar_id, user_id, "submitted", "Supplier response submitted")
        )
    return get_scar_by_id(scar_id)

def verify_scar(scar_id: str, user_id: str, acceptable: bool, reopen: bool = False) -> dict:
    """Verify SCAR (admin action)"""
    new_status = "open" if reopen else ("closed" if acceptable else "open")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE scars SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, datetime.now().isoformat(), scar_id)
        )
        
        action = "reopened" if reopen else ("closed" if acceptable else "returned")
        details = "SCAR reopened for revision" if reopen else (
            "SCAR verified and closed" if acceptable else "SCAR returned to supplier for revision"
        )
        cursor.execute(
            "INSERT INTO scar_activity (id, scar_id, user_id, action, details) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), scar_id, user_id, action, details)
        )
    
    return get_scar_by_id(scar_id)

def get_scar_activity(scar_id: str) -> list:
    """Get activity log for a SCAR"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, u.name as user_name
            FROM scar_activity a
            LEFT JOIN users u ON a.user_id = u.id
            WHERE a.scar_id = ?
            ORDER BY a.created_at DESC
        """, (scar_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_scar_stats(vendor_id: str = None) -> dict:
    """Get SCAR statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        base_query = "SELECT COUNT(*) FROM scars WHERE 1=1"
        params = []
        
        if vendor_id:
            base_query += " AND vendor_id = ?"
            params = [vendor_id]
        
        # Total
        cursor.execute(base_query, params)
        total = cursor.fetchone()[0]
        
        # By status
        stats = {"total": total}
        for status in ['new', 'open', 'submitted', 'closed']:
            cursor.execute(base_query + " AND status = ?", params + [status])
            stats[status] = cursor.fetchone()[0]
        
        # Overdue
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            base_query + " AND status IN ('new', 'open') AND response_due_date < ?",
            params + [today]
        )
        stats['overdue'] = cursor.fetchone()[0]
        
        return stats
