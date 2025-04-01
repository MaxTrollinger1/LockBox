import random
import socket

def get_local_ip():
    """Get the local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def generate_random_port(min_port: int = 1024, max_port: int = 65535) -> int:
    """
    Generate a random port number within the valid range.
    Default range is from 1024 to 65535 (excluding well-known ports 0-1023).
    """
    return random.randint(min_port, max_port)