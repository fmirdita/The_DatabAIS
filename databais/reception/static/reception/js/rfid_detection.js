var patt = new RegExp("[0-9]{3}:[0-9]{8}");
function checkScan() {
    rfid = document.getElementById("id_rfid").value;
    console.log(rfid);
    if (patt.test(rfid)) {
        document.getElementById("scan_field").submit();
    }
}
function clearScanField() {
    scan = document.getElementById("id_rfid").value;
}
scan_field = document.getElementById('id_rfid');
scan_field.setAttribute('onkeyup', 'checkScan()');
scan_field.focus();
// setInterval(clearScanField, 5000);