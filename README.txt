1. Create MySQL database auth_db
2. Create users table (see SQL below)
3. Install requirements: pip install -r requirements.txt
4. Run: python app.py

SQL:

MariaDB [(none)]>
CREATE DATABASE cohsem_IT;
USE cohsem_IT;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL
);

