from fitnesstracker import create_app

from flask import session
from datetime import datetime

app = create_app(environment='debug')

if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0")
