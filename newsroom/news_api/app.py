import os
from asgiref.wsgi import WsgiToAsgi
from .factory import get_app


app = get_app()
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("APIPORT", "5400"))
    app.run(host=host, port=port, debug=True, use_reloader=True)
