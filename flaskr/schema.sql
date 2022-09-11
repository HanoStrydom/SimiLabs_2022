CREATE DATABASE IF NOT EXISTS SimiLabs DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE Similabs;

DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
  id int PRIMARY KEY AUTO_INCREMENT,
  username nvarchar(55) UNIQUE NOT NULL,
  password nvarchar(255) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- password is admin
INSERT INTO accounts VALUES (1,'admin','pbkdf2:sha256:260000$j2dCQrXnaDgBrbmO$896a6fe3480ca5cca5a433f78a52dc123ecd81c479620e5bb179de0cce115fef');