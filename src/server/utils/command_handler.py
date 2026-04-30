from typing import Optional


def handle_command(command: str, client_manager):
    parts = command.strip().split()

    if not parts:
        return

    cmd = parts[0].lower()

    if cmd == "list":
        list_clients(client_manager)

    elif cmd == "interact":
        if len(parts) < 2:
            print("[!] Usage: interact <client_id>")
            return

        interact_with_client(parts[1], client_manager)

    elif cmd == "help":
        show_help()

    else:
        print(f"[!] Unknown command: {cmd}")


#-------------- COMMANDS IMPLEMENTATION -------------#

def list_clients(client_manager):
    clients = client_manager.get_all()

    if not clients:
        print("[!] No connected clients.")
        return

    print("\nConnected clients:")
    print("-" * 40)

    for client in clients:
        print(f"ID: {client.id} | IP: {client.ip} | Status: {client.status}")

    print("-" * 40)


def interact_with_client(client_id: str, client_manager):
    client = client_manager.get(client_id)

    if not client:
        print("[!] Client not found.")
        return

    print(f"[+] Interacting with client {client.id} ({client.ip})")
    print("Type 'back' to return.\n")

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
            print("\n[!] Type 'back' to exit session.")


#---------- SESSION COMMANDS ---------#

def send_command_to_client(command: str, client):
    try:
        client.send(command)
        response = client.receive()

        if response:
            print(response)
        else:
            print("[!] No response.")

    except Exception as e:
        print(f"[!] Error communicating with client: {e}")


def print_client_info(client):
    print("\nClient info:")
    print(f"ID      : {client.id}")
    print(f"IP      : {client.ip}")
    print(f"Status  : {client.status}")
    print("")


def handle_upload(command: str, client):
    parts = command.split()

    if len(parts) < 3:
        print("[!] Usage: upload <local_path> <remote_path>")
        return

    local_path = parts[1]
    remote_path = parts[2]

    try:
        from file_transfer import upload_file
        upload_file(client, local_path, remote_path)
        print("[+] File uploaded.")

    except Exception as e:
        print(f"[!] Upload failed: {e}")


def handle_download(command: str, client):
    parts = command.split()

    if len(parts) < 3:
        print("[!] Usage: download <remote_path> <local_path>")
        return

    remote_path = parts[1]
    local_path = parts[2]

    try:
        from file_transfer import download_file
        download_file(client, remote_path, local_path)
        print("[+] File downloaded.")

    except Exception as e:
        print(f"[!] Download failed: {e}")


#----------- HELPERS --------------#

def show_help():
    print("""
Server commands:
    list                List connected clients
    interact <id>       Interact with a client
    help                Show this help
    exit                Exit server
""")


def session_help():
    print("""
Session commands:
    info                        Show client info
    upload <local> <remote>     Upload file
    download <remote> <local>   Download file
    back                        Return to main menu

Any other command will be executed on the client.
""")