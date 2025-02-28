from fitnesstracker import create_app
import os
import dotenv

dotenv.load_dotenv()

environment = str(os.getenv('FLASK_ENV'))
debug=str(os.getenv('DEBUG_MODE', 'TRUE')).lower() in ('true', '1', 't')

app = create_app(environment=environment)

if __name__ == "__main__":

    app.run(debug=debug, host="0.0.0.0")
