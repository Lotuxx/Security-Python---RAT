import socket
import threading

from utils.client_manager import ClientManager
from utils.ui import CLI
from utils.logger import logger


def start_listener(client_manager, host="127.0.0.1", port=4444):
    def listener():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()

        logger.info(f"Listening on {host}:{port}")

        while True:
            try:
                client_socket, addr = server.accept()
                logger.info(f"Connection from {addr[0]}:{addr[1]}")

                client_manager.add(client_socket, addr)

            except Exception as e:
                logger.error(f"Listener error: {e}")

    thread = threading.Thread(target=listener, daemon=True)
    thread.start()


def main():
    # Shared manager
    client_manager = ClientManager()

    # Start listener in background
    start_listener(client_manager)

    # Start CLI
    cli = CLI(client_manager)
    cli.start()


if __name__ == "__main__":
    main()