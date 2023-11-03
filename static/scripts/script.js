function isManual(component) {
    properties[component]['isManual'] = getMode(properties[component][0]) * true;
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
    //div - method - button - icon - isManualState
    light : {
        div: ".light-div", 
        func: "/set_light", 
        btn: "#light-btn", 
        icon: "#light-icon", 
        isManual: false
    },
    motor : {
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
    $.post(url, {state: newState});
}

function toggleMode(name) {
    const e = properties[name];

    //set light + icon render
    setShadowLight(e['div']);
    setIconShadow(e['icon'])

    const on = getMode(e['div']);

    //set button text
    setTextMode(e['btn'], on);

    //set RPi device mode
    setDeviceMode(e['func'], on);

    //special effect for Fans: rotate 
    if (name == 'motor') {
        setAnimation(e['icon'], 'rotate');
    }

}

// const mail_cd_to_set = 60; //based cd, 3mins in second
// var cur_mail_cd = 10; //the cd that will be reduce
let data = {temp: 0, light: 0, humid: 0};
let motorEmailSent = false;
let lightEmailSent = false;

setInterval(() => {
    $.get('/get_data', function(res) {
        if (!res)
            return;
        pasteData(res);
    });

    console.log(data);

    //update data on dashboard
    $("#temp-text").html(data.temp);
    $("#humid-text").html(data.humid);
    $("#lightInt-text").html(data.light);

    renderIconShadow();

    motor_email_handler();
    light_email_handler();

}, 1000);

function light_email_handler() {
    if (properties['light']['isManual']) return;
    if (data.light >= 400) return;
    lightState = getMode(properties['light']['div']);
    if (lightState) return;
    
    // toggleMode('light');

    //do your code here v
}

function motor_email_handler() {
    motor_state = getMode(properties['motor']['div']);
    // $.post('/read_motor_mail', function(res) {
    //     motorState = motor_state;
    //     if (!res.response)
    //         return;
    //     if (motorState == res.response)
    //         return;
    //     toggleMode('motor');
    // });

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
            // $.post('/send_motor_mail', {
            //     subject: "Hello from automatic service - Fans Service",
            //     content: mailContent
            // });
            motorEmailSent = true;
        } catch {
        }
    }
}

function pasteData(res) {
    data.light = res.light ?? data.light;
    data.temp = res.temp ?? data.temp;
    data.humid = res.humid ?? data.humid;
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
        func: "getTemp()",
        minVal: 20,
        maxVal: 26,
        hue_rotation: 320,
        red: 255,
        green: 10,
        blue: 10,
    },
    humid: {
        icon: "#humid-icon",
        func: "getHumid()",
        minVal: 10, 
        maxVal: 70,
        hue_rotation: 120,
        red: 10,
        green: 255,
        blue: 235,
    },
    light: {
        icon: "#lightInt-icon",
        func: "getLight()",
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
        const val = eval(prop['func']);

        const invert = (clamp(val, prop['minVal'], prop['maxVal']) - prop['minVal']) / prop['slope'];

        $(prop['icon']).css({'filter': 
            `
            contrast(300%)
            saturate(500%)
            invert(${(invert)}%)
            sepia(80%) 
            hue-rotate(${prop['hue_rotation']}deg)
            drop-shadow(0px 0px 5px rgba(${prop['red']}, ${prop['green']}, ${prop['blue']}, ${invert/100 * 1.25}))
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

function getTemp() {
    return data.temp;
}

function getHumid() {
    return data.humid;
}

function getLight() {
    return data.light;
}