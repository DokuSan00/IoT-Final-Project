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


let updating_client = false;
function is_client_updating(state) {
    updating_client = state;
}
function update_client_setting() {
    let user = document.getElementById('username').value;
    let tempVal = document.getElementById('fav_temp').value;
    // let humidVal = document.getElementById('fav_humid').value;
    let humidVal = 40
    let lightVal = document.getElementById('fav_lightInt').value;

    is_client_updating(true);
    $.post("/update_client", { username: user, temp: tempVal, humid: humidVal, light: lightVal }, function(res, status) {
        if (parseInt(res))
            showAlert('Updated Successfull');
        else
            showAlert('Updated Failed');

        setTimeout(is_client_updating(false), 1000);
    });
}

// here is the data for html
let data = { temp: 0, light: 0, humid: 0 };
let motorEmailSent = false;
let lightEmailSent = false;

let client_setting = {}
let currentTime = "--:--:--"

function get_date() {
    date = new Date();
    return new Date(
        date.toLocaleString('en-US', {
            timeZone: "America/New_York"
        })
    );
}

function update_dashboard_time() {
    date = get_date()
    const pad = 2;
    const hr = date.getHours().toString();
    const mi = date.getMinutes().toString();
    const sc = date.getSeconds().toString();

    const day = date.getDate();
    const month = date.getMonth()+1;
    const year = date.getFullYear();

    currentTime = `
        ${hr.padStart(pad, '0')}:${mi.padStart(pad, '0')}:${sc.padStart(pad, '0')}
    `;
    $("#time-text").html(currentTime);

    $("#date-text").html(`${day}-${month}-${year}`);
}

prev_client = {}
function set_user(client) {
    if (JSON.stringify(client) == JSON.stringify(prev_client))
        return;
    if (JSON.stringify(client) == JSON.stringify(client_setting))
        return;

    setTimeout(() => {
        prev_client = client_setting;
    }, 1500);
    client_setting = client;

    update_animation_threshold()
    update_user_dashboard();

    // showAlert("Welcome " + client.username + " !")
}

function get_data() {
    $.get('/get_data', function (res) {
        pasteData(res);
        set_user(res.client_setting)
    });
}

// Do every 1s
setInterval(() => {
    update_dashboard_time()

    //get breadboard data from app.py named get_data every other second, and call pasteData callback function
    if (!updating_client)
        get_data();

    //update values of the dashboard
    $("#temp-text").html(data.temp);
    $("#humid-text").html(data.humid);
    $("#lightInt-text").html(data.light);

    renderIconShadow();

    motor_email_handler();
    light_email_handler();

}, 500)


function update_user_dashboard() {
    console.log(client_setting);
    document.getElementById('username').value = client_setting.username;
    document.getElementById('fav_temp').value = client_setting.fav_temp;
    // document.getElementById('fav_humid').value = client_setting.fav_humid;
    document.getElementById('fav_lightInt').value = client_setting.fav_light_intensity;

    return;
}

function light_email_handler() {
    if (properties['light']['isManual']) return;
    
    lightState = getMode(properties['light']['div']);
    if (data.light >= client_setting.fav_light_intensity) {
        lightEmailSent = 0;
        if (lightState) {
            toggleMode('light');
        }
        return;
    }
    if (lightState) return;

    //Getting current date and time
    var content = "The Light is ON at " + currentTime;

    //Send email to say that the light is on
    if (lightEmailSent) return;
    lightEmailSent = 1;
    $.post('/send_mail', {
        subject: "Hello from automatic service",
        content: content
    }, function (data, status) {
        if (status == 'success')
            showAlert("Note: Light notification email has been sent");
        toggleMode('light');
    });

}

function showAlert(alertMessage) {
    const duration = 7000; //7s
    const message = alertMessage;
    const wrapper = document.createElement('div');

    const alertDiv = document.getElementById('alert-notif');
    const appendAlert = () => {
        wrapper.innerHTML = `<div class="alert-custom" role="alert">${message}</div>`;
        alertDiv.prepend(wrapper);   
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

    if (data.temp < client_setting.fav_temp) {
        if (!properties['motor']['isManual']) { // turn off motor when temp <= 24
            if (motor_state != 0) {
                toggleMode('motor');
            }
            motorEmailSent = false;
        }
    }
    if (!motor_state && !motorEmailSent && data.temp > client_setting.fav_temp) {
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
}

//Rendering + Animation
function setAnimation(name, animation) {
    $(name).toggleClass(animation);
}

hot = false;
const icons = ['temp', 'humid', 'light'];
const icon_properties = {
    maxInvert: 80,
    temp: {
        icon: "#temp-icon",
        minVal: client_setting.fav_temp - 10,
        maxVal: client_setting.fav_temp + 4,
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
        minVal: client_setting.fav_light_intensity - 100,
        maxVal: client_setting.fav_light_intensity + 200,
        hue_rotation: 10,
        red: 255,
        green: 252,
        blue: 127,
    }
};

function update_animation_threshold() {
    icon_properties['temp']['minVal'] = client_setting.fav_temp - 10;
    icon_properties['temp']['maxVal'] = client_setting.fav_temp + 10;
    icon_properties['light']['minVal'] = client_setting.fav_light_intensity - 100;
    icon_properties['light']['maxVal'] = client_setting.fav_light_intensity + 200;
    calcAllSlope();
}

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

    if (hot == (data.temp > client_setting.fav_temp)) return;
    hot = !hot;
    $(".temp-div").toggleClass("hot-temp-shadow");
}

function clamp(val, min, max) {
    return Math.max(Math.min(val, max), min);
}
