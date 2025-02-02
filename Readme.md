# Fitness Tracker App

This application is designed to help you track your workouts efficiently.
You can create workout templates, log your exercises, and monitor your progress over time. The app remembers the
weights and repetitions from your last session and features an autocomplete function to make logging exercises quicker and easier.
Additionally, it provides graphical representations of your workout progress. The app connects to a database to store your workout data securely,
ensuring that your progress is saved and accessible across sessions.
Deploy it easily using the included docker-compose.yml file.

## Features

- Exercise Tracking: Log and track weights and repetitions for each exercise.
- Autocomplete: Quickly select exercises with the autocomplete feature.
- Persistency: The app remembers your last session's weights and repetitions.
- Database Integration: Connects to a database to securely store and retrieve your workout data.
- Docker Support: Easy deployment using Docker Compose.
- Progress Visualization: View your workout progress through intuitive graphics
- Development & Production Modes: Seamlessly switch between development and production environments.
  

## Docker Images

Pre-built Docker images are available:

- Docker Hub: chavias/fitnesstracker
    

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
    ```
    This will build the image (if necessary) and start the app. You can now access the app at http://localhost:5000.
    You can also connect it to a SQLlight database using the docker-compose.debug.yml

5. Switching Between SQLlite and Mariadb mode
    
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