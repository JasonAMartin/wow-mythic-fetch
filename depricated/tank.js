const axios = require("axios");

const dungeons = [197, 198, 199, 200, 206, 207, 208, 209, 210, 227, 233, 234, 239];
/*
    57 = illidan
    5 = proudmoore
    1566 = area 52
    61 = Zul Jin
    76 = Sargeras
*/
const servers = [5, 57, 1566, 61, 76]
const maxRank = 6; // 1 - 100 = max ranking to count
const classCounts = {
    'Druid': 0,
    'Monk': 0,
    'Paladin': 0,
    'Warrior': 0,
    'DemonHunter': 0,
    'DeathKnight': 0
}


/*
TOP 30:
{ Druid: 185, Monk: 101, Paladin: 207, Warrior: 100, DemonHunter: 282, DeathKnight: 516 }

TOP 20:
{ Druid: 109, Monk: 68, Paladin: 141, Warrior: 60, DemonHunter: 209, DeathKnight: 372 }


TOP 10:
{ Druid: 42, Monk: 29, Paladin: 74, Warrior: 31, DemonHunter: 119, DeathKnight: 185 }

TOP 5:
{ Druid: 13, Monk: 17, Paladin: 35, Warrior: 14, DemonHunter: 66, DeathKnight: 95 }

*/

function fetchData(realm, dungeon) {

    const url =
    `https://us.api.battle.net/data/wow/connected-realm/${realm}/mythic-leaderboard/${dungeon}/period/602?namespace=dynamic-us&locale=en_US&access_token=j6945863mx3g8zdr59kx5tee`;
  axios
    .get(url)
    .then(response => {
        var groups = response.data.leading_groups; // array
        for (let index = 0; index < groups.length; index++) {
          var currentGroup = groups[index];
          var ranking = currentGroup.ranking;
          var members = currentGroup.members; //array
  
          // iterate members
          for (let pointer = 0; pointer < members.length; pointer++) {
              /*
               66 - Paladin: Protection
                73 - Warrior: Protection
                104 - Druid: Guardian
                250 - Death Knight: Blood
                268 - Monk: Brewmaster
                581 - Demon Hunter: Vengeance

              */
              var spec = members[pointer].specialization.id;
  
              if (spec === 66 && ranking < maxRank) classCounts['Paladin']++;
              if (spec === 73 && ranking < maxRank) classCounts['Warrior']++;
              if (spec === 104 && ranking < maxRank) classCounts['Druid']++;
              if (spec === 250 && ranking < maxRank) classCounts['DeathKnight']++;
              if (spec === 268 && ranking < maxRank) classCounts['Monk']++;
              if (spec === 581 && ranking < maxRank) classCounts['DemonHunter']++;              
          }
  
        }
  
        console.log('Final counts: ', classCounts);
  
    })
    .catch(error => {
      //console.log(error);
    });
}

// iterate servers and dungeons within them
for (key = 0; key < servers.length; key++) {
    for (index = 0; index < dungeons.length; index++) {
        fetchData(servers[key], dungeons[index]);    
    }
}


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
