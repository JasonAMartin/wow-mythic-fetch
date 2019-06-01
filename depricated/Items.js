
const axios = require("axios");
const log4js = require('log4js');
const _ = require('lodash');
log4js.configure(
    {
        appenders: {
            file: {
                type: 'file',
                filename: 'errors-Items.log',
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



function logItems (database, data, playerid) {
    console.log('adding player: ', data);
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

    database.run("INSERT INTO Items (playerid) VALUES (?)", [playerid]);



}

module.exports.addItems = function (database) {     // new player
            const playerid = 999;
            const server = 'Thrall';
            const name = 'Moonseeker';
            axios.get(`https://us.api.battle.net/wow/character/${server}/${name}?fields=items&locale=en_US&apikey=gtzfar8g9nkgd6jzhaug9nn7hfk32sgq`)
                .then(function (response) {
                    logger.info('Calling newPlayer');
                    logItems(database, response.data.items, playerid);
                })
                .catch(function (error) {
                    // logger.info(error);
                });
};
