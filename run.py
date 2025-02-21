from fitnesstracker import create_app, db

from flask import session
from datetime import datetime

app = create_app(enviroment='debug')

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    @app.route('/debug_session')
    def debug_session():
        if session.permanent:
            expiration = datetime.now() + app.permanent_session_lifetime
            return f"Session is permanent and will expire at: {expiration}"
        return "Session is not permanent and will expire when the browser is closed."


    app.run(debug=True, host="0.0.0.0")
