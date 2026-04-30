from .logger import logger


class Session:
    def __init__(self, client_id: str, conn, addr):
        self.id = client_id
        self.conn = conn
        self.addr = addr
        self.status = "connected"


    # --------- SEND DATA --------- #
    def send(self, data: str):
        try:
            self.conn.send(data.encode())
        except Exception as e:
            logger.error(f"[{self.id}] Send failed: {e}")
            self.status = "disconnected"


    # -------- RECEIVE DATA -------- #
    def receive(self, buffer_size=4096) -> str:
        try:
            data = self.conn.recv(buffer_size)

            if not data:
                self.status = "disconnected"
                return ""

            return data.decode()

        except Exception as e:
            logger.error(f"[{self.id}] Receive failed: {e}")
            self.status = "disconnected"
            return ""

    # ------- CLOSE CONNECTION ------- #
    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

        self.status = "disconnected"
        logger.info(f"[{self.id}] Session closed")


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