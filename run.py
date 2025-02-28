from fitnesstracker import create_app
import os
from dotenv import load_dotenv

load_dotenv(override=True)

<<<<<<< HEAD
app = create_app(environment='production')
=======
environment = str(os.getenv('FLASK_ENV'))
print("Environment: ", environment)
debug=str(os.getenv('DEBUG_MODE', 'TRUE')).lower() in ('true', '1', 't')

app = create_app(environment=environment)
>>>>>>> testing

if __name__ == "__main__":

    app.run(debug=debug, host="0.0.0.0")
