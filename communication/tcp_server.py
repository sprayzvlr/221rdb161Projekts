import socket
from model.predict import predict

def run_tcp_server(host='0.0.0.0', port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)
    print(f"Listening on {host}:{port} ...")
    conn, _ = sock.accept()
    with conn:
        data = conn.recv(1024).decode()
        # Sagaida JSON: {"temp":..,"pressure":..,"flow":..}
        import json
        sample = json.loads(data)
        result = predict(sample)
        conn.send(str(result).encode())