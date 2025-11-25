from netmiko import ConnectHandler
import time

class DeviceConnection:
    """
    Manages Netmiko connections to network devices.
    """
    def __init__(self):
        self.connection = None

    def connect(self, device_type, host, username, password, port=22, secret=None, use_tunnel=False, tunnel_port=None, sock=None):
        """
        Establishes a connection to the network device.
        
        Args:
            device_type (str): Netmiko device type (e.g., 'cisco_ios').
            host (str): Device IP or hostname.
            username (str): Device username.
            password (str): Device password.
            port (int): SSH port (default 22).
            secret (str): Enable secret (optional).
            use_tunnel (bool): Whether to use an SSH tunnel.
            tunnel_port (int): Local port of the SSH tunnel (required if use_tunnel is True).
            sock (socket): Optional existing socket/channel (for GatewaySession).
            
        Returns:
            bool: True if connection successful, False otherwise.
        """
        device_params = {
            'device_type': device_type,
            'host': host,
            'username': username,
            'password': password,
            'port': port,
        }
        
        if secret:
            device_params['secret'] = secret

        if sock:
            device_params['sock'] = sock
            # When using a socket, host/port are technically unused by Netmiko for connection,
            # but kept for reference.
        
        # If using a tunnel (legacy), connect to localhost on the tunnel port
        elif use_tunnel and tunnel_port:
            device_params['host'] = '127.0.0.1'
            device_params['port'] = tunnel_port
        
        try:
            self.connection = ConnectHandler(**device_params)
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            raise e

    def send_command(self, command):
        """Sends a command to the device and returns the output."""
        if not self.connection:
            raise Exception("Not connected to any device.")
        return self.connection.send_command(command)

    def send_config_set(self, config_commands):
        """Sends a set of configuration commands."""
        if not self.connection:
            raise Exception("Not connected to any device.")
        return self.connection.send_config_set(config_commands)

    def disconnect(self):
        """Disconnects from the device."""
        if self.connection:
            self.connection.disconnect()
            self.connection = None

    def is_connected(self):
        return self.connection is not None
