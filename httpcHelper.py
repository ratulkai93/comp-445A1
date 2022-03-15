
class HttpRequest:

    def __init__(self, host, path, query, headers):
        self.path = path
        self.host = host
        self.query = query
        self.headers = headers

    def get_info(self):
        headers = ("GET " + self.path + "?" + self.query + " HTTP/1.0\r\n"
                                                           "{headers}\r\n"
                                                           "Host:" + self.host + "\r\n\r\n")
        header_bytes = headers.format(
            headers=self.headers
        ).encode('utf-8')
        return header_bytes

    def post_info(self):
        headers = ("POST {path} HTTP/1.0\r\n"
                   "{headers}\r\n"
                   "Content-Length: {content_length}\r\n"
                   "Host: {host}\r\n"
                   "User-Agent: Concordia-HTTP/1.0\r\n"
                   "Connection: close\r\n\r\n")

        body_bytes = self.query.encode('utf-8')
        header_bytes = headers.format(
            path=self.path,
            headers=self.headers,
            content_length=len(self.query),
            host=self.host
        ).encode('utf-8')
        return header_bytes + body_bytes


class HttpResponse:

    def __init__(self, response):
        self.text = response.decode('utf-8')
        self.parseText()

    def parseText(self):
        parsedLine = self.text.split("\r\n\r\n")
        self.header = parsedLine[0]
        self.body = parsedLine[1]
        lines = self.header.split("\r\n")
        infos = lines[0].split(" ")
        self.code = infos[1]
        self.status = infos[2]
        if self.code == "301":
            self.location = lines[1].split(" ")[1].split("//")[1][:-1]
            print("Redirect to " + self.location)