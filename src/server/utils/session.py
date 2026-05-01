from .logger import logger
from .protocol import encode_message, decode_message


class Session:
    def __init__(self, client_id, conn, addr):
        self.id = client_id
        self.conn = conn
        self.addr = addr

        # -------- SESSION STATE -------- #
        self.status = "connected"
        self.mode = "normal"   # normal | shell

        # buffer for streaming output (shell, etc.)
        self.buffer = []

    # -------- SEND -------- #
    def send(self, packet: dict):
        try:
            if not isinstance(packet, dict):
                raise ValueError("Session.send expects dict")

            self.conn.send(encode_message(packet))

        except Exception as e:
            logger.error(f"[{self.id}] send error: {e}")
            self.status = "disconnected"

    # -------- RECEIVE (SAFE) -------- #
    def receive(self):
        try:
            data = self.conn.recv(4096)

            if not data:
                self.status = "disconnected"
                return None

            msg = decode_message(data)

            if not msg:
                return {
                    "type": "raw",
                    "data": data.decode(errors="ignore")
                }

            return msg

        except Exception as e:
            logger.error(f"[{self.id}] receive error: {e}")
            self.status = "disconnected"
            return None

    # -------- ROUTE MESSAGE -------- #
    def handle_message(self, msg):
        if not msg:
            return None

        # shell streaming output
        if msg["type"] == "shell_output":
            return "shell_output", msg.get("data")

        # normal response
        if msg["type"] == "response":
            return "response", msg.get("result")

        return "unknown", msg

    # -------- MODE MANAGEMENT -------- #
    def set_mode(self, mode: str):
        self.mode = mode

    def is_shell(self):
        return self.mode == "shell"

    # -------- CLOSE -------- #
    def close(self):
        try:
            self.conn.close()
        except:
            pass

        self.status = "disconnected"

    # -------- INFO -------- #
    def info(self):
        return {
            "id": self.id,
            "ip": self.addr[0],
            "port": self.addr[1],
            "status": self.status,
            "mode": self.mode
        }