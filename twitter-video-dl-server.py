from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import src.twitter_video_dl.twitter_video_dl as tvdl

DCEBUG_MODE = False


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        url = params.get("url", [""])[0]
        fileName = params.get("fileName", [""])[0]
        if url:
            tvdl.download_video_for_sc(url, fileName)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"URL received")
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"No URL received")

    def log_message(self, format, *args):
        if DCEBUG_MODE:
            # Display log only when debug mode is True.
            super().log_message(format, *args)


def run(server_class=HTTPServer, handler_class=RequestHandler, port=3000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
