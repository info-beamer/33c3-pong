import json
import websocket

def viewer():
    ws = websocket.create_connection(
        url = "ws://33c3.infobeamer.com/pong/socket",
        timeout = 120,
    )
    ws.send(json.dumps(dict(
        mode = "viewer",
        game = "hall6",
    )))
    while 1:
        print ws.recv()

if __name__ == "__main__":
    viewer()
