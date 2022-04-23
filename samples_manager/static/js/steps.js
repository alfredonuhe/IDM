console.log('loaded steps.js')
$(document).ready(function () {
    var speed = '250ms';

    /**
     * Handler for forward form page transitions.
     */
    var nextStepHandler = function (e) {
        e.preventDefault();
        var stepElement = $(this).closest('[id^=step-]')[0];
        var stepID = stepElement.id;
        var stepNumber = Number(stepID.charAt(stepID.length - 1));
        var notLast = (stepElement.nextElementSibling != null);

        if(notLast){
            var step = $('#step-' + stepNumber);
            var stepTab = $('#step-tab-' + stepNumber);
            var nextStep = $('#step-' + (stepNumber + 1));
            var nextStepTab = $('#step-tab-' + (stepNumber + 1));

            stepTab.addClass('unactive-tab');
            nextStepTab.removeClass('unactive-tab');

            step.animate({}, undefined, function () {

                $('body').css('background-color', '#06000a');
                step.transition('hide');
                nextStep.transition({
                    animation  : 'fly left',
                    duration   : speed,
                  });
            });
        } else {
            throw new Error('Can\'t navigate to next page. No page.')
        }
    };

    /**
     * Handler for backwards form page transitions.
     */
    var prevStepHandler = function (e) {
        e.preventDefault();
        var stepElement = $(this).closest('[id^=step-]')[0];
        var stepID = stepElement.id;
        var stepNumber = Number(stepID.charAt(stepID.length - 1));
        var notFirst = (stepElement.previousElementSibling != null);

        if(notFirst){
            var step = $('#step-' + stepNumber);
            var stepTab = $('#step-tab-' + stepNumber);
            var prevStep = $('#step-' + (stepNumber - 1));
            var prevStepTab = $('#step-tab-' + (stepNumber - 1));

            stepTab.addClass('unactive-tab');
            prevStepTab.removeClass('unactive-tab');

            step.animate({}, undefined, function () {

                $('body').css('background-color', '#06000a');
                step.transition('hide');
                prevStep.transition({
                    animation  : 'fly right',
                    duration   : speed
                  });
            });
        } else {
            throw new Error('Can\'t navigate to next page. No page.');
        }
    };

    /**
     * Handler for tab form page transitions.
     */
    var tabHandler = function (e) {
        var stepElement = $('[id^=step-].visible')[0];
        var stepID = stepElement.id;
        var stepNumber = Number(stepID.charAt(stepID.length - 1));
        var futureStepNumber = Number(
            $(this)[0].id.charAt($(this)[0].id.length - 1)
            );
        var exists = ($('#step-' + futureStepNumber)[0].id != undefined);

        if(exists){
            if (futureStepNumber != stepNumber) {
                var step = $('#step-' + stepNumber);
                var stepTab = $('#step-tab-' + stepNumber);
                var futureStep = $('#step-' + futureStepNumber);
                var futureStepTab = $('#step-tab-' + futureStepNumber);
                var direction = 
                    (futureStepNumber > stepNumber) ? 'left' : 'right';

                stepTab.addClass('unactive-tab');
                futureStepTab.removeClass('unactive-tab');

                step.animate({}, undefined, function () {

                    $('body').css('background-color', '#06000a');
                    step.transition('hide');
                    futureStep.transition({
                        animation  : "fly " + direction,
                        duration   : speed
                      });
                });
            }
        } else {
            throw new Error('Can\'t navigate to step. Step' + 
                futureStepNumber + ' doesn\'t exist.');
        }
    };

    //Event listener locators
    var eventListeres = [
        // Create, update, clone and delete forms
        {
            "selector": ".next-step", 
            "event": "click", 
            "childSelector": undefined, 
            "handler": nextStepHandler
        },
        {
            "selector": ".prev-step", 
            "event": "click", 
            "childSelector": undefined, 
            "handler": prevStepHandler
        },
        {
            "selector": "[id^=step-tab-]", 
            "event": "click", 
            "childSelector": undefined, 
            "handler": tabHandler
        }
    ];

    //Remove and afterwards add event listeners
    for (item of eventListeres) {
        $(item.selector).off(item.event, item.handler);
        $(item.selector).on(item.event, item.childSelector, item.handler);
    }
});