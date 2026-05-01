import socket
import threading
import ssl

from utils.client_manager import ClientManager
from utils.ui import CLI
from utils.logger import logger


def start_listener(client_manager, host="127.0.0.1", port=4444):
    def listener():
        # --- TLS context --- #
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

        # --- RAW SOCKET ---
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # --- allow fast restart --- #
        raw_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        raw_socket.bind((host, port))
        raw_socket.listen()

        logger.info(f"Listening securely on {host}:{port}")

        try:
            while True:
                client_socket, addr = raw_socket.accept()

                # --- Wrap EACH client connection --- #
                secure_client = context.wrap_socket(client_socket, server_side=True)

                logger.info(f"Secure connection from {addr[0]}:{addr[1]}")

                client_manager.add(secure_client, addr)

        except Exception as e:
            logger.error(f"Listener error: {e}")

        finally:
            raw_socket.close()

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