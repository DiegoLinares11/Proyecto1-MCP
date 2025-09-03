DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS orders;

CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT,
  created_at TEXT
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  total REAL,
  created_at TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- seed básico (pocas filas, suficiente para probar)
INSERT INTO users(id,email,created_at) VALUES
  (1,'user00001@example.com','2024-01-01'),
  (2,'user00002@example.com','2024-01-01'),
  (3,'user00003@example.com','2024-01-01'),
  (4,'user00004@example.com','2024-01-01'),
  (5,'user00005@example.com','2024-01-01');

INSERT INTO orders(id,user_id,total,created_at) VALUES
  (1,1,120,'2024-06-01'),
  (2,2,80,'2024-06-02'),
  (3,3,50,'2024-06-03'),
  (4,4,200,'2024-06-04'),
  (5,5,70,'2024-06-05'),
  (6,1,30,'2024-06-06'),
  (7,2,15,'2024-06-07'),
  (8,3,90,'2024-06-08');
