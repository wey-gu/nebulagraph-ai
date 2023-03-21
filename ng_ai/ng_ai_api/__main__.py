import os

from ng_ai import ng_ai_api_app as app


def run():
    print(dir(app))
    app.run(host="0.0.0.0", port=int(os.environ.get("ng_ai_PORT", 9999)))
