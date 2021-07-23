class HTTPResponse:
    def __init__(self):
        self.headers = {}

    def set_header(self, key, value):
        self.headers[key] = value

    def set_headers(self, new_header):
        self.headers.update(new_header)

    def flush(self):
        self.headers = {}