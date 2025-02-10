from fitnesstracker import create_app, db
from flask_migrate import Migrate

app = create_app(enviroment='debug')

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    migrate = Migrate(app, db)

    app.run(debug=True, host="0.0.0.0")
