$(document).ready(function ($) {
    $(".table-row-clickable").click(function () {
        window.document.location = $(this).data("href");
    });
});