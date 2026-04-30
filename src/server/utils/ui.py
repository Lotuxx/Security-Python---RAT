from command_handler import handle_command


class CLI:
    def __init__(self, client_manager):
        self.client_manager = client_manager
        self.running = True

    def start(self):
        print("Server started. Type 'help' for commands.")

        while self.running:
            try:
                command = input("server > ").strip()
                self.process_command(command)

            except KeyboardInterrupt:
                print("\n[!] Use 'exit' to quit.")


    def process_command(self, command: str):
        if not command:
            return

        if command == "exit":
            self.running = False
            print("Exiting...")
            return

        elif command == "help":
            self.show_help()

        else:
            handle_command(command, self.client_manager)


    def show_help(self):
        print("""
Available commands:
    help                Show this help
    list                List connected clients
    interact <id>       Interact with a client
    exit                Exit server
        """)