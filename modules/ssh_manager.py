import time
from sshtunnel import SSHTunnelForwarder

class SSHTunnelManager:
    """
    Manages SSH tunnels for bastion host connections, including double jump support.
    """
    def __init__(self):
        self.tunnel1 = None
        self.tunnel2 = None
        self.local_bind_port = None

    def start_tunnel(self, bastion_host, bastion_port, bastion_user, bastion_password, remote_host, remote_port=22, bastion2_config=None):
        """
        Starts an SSH tunnel through a bastion host, optionally chaining a second bastion.
        
        Args:
            bastion_host (str): IP or hostname of the first bastion.
            bastion_port (int): SSH port of the first bastion.
            bastion_user (str): Username for the first bastion.
            bastion_password (str): Password for the first bastion.
            remote_host (str): IP or hostname of the target device.
            remote_port (int): SSH port of the target device (default 22).
            bastion2_config (dict, optional): Config for the second bastion (host, port, username, password).
            
        Returns:
            int: The local bind port if successful.
        """
        try:
            # First Jump: Local -> Bastion 1
            # If double jump, target is Bastion 2. If single jump, target is Device.
            
            target_host = remote_host
            target_port = int(remote_port)
            
            if bastion2_config:
                target_host = bastion2_config['host']
                target_port = int(bastion2_config['port'])

            print(f"Starting Tunnel 1: Local -> {bastion_host} -> {target_host}:{target_port}")
            self.tunnel1 = SSHTunnelForwarder(
                (bastion_host, int(bastion_port)),
                ssh_username=bastion_user,
                ssh_password=bastion_password,
                remote_bind_address=(target_host, target_port),
                local_bind_address=('127.0.0.1', 0),
                set_keepalive=10.0
            )
            self.tunnel1.start()
            
            if not bastion2_config:
                # Single Jump Case
                self.local_bind_port = self.tunnel1.local_bind_port
                return self.local_bind_port
            
            # Double Jump Case
            # Tunnel 1 is now forwarding Local:RandomPort -> Bastion 2:22 (via Bastion 1)
            # We need Tunnel 2: Local -> (Through Tunnel 1) -> Device
            
            print(f"Starting Tunnel 2: Local -> Tunnel 1 ({self.tunnel1.local_bind_port}) -> {remote_host}:{remote_port}")
            
            # For the second tunnel, we connect to localhost at the port exposed by Tunnel 1.
            # This effectively connects us to Bastion 2.
            self.tunnel2 = SSHTunnelForwarder(
                ('127.0.0.1', self.tunnel1.local_bind_port),
                ssh_username=bastion2_config['username'],
                ssh_password=bastion2_config['password'],
                remote_bind_address=(remote_host, int(remote_port)),
                local_bind_address=('127.0.0.1', 0),
                set_keepalive=10.0
            )
            self.tunnel2.start()
            self.local_bind_port = self.tunnel2.local_bind_port
            return self.local_bind_port

        except Exception as e:
            print(f"Error starting tunnel: {e}")
            self.stop_tunnel()
            raise e

    def stop_tunnel(self):
        """Stops all active SSH tunnels."""
        if self.tunnel2:
            try:
                self.tunnel2.stop()
            except:
                pass
            self.tunnel2 = None
            
        if self.tunnel1:
            try:
                self.tunnel1.stop()
            except:
                pass
            self.tunnel1 = None
            
        self.local_bind_port = None

    def is_active(self):
        """Checks if the tunnel is active."""
        if self.tunnel1:
            return self.tunnel1.is_active
        return False

import paramiko

class GatewaySession:
    """
    Manages a persistent connection to a Gateway (Jump Host) using Paramiko.
    Allows multiplexing multiple device connections through a single transport.
    """
    def __init__(self):
        self.client = None
        self.transport = None
        self.gateway_host = None

    def connect(self, host, port, username, password, jumphost2_config=None):
        """
        Establishes the connection to the Gateway.
        If jumphost2_config is provided, it chains the connection: Local -> JH1 -> JH2.
        """
        try:
            # 1. Connect to First Jump Host
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            print(f"Connecting to Gateway 1: {host}:{port}...")
            self.client.connect(
                hostname=host,
                port=int(port),
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10,
                banner_timeout=30,
                auth_timeout=30
            )
            
            self.transport = self.client.get_transport()
            self.transport.set_keepalive(10)
            self.gateway_host = host
            print(f"Gateway 1 connection established: {host}")

            # 2. Connect to Second Jump Host (if configured)
            if jumphost2_config:
                jh2_host = jumphost2_config['host']
                jh2_port = int(jumphost2_config['port'])
                jh2_user = jumphost2_config['username']
                jh2_pass = jumphost2_config['password']

                print(f"Chaining to Gateway 2: {jh2_host}:{jh2_port}...")
                
                # Open a channel from JH1 to JH2
                jh2_channel = self.transport.open_channel(
                    "direct-tcpip",
                    (jh2_host, jh2_port),
                    ("127.0.0.1", 0)
                )
                
                # Create a new SSHClient for JH2 using the channel as the socket
                self.client2 = paramiko.SSHClient()
                self.client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                self.client2.connect(
                    hostname=jh2_host, # Hostname is needed for host key verification (even if skipped)
                    username=jh2_user,
                    password=jh2_pass,
                    sock=jh2_channel, # Use the channel as the socket
                    look_for_keys=False,
                    allow_agent=False,
                    timeout=10,
                    banner_timeout=30,
                    auth_timeout=30
                )
                
                # Update transport to point to JH2's transport
                # Now, open_channel calls will go through JH2
                self.transport = self.client2.get_transport()
                self.transport.set_keepalive(10)
                self.gateway_host = f"{host} -> {jh2_host}"
                print(f"Gateway 2 connection established: {jh2_host}")

            return True
        except Exception as e:
            print(f"Gateway connection failed: {e}")
            self.close()
            raise e

    def open_channel(self, target_host, target_port):
        """
        Opens a direct-tcpip channel to the target device through the gateway.
        Returns a socket-like object.
        """
        if not self.is_active():
            raise Exception("Gateway is not connected.")
            
        print(f"Opening channel via {self.gateway_host} -> {target_host}:{target_port}")
        # direct-tcpip channel behaves like a socket
        channel = self.transport.open_channel(
            "direct-tcpip",
            (target_host, int(target_port)),
            ("127.0.0.1", 0) # Source address (local)
        )
        return channel

    def is_active(self):
        return self.transport and self.transport.is_active()

    def close(self):
        if self.client:
            self.client.close()
        self.client = None
        self.transport = None
        self.gateway_host = None
