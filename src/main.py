from waitress import serve
from server import create_server


def main():
    srv = create_server()
    serve(srv, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
