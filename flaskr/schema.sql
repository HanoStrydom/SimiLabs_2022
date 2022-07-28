DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);



-- password is admin
INSERT INTO user VALUES (1,'admin','pbkdf2:sha256:260000$j2dCQrXnaDgBrbmO$896a6fe3480ca5cca5a433f78a52dc123ecd81c479620e5bb179de0cce115fef');