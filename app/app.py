from flask import Flask, request, jsonify
from contextlib import contextmanager
from rcon import SourceRcon
from util import RconParser

app = Flask(__name__)
app.config.from_pyfile("settings.py")
parser = RconParser()


def get_rcon():
    return SourceRcon(
            app.config.get("RCON_HOST"),
            app.config.get("RCON_PORT", 27015),
            app.config.get("RCON_PASSWORD"))

@contextmanager
def rcon():
    rcon = get_rcon()
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

@app.route("/api/map/change")
def route_map_change():
    next_map = request.values.get("map")

    with rcon() as r:
        maps = parser.parse_maps(r.rcon("maps *"))

        if next_map not in maps:
            return jsonify({"error": "Invalid Map"})

        r.rcon("map %s" % next_map)

@app.route("/api/map/list")
def route_map_list():
    with rcon() as r:
        maps = parser.parse_maps(r.rcon("maps *"))

        return jsonify({
            "maps": maps
        })

@app.route("/api/cvar/list")
def route_cvar_list():
    with rcon() as r:
        cvars = parser.parse_cvars(r.rcon("cvarlist"))

        return jsonify({
            "cvars": cvars
        })

@app.route("/api/cvar/get")
def route_cvar_get():
    with rcon() as r:
        return jsonify({
            "value": parser.parse_cvar(r.rcon(request.values.get("name")))[1]
        })

@app.route("/api/cvar/set")
def route_cvar_set():
    with rcon() as r:
        r.rcon("%s %s" % (request.values.get('name'), request.values.get('value')))

        return jsonify({})

if __name__ == "__main__":
    app.run(debug=True)

