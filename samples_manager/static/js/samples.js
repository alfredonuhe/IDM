console.log('loaded samples.js');
$(function () {
    /**
    * Handler for display sample form button.
    */
    var loadSampleForm = function () {
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var btn = $(this);
        var url = btn.attr('data-url');
        var modalID = '#modal-sample';
        var type = 'get';
        var data = serialized_checkboxes;
        var dataType = 'json';
        var beforeSend = function () {
            $(modalID).modal({
                    autofocus: false,
                    allowMultiple: true,
                    closable: false
                });
        };
        var success = function (data) {
            $(modalID + ' .modal-content').html(data.html_form);
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, modalID, type, dataType, beforeSend, success, undefined, data);
    };

    /**
    * Handler for save sample form button.
    */
    var saveSampleForm = function (e) {
        e.preventDefault();

        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var form = $(this);
        var url = form.attr('action');
        var modalID = '#modal-sample';
        var type = form.attr('method');
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var success = function (data) {
            if (data.form_is_valid) {
                $('#partial-template').html(data.html_list); // <-- Replace the table body
            } else {
                $(modalID + ' .modal-content').html(data.html_form);
            }
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, modalID, type, dataType, undefined, success, undefined, data);
    };

    /**
    * Handler for assign sample ID button.
    */
    var assignids = function () {
        var confirmed = confirm(
            'Allocating SET-ID means that your samples are ready to be irradiated. Please, proceed only if you are sure.'
        );
        if (confirmed) {
            var serialized_checkboxes = $("input[name='checks[]']").serialize();

            var btn=$(this);
            var form = $('#move-samples');
            var url = btn.attr('data-url');
            var type = form.attr('method');
            var dataType = 'json';
            var data = form.serialize() + '&' + serialized_checkboxes;
            var withModal = false;
            var success = function (data) {
                if (data.form_is_valid) {
                    $('#partial-template').html(data.html_list); // <-- Replace the table body
                }
                if (data.alert_message)
                    alert(data.alert_message);
            };

            formRequest(url, undefined, type, dataType, undefined, success, undefined, data, withModal);
        }
    };

    /**
    * Handler for submission of sample box assignment form.
    */
    var saveSampleAssignBoxForm = function (e) {
        e.preventDefault();

        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var form = $(this);
        var url = form.attr('action');
        var modalID = '#modal-sample';
        var type = form.attr('method');
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var success = function (data) {
            if (data.form_is_valid) {
                $('#partial-template').html(data.html_list); // <-- Replace the table body
            } else {
                $(modalID + ' .modal-content').html(data.html_form);
            }
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, modalID, type, dataType, undefined, success, undefined, data);
    };

    /**
    * Handler for move sample button.
    */
    var moveSamples = function () {
        var serialized_checkboxes = $('input[name="checks[]"]').serialize();

        var btn=$(this);
        var form = $('#move-samples');
        var url = btn.attr('data-url');
        var type = form.attr('method');
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var withModal = false;
        var success = function (data) {
            if (data.form_is_valid) {
                $('#partial-template').html(data.html_list); // <-- Replace the table body
            }
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, undefined, type, dataType, undefined, success, undefined, data, withModal);
    };

    /**
     * Event listener for changes in experiment's visibility. 
     */
    var updateVisibility =  function () {
        var form = $('#change-experiment_visibility');
        current_url = form.attr('action');
        if (this.checked) {
            modified_url = current_url + 'on/';
        } else {
            modified_url = current_url + 'off/';
        }
        console.log(form.attr('method'), form.attr('action'), modified_url);


        var form = $(this);
        var url = modified_url;
        var type = form.attr('method');
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var withModal = false;
        var success = function (data) {
            if (data.form_is_valid) {
                document.location.reload(true);
            }
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, undefined, type, dataType, undefined, success, undefined, data, withModal);
    };

    /**
     * Handler for display compound form button.
     */
    var loadCompoundForm = function () {
        var btn = $(this);
        var url = btn.attr('data-url');
        var modalID = '#modal-compound';
        var type = 'get';
        var dataType = 'json';
        var beforeSend = function () {
            $(modalID).modal({
                autofocus: false,
                allowMultiple: true,
                closable: false
            });
        };
        var success = function (data) {
            $(modalID + ' .modal-content').html(data.html_form);
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, modalID, type, dataType, beforeSend, success);
    };

    /**
    * Handler for submit compound form button.
    */
   var saveCompoundForm = function (e) {
        e.preventDefault();

        var form = $(this);
        var url = form.attr('action');
        var modalID = '#modal-compound';
        var type = form.attr('method');
        var dataType = 'json';
        var data = form.serialize();
        var success = function (data) {
            if (data.form_is_valid) {
                refreshSampleForm();
            } else {
                $('#modal-compound .modal-content').html(data.html_form);
            }
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, modalID, type, dataType, undefined, success, undefined, data);
    };

    /**
    * Helper function for compounds created in sample form.
    */
    var refreshSampleForm = function () {
        var serialized_checkboxes = $('input[name="checks[]"]').serialize();

        var form = $('#modal-sample form');
        var url = form.attr('action');
        var modalID = '#modal-sample';
        var type = form.attr('method');
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var success = function (data) {
            if (data.form_is_valid) {
                $(modalID + ' .modal-content').html(data.html_form);
            }
            if (data.alert_message)
                alert(data.alert_message);
        };

        data = data + '&current_page=2&render_with_errors=off&with_alert_message=off';

        formRequest(url, modalID, type, dataType, undefined, success, undefined, data, false);
    };

    /**
    * Handler for submit irradiation form button.
    */
    var loadIrradiationGroupForm = function () {
        var serialized_checkboxes = $('input[name="checks[]"]').serialize();

        var btn = $(this);
        var form = $('#move-samples');
        var url = btn.attr('data-url');
        var modalID = '#modal-irradiation';
        var type = 'get';
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var beforeSend = function () {
            $(modalID).modal({
                autofocus: false,
                allowMultiple: true,
                closable: false
            });
        };
        var success = function (data) {
            checkedSampleValues = 0;
            $(modalID + ' .modal-content').html(data.html_form);
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, modalID, type, dataType, beforeSend, success, undefined, data);
    };

    /**
    * Handler for submit irradiation form button.
    */
    var saveIrradiationGroupForm = function (e) {
        e.preventDefault();

        var serialized_checkboxes = $('input[name="checks[]"]').serialize();

        var form = $(this);
        var url = form.attr('action');
        var modalID = '#modal-irradiation';
        var type = form.attr('method');
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var success = function (data) {
            if (data.form_is_valid) {
                // Replace partial template
                $('#partial-template').html(data.html_list);
            }
            else {
                $(modalID + ' .modal-content').html(data.html_form);
            }
            if (data.alert_message)
                alert(data.alert_message);
            console.log(form.attr('data-url'), data.form_is_valid)
            if (data.form_is_valid)
                window.location.href = form.attr('data-url');
        };

        formRequest(url, modalID, type, dataType, undefined, success, undefined, data);
    };

    /**
     * Redirects to different page.
     */
    var redirect = function (e) {
        e.preventDefault();
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var btn = $(this);
        var url = btn.attr('data-url');
        var type = 'get';
        var dataType = 'json';
        var data = serialized_checkboxes;
        var success = function (data) {
            if (data.form_is_valid) {
                if (data.redirect_url)
                    window.location = data.redirect_url
            }
            
            if (data.alert_message) {
                alert(data.alert_message);
            }
        };
        formRequest(url, undefined, type, dataType, undefined, success, undefined, data, false, false);
        return false;
    }

    /**
     * Handler for assign dosimeter button. 
     */
    var assignDosimiterHandler = function () {
        alert('A Sample-ID will be generated for the samples that they do not have one.');
    }

    /**
     * Handler for dynamic sample move form.
     */
    var dynamicMoveSampleForm = function (e) {
        e.preventDefault();
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var form = $(this).parents('form');
        var url = form.attr('action');
        var modalID = '#modal-sample';
        var type = 'get';
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var withModal = false;
        var success = function (data) {
            if (data.form_is_valid) {
                $(modalID + ' .modal-content').html(data.html_form);
            }
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, undefined, type, dataType, undefined, success, undefined, data, withModal);
    }

    // Event listener locators
    var eventListeres = [
        // Create, update, clone and delete forms
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-load-sample-form", 
            "handler": loadSampleForm
        },
        {
            "selector": "body", 
            "event": "submit", 
            "childSelector": ".js-submit-sample-form", 
            "handler": saveSampleForm
        },
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-load-compound-form", 
            "handler": loadCompoundForm
        },
        {
            "selector": "body", 
            "event": "submit", 
            "childSelector": ".js-submit-compound-form", 
            "handler": saveCompoundForm
        },
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-load-irradiation-group-form", 
            "handler": loadIrradiationGroupForm
        },
        {
            "selector": "body", 
            "event": "submit", 
            "childSelector": ".js-submit-irradiation-group-form", 
            "handler": saveIrradiationGroupForm
        },
        // Dosimeter assignation
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": "#assign_dosimeters", 
            "handler": assignDosimiterHandler
        },
        // Experiment visibility
        {
            "selector": "body", 
            "event": "change", 
            "childSelector": ".public_experiment_checkbox", 
            "handler": updateVisibility
        },
        // Assign SET_IDs
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": "#sample-assign-set-id", 
            "handler": assignids
        },
        // Move samples
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": "#change-experiment", 
            "handler": moveSamples
        },
        // Assign Box
        {
            "selector": "body", 
            "event": "submit", 
            "childSelector": ".js-submit-assign-box-form", 
            "handler": saveSampleAssignBoxForm
        },
        // Redirect buttons
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-redirect-form", 
            "handler": redirect
        },
        // Dynamic move sample form
        {
            "selector": "body", 
            "event": "change", 
            "childSelector": ".js-sample-move-form #id_experiment", 
            "handler": dynamicMoveSampleForm
        }
    ];

    // Remove and afterwards add event listeners
    for (item of eventListeres) {
        $(item.selector).off(item.event, item.handler);
        $(item.selector).on(item.event, item.childSelector, item.handler);
    }

    // Activate tabs
    activateTabs();
});
