import threading
import sys

from .logger import logger

print_lock = threading.Lock()

current_prompt = ""
current_input = ""


def set_prompt(prompt: str):
    global current_prompt
    current_prompt = prompt


def safe_print(message: str):
    with print_lock:
        # --- move to new line safely --- #
        sys.stdout.write("\r")
        sys.stdout.flush()

        logger.info(message)

        # --- redraw prompt --- #
        if current_prompt:
            sys.stdout.write(current_prompt)
            sys.stdout.flush()