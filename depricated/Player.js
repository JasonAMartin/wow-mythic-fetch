
const axios = require("axios");
const log4js = require('log4js');
const _ = require('lodash');
log4js.configure(
    {
        appenders: {
            file: {
                type: 'file',
                filename: 'errors.log',
                maxLogSize: 10 * 1024 * 1024, // = 10Mb
                numBackups: 5, // keep five backup files
                compress: true, // compress the backups
                encoding: 'utf-8',
                mode: 0o0640,
                flags: 'w+'
            }
        },
        categories: {
            default: { appenders: ['file'], level: 'trace' }
        }
    }
);
const logger = log4js.getLogger('file');

function modifyPlayer(database, name, server, data) {
    logger.info('modifying player', name, server)
}

function newPlayer(database, profileID, data) {
    database.run(`INSERT INTO Players(wow_id, name, server, faction, class, race, gender, level, achievementPoints, faction, totalHonorableKills, thumbnail) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`, [profileID, data.name, data.realm, data.faction, data.class, data.race, data.gender, data.level, data.achievementPoints, data.faction, data.totalHonorableKills, data.thumbnail], function(err) {
        if (err) {
           logger.info('---- NEW PLAYER ERROR ----- ', err.message);
        }
        // get the last insert id
       // const playerid = this.lastID;
        // add items
        logger.info('calling ADDITEMS',profileID,data.items);
        addItems(database, profileID, data.items)
      });
}

function addItems (database, playerid, data) {
    logger.info('adding items for player', playerid);
    const offhand = _.get(data, ['offHand', 'id'], 0);
    const mainRelics = _.get(data, ['mainHand', 'relics'], []);
    let relic1 = _.get(mainRelics, ['0', 'bonusLists'], [0,0,0]);
    let relic2 = _.get(mainRelics, ['1', 'bonusLists'], [0,0,0]);
    let relic3 = _.get(mainRelics, ['2', 'bonusLists'], [0,0,0]);
    let averageItemLevel = _.get(data, 'averageItemLevel', 0);
    let averageItemLevelEquipped = _.get(data, 'averageItemLevelEquipped', 0);
    let headID = _.get(data, ['head','id'], 0);
    let neckID = _.get(data, ['neck','id'], 0);
    let shoulderID = _.get(data, ['shoulder','id'], 0);
    let backID = _.get(data, ['back','id'], 0);
    let chestID = _.get(data, ['chest','id'], 0);
    let wristID = _.get(data, ['wrist','id'], 0);
    let handsID = _.get(data, ['hands','id'], 0);
    let waistID = _.get(data, ['waist','id'], 0);
    let legsID = _.get(data, ['legs','id'], 0);
    let feetID = _.get(data, ['feet','id'], 0);
    let finger1ID = _.get(data, ['finger1','id'], 0);
    let finger2ID = _.get(data, ['finger2','id'], 0);
    let trinket1ID = _.get(data, ['trinket1','id'], 0);
    let trinket2ID = _.get(data, ['trinket2','id'], 0);
    let mainHandID = _.get(data, ['mainHand','id'], 0);

        // logger.info(`Items for player ${playerid}: offhand: ${offhand} mainRelics: ${mainRelics} relic1: ${relic1} relic2: ${relic2} relic3: ${relic3}`);
    //logger.info(`Items for player ${playerid}: 1: ${_.get(data, 'averageItemLevel', '')},2:    ${_.get(data, 'averageItemLevelEquipped', '')},3:  ${_.get(data, ['head','id'], '')},4: ${_.get(data, ['neck', 'id'], '')},5:${_.get(data, ['shoulder','id'], '')},6: ${_.get(data, ['back','id'], '')},7: ${_.get(data, ['chest','id'], '')}, 8: ${_.get(data, ['wrist','id'], '')},9: ${_.get(data, ['hands','id'], '')},10: ${_.get(data, ['waist','id'], '')},11: ${_.get(data, ['legs','id'], '')},12:  ${_.get(data, ['feet','id'], '')},13:  ${_.get(data, ['finger1','id'], '')},14:  ${_.get(data, ['finger2','id'], '')}, 15: ${_.get(data, ['trinket1','id'], '')},16: ${_.get(data, ['trinket2','id'], '')}, 17: ${_.get(data, ['mainHand','id'], '')}`);

database.run(`INSERT INTO Items(
    playerid, averageItemLevel, averageItemLevelEquipped, head_id, neck_id, shoulder_id, back_id, 
    chest_id, wrist_id, hands_id, waist_id, legs_id, feet_id, finger1_id,
    finger2_id, trinket1_id, trinket2_id, mainHand_id, offHand_id, relics1_bonus1, relics1_bonus2,
    relics1_bonus3, relics2_bonus1, relics2_bonus2, relics2_bonus3, relics3_bonus1, relics3_bonus2, relics3_bonus3
    ) 
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?,)`,
    [
        playerid,
        averageItemLevel,
        averageItemLevelEquipped,
        headID,
        neckID,
        shoulderID,
        backID,
        chestID,
        wristID,
        handsID,
        waistID,
        legsID,
        feetID,
        finger1ID,
        finger2ID,
        trinket1ID,
        trinket2ID,
        mainHandID,
        offhand,
        relic1[0],
        relic1[1],
        relic1[2],
        relic2[0],
        relic2[1],
        relic2[2],
        relic3[0],
        relic3[1],
        relic3[2],
    ], function(err) { logger.info( '------- ITEMS ENTRY ERROR ------', err )})
}

module.exports.addPlayer = function (database, profileID, name, server, data) {
    logger.info('ADDING PLAYER', name);
    // If player exists, modify instead.
    let sql = `SELECT name, server FROM Players
    WHERE name = '${name}' and server = '${server}'`;

    database.all(sql, [], (err, rows) => {
    if (rows.length > 0) {
        logger.info('Skipping newPlayer');
        // player exists
       // Not modifying players right now---> modifyPlayer(database, name, server, data);
    } else {
        // new player
        axios.get(`https://us.api.battle.net/wow/character/${server}/${name}?fields=items&locale=en_US&apikey=gtzfar8g9nkgd6jzhaug9nn7hfk32sgq`)
            .then(function (response) {
                logger.info('Calling newPlayer');
                newPlayer(database, profileID, response.data);
            })
            .catch(function (error) {
               // logger.info(error);
            });
    }
    });
}


// https://us.api.battle.net/wow/character/uther/enviro?fields=items&locale=en_US&apikey=gtzfar8g9nkgd6jzhaug9nn7hfk32sgq
