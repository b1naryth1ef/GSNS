from flask import Flask, request, jsonify
from contextlib import contextmanager
from rcon import SourceRcon
from util import RconParser

app = Flask(__name__)
app.config.from_pyfile("settings.py")
parser = RconParser()

@contextmanager
def rcon():
    rcon = SourceRcon(
            app.config.get("RCON_HOST"),
            app.config.get("RCON_PORT", 27015),
            app.config.get("RCON_PASSWORD"))

    yield rcon

    rcon.disconnect()

@app.before_request
def app_before_request():
    if app.config['AUTH_REQUIRED']:
        if not request.values.get("AUTH_KEY") in app.config["AUTH_KEYS"]:
            return jsonify({}), 401

@app.route("/api/server/status")
def route_server_status():
    with rcon() as r:
        data = r.rcon("status")
        return jsonify(parser.parse_status(data))

@app.route("/api/server/stats")
def route_server_stats():
    with rcon() as r:
        data = r.rcon("stats")
        return jsonify(parser.parse_stats(data))

@app.route("/api/server/map")
def route_server_map():
    next_map = request.values.get("map")

    with rcon() as r:
        maps = parser.parse_maps(r.rcon("maps *"))

        if next_map not in maps:
            return jsonify({"error": "Invalid Map"})

        r.rcon("map %s" % next_map)

if __name__ == "__main__":
    app.run(debug=True)
