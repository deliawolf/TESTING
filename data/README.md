# Data Directory

This directory contains JSON files for storing application data.

## ⚠️ IMPORTANT - Before First Use

The actual data files (`credentials.json`, `jumphosts.json`, `inventory.json`) are gitignored for security.

**You must create them from the examples:**

```bash
# In the data/ directory
cp credentials.json.example credentials.json
cp jumphosts.json.example jumphosts.json
cp inventory.json.example inventory.json
```

Then edit these files with your actual:

- Device credentials
- Jump host configurations
- Network device inventory

## File Descriptions

### credentials.json

Stores SSH credentials for network devices.

```json
{
  "credential_name": {
    "username": "admin",
    "password": "your_password",
    "secret": "enable_secret"
  }
}
```

### jumphosts.json

Stores jump host/bastion configurations.

```json
{
  "jumphost_name": {
    "host": "10.0.0.1",
    "port": 22,
    "username": "user",
    "password": "password"
  }
}
```

### inventory.json

Stores network device inventory.

```json
{
  "DEVICE_NAME": {
    "device_type": "cisco_nxos",
    "host": "192.168.1.1",
    "port": 22,
    "credential_name": "admin_creds",
    "jumphost_profile": "jh1",
    "jumphost2_profile": null,
    "tags": ["production", "core"]
  }
}
```

## Security Notes

- **NEVER commit the actual `.json` files to Git**
- Only `.json.example` files are tracked
- Real data files are in `.gitignore`
- Store sensitive data securely (consider using environment variables or secrets manager for production)
