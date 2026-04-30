import json


# -------- ENCODE MESSAGE -------- #
def encode_message(msg: dict) -> bytes:
    """
    Convert dict → JSON bytes
    """
    try:
        return json.dumps(msg).encode()
    except Exception as e:
        raise ValueError(f"Encoding error: {e}")


# -------- DECODE MESSAGE -------- #
def decode_message(data: bytes) -> dict:
    """
    Convert JSON bytes → dict
    """
    try:
        return json.loads(data.decode())
    except Exception:
        return {}


# -------- BUILD COMMAND PACKET -------- #
def build_command(cmd: str, args=None):
    if args is None:
        args = []

    return {
        "type": "command",
        "cmd": cmd,
        "args": args
    }


# -------- BUILD RESPONSE PACKET -------- #
def build_response(status: str, result: str):
    return {
        "type": "response",
        "status": status,
        "result": result
    }