import ssl
from http.server import HTTPServer, SimpleHTTPRequestHandler


def main():
    server = HTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        certfile="domain.cert.pem",
        keyfile="private.key.pem",
    )

    server.socket = context.wrap_socket(
        server.socket,
        server_side=True,
    )

    print("Serving HTTPS on port 8080...")
    server.serve_forever()


if __name__ == "__main__":
    main()
