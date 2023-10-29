var motor_self_turned = false;
function isManual() {
    motor_self_turned = !motor_self_turned;
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

var properties = {
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
var data = {};
var emailSent = false;

setInterval(() => {
    $.get('/get_data', function(res) {
        pasteData(res);
    });

    //update data on dashboard
    $("#temp-text").html(data.temp); toggleHotTempShadow();
    $("#humid-text").html(data.humid);

    //other tasks
    $.post('/read_motor_mail', function(res) {
        motorState = getMode(properties['motor'][0]);
        if (!res.response)
            return;
        if (motorState == res.response)
            return;
        toggleMode('motor');
    });

    if (data.temp <= 24) {
        if (!motor_self_turned) { // turn off motor when temp <= 24
            motorState = getMode(properties['motor'][0]);
            if (motorState != 0) {
                toggleMode('motor');
            }
            emailSent == false;
        }
    }

    // if (--cur_mail_cd > 0) return;
    // cur_mail_cd = mail_cd_to_set;
    if (!emailSent && data.temp > 24) {
        // send mail asking turn on motor if temp > 24
        try {
            $.post('/send_motor_mail', {temp: data.temp});
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
function toggleHotTempShadow() {
    if (hot == (data.temp > 24)) return;
    hot = !hot;
    $(".temp-div").toggleClass("hot-temp-shadow");
    
    $("#temp-icon").toggleClass("icon-shadow-off");
    $("#temp-icon").toggleClass("icon-hot-temp-shadow-on");
}