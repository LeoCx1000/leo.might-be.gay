for (let elem of document.querySelectorAll("h2 > a")) {
    elem.addEventListener("click", function () {
        navigator.clipboard.writeText(elem.href);

    });
}