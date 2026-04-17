const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');

const db = new sqlite3.Database(
  process.env.DATABASE_PATH || ':memory:',
  (err) => { if (err) console.error('DB connection error:', err.message); }
);

async function initDb() {
  const passwordHash = await bcrypt.hash('123456', 10);

  return new Promise((resolve, reject) => {
    db.serialize(() => {
      db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
      db.run("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
      db.run("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
      db.run("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
      db.run("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");
      db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", ['Leonan', 'leonan@fullcycle.com.br', passwordHash]);
      db.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1)");
      db.run("INSERT INTO courses (title, price, active) VALUES ('Docker', 497.00, 1)");
      db.run("INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)");
      db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')", (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  });
}

module.exports = { db, initDb };
