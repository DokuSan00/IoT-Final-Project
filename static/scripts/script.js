function setTextMode(id, isOn) {
    $(id).html(isOn ? "Turn Off" : "Turn On");
}

function setShadowLight(name) {
    if (!name) return;

    $(name).toggleClass("off"); // flip mode
    $(name).toggleClass("on") // flip mode 
}

var properties = {
    //div - method - button
    light : [".light-div", "/set_light", "#light-btn"],
    motor : [".motor-div", "/set_motor", "#motor-btn"]
}

function toggleMode(name) {
    const e = properties[name];

    setShadowLight(e[0]);
    const on = $(e[0]).hasClass("on");

    // $.post(e[1], {state: on});
    setTextMode(e[2], on);
}

// const mail_cd_to_set = 60; //based cd, 3mins in second
// var cur_mail_cd = 10; //the cd that will be reduce
var data = {};
var motorState = false;
var emailSent = false;

setInterval(() => {
    $.get('/get_data', function(res) {
        pasteData(res);
    });

    //update data on dashboard
    $("#temp-text").html(data.temp);
    $("#humid-text").html(data.humid);

    $.post('/read_motor_mail', function(res) {
        if (!res.response)
            return;
        if (motorState == res.response)
            return;
        motorState = res.response;
        $.post('/set_motor', {state: motorState})
    });
        
    // console.log(cur_mail_cd);
    if (data.temp <= 24) { // turn off motor when temp <= 24
        if (motorState != 0) {
            $.post('/set_motor', {state: 0});
            motorState = 0;
        }
    }

    // if (--cur_mail_cd > 0) return;
    // cur_mail_cd = mail_cd_to_set;

    if (emailSent) return;
    if (data.temp > 24) {
        //send mail asking turn on motor if temp > 24
        $.post('/send_motor_mail', {temp: data.temp});
    }
    
}, 1000);

function pasteData(res) {
    data = res
}