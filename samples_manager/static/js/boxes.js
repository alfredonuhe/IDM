console.log('loaded boxes.js');
$(function () {

    /**
    * Handler for loading of box create, update, clone and delete actions.
    */
    var loadForm = function () {
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var btn = $(this);
        var url = btn.attr('data-url');
        var modalID = '#modal-box';
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
        };

        formRequest(url, modalID, type, dataType, beforeSend, success, undefined, data);
    };

    /**
    * Handler for submission of box create, update, clone and delete actions.
    */
    var saveForm = function (e) {
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        e.preventDefault();
        console.log('event');
        var form = $(this);
        var url = form.attr('action');
        var modalID = '#modal-box';
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
    };

    /**
    * Handler for loading of box item create, update, clone and delete actions.
    */
    var loadBoxItemForm = function () {
        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var btn = $(this);
        var url = btn.attr('data-url');
        var modalID = '#modal-box-item';
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
        };

        formRequest(url, modalID, type, dataType, beforeSend, success, undefined, data);
    };

    /**
    * Handler for submission of box item forms.
    */
    var saveBoxItemForm = function (e) {
        e.preventDefault();

        var serialized_checkboxes = $("input[name='checks[]']").serialize();

        var form = $(this);
        var url = form.attr('action');
        var modalID = '#modal-box-item';
        var type = form.attr('method');
        var dataType = 'json';
        var data = form.serialize() + '&' + serialized_checkboxes;
        var success = function (data) {
            if (data.form_is_valid) {
                $('#partial-template').html(data.html_list); // <-- Replace the table body
                $('tbody .checkbox:checked').removeAttr('checked');
            } else {
                $(modalID + ' .modal-content').html(data.html_form);
            }
            if (data.alert_message)
                alert(data.alert_message);
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

    //Event listener locators
    var eventListeres = [
        // Box actions
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-load-box-form", 
            "handler": loadForm
        },
        {
            "selector": "body", 
            "event": "submit", 
            "childSelector": ".js-submit-box-form", 
            "handler": saveForm
        },
        // Box item actions
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-load-box-item-form", 
            "handler": loadBoxItemForm
        },
        {
            "selector": "body", 
            "event": "submit", 
            "childSelector": ".js-submit-box-item-form", 
            "handler": saveBoxItemForm
        },
        // Redirect
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".js-redirect-form", 
            "handler": redirect
        },
    ];

    // Remove and afterwards add event listeners
    for (item of eventListeres) {
        $(item.selector).off(item.event, item.handler);
        $(item.selector).on(item.event, item.childSelector, item.handler);
    }

    // Activate tabs
    activateTabs();
});