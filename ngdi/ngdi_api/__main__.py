from ngdi import ngdi_api_app as app

import os


def run():
    print(dir(app))
    app.run(host="0.0.0.0", port=int(os.environ.get("NGDI_PORT", 9999)))
