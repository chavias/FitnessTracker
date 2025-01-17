from fitnesstracker import app, db


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # from sqlalchemy import inspect
        # inspector = inspect(db.engine)
        # tables = inspector.get_table_names()
        # print(f"{tables}")
    app.run(debug=True)
