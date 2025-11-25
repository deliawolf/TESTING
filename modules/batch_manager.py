import concurrent.futures
import os
from datetime import datetime
from modules.ssh_manager import SSHTunnelManager
from modules.device_manager import DeviceConnection

import streamlit as st

class BatchProcessor:
    """
    Manages batch execution of commands on multiple devices using threading.
    """
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def process_single_device(self, device_name, device_config, command, gateway_session=None):
        """
        Connects to a single device, executes the command, and saves the output.
        Designed to be run in a separate thread.
        """
        ssh_manager = SSHTunnelManager()
        device_manager = DeviceConnection()
        result = {
            "device": device_name,
            "status": "pending",
            "output": "",
            "file": None,
            "error": None
        }

        try:
            # 1. Setup Tunnel (if needed)
            tunnel_port = None
            sock = None
            
            if gateway_session and gateway_session.is_active():
                # Use Shared Gateway Session
                try:
                    sock = gateway_session.open_channel(device_config['host'], device_config['port'])
                except Exception as e:
                    raise Exception(f"Failed to open channel via gateway: {e}")
            
            elif device_config.get('jumphost_profile'):
                # Legacy: Create new tunnel
                # Load Jump Host Config
                jumphost = self.data_manager.get_jumphost(device_config['jumphost_profile'])
                if not jumphost:
                    raise Exception(f"Jump host profile '{device_config['jumphost_profile']}' not found.")
                
                # Load Second Jump Host (if any)
                bastion2_conf = None
                if device_config.get('jumphost2_profile'):
                    bastion2_conf = self.data_manager.get_jumphost(device_config['jumphost2_profile'])

                tunnel_port = ssh_manager.start_tunnel(
                    jumphost['host'],
                    jumphost['port'],
                    jumphost['username'],
                    jumphost['password'],
                    device_config['host'],
                    device_config['port'],
                    bastion2_config=bastion2_conf
                )

            # 2. Connect to Device
            # Load Credentials
            creds = self.data_manager.get_credential(device_config['credential_name'])
            if not creds:
                raise Exception(f"Credential '{device_config['credential_name']}' not found.")

            success = device_manager.connect(
                device_config['device_type'],
                device_config['host'],
                creds['username'],
                creds['password'],
                port=device_config['port'],
                secret=creds.get('secret'),
                use_tunnel=bool(tunnel_port),
                tunnel_port=tunnel_port,
                sock=sock
            )

            if not success:
                raise Exception("Connection failed (unknown reason).")

            # 3. Execute Command
            output = device_manager.send_command(command)
            result['output'] = output
            result['status'] = "success"

            # 4. Save to File
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_command = "".join([c if c.isalnum() else "_" for c in command])
            filename = f"{device_name}_{safe_command}_{timestamp}.txt"
            filepath = os.path.join("downloads", filename)
            
            with open(filepath, "w") as f:
                f.write(output)
            result['file'] = filepath

        except Exception as e:
            result['status'] = "failed"
            result['error'] = str(e)
        
        finally:
            # 5. Cleanup
            try:
                device_manager.disconnect()
            except:
                pass
            try:
                ssh_manager.stop_tunnel()
            except:
                pass
            # Note: We do NOT close the gateway_session here as it is shared.
            # The channel (sock) is closed by Netmiko disconnect or GC.

        return result

    def execute_batch(self, device_names, command):
        """
        Executes the command on all specified devices in parallel.
        """
        results = []
        
        # Check for active gateway session in main thread
        gateway_session = None
        if 'gateway_session' in st.session_state and st.session_state['gateway_session']:
            gateway_session = st.session_state['gateway_session']

        # Increased max_workers back to 10 since we are multiplexing (if using gateway)
        # or if not using gateway, we rely on the user to be careful.
        # Actually, let's keep it at 5 to be safe even with multiplexing.
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_device = {}
            for name in device_names:
                device_config = self.data_manager.get_device(name)
                if device_config:
                    future = executor.submit(self.process_single_device, name, device_config, command, gateway_session)
                    future_to_device[future] = name
                else:
                    results.append({
                        "device": name,
                        "status": "failed",
                        "error": "Device config not found"
                    })

            for future in concurrent.futures.as_completed(future_to_device):
                results.append(future.result())
        
        return results
