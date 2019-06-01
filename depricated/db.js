const sqlite3 = require('sqlite3').verbose();

// open the database
module.exports.openDB = function () {
  let db = new sqlite3.Database('./db/WOW.db', sqlite3.OPEN_READWRITE, (err) => {
    if (err) {
      console.error(err.message);
    }
    console.log('Connected to the WOW database.');
  });
  return db;
}

module.exports.closeDB = function (db) {
  db.close((err) => {
    if (err) {
      console.error(err.message);
    }
    console.log('Close the database connection.');
  });
}

function writeMythicData(data) {

}

function writePlayerData(player) {
  
}
