class Responses:
    BADPACKET = {"result": "invalid packet format", "resultcode": -1}

    NOBUNDLE = {"result": "bundle not found", "resultcode": 100}
    NOFILE = {"result": "file not found", "resultcode": 101}
