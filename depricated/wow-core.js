const axios = require("axios");
const Player = require('./Player');
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


const specs = {
    62: { name: 'Mage: Arcane', role: 'dps', count: 0},
    63: { name: 'Mage: Fire', role: 'dps', count: 0},
    64: { name: 'Mage: Frost', role: 'dps', count: 0},
    65: { name: 'Paladin: Holy', role: 'heal', count: 0},
    66: { name: 'Paladin: Protection', role: 'tank', count: 0},
    70: { name: 'Paladin: Retribution', role: 'dps', count: 0},
    71: { name: 'Warrior: Arms', role: 'dps', count: 0},
    72: { name: 'Warrior: Fury', role: 'dps', count: 0},
    73: { name: 'Warrior: Protection', role: 'tank', count: 0},
    102: { name: 'Druid: Balance', role: 'dps', count: 0},
    103: { name: 'Druid: Feral', role: 'dps', count: 0},
    104: { name: 'Druid: Guardian', role: 'tank', count: 0},
    105: { name: 'Druid: Restoration', role: 'heal', count: 0},
    250: { name: 'Death Knight: Blood', role: 'tank', count: 0},
    251: { name: 'Death Knight: Frost', role: 'dps', count: 0},
    252: { name: 'Death Knight: Unholy', role: 'dps', count: 0},
    253: { name: 'Hunter: Beast Mastery', role: 'dps', count: 0},
    254: { name: 'Hunter: Marksmanship', role: 'dps', count: 0},
    255: { name: 'Hunter: Survival', role: 'dps', count: 0},
    256: { name: 'Priest: Discipline', role: 'heal', count: 0},
    257: { name: 'Priest: Holy', role: 'heal', count: 0},
    258: { name: 'Priest: Shadow', role: 'dps', count: 0},
    259: { name: 'Rogue: Assassination', role: 'dps', count: 0},
    260: { name: 'Rogue: Combat', role: 'dps', count: 0},
    261: { name: 'Rogue: Subtlety', role: 'dps', count: 0},
    262: { name: 'Shaman: Elemental', role: 'dps', count: 0},
    263: { name: 'Shaman: Enhancement', role: 'dps', count: 0},
    264: { name: 'Shaman: Restoration', role: 'heal', count: 0},
    265: { name: 'Warlock: Affliction', role: 'dps', count: 0},
    266: { name: 'Warlock: Demonology', role: 'dps', count: 0},
    267: { name: 'Warlock: Destruction', role: 'dps', count: 0},
    268: { name: 'Monk: Brewmaster', role: 'tank', count: 0},
    269: { name: 'Monk: Windwalker', role: 'dps', count: 0},
    270: { name: 'Monk: Mistweaver', role: 'heal', count: 0},
    577: { name: 'Demon Hunter: Havoc', role: 'dps', count: 0},
    581: { name: 'Demon Hunter: Vengeance', role: 'tank', count: 0}
}


const dungeons = [197, 198, 199, 200, 206, 207, 208, 209, 210, 227, 233, 234, 239];
/*
    57 = illidan
    5 = proudmoore
    1566 = area 52
    61 = Zul Jin
    76 = Sargeras
*/
const servers = [5, 57, 1566, 61, 76]


class WOWCore {

    constructor() {
        // deep copy specs so each instantiation gets non-referenced copy of specs.
        this.charSpecs = JSON.parse(JSON.stringify( specs ));
    }
    getRole(role) {
        let data = [];
        for(var id in this.charSpecs) {
            if (this.charSpecs[id].role === role) data.push(this.charSpecs[id]);
        }
        return data;
    }

    getServers() {
        return servers;
    }

    getDungeons() {
        return dungeons;
    }

buildMythicApiCalls() {
        var data = [];
        
        servers.map(function(d){
            for (var index =0; index<dungeons.length; index++) {
                const url =
        `https://us.api.battle.net/data/wow/connected-realm/${d}/mythic-leaderboard/${dungeons[index]}/period/602?namespace=dynamic-us&locale=en_US&access_token=j6945863mx3g8zdr59kx5tee`;
  
                data.push(url);
            }
        });
        return data;
    }

    getResults2(role, maxRank) {
        this.fetchData(this.buildMythicApiCalls(), maxRank)
    }

    addCount(id) {
        this.charSpecs[id].count++;
    }

    getCount(id) {
        return this.charSpecs[id].count;
    }

    getRoles(db, members) {
        logger.info('adding members', members.length)
        let dps = 1;
        let group = {}
        for (let index = 0; index < members.length; index++) {
            const currentMember = members[index];
            const profileID = currentMember.profile.id;
            const profileName = currentMember.profile.name;
            const realmSlug = currentMember.profile.realm.slug;
            const specID = currentMember.specialization.id;
            const specName = currentMember.specialization.name;
            const spec = this.charSpecs[specID];

            if (spec.role === 'tank') group['tank'] = {'name': specName, 'id': specID, 'charName': profileName, 'realm': realmSlug, 'wowID': profileID};
            if (spec.role === 'heal') group['healer'] = {'name': specName, 'id': specID, 'charName': profileName, 'realm': realmSlug, 'wowID': profileID};
            if (spec.role === 'dps') {
                group['dps' + dps] = {'name': specName, 'id': specID, 'charName': profileName, 'realm': realmSlug, 'wowID': profileID};
                dps++;
            }

            // TODO? add player here????
            Player.addPlayer(db, profileID, profileName, realmSlug, {})

        }
        return group
    }


    addMythic(db, data, dungeon_id, dungeon_name) {
        logger.info('adding mythic', dungeon_id, dungeon_name);
        const completedTimestamp = _.get(data, 'completed_timestamp', '');
        const keystoneLevel = _.get(data, 'keystone_level', '');
        const keystoneAffixes = _.get(data, 'keystone_affixes', '');
        const members = _.get(data, 'members', '');
        const affix1 = _.get(keystoneAffixes, ['0', 'name'], '');
        const affix2 = _.get(keystoneAffixes, ['1', 'name'], '');
        const affix3 = _.get(keystoneAffixes, ['2', 'name'], '');
        const role = this.getRoles(db, members);
        const tankID = _.get(role, ['tank', 'wowID'], '');
        const healerID = _.get(role, ['healer', 'wowID'], '');
        // if in db, don't insert
        let sql = `SELECT * FROM Mythics
    WHERE keystone_level = '${keystoneLevel}' and dungeon_id = '${dungeon_id}' and dungeon_name = '${dungeon_name}' and completed_timestamp = '${completedTimestamp}' 
    and tank_id = '${tankID}' and healer_id = '${healerID}'`;


        database.all(sql, [], (err, rows) => {
            if (rows.length === 0) {
                db.run(`INSERT INTO Mythics(
            keystone_level, dungeon_id, dungeon_name, complete_time, ranking, affix1, affix2, affix3, tank, tank_id,
            healer, healer_id, dps1, dps1_id, dps2, dps2_id, dps3, dps3_id, completed_timestamp
            ) 
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )`,
                    [
                        keystoneLevel,
                        dungeon_id,
                        dungeon_name,
                        _.get(data, 'duration', ''),
                        _.get(data, 'ranking', ''),
                        affix1,
                        affix2,
                        affix3,
                        _.get(role, ['tank', 'name'], ''),
                        _.get(role, ['tank', 'wowID'], ''),
                        _.get(role, ['healer', 'name'], ''),
                        _.get(role, ['healer', 'wowID'], ''),
                        _.get(role, ['dps1', 'name'], ''),
                        _.get(role, ['dps1', 'wowID'], ''),
                        _.get(role, ['dps2', 'name'], ''),
                        _.get(role, ['dps2', 'wowID'], ''),
                        _.get(role, ['dps3', 'name'], ''),
                        _.get(role, ['dps3', 'wowID'], ''),
                        completedTimestamp
                    ], function(err) { logger.info(' MYTHICS ERRROR! --------> ', err)});
            } });
    }


    // TODO PRomise is ALL or nothing. NEed to check URL for 404 before putting it in promise. So damn stupid
    getResults(db) {
        const urls = this.buildMythicApiCalls();
        const grabContent = url => axios.get(url)
            .then(res => {
                // data fetched for 100 mythic
                // log all the data
                const mythicGroups = res.data.leading_groups;
                for (let index = 0; index < mythicGroups.length; index++) {
                    const group = mythicGroups[index];                    
                    // check if this group is in Mythic DB. 
                    this.addMythic(db, mythicGroups[index], res.data.map_challenge_mode_id, res.data.name)
                }
    
            });


            axios
            .all(urls.map(grabContent))
            .then(axios.spread(function () {
                logger.info('axios done')
            }))
            .catch(err => console.error())
            

    }

    fetchData(urls, maxRank) {
        let promises = [];

        for (let i = 0; i < urls.length; i++) {
            promises.push(axios.get(urls[i]));
            //logger.info(urls[i])
        }


         axios
         .all(promises)
        .then(response => {
            var groups = response.data.leading_groups; // array
            for (let index = 0; index < groups.length; index++) {
              var currentGroup = groups[index];
              var ranking = currentGroup.ranking;
              var members = currentGroup.members; //array
              // iterate members
              for (let pointer = 0; pointer < members.length; pointer++) {
                  var spec = members[pointer].specialization.id;
                  if (ranking < maxRank) this.charSpecs[spec].count++;
              }
      
            }
           logger.info('Final counts: ', this.charSpecs);
        })
        .then(
            logger.info('actually done')
        )
        .catch(error => {
          //logger.info(error);
        });
    }
    





    // TODO fix this. How is store being handled?
    // extractBest(careThreshold, role) {
    //     let totalSpecs = 0;
    //     let roles = getRole(role);



    //     for (let spec in classCounts) {
    //         if( classCounts.hasOwnProperty(spec) ) {
    //             totalSpecs += classCounts[spec];
    //         } 
    //     }     
        
    //     // TODO fix double iterate
    //     for (let spec in classCounts) {
    //         if( classCounts.hasOwnProperty(spec) ) {
    //             var specPercent = classCounts[spec] / totalSpecs * 100;
    //             if (specPercent >= careThreshold) logger.info(spec, totalSpecs, specPercent, careThreshold);
    //         } 
    //     }     
            
    // }
}

module.exports = WOWCore;




  /*
  62 - Mage: Arcane
63 - Mage: Fire
64 - Mage: Frost
65 - Paladin: Holy
66 - Paladin: Protection
70 - Paladin: Retribution
71 - Warrior: Arms
72 - Warrior: Fury
73 - Warrior: Protection
102 - Druid: Balance
103 - Druid: Feral
104 - Druid: Guardian
105 - Druid: Restoration
250 - Death Knight: Blood
251 - Death Knight: Frost
252 - Death Knight: Unholy
253 - Hunter: Beast Mastery
254 - Hunter: Marksmanship
255 - Hunter: Survival
256 - Priest: Discipline
257 - Priest: Holy
258 - Priest: Shadow
259 - Rogue: Assassination
260 - Rogue: Combat
261 - Rogue: Subtlety
262 - Shaman: Elemental
263 - Shaman: Enhancement
264 - Shaman: Restoration
265 - Warlock: Affliction
266 - Warlock: Demonology
267 - Warlock: Destruction
268 - Monk: Brewmaster
269 - Monk: Windwalker
270 - Monk: Mistweaver
577 - Demon Hunter: Havoc
581 - Demon Hunter: Vengeance
*/



/*
Dungeons
:
{key: {…}, name: "Eye of Azshara", id: 197}
1
:
{key: {…}, name: "Darkheart Thicket", id: 198}
2
:
{key: {…}, name: "Black Rook Hold", id: 199}
3
:
{key: {…}, name: "Halls of Valor", id: 200}
4
:
{key: {…}, name: "Neltharion's Lair", id: 206}
5
:
{key: {…}, name: "Vault of the Wardens", id: 207}
6
:
{key: {…}, name: "Maw of Souls", id: 208}
7
:
{key: {…}, name: "The Arcway", id: 209}
8
:
{key: {…}, name: "Court of Stars", id: 210}
9
:
{key: {…}, name: "Return to Karazhan: Lower", id: 227}
10
:
{key: {…}, name: "Cathedral of Eternal Night", id: 233}
11
:
{key: {…}, name: "Return to Karazhan: Upper", id: 234}
12
:
{key: {…}, name: "Seat of the Triumvirate", id: 239}
*/
