function toggleLight() {
    var e = ".light-toggle-div";
    $(e).toggleClass("off");
    $(e).toggleClass("on");

    if ($(e).hasClass("on"))
        $("#light-toggle-btn").html("Light On");
    if ($(e).hasClass("off"))
        $("#light-toggle-btn").html("Light Off");
        
        $.post("/toggle_light");
}