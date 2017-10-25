$(document).ready(function ($) {
    $('.table-row-clickable').click(function () {
        window.document.location = $(this).data("href");
    });

    $('.table-col-nowrap').each(function () {
        if ($(this).text()) $(this).attr('title', $(this).text());
    });

    setTimeout(function () {
        window.location.reload();
    }, 60000);
});

// function addForm() {
//     form = document.getElementsByClassName("form__railcar")
// }