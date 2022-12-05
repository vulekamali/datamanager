$(document).ready(function () {
    prepareUIElements();
});

function prepareUIElements() {
    document.getElementById('eqprsfileupload_form').addEventListener('submit', formSubmit);

    enableDisableElement('id_user', true);
}

function formSubmit() {
    enableDisableElement('id_user', false);
}

function enableDisableElement(id, enable) {
    if (document.getElementById(id)) {
        document.getElementById(id).disabled = enable;
    }
}