function toggleLight() {
    var e = ".light-toggle-div";

    $(e).toggleClass("off");
    $(e).toggleClass("on");

    $("#light-toggle-btn").html($(e).hasClass("on") ? "Light On" : "Light Off");
        
    $.post("/toggle_light");
} 

var mail_cd_to_set = 120; //based cd, 2mins in second
var cur_mail_cd = mail_cd_to_set //the cd that will be reduce

$.post('/read_motor_mail');

setInterval(() => {
    $.get('/get_data', function(data) {
        //update data on dashboard
        $("#temp-text").html(data.temp);
        $("#humid-text").html(data.humid);
        // reduce cd, if cd = 0 execute under
        // $.post('/motor_mail', {temp: data.temp});
        console.log(cur_mail_cd);
        if (--cur_mail_cd > 0) return; 

        if (data.temp > 24) {
            // $.post('/motor_mail', {temp: data.temp});
            cur_mail_cd = mail_cd_to_set;
        }

    });
    
}, 1000); //execute the above every 1s