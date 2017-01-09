import sys, json
from time import time
from flask import Flask, request, render_template, url_for, Response
from gevent import pywsgi, sleep
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocketError

TIMEOUT = 15
ADDR = '127.0.0.1'

# XXX: Set this to the request environ variable that
# holds the remote ip address for the connecting client.
# This will prevent the same client from connecting
# multiple times.
IP_KEY = 'REMOTE_ADDR'

# If you're behind cloudflare:
# IP_KEY = 'HTTP_CF_CONNECTING_IP'

class Player(object):
    def __init__(self):
        self._last = time()
        self._l = None
        self._r = None

    def set_pos(self, l, r):
        self._l, self._r = l, r
        self._last = time()

    def get_pos(self, now):
        if self._last + TIMEOUT < now:
            return None, None
        else:
            return self._l, self._r

class Pong(object):
    def __init__(self):
        self._players = {}
        self._ips = set()

    def add_player(self, socket):
        ip = socket.ip
        if ip in self._ips:
            raise ValueError("duplicate player")
        self._ips.add(ip)
        player = self._players[socket] = Player()
        print >>sys.stderr, "adding player, now %d" % len(self._players)
        return player

    def del_player(self, socket):
        if not socket in self._players:
            return
        ip = socket.ip
        self._ips.remove(ip)
        del self._players[socket]
        print >>sys.stderr, "removing player, now %d" % len(self._players)

    @property
    def num_players(self):
        return len(self._players)

    def calc_pos(self):
        l_sum, r_sum = 0, 0
        l_cnt, r_cnt = 0, 0
        for player in self._players.itervalues():
            l, r = player.get_pos(time())
            if l is not None:
                l_sum += l
                l_cnt += 1
            if r is not None:
                r_sum += r
                r_cnt += 1

        l, r = 50, 50
        if l_cnt > 0:
            l = l_sum / l_cnt
        if r_cnt > 0:
            r = r_sum / r_cnt
        return l, r

GAMES = {
    'hall1': Pong(),
    'hall2': Pong(),
    'hall6': Pong(),
    'hallg': Pong(),
    'test':  Pong(),
}

class Socket(object):
    def __init__(self, ws, ip):
        print(self, ws)
        self._ws = ws
        self._ip = ip

    @property
    def ip(self):
        return self._ip

    def receive(self):
        pkt = self._ws.receive()
        if pkt is None:
            return None
        return json.loads(pkt)

    def send(self, **data):
        self._ws.send(json.dumps(data))

    def run(self):
        try:
            print >>sys.stderr, ">>> new client", self._ws
            handshake = self.receive()
            mode = handshake['mode']
            game = GAMES[handshake['game']]
            try:
                if mode == 'client':
                    self.client(game)
                elif mode == 'viewer':
                    self.viewer(game)
            except WebSocketError, err:
                print err
        finally:
            print >>sys.stderr, "<<< close client", self._ws
            self._ws.close()
        return ''

    def viewer(self, game):
        while 1:
            l, r = game.calc_pos()
            self.send(l=l, r=r, num=game.num_players)
            sleep(0.1)
            
    def client(self, game):
        try:
            player = game.add_player(self)
            while 1:
                command = self.receive()
                if command is None:
                    break
                if 'p' in command:
                    self.send(p=1, num=game.num_players)
                    continue
                l, r = command['l'], command['r']
                if not isinstance(l, int) or not isinstance(r, int):
                    raise ValueError("narf")
                if not 0 <= l <= 100:
                    raise ValueError("l wrong")
                if not 0 <= r <= 100:
                    raise ValueError("r wrong")
                player.set_pos(l, r)
        finally:
            game.del_player(self)

app = Flask(__name__, static_url_path='/pong/static')

@app.route('/pong/package.links')
def package():
    def f(filename):
        return "%s %s" % (filename, url_for(
            'static', filename=filename, _external=True,
        ))
    lines = [
        "[info-beamer-links]",
        f("package.png"),
        f("package.json"),
        f("node.json"),
        f("tile.lua"),
        f("font.ttf"),
        f("service"),
        f("hosted.py"),
        f("websocket.py"),
    ]
    return Response(
        ''.join(line + '\n' for line in lines),
        mimetype = 'text/plain',
    )

@app.route('/pong')
def game():
    game = request.values.get("game")
    if game in GAMES:
        return render_template("pong_game.jinja", game=game)
    else:
        return render_template("pong_game_select.jinja", games=sorted(GAMES.keys()))

@app.route('/pong/socket')
def websocket():
    return Socket(request.environ['wsgi.websocket'], request.environ[IP_KEY]).run()

def main():
    server = pywsgi.WSGIServer((ADDR, 30000), app, handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
