console.log('loaded irradiations.js');
if (refreshInterval)
    clearInterval(refreshInterval);
if (secTimeout)
    clearTimeout(secTimeout);
var refreshInterval = undefined;
var secTimeout = undefined;
var refreshTimerRate = 500;
var concurrencyTimerRate = Math.round(refreshTimerRate / 2);
var updateSecTimerRate = 1000;
var updateSecActive = true;
var noConcurrentJobs = true;
var lastRequest = undefined;
$(function () {
    /**
    * Handler for display irradiation form button.
    */
    var loadForm = function () {
        // Needed to not have checkUpdateSec interfere with database.
        setNoConcurrentJobs(false);
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var btn = $(this);
        var url = btn.attr('data-url');
        var modalID = '#modal-irradiation';
        var type = 'get';
        var dataType = 'json';
        var data = serialized_checkboxes;
        var beforeSend = function () {
            $(modalID).modal({
                autofocus: false,
                closable: false
            });
        };
        var success = function (data) {
            $(modalID + ' .modal-content').html(data.html_form);
            if (data.alert_message)
                alert(data.alert_message);
            // Needed to not have checkUpdateSec interfere with database.
            setNoConcurrentJobs(true);
        };
        formRequest(url, modalID, type, dataType, beforeSend, success, undefined, data);
    };

    /**
    * Handler for submit irradiation form button.
    */
    var saveIrradiationForm = function (e, self) {
        // Needed to not have checkUpdateSec interfere with database.
        setNoConcurrentJobs(false);
        setLoaderState('loader')
        self = typeof self !== 'undefined' ? self : this;
        e.preventDefault();
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var form = $(self);
        var url = form.attr('action');
        var modalID = '#modal-irradiation';
        var type = form.attr('method');
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var success = function (data) {
            if (data.form_is_valid) {
                // Replace partial template
                $('#partial-template').html(data.html_list);
            } else {
                $(modalID + ' .modal-content').html(data.html_form);
            }
            if (data.alert_message)
                alert(data.alert_message);
            // Needed to not have checkUpdateSec interfere with database.
            setNoConcurrentJobs(true);
        };
        var error = function(xhr){
            if (xhr.status == 504){
                lastRequest.abort();
                setNoConcurrentJobs(true);
            }
        };
        // Send request only if no other request is in process.
        if (!updateSecActive) {
            setTimeout(function() {saveIrradiationForm(e, self);}, concurrencyTimerRate);
        } else { 
            setLoaderState('inactive');
            lastRequest = 
                formRequest(url, modalID, type, dataType, undefined, success, error, data);
        }
    };

    /**
     * Enables/Disables sec updating.
     */
    var setUpdateSec = function (bool) {
        updateSecActive = bool;
    }

    /**
     * Enables/Disables sec updating if concurrent jobs are present.
     */
     var setNoConcurrentJobs = function (bool) {
        noConcurrentJobs = bool;
    }

    /**
     * Updates sec value of visible irradiations.
     */
    var updateSec = function (ids) {
        var btn = $('#irradiation-set-beam-status');
        var url = btn.attr('sec-url');
        var type = 'get';
        var dataType = 'json';
        var data = serializeCheckedElements(ids);
        var withModal = false;
        var withLoader = false;
        var withErrorMessage = false;
        var success = function (data) {
            if (data.form_is_valid) {
                // Replace sec values
                var irradiations = data.irradiation_data;
                for (var i = 0; i < irradiations.length; i++){
                    if (irradiations[i]['in_beam']){
                        row = $($('#irradiation-' + irradiations[i]['pk'])
                            .parent().parent()[0])
                        if (row.length > 0) {
                            row.find('.sec')[0]. innerText = 
                                irradiations[i]['sec'];
                            row.find('.factor-value')[0]. innerText = 
                                irradiations[i]['factor_value'];
                            row.find('.estimated-fluence')[0]. innerText = 
                                irradiations[i]['estimated_fluence'];
                            row.find('.updated-at')[0]. innerText = 
                                irradiations[i]['updated_at'];
                        }
                    }
                }
                clearTimeout(secTimeout);
                // Execute updateSec after some margin time.
                secTimeout = setTimeout(function () {
                    setUpdateSec(true);}, updateSecTimerRate);
            }
            if (data.alert_message)
                alert(data.alert_message);
        };
        var error = function(xhr){
            if (xhr.status == 504){
                lastRequest.abort();
                alert('SEC calculation is taking too long (> 30 seconds). ' + 
                    'To see updated results please reduce the number of ' + 
                    'elements per page.');
                setNoConcurrentJobs(true);
                setUpdateSec(true);
            }
        };
        lastRequest = 
            formRequest(url, undefined, type, dataType, undefined, success,
                error, data, withModal, withLoader, withErrorMessage);
    }

    /**
     * Creates CSV file with table values.
     */
    var downloadCSV = function (csv, filename) {
        var csvFile;
        var downloadLink;

        // CSV file.
        csvFile = new Blob([csv], { type: "text/csv" });

        // Download link.
        downloadLink = document.createElement('a');

        // File name.
        downloadLink.download = filename;

        // Create a link to the file.
        downloadLink.href = window.URL.createObjectURL(csvFile);

        // Hide download link.
        downloadLink.style.display = 'none';

        // Add the link to DOM.
        document.body.appendChild(downloadLink);

        // Click download link.
        downloadLink.click();
    }

    /**
     * Exports dosimetry results as CSV file.
     */
    var exportTableToCSV = function () {
        // Activate loader
        $('#loader').addClass('active');

        var csv = [];
        var filename = 'dosimetry_results.csv';
        var allRows = document.querySelectorAll('table tr');

        var rows = [];
        for (var i = 0; i < allRows.length; i++) {
            var isChecked = (allRows[i].children[0].children[0].checked || i == 0);
            if (isChecked)
                rows.push(allRows[i]);
        }

        for (var i = 0; i < rows.length; i++) {
            var row = [], cols = rows[i].querySelectorAll('td, th');

            for (var j = 1; j < cols.length; j++)
                row.push(cols[j].innerText);

            csv.push(row.join(','));
        }

        // Download CSV file.
        downloadCSV(csv.join('\n'), filename);

        // Deactivate loader.
        $('#loader').removeClass('active');
    }

    /**
     * Starts updates beam if an irradiation is in beam.
     */
    var checkUpdateSec = function (){
        if (refreshInterval == undefined){
            refreshInterval = setInterval(checkUpdateSec, refreshTimerRate);
        } else {
            if (updateSecActive && noConcurrentJobs){
                var tableRows = $('tbody tr');
                var ids = [];
                for (var i = 0; i < tableRows.length; i++){
                    var lastColumn = tableRows[i].children[tableRows[i].children.length - 1];
                    var str = lastColumn.innerText.toLowerCase();
                    isInBeam = (str.includes('in') && str.includes('beam'));
                    if (isInBeam){
                        id = Number(tableRows[i].children[0].children[0].value);
                        ids.push(id);
                    }
                }
                var existOngoingIrradiations = (ids.length > 0)
                if (existOngoingIrradiations){
                    // Disable updateSecActive until server response reactivates it. 
                    setUpdateSec(false);
                    updateSec(ids);
                }
            }
        }
    }

    //Event listener locators.
    var eventListeres = [
        // Create, update, clone and delete forms.
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-load-irradiation-form", 
            "handler": loadForm
        },
        {
            "selector": "body", 
            "event": "submit", 
            "childSelector": ".js-submit-irradiation-form", 
            "handler": saveIrradiationForm
        },
        // Export irradiation data.
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": "#dosimetry-results-export", 
            "handler": exportTableToCSV
        },
    ];

    //Remove and afterwards add event listeners.
    for (item of eventListeres) {
        $(item.selector).off(item.event, item.handler);
        $(item.selector).on(item.event, item.childSelector, item.handler);
    }

    // Activate tabs.
    activateTabs();
    checkUpdateSec();
});
