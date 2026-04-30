import threading
import uuid
from dataclasses import dataclass
from .logger import logger


@dataclass
class ClientSession:
    id: str
    conn: object   # socket object
    addr: tuple
    status: str = "connected"


class ClientManager:
    def __init__(self):
        self._clients = {}   # id -> ClientSession
        self._lock = threading.Lock()


    # ------- ADD CLIENT --------#
    def add(self, conn, addr) -> str:
        client_id = str(uuid.uuid4())[:8]

        session = ClientSession(
            id=client_id,
            conn=conn,
            addr=addr,
        )

        with self._lock:
            self._clients[client_id] = session

        logger.critical(f"[+] Client connected: {client_id} ({addr[0]}:{addr[1]})")
        return client_id


    # -------- REMOVE CLIENT ---------#
    def remove(self, client_id: str):
        with self._lock:
            if client_id in self._clients:
                try:
                    self._clients[client_id].conn.close()
                except Exception:
                    pass

                del self._clients[client_id]
                logger.critical(f"[-] Client removed: {client_id}")


    # --------- GET ONE CLIENT ---------#
    def get(self, client_id: str):
        with self._lock:
            return self._clients.get(client_id)


    # --------- GET ALL CLIENTS --------- #
    def get_all(self):
        with self._lock:
            return list(self._clients.values())


    # ---------- BROAD SAFE VIEW  ----------#
    def count(self):
        with self._lock:
            return len(self._clients)