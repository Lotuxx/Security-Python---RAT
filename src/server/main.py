import socket
import threading
import ssl

from utils.client_manager import ClientManager
from utils.session import Session
from utils.ui import CLI
from utils.logger import logger


# ----------- LISTENER ---------- #
def start_listener(client_manager, host="127.0.0.1", port=4444):

    def listener():
        # --- TLS CONTEXT --- #
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

        # --- SOCKET --- #
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind((host, port))
        server_socket.listen()

        logger.info(f"Listening securely on {host}:{port}")

        try:
            while True:
                raw_client, addr = server_socket.accept()

                # ----- TLS wrap ----- #
                secure_client = context.wrap_socket(
                    raw_client,
                    server_side=True
                )

                client_manager.add(secure_client, addr)

        except Exception as e:
            logger.error(f"Listener error: {e}")

        finally:
            server_socket.close()

    threading.Thread(target=listener, daemon=True).start()


# ----------- MAIN ----------- #
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