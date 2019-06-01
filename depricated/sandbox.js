const _ = require('lodash');
const data = {
    'tank': {
        'name': 'moonseeker',
        'id': 423434
    }
};

const data2 = [
    {
        'name': 'me'
    },
    {
        'name': 'works'
    },
    {}
];
//_.get(keystoneAffixes, keystoneAffixes[0].name, '');
console.log(data.tank)

console.log(_.get(data2, ['1', 'name'], 'fail'));

// Mythics 4800
// Players 1486
