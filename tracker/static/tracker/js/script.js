$(document).ready(function ($) {
    $(".table-row-clickable").click(function () {
        window.document.location = $(this).data("href");
    });
});

function addForm(){
    form = document.getElementsByClassName("form__railcar")
}