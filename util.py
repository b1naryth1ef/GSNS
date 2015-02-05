import re

STATUS_PLAYER_RE = re.compile(r'''^#\s*(?P<cid>\d+) (?:\d+) "(?P<name>.+)" (?P<guid>\S+) (?P<duration>\d+:\d+) (?P<ping>\d+) (?P<loss>\S+) (?P<state>\S+) (?P<rate>\d+) (?P<ip>\d+\.\d+\.\d+\.\d+):(?P<port>\d+)$''')

MAPS_LIST_RE = re.compile(r"^PENDING:\s+\(fs\)\s+(?P<map_name>.+)\.bsp$")

class RconParser(object):
    def player_match_to_dict(self, match):
        return {
            "cid": match.group("cid"),
            "name": match.group("name"),
            "guid": match.group("guid"),
            "duration": match.group("duration"),
            "ping": match.group("ping"),
            "loss": match.group("loss"),
            "state": match.group("state"),
            "ip": match.group("ip"),
            "port": match.group("port")
        }

    def parse_status(self, data):
        obj = {
            "hostname": None,
            "version": None,
            "map": None,
            "players": []
        }

        for line in data.split("\n"):
            if not line or line.startswith("L "):
                continue

            if line.startswith("hostname: "):
                obj['hostname'] = line.split(": ")[-1]
            elif line.startswith("version"):
                obj['version'] = line.split(" : ")[-1].rstrip(" ")
            elif line.startswith("map"):
                obj['map'] = line.split(": ")[-1]
            else:
                m = re.match(STATUS_PLAYER_RE, line)
                if m:
                    obj['players'].append(self.player_match_to_dict(m))

        return obj

    def parse_stats(self, data):
        data = data.split("\n")

        headers = [i.lower() for i in data[0].split(" ") if i]
        entries = [i for i in data[1].split(" ") if i]

        return dict(zip(headers, entries))

    def parse_maps(self, data):
        maps = []

        for line in data:
            m = re.match(MAPS_LIST_RE, line)
            maps.append(m.group("map_name"))

        return maps

