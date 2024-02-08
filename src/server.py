from flask import Flask, jsonify, Response, request

import logging

# TODO(kba): move logger to config file
logger = logging.getLogger()
logger.setLevel("INFO")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def create_server(test_config=None) -> Flask:
    # Create Flask app
    app = Flask(__name__)

    ##################
    # Define endponits
    @app.get("/ready")
    def ready() -> str:
        return "ready"

    @app.post("/productionplan")
    def productionplan() -> tuple[Response, int]:
        return jsonify({"key": "value"}), 200

    # TODO(kba): catch errors
    # Logs
    @app.after_request
    def after_request(response: Response) -> Response:
        logger.info("%s %s %s", request.method, request.path, response.status)
        return response

    return app
