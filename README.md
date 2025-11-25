# Network Automation Tool

A modern, full-stack network automation tool built with Next.js (frontend) and FastAPI (backend). Manage network devices, execute batch commands, and automate network operations through an intuitive web interface.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🔐 **Gateway Session Management** - Persistent SSH connections through jump hosts (single or double-hop)
- 📊 **Device Inventory** - Full CRUD operations with CSV import/export
- 🏷️ **Tag-Based Filtering** - Organize and batch-select devices using tags
- ⚡ **Batch Operations** - Execute commands on multiple devices simultaneously
- 📥 **Downloadable Results** - Export command outputs as ZIP files with individual device logs
- 🎯 **Real-Time Progress Tracking** - Monitor execution status for each device
- 🔑 **Credential Management** - Securely store and manage device credentials
- 🌉 **Jump Host Profiles** - Configure bastion/jump host chains

## Architecture

- **Frontend**: Next.js 14 + TailwindCSS + Shadcn/UI
- **Backend**: FastAPI + Python 3.13
- **SSH**: Netmiko + Paramiko
- **Data Storage**: JSON files (local filesystem)

## Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher

## Installation & Deployment

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd Tollkit-Dev-temp
```

### 2️⃣ Backend Setup

```bash
# Create Python virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python --version  # Should be 3.10+
```

### 3️⃣ Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Verify installation
node --version  # Should be 18+
npm --version   # Should be 9+
```

### 4️⃣ Start the Application

**Terminal 1 - Backend (FastAPI):**

```bash
# From project root
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend (Next.js):**

```bash
cd frontend
npm run dev
```

**Access the Application:**

- 🌐 **Frontend**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs

## First-Time Setup

### 1. Configure Jump Hosts

1. Navigate to **Jump Hosts** page
2. Click "Add Jump Host"
3. Enter SSH connection details for your bastion hosts

### 2. Add Credentials

1. Navigate to **Settings** page
2. Click "Add Credential"
3. Store device authentication credentials

### 3. Add Devices

1. Navigate to **Inventory** page
2. Click "Add Device" or "Import CSV"
3. Configure devices with their credentials and jump host profiles
4. Assign tags for easy batch selection (e.g., "production", "core", "access")

### 4. Connect Gateway

1. Click "Connect Gateway" in the top-right header
2. Select your jump host chain (JH1 → JH2)
3. Wait for "Gateway: Connected" status

### 5. Run Batch Commands

1. Navigate to **Batch Operations**
2. Select devices (individually or by tag)
3. Enter command (e.g., `show version`)
4. Click "Execute Command"
5. Download results as ZIP file

## Project Structure

```
.
├── backend/                 # FastAPI Backend
│   ├── main.py             # API entry point
│   ├── routers/            # API endpoints
│   │   ├── inventory.py    # Device CRUD + CSV import/export
│   │   ├── jumphosts.py    # Jump host management
│   │   ├── credentials.py  # Credential management
│   │   ├── gateway.py      # Gateway session management
│   │   └── batch.py        # Batch command execution
│   └── modules/            # Core logic
│       ├── data_manager.py # Data persistence
│       ├── device_manager.py # Device connections
│       └── ssh_manager.py  # SSH tunneling & gateway
│
├── frontend/               # Next.js Frontend
│   ├── app/               # Pages & layouts
│   │   ├── layout.tsx     # Root layout with sidebar
│   │   ├── page.tsx       # Dashboard
│   │   ├── inventory/     # Device management
│   │   ├── jumphosts/     # Jump host profiles
│   │   ├── batch/         # Batch operations
│   │   └── settings/      # Credentials & config
│   └── components/        # Reusable UI components
│
├── data/                  # JSON data storage
│   ├── inventory.json     # Device configurations
│   ├── credentials.json   # SSH credentials (gitignored)
│   └── jumphosts.json     # Jump host profiles
│
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration Files

### Backend Dependencies (`requirements.txt`)

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `netmiko` - Network device SSH
- `paramiko` - SSH protocol
- `sshtunnel` - SSH tunneling
- `python-multipart` - File upload support

### Frontend Dependencies

- `next` - React framework
- `react` - UI library
- `tailwindcss` - Styling
- `shadcn/ui` - UI components
- `lucide-react` - Icons

## Data Files

All configuration is stored in `data/` directory:

- **inventory.json**: Device configurations
- **credentials.json**: SSH credentials (⚠️ **Add to .gitignore!**)
- **jumphosts.json**: Jump host profiles

### Security Note

**Never commit `credentials.json` to Git**. Consider using environment variables or a secrets manager for production deployments.

## Production Deployment

### Backend

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000
```

### Frontend

```bash
cd frontend

# Build for production
npm run build

# Start production server
npm run start
```

### Environment Variables

Create `.env` files for configuration:

**Backend (.env):**

```env
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
```

**Frontend (.env.local):**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Backend won't start

- Verify Python version: `python --version` (3.10+)
- Check virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend won't start

- Verify Node version: `node --version` (18+)
- Clear cache: `rm -rf frontend/.next`
- Reinstall: `rm -rf frontend/node_modules && npm install`

### Gateway connection fails

- Verify jump host SSH credentials
- Check firewall rules
- Ensure jump hosts are reachable from your machine

### Batch operations show "not found in inventory"

- Backend auto-reloads inventory on each request
- If issue persists, restart backend server

## CSV Import Format

```csv
name,host,device_type,port,credential_name,jumphost_profile,jumphost2_profile,tags
DEVICE1,10.1.1.1,cisco_nxos,22,admin_creds,jh1,jh2,"production,core"
DEVICE2,10.1.1.2,cisco_ios,22,admin_creds,jh1,,"production,access"
```

## Supported Device Types

- `cisco_nxos` - Cisco Nexus
- `cisco_ios` - Cisco IOS
- `cisco_xe` - Cisco IOS-XE
- `cisco_xr` - Cisco IOS-XR
- `arista_eos` - Arista EOS
- `juniper_junos` - Juniper Junos

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ using Next.js and FastAPI**
