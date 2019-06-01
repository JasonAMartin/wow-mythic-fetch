const WOW = require('./wow-core');
const database = require('./db');
const db = database.openDB();
const task = new WOW();
task.getResults(db);