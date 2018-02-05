

function back_prev() {
    window.history.back();
}

function warning_text(obj, second) {
    obj.html("还有 <code>" +  second  + "</code> S回到上一页")
}
function write(delay_time) {
    var count = 5;
    var timer = null;
    function print () {
        clearTimeout(timer);
        warning_text(delay_time, count--);
        timer = setTimeout(function () {
            print();
        }, 1000);
        if(count<0) {
            clearTimeout(timer);
            back_prev();
        }
    }

    timer = setTimeout(function () {
        print();
    }, 100);
}
$(function () {
    var delay_time = $("#delay_time");
    write(delay_time);
});
