console.log('loaded base.js');
$(document).ready(function () {
    /**
     * Cookie consent event handler.
     */
    window.addEventListener('load', function () {
        window.cookieconsent.initialise({
            "palette": {
                "popup": {
                    "background": "#000"
                },
                "button": {
                    "background": "#f1d600"
                }
            },
            "position": "bottom",
            "content": {
                "message": 'This web application uses cookies to ensure you get the best experience on our web application.',
            }
        })
    });

    // Activate dropdown fields.
    allowDropdown();

    /**
    * Handler for elemets per page.
    */
    var updateElementsPerPage = function (e) {
        cookieName = 'elements_per_page';
        cookieValue = $(this).attr('data-value');
        cookieExpirationDays = 1;
        cookiePath = '/';
        setCookie(cookieName, cookieValue, cookieExpirationDays)
        
        e.preventDefault();

        var form = $('form[name=\'search_form\']');
        var filterValue = $('#search-box')[0].attributes['filter-value'].value
        var data = 'search_box=' + filterValue + '&' + 'url=' + window.location.pathname;
        filterListCallback(form, data);
    };

    /**
    * Handler for ENTER key form submit events.
    */
    var enterKeyFormHandler = function (e) {
        return e.key != "Enter";
    };

    /**
     * Handler for collapsible text toggle button.
     */
    var toggleCollapsibleText = function (e) {
        e.preventDefault();
        var locator = '.text-toggle';
        toggleElements(locator);
    }

    /**
     * Handler for filtering list pages.
     */
    var filterList = function (e) {
        e.preventDefault();
        var form = $(this);
        var data = form.serialize() + '&' + 'url=' + window.location.pathname;
        filterListCallback(form, data);
    };

    /**
     * Callback for list page filtering. Also used in updating 
     * elements per page.
     */
    var filterListCallback = function(form, data){
        var url = form.attr('action');
        var type = form.attr('method');
        var dataType = 'json';
        var success = function (data) {
            if (data.form_is_valid) {
                var valueFilter = $("#search-box").val();
                // Replace partial template
                $('#partial-template').html(data.html_list);
                $('#search-box')[0].attributes['filter-value'].value = data.query_str
                if (valueFilter != '')
                    $('#search-clear').removeClass('disabled');
            }
            if (data.alert_message)
                alert(data.alert_message);
        };

        formRequest(url, undefined, type, dataType, undefined, success, undefined, data);
    }

    /**
     * Handler for clearing filters.
     */
    var clearFilters = function (e) {
        e.preventDefault();
        $('#search-clear').addClass('disabled');
        $("#search-box").val('');
        $('#search-submit').click();
    };

    //Event listener locators
    var eventListeres = [
        // Create, update, clone and delete forms
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".update-elements-per-page .item", 
            "handler": updateElementsPerPage
        },
        // Disable ENTER form submission
        {
            "selector": "body", 
            "event": "keydown", 
            "childSelector": "form", 
            "handler": enterKeyFormHandler
        },
        // Toggle collapsible text
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": ".text-toggle-action", 
            "handler": toggleCollapsibleText
        },
        // Filter bar submission
        {
            "selector": "body", 
            "event": "submit", 
            "childSelector": "form[name='search_form']", 
            "handler": filterList
        },
        // Filter bar clear
        {
            "selector": "body", 
            "event": "click", 
            "childSelector": "#search-clear", 
            "handler": clearFilters
        }
    ];

    //Remove and afterwards add event listeners
    for (item of eventListeres) {
        $(item.selector).off(item.event, item.handler);
        $(item.selector).on(item.event, item.childSelector, item.handler);
    }

});