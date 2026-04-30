from .command_handler import handle_command
from .logger import logger

class CLI:
    def __init__(self, client_manager):
        self.client_manager = client_manager
        self.running = True

    def start(self):
        logger.info("Server started. Type 'help' for commands.")

        while self.running:
            try:
                command = input("server > ").strip()
                self.process_command(command)

            except KeyboardInterrupt:
                logger.exception("\n[!] Use 'exit' to quit.")


    def process_command(self, command: str):
        if not command:
            return

        if command == "exit":
            self.running = False
            logger.info("Exiting...")
            return

        elif command == "help":
            self.show_help()

        else:
            handle_command(command, self.client_manager)


    def show_help(self):
        logger.debug("""
Available commands:
    help                Show this help
    list                List connected clients
    interact <id>       Interact with a client
    exit                Exit server
        """)