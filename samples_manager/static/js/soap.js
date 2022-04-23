$(function () {
    $('.soap').click(function (event) {
        console.log('Soap request');

        try {
            xmlhttp = new XMLHttpRequest();
        } catch (e) {
            xmlhttp = new ActiveXObject('Microsoft.XMLHTTP');
        }

        xmlhttp.open('POST', 'placeholder.url.com', true);

        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState != 4) return;
            if (!xmlhttp.status || xmlhttp.status == 200)
                console.log(xmlhttp.responseText);
            else alert('Request failed!');
        };
        xmlhttp.send(
            '<soapenv:Envelope xmlns:soapenv="placeholder.url.com" xmlns:wsh="placeholder.url.com">' +
            '<soapenv:Header/>' +
            '<soapenv:Body>' +
            '<wsh:readEquipment>' +
            '<equipmentCode>PXXISET001-CR002706</equipmentCode>' +
            '<credentials>' +
            '<password>password</password>' +
            '<username>username</username>' +
            '</credentials>' +
            '<sessionID></sessionID>' +
            '</wsh:readEquipment>' +
            '</soapenv:Body>' +
            '</soapenv:Envelope>'
        );
    });
});

//no soap yet
