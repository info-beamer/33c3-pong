# Massive Multiplayer PONG for info-beamer (hosted) running at 33C3

![Pong at 33c3](misc/pong.jpg)

(Original image by [Tom / @weakmath](https://twitter.com/weakmath/status/814521296700788741))

While 33c3 was running I got the idea of implementing a
massive multiplayer pong game on the big screens in the main
halls of the conference.

Players could play on their phones, tablets or laptops
simply by visiting a webpage that was advertised on the
screens.  Players would select their hall on that site and
immediately enter the game. The game screen looks like this:

![Playing pong](misc/pong-client.jpg)

On the left and right side you see the paddles. Tap any
vertical position on either the left or right third of the
screen will set your paddle positions. You positions are
also sent to the central game server using a websocket
connection. All paddle positions for all connected players
are averaged on the server to get the final paddle
positions. 

A custom info-beamer hosted package was running on the
info-beamer device in each hall. It's 
[service program](https://info-beamer.com/doc/package-services)
connects to the game server and gets the averaged position
of the left/right paddle 10 times per second.  If forwards
that position to the locally running info-beamer program
where the pong code handles these updates and renderes the
game. Have a look at `static/tile.lua` for the game logic.

## Installation

Tested on Ubuntu 16.04:

```
$ virtualenv --system-site-packages env
$ . env/bin/activate
$ pip install -r requirements.txt
```

The directory also serves as a daemontools runnable
directory. To start the pong web server, link this directory
to /etc/service. After a few seconds the server should be up
and listen to port 30000.

During 33c3 the site itself was exposed through a locally
running nginx server. You can see the configuration used in
misc/33c3.conf. Additionally everything was running behind
cloudflare for trivial SSL setup.

## Integration with info-beamer hosted

You can import the pong package into
[info-beamer hosted](https://info-beamer.com/hosted)
by adding a new package from this url (replace example.com
with the domain where you setup the pong webserver):

```
https://example.com/pong/package.links
```

The package integrates with the 
[33c3 info-beamer package](https://github.com/info-beamer/package-33c3)
. So you can add the imported package as a child package
to the 33c3 package. See the 33c3 package on how to configure
playback of the pong package.
