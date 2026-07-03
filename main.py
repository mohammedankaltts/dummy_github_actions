import os
import socket

if __name__ == "__main__":
    print(f"Hello from: {os.getcwd()} -- Machine name: {socket.gethostname()}")
