window.onload(() => {
    
})

async function get_client() {
    // client = fetch("/get_data")
}

function isManual(component) {
    properties[component]['isManual'] = getMode(properties[component]['div']) * true;
}

const properties = {
    //div - method - button - icon - isManualState
    light: {
        div: ".light-div",
        func: "/set_light",
        btn: "#light-btn",
        icon: "#light-icon",
        isManual: false
    },
    motor: {
        div: ".motor-div",
        func: "/set_motor",
        btn: "#motor-btn",
        icon: "#fan-icon",
        isManual: false
    }
}

function getMode(name) {
    return $(name).hasClass("on");
}

function setDeviceMode(url, newState) {
    $.post(url, { state: newState });
}

function toggleMode(name) {
    const e = properties[name];

    //set light + icon render
    $(e['div']).toggleClass("off"); // flip mode
    $(e['div']).toggleClass("on") // flip mode

    $(e['icon']).toggleClass("icon-shadow-off");
    $(e['icon']).toggleClass("icon-shadow-on");

    const on = getMode(e['div']);

    //set button text
    $(e['btn']).html(on ? "Turn Off" : "Turn On");

    //set RPi device mode
    setDeviceMode(e['func'], on);

    //special effect for Fans: rotate 
    if (name == 'motor') {
        setAnimation(e['icon'], 'rotate');
    }

}

// const mail_cd_to_set = 60; //based cd, 3mins in second
// var cur_mail_cd = 10; //the cd that will be reduce
// here is the data for html
let data = { temp: 0, light: 0, humid: 0, username: "" };
let motorEmailSent = false;
let lightEmailSent = false;
let user_setting = {}


// Do every 0.5s
setInterval(() => {
    //get breadboard data from app.py named get_data every other second, and call pasteData callback function
    // $.get('/get_data', function (res) {
    //     pasteData(res);
    // });

    //update values of the dashboard
    $("#temp-text").html(data.temp);
    $("#humid-text").html(data.humid);
    $("#lightInt-text").html(data.light);

    //values of the updateProfileValues
    // $("#username_label").html(data.username);

    //Style?
    // renderIconShadow();

    // //Not quite understand
    // motor_email_handler();
    // light_email_handler();
    // updateProfileValues();

}, 500)

function light_email_handler() {
    if (properties['light']['isManual']) return;
    if (data.light >= 400) {
        lightEmailSent = 0;
        return;
    }
    lightState = getMode(properties['light']['div']);
    if (lightState) return;

    //Getting current date and time
    var currentdate = new Date();
    var content = "The Light is ON at " + currentdate.getHours() + ":" + currentdate.getMinutes() + " .";

    //Send email to say that the light is on
    if (lightEmailSent) return;
    lightEmailSent = 1;
    // $.post('/send_mail', {
    //     subject: "Hello from automatic service",
    //     content: content
    // }, function (data, status) {
    //     if (status == 'success')
    //         showAlert("Note: Light notification email has been sent");
    //     toggleMode('light');
    // });

}

function showAlert(alertMessage) {
    const duration = 10000;
    const message = alertMessage;
    const wrapper = document.createElement('div');

    const alertDiv = document.getElementById('alert-notif');
    const appendAlert = () => {
        wrapper.innerHTML = `<div class="alert-custom" role="alert">${message}</div>`;
        alertDiv.append(wrapper);   
    }
    appendAlert();

    setTimeout(function () {
        wrapper.parentNode.removeChild(wrapper);
    }, duration);
}

function motor_email_handler() {
    motor_state = getMode(properties['motor']['div']);
    $.post('/read_motor_mail', function(res) {
        motorState = motor_state;
        if (!res.response)
            return;
        if (motorState == res.response)
            return;
        toggleMode('motor');
    });

    if (data.temp <= 24) {
        if (!properties['motor']['isManual']) { // turn off motor when temp <= 24
            if (motor_state != 0) {
                toggleMode('motor');
            }
            motorEmailSent = false;
        }
    }
    if (!motor_state && !motorEmailSent && data.temp > 24) {
        // send mail asking turn on motor if temp > 24
        try {
            mailContent = "The current temperature is " + data.temp + ". Would you like to turn on the fan?";
            $.post('/send_mail', {
                subject: "Hello from automatic service - Fans Service",
                content: mailContent
            });
            motorEmailSent = true;
        } catch {
        }
    }
}

function pasteData(res) {
    if(!res) return
    data.light = res.light ?? data.light;
    data.temp = res.temp ?? data.temp;
    data.humid = res.humid ?? data.humid;
    data.username = res.username ?? data.username;
    console.log(res);
}

function setAnimation(name, animation) {
    $(name).toggleClass(animation);
}

hot = false;
const icons = ['temp', 'humid', 'light'];
const icon_properties = {
    maxInvert: 80,
    temp: {
        icon: "#temp-icon",
        minVal: 20,
        maxVal: 26,
        hue_rotation: 320,
        red: 255,
        green: 10,
        blue: 10,
    },
    humid: {
        icon: "#humid-icon",
        minVal: 10,
        maxVal: 70,
        hue_rotation: 120,
        red: 10,
        green: 255,
        blue: 235,
    },
    light: {
        icon: "#lightInt-icon",
        minVal: 100,
        maxVal: 700,
        hue_rotation: 10,
        red: 255,
        green: 252,
        blue: 127,
    }
};

calcAllSlope();
function calcAllSlope() {
    function calcSlope(icon) {
        prop = icon_properties[icon];
        icon_properties[icon]['slope'] = (prop['maxVal'] - prop['minVal']) / icon_properties['maxInvert'];
    }
    icons.forEach(calcSlope)
}

function renderIconShadow() {
    icons.forEach(render);
    function render(icon) {
        const prop = icon_properties[icon];
        const val = (icon == 'light') * data.light + (icon == 'temp') * data.temp + (icon == 'humid') * data.humid;

        const invert = (clamp(val, prop['minVal'], prop['maxVal']) - prop['minVal']) / prop['slope'];

        $(prop['icon']).css({
            'filter':
            `
            contrast(300%)
            saturate(500%)
            invert(${(invert)}%)
            sepia(80%) 
            hue-rotate(${prop['hue_rotation']}deg)
            drop-shadow(0px 0px 5px rgba(${prop['red']}, ${prop['green']}, ${prop['blue']}, ${invert / 100 * 1.25}))
            brightness(${invert * 1.4 / 93})
            `
        });
    }

    if (hot == (data.temp > 24)) return;
    hot = !hot;
    $(".temp-div").toggleClass("hot-temp-shadow");
}

function clamp(val, min, max) {
    return Math.max(Math.min(val, max), min);
}

function updateProfileValues(){

}