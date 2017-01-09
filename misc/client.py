import json, time, sys
import websocket

def client(l, r):
    ws = websocket.create_connection(
        url = "ws://localhost:30000/pong/socket",
        timeout = 120,
        sslopt = dict(
            ca_certs = "cacert.pem",
        )
    )
    ws.send(json.dumps(dict(
        mode = "client",
        game = "hall1",
    )))

    while 1:
        ws.send(json.dumps(dict(
            l = l,
            r = r,
        )))
        time.sleep(0.3)

if __name__ == "__main__":
    client(int(sys.argv[1]), int(sys.argv[2]))
