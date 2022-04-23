console.log('loaded checkboxes.js');
$(function () {

    /**
     * Switches between tabs.
     */
    var activateTab = function (action) {
        var filterElements = $('*[data-tab=filters]');
        var actionElements = $('*[data-tab=actions]');

        for (var i = 0; i < filterElements.length; i++) {
            filterElements[i].className = filterElements[i].className.replace(' active', '');
            if (action == 'filters')
                filterElements[i].className = filterElements[i].className + ' active';
        }
        for (var i = 0; i < actionElements.length; i++) {
            actionElements[i].className = actionElements[i].className.replace(' active', '');
            if (action == 'actions')
                actionElements[i].className = actionElements[i].className + ' active';
        }
    };

    /**
     * Disables single and group action buttons.
     */
    var diableActionButtons = function (action) {
        var singleActions = $('.single-action');
        var groupActions = $('.group-action');

        for (var i = 0; i < groupActions.length; i++) {
            if (action == 'group' || action == 'none')
                groupActions[i].className = groupActions[i].className.replace(' disabled', '');
            if (action == 'group')
                groupActions[i].className = groupActions[i].className + ' disabled';
        }
        for (var i = 0; i < singleActions.length; i++) {
            if (action == 'single' || action == 'none')
                singleActions[i].className = singleActions[i].className.replace(' disabled', '');
            if (action == 'single')
                singleActions[i].className = singleActions[i].className + ' disabled';
        }
    };

    /**
     * Handler for change in list checkbox.
     */
    var checkCheckboxHandler = function () {
        applyCheckboxState();
    };

    /**
     * Applies checkbox state enabling and disabling group and 
     * individual actions.
     */
    var applyCheckboxState = function () {
        var state = getCheckboxesState();
        if (state['allChildrenChecked'] && 
            state['numChildCheckboxes'] > 0) {
            var parentCheckbox = $('#all-checkbox');
            changeCheckboxState(parentCheckbox, true);
            activateTab('actions');
        } else if(state['checkedChildCheckboxes'] > 0) {
            var parentCheckbox = $('#all-checkbox');
            changeCheckboxState(parentCheckbox, false);
            activateTab('actions');
        } else {
            var parentCheckbox = $('#all-checkbox');
            changeCheckboxState(parentCheckbox, false);
        }

        if(state['checkedChildCheckboxes'] == 0){
            diableActionButtons('none');
            diableActionButtons('single');
            diableActionButtons('group');
        } else if (state['checkedChildCheckboxes'] == 1) {
            diableActionButtons('none');
        } else if (state['checkedChildCheckboxes'] > 1) {
            diableActionButtons('none');
            diableActionButtons('single');
        }
    };

    /**
     * Handler for change in all samples checkbox.
     */
    var checkAllCheckboxHandler = function () {
        if (this.checked) {
            changeAllCheckboxState(true);
            activateTab('actions');
        } else {
            changeAllCheckboxState(false);
        }
        
        applyCheckboxState();
    };

    /**
     * Checks individual checkbox.
     */
    var changeCheckboxState = function (checkbox, check) {
        $(checkbox).prop('checked', check);
    };

    /**
     * Checks all checkboxes.
     */
    var changeAllCheckboxState = function (check) {
        $('tbody .checkbox').prop('checked', check);
        $('#all-checkbox').prop('checked', check);
    };

    /**
     * Checks all checkboxes.
     */
    var getCheckboxesState = function () {
        var childCheckboxes = $('tbody .checkbox');
        var parentCheckbox = $('#all-checkbox');
        var checkedChildCheckboxes = 0;
        for (var i = 0; i < childCheckboxes.length; i++) {
            if (childCheckboxes[i].checked) {
                checkedChildCheckboxes++;
            }
        }
        var result = {
            'checkedChildCheckboxes': checkedChildCheckboxes,
            'checkedParentCheckbox': parentCheckbox[0].checked,
            'numChildCheckboxes': childCheckboxes.length,
            'allChildrenChecked': (childCheckboxes.length == checkedChildCheckboxes)
        }

        return result
    };

    //Event listener locators
    var eventListeres = [
        // Single checkbox
        {
            "selector": "body",
            "event": "change",
            "childSelector": ".checkbox",
            "handler": checkCheckboxHandler
        },
        // All checkboxes
        {
            "selector": "body",
            "event": "click",
            "childSelector": "#all-checkbox",
            "handler": checkAllCheckboxHandler
        }
    ];

    //Remove and afterwards add event listeners
    for (item of eventListeres) {
        $(item.selector).off(item.event, item.handler);
        $(item.selector).on(item.event, item.childSelector, item.handler);
    }

    // Apply checkbox state at script load
    applyCheckboxState();
});