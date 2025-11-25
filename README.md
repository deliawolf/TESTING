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

## Quick Start (5 Minutes)

Follow these steps exactly to deploy the application:

### Step 1: Clone the Repository

```bash
git clone https://github.com/deliawolf/TESTING.git
cd TESTING
```

### Step 2: Backend Setup (Python)

```bash
# Create and activate virtual environment
python3 -m venv .venv

# Activate it:
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install all Python dependencies
pip install -r requirements.txt
```

**✅ Verify backend installation:**

```bash
python --version  # Should show Python 3.10+
pip list | grep fastapi  # Should show fastapi installed
```

### Step 3: Create Data Files

```bash
# Navigate to data directory
cd data

# Create your configuration files from examples
cp credentials.json.example credentials.json
cp jumphosts.json.example jumphosts.json
cp inventory.json.example inventory.json

# Return to project root
cd ..
```

**📝 Edit these files with your actual:**

- Device credentials (`data/credentials.json`)
- Jump host configurations (`data/jumphosts.json`)
- Network device inventory (`data/inventory.json`)

### Step 4: Frontend Setup (Node.js)

```bash
# Navigate to frontend directory
cd frontend

# Install all Node dependencies
npm install

# Create environment file
cp .env.example .env.local

# Return to project root
cd ..
```

**✅ Verify frontend installation:**

```bash
node --version  # Should show v18+
npm --version   # Should show v9+
cd frontend && npm list next  # Should show next installed
cd ..
```

### Step 5: Start the Application

Open **TWO separate terminal windows/tabs**:

**Terminal 1 - Backend:**

```bash
cd TESTING
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Terminal 2 - Frontend:**

```bash
cd TESTING/frontend
npm run dev
```

**Expected output:**

```
▲ Next.js 14
- Local:        http://localhost:3000
```

### Step 6: Access the Application

Open your browser and navigate to:

- 🌐 **Application**: http://localhost:3000
- 🔌 **API Docs**: http://localhost:8000/docs

## First-Time Configuration

### 1. Add Jump Hosts

1. Go to **Jump Hosts** page
2. Click **"Add Jump Host"**
3. Enter:
   - Name: `jumphost1`
   - Host: Your jump host IP
   - Port: `22`
   - Username & Password

### 2. Add Credentials

1. Go to **Settings** page
2. Click **"Add Credential"**
3. Enter your device SSH credentials

### 3. Add Devices

1. Go to **Inventory** page
2. Click **"Add Device"** OR **"Import CSV"**
3. Configure:
   - Device details (name, IP, type)
   - Select credential profile
   - Select jump host chain
   - Add tags (e.g., "production", "core")

### 4. Connect Gateway

1. Click **"Connect Gateway"** (top-right)
2. Select jump host chain
3. Wait for green **"Gateway: Connected"** badge

### 5. Run Commands

1. Go to **Batch Operations**
2. Select devices (by clicking or by tag)
3. Enter command (e.g., `show version`)
4. Click **"Execute Command"**
5. Download results as ZIP

## Troubleshooting

### ❌ "Address already in use" (Port 8000)

**Problem:** Another service is using port 8000

**Solution 1 - Kill the process:**

```bash
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Solution 2 - Use different port:**

```bash
# Start backend on different port
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# Update frontend/.env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > frontend/.env.local

# Restart frontend
cd frontend && npm run dev
```

### ❌ "Backend Connection Lost"

**Problem:** Frontend can't connect to backend

**Checklist:**

1. ✅ Is backend running? Check Terminal 1
2. ✅ Is it on port 8000? Check the logs
3. ✅ Does `http://localhost:8000/health` return OK?
4. ✅ Check `frontend/.env.local` has correct API URL

**Fix:**

```bash
# Verify backend is running
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# If using different port, update frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > frontend/.env.local
cd frontend && npm run dev
```

### ❌ "Module not found" or Import Errors

**Problem:** Missing dependencies

**Solution:**

```bash
# Backend dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Frontend dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### ❌ "python-multipart" error

**Problem:** File upload dependency missing

**Solution:**

```bash
source .venv/bin/activate
pip install python-multipart
# Restart backend
```

### ❌ Frontend shows blank page

**Problem:** Build or node_modules issue

**Solution:**

```bash
cd frontend
rm -rf .next
npm run dev
```

### ❌ Gateway connection fails

**Problem:** Can't establish SSH connection

**Checklist:**

1. ✅ Jump host credentials correct?
2. ✅ Jump host reachable? (`ping <jumphost-ip>`)
3. ✅ SSH port open? (`telnet <jumphost-ip> 22`)
4. ✅ Firewall blocking connection?

## Installation & Deployment

### Prerequisites Verification

Before starting, verify you have the required versions:

```bash
# Python (3.10 or higher)
python3 --version

# Node.js (18.x or higher)
node --version

# npm (9.x or higher)
npm --version
```

If any are missing or wrong version, install them first:

- **Python**: https://www.python.org/downloads/
- **Node.js**: https://nodejs.org/ (includes npm)

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
