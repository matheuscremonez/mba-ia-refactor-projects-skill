const { db } = require('../config/database');

function findActiveById(id) {
  return new Promise((resolve, reject) => {
    db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

module.exports = { findActiveById };
