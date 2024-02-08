from flask import Flask, jsonify, Response



def create_server(test_config=None) -> Flask:
    # Create Flask app
    app = Flask(__name__)

    ##################
    # Define endponits
    @app.get('/ready')
    def ready() -> str:
        return 'ready'

    @app.post('/productionplan')
    def productionplan() -> tuple[Response, int]:
        return jsonify({"key": "value"}), 200

    return app
