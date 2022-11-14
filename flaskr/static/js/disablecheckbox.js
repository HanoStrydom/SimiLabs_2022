$(function() {
    $("input[name='ExtensiveText']").click(function () {
        if ($("#ischecked").is(":checked")) {
            document.getElementById("extensiveBox").disabled=false;
        } else {
            document.getElementById("extensiveBox").disabled=true;
        }
    });
});