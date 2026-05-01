import socket
import threading

from utils.client_manager import ClientManager
from utils.ui import CLI
from utils.logger import logger


def start_listener(client_manager, host="127.0.0.1", port=4444):
    def listener():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # --- allow fast restart ---
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((host, port))
        server.listen()

        logger.info(f"Listening on {host}:{port}")

        try:
            while True:
                client_socket, addr = server.accept()
                logger.info(f"Connection from {addr[0]}:{addr[1]}")

                client_manager.add(client_socket, addr)

        except Exception as e:
            logger.error(f"Listener error: {e}")

        finally:
            server.close()

    # 🔥 THIS WAS MISSING
    thread = threading.Thread(target=listener, daemon=True)
    thread.start()

def main():
    client_manager = ClientManager()
    start_listener(client_manager)

    try:
        cli = CLI(client_manager)
        cli.start()

    except KeyboardInterrupt:
        logger.info("Shutting down server...")

    except Exception as e:
        logger.exception(f"Fatal error: {e}")


if __name__ == "__main__":
    main()