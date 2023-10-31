let motor_self_turned = false;
function isManual() {
    motor_self_turned = getMode(properties['motor'][0]) * true;
}

function setTextMode(id, isOn) {
    $(id).html(isOn ? "Turn Off" : "Turn On");
}

function setShadowLight(name) {
    if (!name) return;

    $(name).toggleClass("off"); // flip mode
    $(name).toggleClass("on") // flip mode
}

function setIconShadow(name) {
    if (!name) return;
    
    $(name).toggleClass("icon-shadow-off");
    $(name).toggleClass("icon-shadow-on");
}

const properties = {
    //div - method - button - icon
    light : [".light-div", "/set_light", "#light-btn", "#light-icon"],
    motor : [".motor-div", "/set_motor", "#motor-btn", "#fan-icon"]
}

function getMode(name) {
    return $(name).hasClass("on");
}

function setDeviceMode(url, newState) {
    $.post(url, {state: newState});
}

function toggleMode(name) {
    const e = properties[name];

    setShadowLight(e[0]);
    setIconShadow(e[3])

    const on = getMode(e[0]);

    //set button text
    setTextMode(e[2], on);

    //set RPi device mode
    setDeviceMode(e[1], on);

    if (name == 'motor') {
        setAnimation(e[3], 'rotate');
    }

}

// const mail_cd_to_set = 60; //based cd, 3mins in second
// var cur_mail_cd = 10; //the cd that will be reduce
let data = {temp: 0, humid: 0};
let emailSent = false;

setInterval(() => {
    $.get('/get_data', function(res) {
        if (!res)
            return;
        pasteData(res);
    });

    //update data on dashboard
    $("#temp-text").html(data.temp); renderHotTempShadow();
    $("#humid-text").html(data.humid); renderHumidityShadow();

    //other tasks
    motor_state = getMode(properties['motor'][0]);
    // $.post('/read_motor_mail', function(res) {
    //     motorState = motor_state;
    //     if (!res.response)
    //         return;
    //     if (motorState == res.response)
    //         return;
    //     toggleMode('motor');
    // });

    if (data.temp <= 24) {
        if (!motor_self_turned) { // turn off motor when temp <= 24
            motorState = motor_state;
            if (motorState != 0) {
                toggleMode('motor');
            }
            emailSent = false;
        }
    }

    // if (--cur_mail_cd > 0) return;
    // cur_mail_cd = mail_cd_to_set;
    if (!motor_state && !emailSent && data.temp > 24) {
        // send mail asking turn on motor if temp > 24
        try {
            // $.post('/send_motor_mail', {temp: data.temp});
            emailSent = true;
        } catch {
        }
    }
}, 1000);

function pasteData(res) {
    data = res;
}

function setAnimation(name, animation) {
    $(name).toggleClass(animation);
}

hot = false;
const maxInvertTemp = 26
const minInvertTemp = 20

const maxInvert = 80
const tempSlope = (maxInvertTemp - minInvertTemp) / maxInvert

function renderHotTempShadow() {
    const invert = (clamp(data.temp, minInvertTemp, maxInvertTemp) - minInvertTemp) / tempSlope;
    
    $("#temp-icon").css({'filter': 
        `saturate(500%) 
        contrast(800%) 
        brightness(500%) 
        invert(${invert}%) 
        sepia(50%) 
        hue-rotate(320deg) 
        drop-shadow(0px 0px 5px rgba(255, 10, 10, ${invert/100})`
    });

    if (hot == (data.temp > 24)) return;
    hot = !hot;
    $(".temp-div").toggleClass("hot-temp-shadow");
}

const maxInvertHumid = 70;
const minInvertHumid = 10;
const humidSlope = (maxInvertHumid - minInvertHumid) / maxInvert;

function renderHumidityShadow() {
    const invert = (clamp(data.humid, minInvertHumid, maxInvertHumid) - minInvertHumid) / humidSlope;
    $("#humid-icon").css({'filter': 
        `saturate(500%) 
        contrast(800%) 
        brightness(500%) 
        invert(${((invert > 10) * invert)}%)
        sepia(50%) 
        hue-rotate(120deg) 
        drop-shadow(0px 0px 5px rgba(10, 255, 235, ${invert/100}))`
    });
}

function clamp(val, min, max) {
    return Math.max(Math.min(val, max), min);
}