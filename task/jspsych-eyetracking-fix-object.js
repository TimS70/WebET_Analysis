/*
 * Example plugin template
 */
jsPsych.plugins["eyetracking-fix-object"] = (function() {

    let plugin = {};

    plugin.info = {
        name: "eyetracking-fix-object",
        description: '',
        parameters: {
            name: {
                type: jsPsych.plugins.parameterType.STRING,
                pretty_name: 'task name',
                default: undefined,
                description: 'What is the name of the task?'
            },
            trial_duration: {
                type: jsPsych.plugins.parameterType.INT,
                pretty_name: 'Stimulus duration',
                default: undefined,
                description: 'How long the stimulus appears.'
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
        }
    }

    plugin.trial = function(display_element, trial) {
        tempDs = [];
        webgazer.resume();

        let w = $(window).width();
        let h = $(window).height();

        // data saving
        let trial_data = {
            x_pos: trial.x_position,
            y_pos: trial.y_position,
            trial_duration: trial.trial_duration,
            window_width: w,
            window_height: h,
            chin: chin,
            task_nr: task_nr,
        };

        init();

        function init() {
            initStimulus();
            if (trial.trial_duration !== null) {
                jsPsych.pluginAPI.setTimeout(function() {
                    end_trial();
                }, trial.trial_duration);
            }
        }

        function initStimulus() {
            display_element.innerHTML =
                '<div id="taskStimulus"' +
                'style="' +
                'left:' + trial.x_position * 100 + '%; ' +
                'top:' + trial.y_position * 100 + '%; ' +
                'position: fixed;">' +
                trial.stimulus + '</div>'
            ;
        }

        function end_trial() {
            webgazer.pause();
            trial_data.et_data = JSON.stringify(tempDs);
            display_element.innerHTML = '';
            jsPsych.finishTrial(trial_data);
        }

    };

    return plugin;
})();
