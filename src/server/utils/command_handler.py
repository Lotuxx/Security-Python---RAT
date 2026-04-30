def handle_command(command: str, client_manager):
    parts = command.split()

    if parts[0] == "list":
        clients = client_manager.get_all()
        for c in clients:
            print(f"{c.id} - {c.ip}")

    elif parts[0] == "interact":
        if len(parts) < 2:
            print("Usage: interact <id>")
            return

        client = client_manager.get(parts[1])
        if client:
            interact_with_client(client)
        else:
            print("Client not found")

    else:
        print("Unknown command")