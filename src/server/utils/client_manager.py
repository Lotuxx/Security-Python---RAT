import threading
import uuid

from .logger import logger
from .session import Session


class ClientManager:
    def __init__(self):
        self._clients = {}   # id -> Session
        self._lock = threading.Lock()

    # ------- ADD CLIENT -------- #
    def add(self, conn, addr) -> str:
        client_id = str(uuid.uuid4())[:8]

        session = Session(client_id, conn, addr)

        with self._lock:
            self._clients[client_id] = session

        logger.info(f"[+] Client connected: {client_id} ({addr[0]}:{addr[1]})")
        return client_id


    # -------- REMOVE CLIENT -------- #
    def remove(self, client_id: str):
        session = None

        with self._lock:
            session = self._clients.pop(client_id, None)

        if session:
            try:
                session.close()
            except Exception:
                pass

            logger.info(f"[-] Client removed: {client_id}")


    # --------- GET ONE CLIENT --------- #
    def get(self, client_id: str):
        with self._lock:
            return self._clients.get(client_id)


    # --------- GET ALL CLIENTS --------- #
    def get_all(self):
        with self._lock:
            return list(self._clients.values())


    # ---------- COUNT ---------- #
    def count(self):
        with self._lock:
            return len(self._clients)


    # ---------- EXISTS CHECK (NEW - IMPORTANT) ---------- #
    def exists(self, client_id: str) -> bool:
        with self._lock:
            return client_id in self._clients