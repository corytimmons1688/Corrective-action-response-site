# Calyx Containers SCAR Management System

A Supplier Corrective Action Report (SCAR) management system built with Streamlit, designed following Calyx Containers brand guidelines.

## Brand Guidelines Applied

This application follows the Calyx Containers Visual Identity System:

### Colors
- **Primary Blue:** #0033A1 (Calyx Blue)
- **Flash Blue:** #004FFF (Accessible alternative)
- **Cloud Blue:** #D9F1FD (Accent)
- **Powder Blue:** #DBE6FF (Accent)
- **Ocean Blue:** #001F60 (Dark accent)
- **Mist Blue:** #202945 (Dark accent)

### Typography
- Uses DM Sans (similar geometric sans-serif to Kentos R1)
- Clean, minimal formatting
- Proper hierarchy with consistent weights

### Design Principles
- Clean, simple, and organized layouts
- Grid-based tables instead of bubbly cards
- Angular elements (no rounded corners on data grids)
- Professional color palette
- Consistent spacing and alignment

## Features

- **Role-based Access Control**
  - Admin: Full access to all SCARs, vendors, and users
  - Supplier: View and respond to assigned SCARs only

- **SCAR Management** with 7 sections:
  1. Details
  2. Non-Conformity Description
  3. Containment Actions
  4. Root Cause Analysis
  5. Corrective Action
  6. Preventive Action
  7. Verification

- **Vendor Management** (Admin only)
- **User Management** with approval workflow (Admin only)
- **Activity Logging** for audit trails

## Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Supplier | supplier | supplier123 |

## Deployment

### Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud
1. Push to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy from main branch

## File Structure
```
├── app.py              # Main application (single file)
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── scar_system.db     # SQLite database (auto-created)
```

## Database

The application uses SQLite for data persistence. The database file (`scar_system.db`) is automatically created on first run with demo data.

---

© Calyx Containers - SCAR Management System
