# import nodules for server application
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import os

# basic HTML template
html = '''
<!DOCTYPE html>
    <title>URI Shortner</title>
    <body/>
        <form action="http://localhost:8000/" method="POST">
            <label>Long URI:
                <input type="text" name="uri" value="mystery">
            </label>
            <br>
            <label>Short Name:
                <input type="text" name="short" value="spooky">
            </label>
            <br>
            <button type="submit">Do a thing!</button>
        </form>
        <hr>
        <pre>
        {list}
        </pre>
    </body>
</html>
'''

# storage for uri as key-value pair {"shortname": "long-uri"}
memory = {}


def checkURI(uri, timeout=5):
    """Check if the URI send OK response else raise error"""
    try:
        r = requests.get(uri, timeout=timeout)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


class MyHandler(BaseHTTPRequestHandler):
    """Class to handle GET and POST requests"""

    def do_GET(self):
        # store the path by excludingh the root symbol "/""
        path = self.path[1:]
        if path:
            if path in memory:
                # redirection
                self.send_response(303)
                self.send_header("location", memory[path])
                self.end_headers()
            else:
                # error
                self.send_response(404)
                self.send_header("content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("Unable to find URI for short name {} " +
                                 "from memory".format(path).encode())
        else:
            # ok status
            # its the part of PRG architecture
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()
            # join all short name and uri to display them in HTML string above
            m = ["{m} : {uri}<br>".format(m=m, uri=memory[m]) for m in memory]
            self.wfile.write(html.format(list="".join(m)).encode())

    def do_POST(self):
        length = int(self.headers.get("Content-length", 0))
        query = self.rfile.read(length).decode()
        q = parse_qs(query)

        # check if the key params exists in query string
        if "uri" in q and "short" in q:
            if checkURI(q["uri"][0]):
                memory[q["short"][0]] = q["uri"][0]
                # redirection to root, part of PRG
                self.send_response(303)
                self.send_header("location", "/")
                self.end_headers()
            else:
                # error
                self.send_response(404)
                self.send_header("content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("Unable to get response " +
                                 "form URI {}.".format(q["uri"][0]).encode())
        else:
            # error
            self.send_response(404)
            self.send_header("content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Not all form fields provided.".encode())

# commands to run the server on localhost at port 8000
if __name__ == "__main__":
    # use port if it's there
    port = int(os.environ.get('PORT', 8000))  
    # added for Heroku
    server = HTTPServer(("", 8000), MyHandler)

    # server = HTTPServer(("127.0.0.1", 8000), MyHandler)
    server.serve_forever()
