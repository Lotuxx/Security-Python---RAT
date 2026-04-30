import socket
from utils.logger import logger


def main():
    host = "127.0.0.1"
    port = 4444

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    logger.info("Connected to server")

    while True:
        try:
            data = client.recv(4096)

            if not data:
                logger.warning("Server closed connection")
                break

            command = data.decode()
            logger.info(f"[SERVER CMD] {command}")

            # Simulate execution
            response = f"[CLIENT RESPONSE] Executed: {command}"

            client.send(response.encode())

        except ConnectionResetError:
            logger.warning("Server disconnected (connection reset)")
            break

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            break

    client.close()
    logger.info("Client stopped")


if __name__ == "__main__":
    main()