import streamlit as st
import os
from datetime import datetime
from modules.styles import card_container, close_card

import streamlit_antd_components as sac

def render_home_page(data_manager):
    """Renders the Home page for connection and execution."""
    st.title("Dashboard")
    
    # Top Section: Quick Actions & Status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Devices", len(data_manager.inventory))
    with col2:
        st.metric("Credentials", len(data_manager.credentials))
    with col3:
        active_tunnels = 1 if st.session_state.get('ssh_manager') and st.session_state['ssh_manager'].is_active() else 0
        st.metric("Active Tunnels", active_tunnels)

    st.markdown("---")

    # Device Connection Section
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("🔌 Connect to Device")
        # Device Selection
        inventory_names = ["Select a device..."] + list(data_manager.inventory.keys())
        selected_device_name = st.selectbox("Target Device", inventory_names, index=0, label_visibility="collapsed")
        
        device_config = {}
        
        if selected_device_name != "Select a device...":
            device_data = data_manager.inventory[selected_device_name]
            
            # Resolve Credentials
            cred_name = device_data.get("credential_name")
            username = ""
            password = ""
            secret = ""
            if cred_name and cred_name in data_manager.credentials:
                cred = data_manager.credentials[cred_name]
                username = cred['username']
                password = cred['password']
                secret = cred.get('secret', '')
                
            # Resolve Jump Hosts
            jumphost_profile = device_data.get("jumphost_profile")
            jumphost_config = {}
            if jumphost_profile and jumphost_profile in data_manager.jumphosts:
                jumphost_config = data_manager.jumphosts[jumphost_profile]

            jumphost2_profile = device_data.get("jumphost2_profile")
            jumphost2_config = {}
            if jumphost2_profile and jumphost2_profile in data_manager.jumphosts:
                jumphost2_config = data_manager.jumphosts[jumphost2_profile]

            device_config = {
                "device_type": device_data['device_type'],
                "host": device_data['host'],
                "port": device_data['port'],
                "username": username,
                "password": password,
                "secret": secret,
                "use_bastion": bool(jumphost_config),
                "bastion_config": jumphost_config,
                "use_second_bastion": bool(jumphost2_config),
                "bastion2_config": jumphost2_config
            }

            # Device Info Card
            st.markdown(f"""
            <div class="stCard">
                <div class="device-card-header">📡 {selected_device_name}</div>
                <div class="device-card-detail">Host: {device_data['host']}</div>
                <div class="device-card-detail">Type: {device_data['device_type']}</div>
                <div class="device-card-detail">Via: {jumphost_profile if jumphost_profile else 'Direct'} {f'-> {jumphost2_profile}' if jumphost2_profile else ''}</div>
            </div>
            """, unsafe_allow_html=True)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                connect_btn = st.button("⚡ Connect Now", type="primary", use_container_width=True)
            with col_btn2:
                disconnect_btn = st.button("❌ Disconnect", use_container_width=True)
                
            return {
                "action": "connect" if connect_btn else "disconnect" if disconnect_btn else None,
                "config": device_config
            }
    
    with c2:
        sac.alert(
            label='Quick Tip', 
            description="Use the 'Batch Operations' tab to run commands on multiple devices simultaneously.", 
            size='sm', 
            radius='md', 
            icon=True, 
            closable=False, 
            color='info'
        )

    return {"action": None, "config": {}}

def render_jumphosts_page(data_manager):
    """Renders the Jump Hosts management page."""
    st.title("Jump Hosts")
    st.markdown("Manage your bastion host profiles here.")
    
    with st.expander("➕ Add New Jump Host Profile"):
        jh_name = st.text_input("Profile Name")
        col1, col2 = st.columns(2)
        with col1:
            jh_host = st.text_input("Host IP/Name", key="jh_host")
            jh_user = st.text_input("Username", key="jh_user")
        with col2:
            jh_pass = st.text_input("Password", type="password", key="jh_pass")
            jh_port = st.number_input("Port", value=22, key="jh_port", step=1, format="%d")
        
        if st.button("Save Profile"):
            if jh_name and jh_host and jh_user:
                data_manager.save_jumphost(jh_name, jh_host, jh_user, jh_pass, jh_port)
                sac.alert(label='Success', description=f"Saved profile: {jh_name}", color='success', icon=True)
                st.rerun()
            else:
                sac.alert(label='Error', description="Name, Host, and Username are required.", color='error', icon=True)

    st.markdown("### Saved Profiles")
    if not data_manager.jumphosts:
        st.info("No jump host profiles found.")
    
    for name, data in data_manager.jumphosts.items():
        st.markdown(f"""
        <div class="stCard">
            <div class="device-card-header">🛡️ {name}</div>
            <div class="device-card-detail">Host: {data['host']}</div>
            <div class="device-card-detail">User: {data['username']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Delete", key=f"del_jh_{name}"):
            data_manager.delete_jumphost(name)
            st.rerun()

def render_inventory_page(data_manager):
    """Renders the Inventory management page (Devices + Credentials)."""
    st.title("Inventory Management")
    
    # Modern Tabs using SAC
    tab_selection = sac.tabs([
        sac.TabsItem('Devices', icon='pc-display'),
        sac.TabsItem('Credentials', icon='key-fill'),
    ], align='start', variant='outline', color='blue')
    
    if tab_selection == 'Devices':
        st.subheader("Device Inventory")
        
        # Prepare Data for Editor
        devices_list = data_manager.get_all_devices_list()
        
        # Dropdown Options
        device_types = ["cisco_ios", "cisco_nxos", "cisco_xr", "arista_eos", "juniper_junos", "linux"]
        cred_options = ["None"] + list(data_manager.credentials.keys())
        jh_options = ["None"] + list(data_manager.jumphosts.keys())

        # Configure Column Config
        column_config = {
            "name": st.column_config.TextColumn("Device Name", width="medium", required=True),
            "host": st.column_config.TextColumn("Host IP/Name", width="medium", required=True),
            "device_type": st.column_config.SelectboxColumn("Type", width="small", options=device_types, required=True),
            "port": st.column_config.NumberColumn("Port", format="%d", width="small", default=22),
            "credential_name": st.column_config.SelectboxColumn("Credential", width="small", options=cred_options),
            "jumphost_profile": st.column_config.SelectboxColumn("Jump Host 1", width="small", options=jh_options),
            "jumphost2_profile": st.column_config.SelectboxColumn("Jump Host 2", width="small", options=jh_options),
            "tags_display": st.column_config.TextColumn("Tags (comma-separated)", width="medium"),
        }
        
        st.info("💡 **Tip:** Double-click cells to edit. Add new rows at the bottom. Select rows and press delete to remove.")
        
        # Display Data Editor in a styled container
        with st.container():
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            edited_data = st.data_editor(
                devices_list,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key="inventory_editor"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Save Button
        col_save, col_spacer = st.columns([1, 4])
        with col_save:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                try:
                    data_manager.bulk_update_devices(edited_data)
                    st.toast("Inventory updated successfully!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving inventory: {e}")

    elif tab_selection == 'Credentials':
        st.subheader("Device Credentials")
        with st.expander("➕ Add New Credential"):
            new_cred_name = st.text_input("Credential Name")
            col1, col2 = st.columns(2)
            with col1:
                new_cred_user = st.text_input("Username", key="new_cred_user")
            with col2:
                new_cred_pass = st.text_input("Password", type="password", key="new_cred_pass")
            new_cred_secret = st.text_input("Secret (Optional)", type="password", key="new_cred_secret")
            
            if st.button("Save Credential"):
                if new_cred_name and new_cred_user:
                    data_manager.save_credential(new_cred_name, new_cred_user, new_cred_pass, new_cred_secret)
                    sac.alert(label='Success', description=f"Saved credential: {new_cred_name}", color='success', icon=True)
                    st.rerun()
                else:
                    sac.alert(label='Error', description="Name and Username are required.", color='error', icon=True)
        
        st.markdown("### Saved Credentials")
        if not data_manager.credentials:
            st.info("No credentials found.")

        for name, data in data_manager.credentials.items():
            st.markdown(f"""
            <div class="stCard">
                <div class="device-card-header">🔑 {name}</div>
                <div class="device-card-detail">Username: {data['username']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Delete", key=f"del_cred_{name}"):
                data_manager.delete_credential(name)
                st.rerun()

def render_dashboard_content(logs):
    """Renders the execution logs and command input (part of Home)."""
    st.markdown("### 📟 Terminal")
    
    # Logs Container with new Terminal Styling
    log_html = '<div class="terminal-window">'
    for log in logs:
        # Colorize logs based on content
        color = "#00ff00" # Default Green
        if "Error" in log or "failed" in log:
            color = "#ff4444" # Red
        elif "Initiating" in log or "Connecting" in log:
            color = "#ffff00" # Yellow
        elif "DEBUG" in log:
            color = "#888888" # Grey
            
        log_html += f'<div style="color: {color}; font-family: monospace; margin-bottom: 2px;">{log}</div>'
    log_html += '</div>'
    
    st.markdown(log_html, unsafe_allow_html=True)

    st.markdown("### Execute Command")
    with st.form(key='command_form', clear_on_submit=False):
        col1, col2 = st.columns([4, 1])
        with col1:
            command = st.text_input("Enter command", placeholder="e.g., show ip int brief", label_visibility="collapsed")
        with col2:
            submitted = st.form_submit_button("Run", type="primary", use_container_width=True)
            
        if submitted and command:
            return command

    # Download Section
    if 'last_generated_file' in st.session_state and st.session_state['last_generated_file']:
        filepath = st.session_state['last_generated_file']
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                st.download_button(
                    label="Download Output 📥",
                    data=f,
                    file_name=os.path.basename(filepath),
                    mime="text/plain",
                    use_container_width=True
                )
    return None

def render_batch_page(data_manager):
    """Renders the Batch Operations page."""
    st.header("⚡ Batch Operations")
    st.markdown("### 🚀 Batch Operations Wizard")
    
    # Step 1: Select Devices
    with st.expander("1️⃣ Select Target Devices", expanded=True):
        devices_list = data_manager.get_all_devices_list()
        
        if not devices_list:
            st.info("No devices found in inventory.")
            # Do not return here, allow the rest of the page to render with an empty selection
            selected_devices = []
        else:
            # Tag Filter
            all_tags = set()
            for d in devices_list:
                if 'tags' in d:
                    all_tags.update(d['tags'])
            
            col_filter, col_info = st.columns([3, 1])
            with col_filter:
                selected_tags = st.multiselect("Filter by Tag", list(all_tags))
            
            # Filter devices based on tags
            if selected_tags:
                filtered_devices = []
                for d in devices_list:
                    device_tags = set(d.get('tags', []))
                    if not device_tags.isdisjoint(selected_tags):
                        filtered_devices.append(d)
                devices_list = filtered_devices
                with col_info:
                    st.caption(f"Matches: {len(devices_list)}")

            # Configure Column Config for Batch Selection
            column_config = {
                "name": st.column_config.TextColumn("Device Name", width="medium"),
                "host": st.column_config.TextColumn("Host IP/Name", width="medium"),
                "device_type": st.column_config.TextColumn("Type", width="small"),
                "jumphost_profile": st.column_config.TextColumn("Jump Host 1", width="small"),
                "tags_display": st.column_config.TextColumn("Tags", width="medium"),
            }
            
            # Display Dataframe with Selection
            selection = st.dataframe(
                devices_list,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row",
                key="batch_selection"
            )
            
            selected_devices = []
            if selection and len(selection.selection.rows) > 0:
                rows = selection.selection.rows
                selected_devices = [devices_list[i]['name'] for i in rows]
                st.success(f"✅ Selected {len(selected_devices)} devices.")
            else:
                st.info("Please select devices from the table to proceed.")

    # Step 2: Enter Command
    if selected_devices:
        with st.expander("2️⃣ Enter Command", expanded=True):
            command = st.text_input("Command to Execute", placeholder="e.g., show version")
            
            if command:
                if st.button("🚀 Run Batch Command", type="primary"):
                    from modules.batch_manager import BatchProcessor
                    batch_manager = BatchProcessor(data_manager) # Instantiate here
                    
                    with st.status("Executing Batch...", expanded=True) as status:
                        gateway_session = st.session_state.get('gateway_session')
                        results = batch_manager.execute_batch(selected_devices, command, gateway_session)
                        status.update(label="Batch execution complete!", state="complete", expanded=False)
                    
                    # Store results in session state to persist
                    st.session_state['batch_results'] = results
                    st.session_state['last_batch_command'] = command
    
    # Step 3: View Results
    if 'batch_results' in st.session_state:
        st.markdown("---")
        st.subheader("3️⃣ Execution Results")
        
        results = st.session_state['batch_results']
        
        # Summary Metrics
        total = len(results)
        success = sum(1 for r in results.values() if r['status'] == 'success')
        failed = total - success
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Devices", total)
        m2.metric("Success", success)
        m3.metric("Failed", failed)
        
        # Results Table
        res_data = []
        files_to_zip = [] # Initialize files_to_zip for the download section
        
        for dev_name, res in results.items(): # Iterate over items for device name and result dict
            status_icon = "✅" if res['status'] == 'success' else "❌"
            output_preview = res['output'].splitlines()[0] if res['status'] == 'success' and res['output'] else res.get('error', 'No output/error')
            
            res_data.append({
                "Device": dev_name,
                "Status": f"{status_icon} {res['status'].upper()}",
                "Output": output_preview
            })
            if res.get('file'):
                files_to_zip.append(res['file'])

        st.dataframe(res_data, use_container_width=True)
        
        # 5. Bulk Download
        if files_to_zip:
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for file_path in files_to_zip:
                    zf.write(file_path, os.path.basename(file_path))
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"batch_output_{timestamp}.zip"
            
            st.download_button(
                label=f"Download All ({len(files_to_zip)} files) 📦",
                data=zip_buffer.getvalue(),
                file_name=zip_filename,
                mime="application/zip",
                type="primary"
            )


def render_gateway_sidebar(data_manager):
    """Renders the Gateway Login status in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 Gateway Status")
    
    if 'gateway_session' in st.session_state and st.session_state['gateway_session'] and st.session_state['gateway_session'].is_active():
        st.sidebar.success(f"Connected: {st.session_state['gateway_session'].gateway_host}")
        if st.sidebar.button("Disconnect Gateway"):
            st.session_state['gateway_session'].close()
            st.session_state['gateway_session'] = None
            st.rerun()
        return None
    else:
        st.sidebar.error("Disconnected")
        with st.sidebar.expander("🔐 Login to Gateway", expanded=True):
            # Dropdown to select existing Jump Host profile
            jh_names = ["Select Profile..."] + list(data_manager.jumphosts.keys())
            
            # Initialize session state for gateway fields if not present
            if 'gw_host' not in st.session_state: st.session_state['gw_host'] = ""
            if 'gw_user' not in st.session_state: st.session_state['gw_user'] = ""
            if 'gw_pass' not in st.session_state: st.session_state['gw_pass'] = ""
            if 'gw_port' not in st.session_state: st.session_state['gw_port'] = 22

            def update_gw_fields():
                selected = st.session_state.get('gw_profile_select')
                if selected and selected != "Select Profile...":
                    data = data_manager.jumphosts[selected]
                    st.session_state['gw_host'] = data['host']
                    st.session_state['gw_user'] = data['username']
                    st.session_state['gw_pass'] = data['password']
                    st.session_state['gw_port'] = data['port']

            st.markdown("**Jump Host 1**")
            selected_jh = st.selectbox(
                "Profile", 
                jh_names, 
                key='gw_profile_select', 
                on_change=update_gw_fields,
                label_visibility="collapsed"
            )
            
            # Allow manual override (values bound to session state)
            host = st.text_input("Host", key="gw_host")
            user = st.text_input("Username", key="gw_user")
            password = st.text_input("Password", type="password", key="gw_pass")
            port = st.number_input("Port", key="gw_port", step=1, format="%d")
            
            st.markdown("---")
            st.markdown("**Jump Host 2 (Optional)**")
            selected_jh2 = st.selectbox("Profile", ["None"] + list(data_manager.jumphosts.keys()), key='gw_jh2_select')
            
            if st.button("Connect Gateway"):
                gw_config = {
                    "host": host,
                    "username": user,
                    "password": password,
                    "port": port
                }
                
                jh2_config = None
                if selected_jh2 and selected_jh2 != "None":
                    jh2_data = data_manager.jumphosts[selected_jh2]
                    jh2_config = {
                        "host": jh2_data['host'],
                        "username": jh2_data['username'],
                        "password": jh2_data['password'],
                        "port": jh2_data['port']
                    }
                
                return {
                    "gw_config": gw_config,
                    "jh2_config": jh2_config
                }
    return None
    return None

