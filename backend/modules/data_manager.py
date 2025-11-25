import json
import os

DATA_DIR = "data"
CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")

class DataManager:
    """
    Manages persistence of credentials and device inventory using JSON files.
    """
    def _ensure_data_dir(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        if not os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump({}, f)
        if not os.path.exists(INVENTORY_FILE):
            with open(INVENTORY_FILE, 'w') as f:
                json.dump({}, f)
        
        # Jump Host Profiles
        self.jumphosts_file = os.path.join(DATA_DIR, "jumphosts.json")
        if not os.path.exists(self.jumphosts_file):
            with open(self.jumphosts_file, 'w') as f:
                json.dump({}, f)

    def __init__(self):
        self._ensure_data_dir()
        self.credentials = self.load_credentials()
        self.inventory = self.load_inventory()
        self.jumphosts = self.load_jumphosts()

    def load_jumphosts(self):
        try:
            with open(self.jumphosts_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_jumphost(self, name, host, username, password, port=22):
        self.jumphosts[name] = {
            "host": host,
            "username": username,
            "password": password,
            "port": port
        }
        self._save_file(self.jumphosts_file, self.jumphosts)

    def delete_jumphost(self, name):
        if name in self.jumphosts:
            del self.jumphosts[name]
            self._save_file(self.jumphosts_file, self.jumphosts)

    def load_credentials(self):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_credential(self, name, username, password, secret=""):
        self.credentials[name] = {
            "username": username,
            "password": password,
            "secret": secret
        }
        self._save_file(CREDENTIALS_FILE, self.credentials)

    def delete_credential(self, name):
        if name in self.credentials:
            del self.credentials[name]
            self._save_file(CREDENTIALS_FILE, self.credentials)

    def load_inventory(self):
        try:
            with open(INVENTORY_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_device(self, name, device_type, host, port, credential_name, jumphost_profile=None, jumphost2_profile=None, tags=None):
        self.inventory[name] = {
            "device_type": device_type,
            "host": host,
            "port": port,
            "credential_name": credential_name,
            "jumphost_profile": jumphost_profile,
            "jumphost2_profile": jumphost2_profile,
            "tags": tags if tags else []
        }
        self._save_file(INVENTORY_FILE, self.inventory)

    def delete_device(self, name):
        if name in self.inventory:
            del self.inventory[name]
            self._save_file(INVENTORY_FILE, self.inventory)

    def _save_file(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def get_all_devices(self):
        """Returns the full inventory dictionary."""
        return self.inventory

    def get_all_devices_list(self):
        """Returns inventory as a list of dicts for DataFrames."""
        device_list = []
        for name, data in self.inventory.items():
            item = data.copy()
            item['name'] = name
            # Format tags as string for display
            tags = item.get('tags', [])
            item['tags_display'] = ", ".join(tags) if tags else ""
            device_list.append(item)
        return device_list

    def get_device(self, name):
        """Returns configuration for a specific device."""
        return self.inventory.get(name)

    def get_jumphost(self, name):
        """Returns configuration for a specific jump host."""
        return self.jumphosts.get(name)

    def get_credential(self, name):
        """Returns credentials for a specific profile."""
        return self.credentials.get(name)

    def bulk_update_devices(self, device_list):
        """
        Replaces the entire inventory with the provided list of dictionaries.
        Used for syncing changes from the UI editor.
        """
        new_inventory = {}
        for item in device_list:
            name = item.get('name')
            if not name:
                continue # Skip items without a name
            
            # Reconstruct the device dict
            # Handle tags: if it's a string (from editor), split it. If list, keep it.
            tags = item.get('tags_display', "")
            if isinstance(tags, str):
                tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            else:
                tag_list = item.get('tags', [])

            new_inventory[name] = {
                "device_type": item.get('device_type', 'cisco_ios'),
                "host": item.get('host', ''),
                "port": int(item.get('port', 22)),
                "credential_name": item.get('credential_name'),
                "jumphost_profile": item.get('jumphost_profile'),
                "jumphost2_profile": item.get('jumphost2_profile'),
                "tags": tag_list
            }
        
        self.inventory = new_inventory
        self._save_file(INVENTORY_FILE, self.inventory)
