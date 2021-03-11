jsPsych.plugins["eyetracking-calibration"] = (function() {

    let plugin = {};

    plugin.info = {
        name: "eyetracking-calibration",
        description: '',
        parameters: {
            name: {
                type: jsPsych.plugins.parameterType.STRING,
                pretty_name: 'task name',
                default: undefined,
                description: 'What is the name of the task?'
            },
            x_position: {
                type: jsPsych.plugins.parameterType.FLOAT,
                pretty_name: 'X position start',
                default: 0.5,
                description: 'X-Coord. of object to start',
            },
            y_position: {
                type: jsPsych.plugins.parameterType.FLOAT,
                pretty_name: 'Y position start',
                default: 0.5,
                description: 'X-Coord. of object to start',
            },
            stimulus: {
                type: jsPsych.plugins.parameterType.HTML_STRING,
                pretty_name: 'Stimulus',
                default: undefined,
                description: 'The HTML string to be displayed'
            },
            clickNr: {
                type: jsPsych.plugins.parameterType.INT,
                default: 9
            },
        }
    }

    plugin.trial = function(display_element, trial) {
        tempDs = [];
        webgazer.resume();
        let buttonState = 1;

        let w = $(window).width();
        let h = $(window).height();

        // data saving
        let trial_data = {
            x_pos: trial.x_position,
            y_pos: trial.y_position,
            window_width: w,
            window_height: h,
            chin: chin,
            task_nr: task_nr,
        };

        init();

        function init() {
            $(document).css('pointer-events', 'none');
            initStimulus();
        }

        function initStimulus() {
            display_element.innerHTML =
                '<div id="taskStimulus"' +
                'style="left:' + trial.x_position * 100 + '%; top:' + trial.y_position * 100 + '%; position: fixed;">' +
                trial.stimulus + '</div>'
            ;
            $("button").css('opacity', (0.4 + (0.5/(trial.clickNr+1))));
            $("button").mouseenter(() => {
                $(document).css('pointer-events', 'auto');
            });
            $("button").mouseleave(() => {
                $(document).css('pointer-events', 'none');
            });
            $('#taskStimulus').click(function() {
                changeButtonState();
            });
        }

        function changeButtonState() {
            $("button").css('opacity', (0.4 + buttonState*(0.5/(trial.clickNr+1))));
            if(buttonState > (trial.clickNr-1)) {
                $("#taskStimulus").off('click');
                $("button").css('background-color', 'lime');
                setTimeout(end_trial, 250);
            } else {
                buttonState++;
            }
        }

        function end_trial() {
            webgazer.pause();
            trial_data.et_data = JSON.stringify(tempDs);
            $(document).css('pointer-events', 'auto');
            display_element.innerHTML = '';
            jsPsych.finishTrial(trial_data);
        }
    };

    return plugin;
})();
