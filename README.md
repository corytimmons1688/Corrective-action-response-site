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

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

5. Open your browser to `http://localhost:8501`

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
├── app.py                 # Main Streamlit application
├── database.py            # SQLite database operations
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── pages/
│   ├── __init__.py
│   ├── dashboard.py      # Dashboard page
│   ├── scars.py          # SCARs list page
│   ├── scar_detail.py    # SCAR detail/edit page
│   ├── scar_create.py    # Create new SCAR (admin)
│   ├── settings.py       # User & vendor management
│   └── profile.py        # User profile page
└── data/
    └── scar.db           # SQLite database (auto-created)
```

## SCAR Form Sections

### Section 1: SCAR Details (Admin only)
- SCAR Number, Date Issued, Due Date
- Vendor, Contact, NCR#, PO/SO#
- Part/SKU, Quantity, Lot Numbers

### Section 2: Non-Conformity (Admin only)
- Product Name, Defect Type
- Description, Severity (Minor/Major/Critical)

### Section 3: Containment (Supplier)
- Isolate affected inventory
- Screen and sort actions

### Section 4: Root Cause (Supplier)
- 5 Whys analysis
- Supporting evidence

### Section 5: Corrective Action (Supplier)
- Corrective actions taken
- Rationale

### Section 6: Preventive Action (Supplier)
- Preventive measures
- Responsible parties and target dates

### Section 7: Verification (Admin only)
- Accept/reject response
- Effectiveness check
- Close SCAR

## Database

The application uses SQLite for data storage. The database is automatically created on first run with seed data including:

- 4 sample vendors with contacts
- 2 users (1 admin, 1 supplier)
- 3 sample SCARs in different states

Database location: `./data/scar.db`

## Security Notes

- Passwords are hashed using SHA-256
- Session-based authentication via Streamlit
- Role-based access control throughout
- Suppliers can only access their own vendor's SCARs

## Customization

### Branding
Update the theme colors in `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#DC2626"  # Calyx red
```

### Adding New Fields
1. Update the schema in `database.py` (init_database function)
2. Add UI elements in the appropriate page file
3. Update the database operations as needed

## License

Internal use only - Calyx Containers

## Support

For issues or questions, contact the Calyx Containers IT team.
