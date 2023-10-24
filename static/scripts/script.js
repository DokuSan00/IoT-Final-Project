function toggleLight() {
    var e = ".light-toggle-div";

    $(e).toggleClass("off"); // flip mode
    $(e).toggleClass("on"); // flip mode 
    
    var on = $(e).hasClass("on");

    $.post("/toggle_light", {isOn: on});
    $("#light-toggle-btn").html(on ? "Light On" : "Light Off");
} 

var mail_cd_to_set = 15; //based cd, 2mins in second
var cur_mail_cd = mail_cd_to_set; //the cd that will be reduce
var data = {}


setInterval(() => {
    $.get('/get_data', function(res) {
        pasteData(res); //get data out of callback
    });

    //update data on dashboard
    $("#temp-text").html(data.temp);
    $("#humid-text").html(data.humid);

    $.post('/read_motor_mail');
    if (data.temp <= 24)
        
    //execute under when timer hit 0
    if (--cur_mail_cd > 0) return;
    cur_mail_cd = mail_cd_to_set; //reset timer

    if (data.temp > 24) {
        //send mail asking turn on motor if temp > 24
        // $.post('/send_motor_mail', {temp: data.temp});
    }
    
}, 1000); //execute the above every 1s

function pasteData(res) {
    data = res
}