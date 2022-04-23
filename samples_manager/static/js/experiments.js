console.log('loaded experiments.js');
$(function () {
    /**
    * Handler for display experiment form.
    */
    var loadForm = function () {
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var btn = $(this);
        var url = btn.attr('data-url');
        var modalID = '#modal-experiment';
        var type = 'get';
        var data = serialized_checkboxes;
        var dataType = 'json';
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
        };

        formRequest(url, modalID, type, dataType, beforeSend, success, undefined, data);
    };

    /**
    * Handler for submit experiment form button.
    */
    var saveForm = function (e) {
        e.preventDefault();
        console.log('submit experiment')
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var form = $(this);
        var url = form.attr('action');
        var modalID = '#modal-experiment';
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
        };
        formRequest(url, modalID, type, dataType, undefined, success, undefined, data);
        return false;
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

    //Event listener locators
    var eventListeres = [
        // Create, update, clone and delete forms
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-load-experiment-form", 
            "handler": loadForm
        },
        {
            "selector": "body", 
            "event": "submit", 
            "childSelector": ".js-submit-experiment-form", 
            "handler": saveForm
        },
        // Redirecting
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-redirect-form", 
            "handler": redirect
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