function toggleLight() {
    var e = ".light-toggle-div";

    $(e).toggleClass("off");
    $(e).toggleClass("on");

    $("#light-toggle-btn").html($(e).hasClass("on") ? "Light On" : "Light Off");
        
    $.post("/toggle_light");
} 

// setInterval(() => {
//     $.get('/get_data', function(data) {
//         $("#temp-text").html(data.temp);
//         $("#humid-text").html(data.humid);
//     });
    
// }, 1000);


setInterval(() => {
    $.post('/motor_mail');
}, 10000);