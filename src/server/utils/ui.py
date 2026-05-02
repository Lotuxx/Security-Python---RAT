from .command_handler import handle_command
from .logger import logger
from .terminal import set_prompt

class CLI:
    def __init__(self, client_manager):
        self.client_manager = client_manager
        self.running = True

    # ----- MAIN LOOP ----- #
    def start(self):
        logger.info("Server started. Type 'help' for commands.")

        while self.running:
            try:
                prompt = "server > "
                set_prompt(prompt)
                command = input(prompt).strip()

                if not command:
                    continue

                result = handle_command(command, self.client_manager)

                # handle exit signal from command_handler
                if result == "exit":
                    self.running = False

            except KeyboardInterrupt:
                logger.warning("[!]Use 'exit' to quit.")


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