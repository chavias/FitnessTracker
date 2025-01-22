from fitnesstracker import app, db
from flask_migrate import Migrate


if __name__ == "__main__":

    with app.app_context():
        db.create_all()
        # from sqlalchemy import inspect
        # inspector = inspect(db.engine)
        # tables = inspector.get_table_names()
        # print(f"{tables}")

    migrate = Migrate(app, db)

    app.run(debug=True, host="0.0.0.0")
