# fake_client.py

import socket


def main():
    host = "127.0.0.1"
    port = 4444

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    print("[+] Connected to server")

    while True:
        try:
            data = client.recv(4096).decode()

            if not data:
                break

            print(f"[SERVER CMD] {data}")

            # Simulate command execution
            response = f"[CLIENT RESPONSE] Executed: {data}"

            client.send(response.encode())

        except Exception as e:
            print(f"[!] Error: {e}")
            break

    client.close()


if __name__ == "__main__":
    main()