const database = require('./db');
const Player = require('./Player');


const db = database.openDB();
Player.addPlayer(db, 'enviro', 'uther', {})
//database.closeDB(db);
