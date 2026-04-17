const { db } = require('../config/database');

function findByEmail(email) {
  return new Promise((resolve, reject) => {
    db.get('SELECT id, name, email, pass FROM users WHERE email = ?', [email], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

function create(name, email, passwordHash) {
  return new Promise((resolve, reject) => {
    db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash], function(err) {
      if (err) reject(err);
      else resolve(this.lastID);
    });
  });
}

function remove(id) {
  return new Promise((resolve, reject) => {
    db.run('DELETE FROM users WHERE id = ?', [id], (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

module.exports = { findByEmail, create, remove };
