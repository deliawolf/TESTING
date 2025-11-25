import streamlit as st
import os
from datetime import datetime
from modules.ssh_manager import SSHTunnelManager, GatewaySession
from modules.device_manager import DeviceConnection
from modules.data_manager import DataManager
from modules.ui_components import render_home_page, render_inventory_page, render_jumphosts_page, render_dashboard_content, render_gateway_sidebar
from modules.styles import load_css

# Initialize Session State
if 'ssh_manager' not in st.session_state:
    st.session_state['ssh_manager'] = SSHTunnelManager()
if 'gateway_session' not in st.session_state:
    st.session_state['gateway_session'] = None
if 'device_manager' not in st.session_state:
    st.session_state['device_manager'] = DeviceConnection()
if 'data_manager' not in st.session_state:
    st.session_state['data_manager'] = DataManager()
if 'logs' not in st.session_state:
    st.session_state['logs'] = []
if 'connected_device' not in st.session_state:
    st.session_state['connected_device'] = None

def log(message):
    st.session_state['logs'].append(message)

def main():
    st.set_page_config(page_title="Network Automation Tool", layout="wide", page_icon="🚀")
    load_css()
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("## 🚀 Network Tool")
        st.caption("v1.2.0 • Premium Edition")
        
        import streamlit_antd_components as sac
        
        # Custom Menu using SAC
        page = sac.menu([
            sac.MenuItem('Home', icon='house-fill'),
            sac.MenuItem('Inventory', icon='box-seam-fill'),
            sac.MenuItem('Jump Hosts', icon='shield-lock-fill'),
            sac.MenuItem('Batch Operations', icon='lightning-charge-fill'),
        ], size='middle', open_all=True)
        
        st.markdown("---")
        
        # Gateway Login Sidebar
        gw_data = render_gateway_sidebar(st.session_state['data_manager'])
        if gw_data:
            try:
                gw_config = gw_data['gw_config']
                jh2_config = gw_data['jh2_config']
                
                session = GatewaySession()
                session.connect(
                    gw_config['host'],
                    gw_config['port'],
                    gw_config['username'],
                    gw_config['password'],
                    jumphost2_config=jh2_config
                )
                st.session_state['gateway_session'] = session
                st.rerun()
            except Exception as e:
                st.error(f"Gateway Login Failed: {e}")

        # Connection Status Footer
        if st.session_state['device_manager'].is_connected():
            st.success(f"Connected: {st.session_state['connected_device']}")
        else:
            st.caption("No active device connection")

    if page == "Inventory":
        render_inventory_page(st.session_state['data_manager'])
    
    elif page == "Jump Hosts":
        render_jumphosts_page(st.session_state['data_manager'])

    elif page == "Batch Operations":
        from modules.ui_components import render_batch_page
        render_batch_page(st.session_state['data_manager'])
        
    elif page == "Home":
        # Render Home Page and get actions
        home_state = render_home_page(st.session_state['data_manager'])
        
        # Handle Connect Action
        if home_state['action'] == 'connect':
            config = home_state['config']
            
            with st.status("Connecting...", expanded=True) as status:
                try:
                    log(f"Initiating connection to {config['host']}...")
                    status.write("Initializing connection parameters...")
                    
                    # Handle Bastion Host / Gateway
                    tunnel_port = None
                    sock = None
                    
                    # Check if we have an active Gateway Session
                    if st.session_state['gateway_session'] and st.session_state['gateway_session'].is_active():
                        log("Using active Gateway Session...")
                        status.write("Using active Gateway Session...")
                        sock = st.session_state['gateway_session'].open_channel(config['host'], config['port'])
                    
                    # Fallback to legacy tunnel if configured and no gateway session
                    elif config['use_bastion']:
                        bastion_conf = config['bastion_config']
                        log(f"Starting SSH tunnel to {bastion_conf['host']}...")
                        status.write(f"Starting SSH tunnel to {bastion_conf['host']}...")
                        
                        bastion2_conf = config.get('bastion2_config') if config.get('use_second_bastion') else None
                        if bastion2_conf:
                             log(f"  -> Chaining via second bastion: {bastion2_conf['host']}...")
                             status.write(f"Chaining via second bastion: {bastion2_conf['host']}...")

                        tunnel_port = st.session_state['ssh_manager'].start_tunnel(
                            bastion_conf['host'],
                            bastion_conf['port'],
                            bastion_conf['username'],
                            bastion_conf['password'],
                            config['host'],
                            config['port'],
                            bastion2_config=bastion2_conf
                        )
                        log(f"SSH Tunnel established. Local bind port: {tunnel_port}")
                        status.write("SSH Tunnel established.")

                    # Connect to Device
                    log(f"Connecting to device {config['host']}...")
                    status.write(f"Connecting to device {config['host']}...")
                    success = st.session_state['device_manager'].connect(
                        config['device_type'],
                        config['host'],
                        config['username'],
                        config['password'],
                        port=config['port'],
                        secret=config['secret'],
                        use_tunnel=config['use_bastion'],
                        tunnel_port=tunnel_port,
                        sock=sock
                    )
                    
                    if success:
                        st.session_state['connected_device'] = config['host']
                        log(f"Successfully connected to {config['host']}")
                        status.update(label="Connected!", state="complete", expanded=False)
                        st.success("Connected!")
                
                except Exception as e:
                    log(f"Error: {str(e)}")
                    status.update(label="Connection Failed", state="error", expanded=True)
                    st.error(f"Connection failed: {e}")
                    # Cleanup tunnel if connection failed
                    st.session_state['ssh_manager'].stop_tunnel()

        # Handle Disconnect Action
        if home_state['action'] == 'disconnect':
            if st.session_state['device_manager'].is_connected():
                st.session_state['device_manager'].disconnect()
                log("Disconnected from device.")
            
            if st.session_state['ssh_manager'].is_active():
                st.session_state['ssh_manager'].stop_tunnel()
                log("SSH Tunnel stopped.")
                
            st.session_state['connected_device'] = None
            st.info("Disconnected.")

        # Render Dashboard Content (Logs & Command Input)
        command_to_execute = render_dashboard_content(st.session_state['logs'])
        
        # Handle Command Execution
        # Handle Command Execution
        if command_to_execute:
            if st.session_state['device_manager'].is_connected():
                try:
                    # Execute Command
                    log(f"Executing command: {command_to_execute}...")
                    status_placeholder = st.empty()
                    status_placeholder.info(f"Executing: {command_to_execute}...")
                    
                    output = st.session_state['device_manager'].send_command(command_to_execute)
                    
                    # Generate Filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_command = "".join([c if c.isalnum() else "_" for c in command_to_execute])
                    device_name = st.session_state.get('connected_device', 'unknown_device')
                    filename = f"{device_name}_{safe_command}_{timestamp}.txt"
                    filepath = os.path.join("downloads", filename)
                    
                    # Save to file
                    with open(filepath, "w") as f:
                        f.write(output)
                    
                    st.session_state['last_generated_file'] = filepath
                    log(f"Command executed. Output saved to {filename}")
                    status_placeholder.success("Command executed. Output saved.")
                    
                    # Force Rerun to update UI immediately
                    st.rerun()
                    
                except Exception as e:
                    log(f"Command execution failed: {e}")
                    st.error(f"Error: {e}")
            else:
                st.warning("Please connect to a device first.")

if __name__ == "__main__":
    main()
