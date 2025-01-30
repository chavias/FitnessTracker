-- Grant privileges and create database
GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_USER}';


CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE};
USE ${MYSQL_DATABASE};

-- Create templates table
CREATE TABLE IF NOT EXISTS templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Create template_exercises table
CREATE TABLE IF NOT EXISTS template_exercises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL,
    exercise VARCHAR(100) NOT NULL,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
);

-- Create training_sessions table
CREATE TABLE IF NOT EXISTS training_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    template_id INT,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
);

-- Create exercises table
CREATE TABLE IF NOT EXISTS exercises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (session_id) REFERENCES training_sessions(id) ON DELETE CASCADE
);

-- Create exercise_details table
CREATE TABLE IF NOT EXISTS exercise_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    repetitions INT NOT NULL,
    weight FLOAT NOT NULL,
    exercise_id INT NOT NULL,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
);
