import socket
import ssl

from utils.protocol import decode_message, encode_message
from utils.logger import logger


# --------- FAKE COMMAND EXECUTOR --------- #
def handle_command(command: str, args=None) -> str:
    cmd = command.split()[0].lower()

    if cmd == "ipconfig":
        return "Fake IP config:\nIP: 127.0.0.1\nGateway: 192.168.1.1"

    if cmd == "shell":
        return "Fake shell started"

    if cmd == "download":
        return "Fake file sent to server"

    if cmd == "upload":
        return "Fake file received from server"

    if cmd == "screenshot":
        return "Fake screenshot captured"

    if cmd == "webcam_snapshot":
        return "Fake webcam image captured"

    if cmd == "record_audio":
        return "Fake audio recorded"

    if cmd == "keylogger":
        return "Fake keylogger started"

    if cmd == "hashdump":
        return "Fake hashdump data"

    if cmd == "search":
        return "Fake search results"

    return f"Executed: {command}"


# -------- MAIN CLIENT LOOP -------- #
def main():
    host = "127.0.0.1"
    port = 4444

    # --- TLS CONTEXT --- #
    context = ssl.create_default_context()

    # --- self-signed cert --- #
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # --- RAW SOCKET --- #
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # --- WRAP WITH TLS --- #
    client = context.wrap_socket(raw_socket, server_hostname=host)

    # --- CONNECT --- #
    client.connect((host, port))

    logger.info("Securely connected to server")

    # -------- MAIN LOOP -------- #
    while True:
        try:
            data = client.recv(4096)

            if not data:
                logger.warning("Server closed connection")
                break

            msg = decode_message(data)

            if msg.get("type") == "command":
                cmd = msg.get("cmd")
                args = msg.get("args")

                logger.info(f"[CMD] {cmd}")

                if cmd in ("disconnect", "__DISCONNECT__"):
                    logger.warning("Disconnected by server")
                    break

                result = handle_command(cmd, args)

                response = {
                    "type": "response",
                    "status": "ok",
                    "result": result
                }

                client.send(encode_message(response))

        except ssl.SSLError as e:
            logger.error(f"SSL error: {e}")
            break

        except ConnectionResetError:
            logger.warning("Server disconnected (reset)")
            break

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            break

    client.close()
    logger.info("Client stopped")


if __name__ == "__main__":
    main()