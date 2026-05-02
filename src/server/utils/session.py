from .logger import logger
from .protocol import encode_message, decode_message
import threading


class Session:
    def __init__(self, client_id, conn, addr):
        self.id = client_id
        self.conn = conn
        self.addr = addr

        self.status = "connected"
        self.mode = "normal"   # normal | shell

        self.buffer = []
        """
        self._running = True

        # background listener
        self.listener_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self.listener_thread.start()"""
        self._lock = threading.Lock()

    # -------- SEND -------- #
    def send(self, packet: dict):
        try:
            self.conn.sendall(encode_message(packet))
        except Exception as e:
            logger.error(f"[{self.id}] send error: {e}")
            self.status = "disconnected"

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


    # -------- LISTENER -------- #
    """
    def _listen_loop(self):
        while self._running:
            try:
                data = self.conn.recv(4096)

                if not data:
                    self.status = "disconnected"
                    break

                msg = decode_message(data)

                if msg:
                    self._handle_message(msg)

            except Exception as e:
                logger.error(f"[{self.id}] listener error: {e}")
                self.status = "disconnected"
                break
    """

    # -------- ROUTING ONLY -------- #
    """
    def _handle_message(self, msg):
        if not msg:
            return None

        if msg["type"] == "shell_output":
            return "shell_output", msg.get("data")

        if msg["type"] == "response":
            return "response", msg.get("result")

        return "unknown", msg
    """

    def _listen_loop(self):
        while self._running:
            try:
                data = self.conn.recv(4096)

                if not data:
                    self.status = "disconnected"
                    break

                msg = decode_message(data)

                if msg:
                    msg_type, payload = self._handle_message(msg)
                    self.push_buffer(msg_type, payload)

            except Exception as e:
                logger.error(f"[{self.id}] listener error: {e}")
                self.status = "disconnected"
                break


    def handle_message(self, msg):
        if not msg:
            return None, None

        if msg.get("type") == "shell_output":
            return "shell_output", msg.get("data")

        if msg.get("type") == "response":
            return "response", msg.get("result")

        return "unknown", msg

    # -------- BUFFER -------- #
    def push_buffer(self, msg_type, data):
        with self._lock:
            self.buffer.append((msg_type, data))

    def pop_buffer(self):
        with self._lock:
            data = self.buffer[:]
            self.buffer.clear()
        return data

    # -------- MODE -------- #
    def set_mode(self, mode: str):
        self.mode = mode

    def is_shell(self):
        return self.mode == "shell"

    # -------- CLOSE -------- #
    def close(self):
        self._running = False
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