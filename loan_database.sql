CREATE DATABASE loan_db;
USE loan_db;
CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    f1 INT,
    f2 INT,
    f3 INT,
    f4 INT,
    f5 INT,
    f6 INT,
    f7 INT,
    f8 INT,
    result VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);