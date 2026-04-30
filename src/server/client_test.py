import socket
from utils.logger import logger


def handle_command(command: str) -> str:
    """
    Simulates execution of server commands on victim side.
    """

    cmd = command.split()[0].lower()

    # --------- SYSTEM INFO COMMANDS --------- #
    if cmd == "ipconfig":
        return "Fake IP config:\nIP: 127.0.0.1\nGateway: 192.168.1.1"

    if cmd == "shell":
        return "Fake shell started (no real execution in test client)"

    # -------- FILE OPERATIONS -------- #
    if cmd == "download":
        return "Fake file sent to server"

    if cmd == "upload":
        return "Fake file received from server"

    # --------- SCREEN / MEDIA --------- #
    if cmd == "screenshot":
        return "Fake screenshot captured: screen.png"

    if cmd == "webcam_snapshot":
        return "Fake webcam image captured: cam.jpg"

    if cmd == "record_audio":
        return "Fake audio recorded: audio.wav"

    # ---------- KEYLOGGER / ADVANCED ---------- #
    if cmd == "keylogger":
        return "Fake keylogger started"

    if cmd == "hashdump":
        return "Fake hashdump: user:password123"

    # ------- SEARCH ------- #
    if cmd == "search":
        return "Fake search results: file1.txt, file2.docx"

    # ------- DEFAULT ------- #
    return f"Executed: {command}"


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

            command = data.decode().strip()
            logger.info(f"[SERVER CMD] {command}")

            # -------- SPECIAL CONTROL COMMANDS -------- #
            if command == "__DISCONNECT__":
                logger.warning("Server requested disconnect")
                break

            # -------- EXECUTE SIMULATION ------- #
            response = handle_command(command)

            client.send(response.encode())

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