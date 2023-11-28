
const BarnowlHci = require('barnowl-hci');

let barnowl = new BarnowlHci();

barnowl.addListener(BarnowlHci.SocketListener, {});
const d = {};

barnowl.on('raddec', function (raddec) {
    const f = raddec.toFlattened();
    d[f.transmitterId] = f.rssi;
});

setInterval(() => {
    console.log(d)
}, 2000);