# SCAR Management System

A web-based Supplier Corrective Action Report (SCAR) management system built with Streamlit for Calyx Containers.

## Features

### Authentication & Authorization
- Secure login system for admin and supplier users
- Self-registration for suppliers with admin approval workflow
- Role-based access control (Admin vs Supplier)
- Password management

### Admin Functionality
- **Full SCAR Management**: Create, view, edit, and manage all SCARs
- **User Management**: Approve/reject new accounts, manage user roles and vendors
- **Vendor Management**: Add/edit vendors and their contacts
- **Verification**: Review and verify supplier responses, close SCARs

### Supplier Functionality
- **Restricted Access**: View only SCARs assigned to their vendor
- **Response Submission**: Complete Containment, Root Cause, Correction, and Prevention sections
- **Status Tracking**: Monitor SCAR status from Open → Submitted → Closed

### SCAR Workflow
1. **Open** - Admin creates SCAR with non-conformity details
2. **Submitted** - Supplier completes and submits response
3. **Closed** - Admin verifies and closes SCAR

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd scar-management-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

### Streamlit Cloud Deployment

1. Push the repository to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io/)
3. Connect your GitHub repository
4. Set the main file path to `app.py`
5. Deploy!

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@calyxcontainers.com | admin123 |
| Supplier | jsmith@pacificglass.com | supplier123 |

## Project Structure

```
scar-management-system/
├── app.py                 # Complete Streamlit application (single file)
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .streamlit/
│   └── config.toml       # Streamlit configuration (theme)
└── data/
    └── scar.db           # SQLite database (auto-created)
```

## SCAR Form Sections

1. **SCAR Details** (Admin only) - SCAR Number, Dates, Vendor, Contact info
2. **Non-Conformity** (Admin only) - Product, Defect Type, Description, Severity
3. **Containment** (Supplier) - Isolate affected inventory, Screen and sort
4. **Root Cause** (Supplier) - 5 Whys analysis, Supporting evidence
5. **Corrective Action** (Supplier) - Actions taken, Rationale
6. **Preventive Action** (Supplier) - Preventive measures, Target dates
7. **Verification** (Admin only) - Accept/reject, Effectiveness check

## Database

SQLite database auto-created on first run with seed data:
- 4 sample vendors with contacts
- 2 users (1 admin, 1 supplier)
- 3 sample SCARs in different states

## License

Internal use only - Calyx Containers
