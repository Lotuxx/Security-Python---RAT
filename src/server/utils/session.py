from .logger import logger
from .protocol import encode_message, decode_message


class Session:
    def __init__(self, client_id, conn, addr):
        self.id = client_id
        self.conn = conn
        self.addr = addr
        self.status = "connected"


    # --------- SEND DATA --------- #
    def send(self, data: dict):
        try:
            if not isinstance(data, dict):
                raise ValueError("Session.send() expects dict")

            self.conn.send(encode_message(data))

        except Exception as e:
            logger.error(f"[{self.id}] Send error: {e}")
            self.status = "disconnected"


    # -------- RECEIVE DATA -------- #
    def receive(self):
        try:
            data = self.conn.recv(4096)

            if not data:
                self.status = "disconnected"
                return None

            decoded = decode_message(data)

            if not decoded:
                return {
                    "type": "response",
                    "result": data.decode(errors="ignore")
                }

            return decoded

        except Exception as e:
            logger.error(f"[{self.id}] Receive error: {e}")
            return None


    # ------- CLOSE CONNECTION ------- #
    def close(self):
        try:
            self.conn.close()
        except:
            pass

        self.status = "disconnected"


    # --------- INFO (for display) --------- #
    def info(self):
        return {
            "id": self.id,
            "ip": self.addr[0],
            "port": self.addr[1],
            "status": self.status,
            "os": "Windows",
            "user": "admin"
        }