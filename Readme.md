# Fitness Tracker App

A simple Flask app for tracking your workouts. This app remembers the weights and repetitions of the last time you performed exercises and features an autocomplete to make tracking even easier. It is containerized using Docker and can be quickly deployed with the included docker-compose.yml file.

## Features
 - Exercise Tracking: Keeps track of the weights and repetitions for each exercise.
 - Autocomplete: Autocompletes exercise names for easy selection.
 - Persistency: Remembers the weights and repetitions of your last session.
 - Docker Support: Simple deployment using Docker Compose.
 - Development & Production Modes: Switch easily between development and production modes.

## Getting Started
<!-- To get started with the app, follow these steps: -->

1. Clone the repository

    ```bash
    git clone https://github.com/yourusername/workout-tracker.git
    cd workout-tracker
    ```

1. Create a .env file

    Copy the example .env.example file to create your own .env file with the necessary configuration.

    ```bash
    cp .env.example .env
    ```

    Edit the .env file to include the appropriate settings for your environment (e.g., database credentials, secret keys).

3. Set up Docker

    Ensure you have Docker and Docker Compose installed on your machine. You can check the installation with:

    ```bash
    docker --version
    docker-compose --version
    ```

4. Run the App Using Docker Compose

    Once you have the .env file set up, you can easily start the app by running:

    ```bash
    docker-compose up --build
    This will build the image (if necessary) and start the app. You can now access the app at http://localhost:5000.
    ```

5. Switching Between Debug and Production Mode
    
    The app can be run in either debug or production mode. To switch modes, open the run.py file and set the DEBUG variable to True for development or False for production.

    Example:

    ```python
    DEBUG = True  # Change to False for production
    ```

6. Access the App

Once the app is running, you can access it at http://localhost:5000 and start tracking your workouts.

Docker Commands
Here are some useful Docker commands for managing the app:

Build the Docker image:

```bash
docker-compose build
```

Start the app:

```bash
docker-compose up
```

Stop the app:

```bash
docker-compose down
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.