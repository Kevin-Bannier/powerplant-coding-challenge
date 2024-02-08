import logging
import traceback
from flask import Flask, jsonify, Response, request

from core.productionplan import ProductionPlan


# TODO(kba): move logger to config file
logger = logging.getLogger()
logger.setLevel("INFO")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s -- %(levelname)s -- %(message)s")
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
        # 1. Parse input
        parsed_body = request.json

        # 2. Run production plan
        output = ProductionPlan.proccess(parsed_body)

        # 3. Format output
        return jsonify(output), 200

    # Catch errors
    @app.errorhandler(Exception)
    def catch_exceptions(e: Exception) -> tuple[str, int]:
        tb = traceback.format_exc()
        logger.error(tb)

        message = "INTERNAL SERVER ERROR"
        return {"error": message}, 500

    # Logs
    @app.after_request
    def after_request(response: Response) -> Response:
        if response.status_code >= 200 and response.status_code < 300:
            logger.info("%s %s %s", request.method, request.path, response.status)
        else:
            logger.error("%s %s %s", request.method, request.path, response.status)
        return response

    return app
