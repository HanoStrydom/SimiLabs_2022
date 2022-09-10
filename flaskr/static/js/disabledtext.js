$(function () {
    $("input[name='algorithm']").click(function () {
        if ($("#chkSubstring").is(":checked")) {
            $("#txtSubstring").removeAttr("disabled");
            $("#txtSubstring").focus();
        } else {
            $("#txtSubstring").attr("disabled", "disabled");
        }
    });
});