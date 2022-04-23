var TIMEOUT_TIME = 40000;

/**
 * Standard function used for server requests.
 */
function formRequest(url, modalID, type='get', dataType='json', beforeSendCallback=function(){}, 
    successCallback=function(){}, errorCallback=function(){}, data=undefined, withModal=true, 
    withLoader=true, withTimeout=true, withErrorMessage = true) {
    if (url == undefined) 
        throw new Error('Error. formRequest parameter url is invalid.');
    else if ($(modalID) == undefined && withModal) 
        throw new Error('Error. Locator of modalID ', modalID, ' is undefined.');

    
    var searchParams = new URLSearchParams(window.location.search);
    if(type == 'post' && searchParams.get('page')){
        data = data + '&page=' + searchParams.get('page');
    }

    var timeout = undefined;
   
    var xhr = $.ajax({
        url: url,
        data: data,
        type: type,
        dataType: dataType,
        beforeSend: function () {
            switch (type) {
                case 'get':
                    if (withLoader) setLoaderState('loader');
                    break;
                case 'post':
                    if (withModal) $(modalID).modal('hide'); 
                    if (withLoader) setLoaderState('loader');
                    break;
                default:
                    throw new Error('Error. unrecognized request type.');
            }
            beforeSendCallback();
        },
        success: function (data) {
            clearTimeout(timeout);
            data.form_is_valid = (data.form_is_valid == undefined) ? true : data.form_is_valid;
            if(data.form_is_valid){
                if (withLoader) setLoaderState('success');
            } else {
                if (withLoader) setLoaderState('error');
            }

            successCallback(data);
            if (data.form_is_valid){
                switch (type) {
                    case 'get':
                        if (withLoader) setLoaderState('inactive');
                        if (withModal) $(modalID).modal('show');
                        break;
                    case 'post':
                        if (withLoader) setLoaderState('inactive');
                        break;
                    default:
                        throw new Error('Error. unrecognized request type.');
                }
            } else {
                switch (type) {
                    case 'get':
                        if (withLoader) setLoaderState('inactive');
                        break;
                    case 'post':
                        if (withLoader) setLoaderState('inactive');
                        if (withModal) $(modalID).modal('show');
                        break;
                    default:
                        throw new Error('Error. unrecognized request type.');
                }
            }
            return false;
        },
        error: function (xhr) {
            clearTimeout(timeout);
            var message = undefined
            var condition = (withErrorMessage && xhr.status != 0);
            if (condition){
                message = 'Unrecognized error. Status code: ' + xhr.status;
                if (xhr.status == 504){
                    message = 'Timeout error (' + xhr.status + '). ' + 
                        'Server is taking too long to respond.';
                } else if (xhr.status == 505) {
                    message = 'Internal server error (' + xhr.status + ').';
                }
                formRequestErrorHandler(message, withLoader);
            }
            errorCallback(xhr);
        },
    });

    return xhr
}

/**
 * Activates select fields with searching capabilities.
 */
function activateSearchSelectFields(){
    var choiceFields = $('.modal select:not(.ui.search.dropdown)');
    for(var i = 0; i < choiceFields.length; i++){
        choiceFields[i].className += ' ui search dropdown allowed-dropdown';
    }
    allowDropdown();
}

/**
 * Sets loader state between active, inactive, loading, success and error.
 */
function setLoaderState(state){
    state = state.toLowerCase();
    if (state != 'inactive') {
        $('#loader').addClass('active');

        switch(state) {
            case 'loader':
                $('.loader-container .loader').show();
                $('.loader-container .success').hide();
                $('.loader-container .error').hide();
                break;
            case 'success':
                $('.loader-container .loader').hide();
                $('.loader-container .success').show();
                $('.loader-container .error').hide();
                break;
            case 'error':
                $('.loader-container .loader').hide();
                $('.loader-container .success').hide();
                $('.loader-container .error').show();
                break;
            default:
                break;
          }
    } else {
        $('.loader-container .loader').show();
        $('.loader-container .success').hide();
        $('.loader-container .error').hide();
        $('#loader').removeClass('active');
    }
}

/**
 * Activates dropdowns.
 */
function allowDropdown(){
    $('.allowed-dropdown.link').dropdown();

    $('select.allowed-dropdown:not(.search-remote):not(.elements-per-page)').dropdown({
        duration: 1,
        maxResults: 5,
        onChange: function (value, text, $selectedItem) {
            if(!value) return;
            var dropdown = $(this);
            if (value.includes('clear') && value.includes('input')){
                dropdown.dropdown('clear');
            }
        }
    });

    $('#partial-template-pagination-top .allowed-dropdown').dropdown({
        duration: 1,
        maxResults: 5,
        direction: 'downward',
    });

    $('#partial-template-pagination-bottom .allowed-dropdown').dropdown({
        duration: 1,
        maxResults: 5,
        direction: 'upward',
    });

    var remoteSearchSelector = $('select.allowed-dropdown.search-remote');
    if(remoteSearchSelector.length > 0){
        var str = remoteSearchSelector[0].attributes['search-remote-url'].value
        var url = str.substring(0, str.length - 1) + '?q={query}'
        remoteSearchSelector.dropdown({
            duration: 1,
            maxResults: 20,
            apiSettings: {
                url: url,
                dataType: "json",
                minCharacters: 1,
                method: "get",
            }
        });
    }
}

/**
 * Returns to previous page.
 */
function goBack() {
    window.location.replace(document.referrer);
}

/**
 * Error handler for formRequest function.
 */
function formRequestErrorHandler(message, withLoader){
    if (withLoader) setLoaderState('error');
    if (message)
        alert(message);
    if (withLoader) $('#loader').removeClass('active');
}

/**
 * Collapses and uncollapses text.
 */
function toggleElements(locator){
    var items = $(locator);
    for (var i = 0; i < items.length; i++) {
        var className = items[i].className;
        if (className.indexOf(' hidden') > -1){
            items[i].className = className.replace(' hidden', '');
        } else {
            items[i].className = className + ' hidden';
        }
    }
}

/**
 * Activates Semantic UI tabs.
 */
function activateTabs(){
    $('.menu .item').tab();
}

/**
 * Sets cookie with expiration.
 */
function setCookie(cname, cvalue, exdays, path='/') {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires=" + d.toGMTString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=" + path;
}

/**
 * Retrieves cookie.
 */
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
        c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
        }
    }
    return "";
}

/**
 * Activate popups.
 */
function activatePopups(delay=undefined) {
    // Some pages like the samples page require a 
    // time delay to work. The reason in unknown.
    var selector = '.info-popup'
    var eventType = 'hover'

    $(selector).unbind(eventType);

    if (delay) {
        window.setTimeout(()=>{
            $(selector).popup({
                on: eventType,
                hoverable: true,
                exclusive: true,
                position: 'bottom left'
            });
        }, delay);
    } else {
        $(selector).popup({
            on: eventType,
            hoverable: true,
            exclusive: true,
            position: 'bottom left'
        });
    }
}

/**
 * Populate elements per page with last value.
 */
function syncElementsPerPage() {
    var cookieName = 'elements_per_page';
    var elements_per_page_cookie = getCookie(cookieName);
    if (elements_per_page_cookie == '') elements_per_page_cookie = 10;

    var oldActiveItems = $('.active.selected');
    var newActiveItems = $('.update-elements-per-page .menu \
        .item[data-value="' + elements_per_page_cookie + '"]');
    var texts = $('.update-elements-per-page .text');

    for (var i = 0; i < oldActiveItems.length; i++){
        oldActiveItems[i].className = oldActiveItems[i].className
            .replace(' active selected', '');
    }

    for (var i = 0; i < newActiveItems.length; i++){
        newActiveItems[i].className += ' active selected';
        elements_per_page_text = newActiveItems[i].innerHTML;
    }

    for (var i = 0; i < texts.length; i++){
        texts[i].innerHTML = elements_per_page_text;
    }
}

/**
 * Serialize checked elements.
 */
function serializeCheckedElements(checkedElements){
    result = ''
    for (var i = 0; i < checkedElements.length; i++){
        result += 'checks[]=' + checkedElements[i] + '&';
    }
    result = result.substring(0, result.length - 1);
    result = encodeURI(result);
    return result
}