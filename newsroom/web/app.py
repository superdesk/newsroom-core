import os
from asgiref.wsgi import WsgiToAsgi

from .factory import get_app


app = get_app()
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "5050"))
    app.run(debug=True, host=host, port=port, threaded=True)
