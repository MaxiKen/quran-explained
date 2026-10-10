#!/usr/bin/env python3
"""Dev preview server: static files, nothing cached.

    python3 tools/serve.py            # http://0.0.0.0:8000
    python3 tools/serve.py 8080

`python -m http.server` sends Last-Modified and no Cache-Control, so a browser
may answer a repeated request for sw.js or a guidance payload from its own HTTP
cache. When the service worker is cache-first for same-origin files, that means
an updated payload is invisible in the preview — the worker never learns there is
a new version, so it never activates and never retires its cached files. Every
response here is no-store, which is the only sane setting for a preview whose
whole job is to show content that was just appended.

Offline behaviour is untouched: this only changes what the browser is allowed to
keep, and the service worker still caches for offline use on its own terms.
"""
import functools
import http.server
import os
import socketserver
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(Handler, directory=ROOT)
    with Server(('0.0.0.0', port), handler) as httpd:
        print(f'serving {ROOT} on 0.0.0.0:{port} (no-store)', flush=True)
        httpd.serve_forever()


if __name__ == '__main__':
    main()
