/**
 * jspsych-html-keyboard-response
 * Josh de Leeuw
 *
 * plugin for displaying a stimulus and getting a keyboard response
 *
 * documentation: docs.jspsych.org
 *
 **/


jsPsych.plugins["eyetracking-choice"] = (function() {

    var plugin = {};

    plugin.info = {
        name: 'eyetracking-choice',
        description: '',
        parameters: {
            name: {
                type: jsPsych.plugins.parameterType.STRING,
                pretty_name: 'task name',
                default: undefined,
                description: 'What is the name of the task?'
            },
            option_topLeft: {
                type: jsPsych.plugins.parameterType.HTML_STRING,
                pretty_name: 'Option top left',
                default: undefined,
                description: 'The reward string to be displayed on the left side'
            },
            option_topRight: {
                type: jsPsych.plugins.parameterType.HTML_STRING,
                pretty_name: 'Option top right',
                default: undefined,
                description: 'The reward string to be displayed on the left side'
            },
            option_bottomLeft: {
                type: jsPsych.plugins.parameterType.HTML_STRING,
                pretty_name: 'Option bottom left',
                default: undefined,
                description: 'The reward string to be displayed on the left side'
            },
            option_bottomRight: {
                type: jsPsych.plugins.parameterType.HTML_STRING,
                pretty_name: 'Option bottom right',
                default: undefined,
                description: 'The reward string to be displayed on the left side'
            },
            choices: {
                type: jsPsych.plugins.parameterType.KEYCODE,
                array: true,
                pretty_name: 'Choices',
                default: jsPsych.ALL_KEYS,
                description: 'The keys the subject is allowed to press to respond to the stimulus.'
            },
            stimulus_duration: {
                type: jsPsych.plugins.parameterType.INT,
                pretty_name: 'Stimulus duration',
                default: null,
                description: 'How long to hide the stimulus.'
            },
            trial_duration: {
                type: jsPsych.plugins.parameterType.INT,
                pretty_name: 'Trial duration',
                default: null,
                description: 'How long to show trial before it ends.'
            },
            response_ends_trial: {
                type: jsPsych.plugins.parameterType.BOOL,
                pretty_name: 'Response ends trial',
                default: true,
                description: 'If true, trial will end when subject makes a response.'
            },
            amountLeft: {
                type: jsPsych.plugins.parameterType.BOOL,
                pretty_name: 'Amount on the left side',
                default: undefined,
                description: 'If true, trial will end when subject makes a response.'
            },
        }
    }

    plugin.trial = function(display_element, trial) {
        tempDs = [];
        webgazer.resume();

        // store response
        let response = {
            rt: null,
            key: null
        };

        init();

        function init() {
            initStimulus();
        }

        function initStimulus() {
        let new_html =
            '<div id="taskStimulus">'+
                '<div id="cTop">' +
                    '<div style="text-align: center; position: absolute; display: flex; ' +
                    'left: 0%; width: 40%; height: 100%; top: 0%;">' +
                        '<p style="margin: auto;">' +
                            (trial.option_topLeft) +
                        '</p>' +
                    '</div>' +
                    '<div style="text-align: center; position: absolute; display: flex; ' +
                    'left: 60%; width: 40%; height: 100%; top: 0%;">' +
                        '<p style="margin: auto;">' +
                            (trial.option_topRight) +
                        '</p>' +
                    '</div>' +
                '</div>' +
                '<div id="cBottom">' +
                    '<div style="text-align: center; position: absolute; display: flex; ' +
                    'left: 0%; width: 40%; height: 100%; top: 0%;">' +
                        '<p style="margin: auto;">' +
                        (trial.option_bottomLeft) +
                        '</p>' +
                    '</div>' +
                    '<div style="text-align: center; position: absolute; display: flex; ' +
                    'left: 60%; width: 40%; height: 100%; top: 0%;">' +
                        '<p style="margin: auto;">' +
                            (trial.option_bottomRight) +
                        '</p>' +
                    '</div>' +
                '</div>' +
            '</div>'
        ;
        
        $("<style>")
            .prop("type", "text/css")
            .html("\
            #cTop, #cBottom {\
                position: relative;\
                left: 5%;\
                margin: auto;\
                width: 90%;\
                height: 40%;\
                border-style: solid;\
                position: fixed;\
                font-size: 30pt;\
            }\
            #cTop {top: 5%;}\
            #cBottom {top: 55%;}\
            ")
            .appendTo("body");

            display_element.innerHTML = new_html;
        }



        // function to handle responses by the subject
        let after_response = function(info) {

            // after a valid response, the stimulus will have the CSS class 'responded'
            // which can be used to provide visual feedback that a response was recorded
            display_element.querySelector('#taskStimulus').className += ' responded';

            // only record the first response
            if (response.key == null) {
                response = info;
            }

            if (trial.response_ends_trial) {
                end_trial();
            }
        }

        // function to end trial when it is time
        function end_trial() {
            webgazer.pause();
            jsPsych.pluginAPI.clearAllTimeouts();
            if (typeof keyboardListener !== 'undefined') {
                jsPsych.pluginAPI.cancelKeyboardResponse(keyboardListener);
            }

            let w = $(window).width();
            let h = $(window).height();

            let trial_data = {
                "trial_duration": trial.trial_duration,
                "rt": response.rt,
                "option_topLeft": trial.option_topLeft,
                "option_bottomLeft": trial.option_bottomLeft,
                "option_topRight": trial.option_topRight,
                "option_bottomRight": trial.option_bottomRight,
                "key_press": response.key,
                window_width: w,
                window_height: h,
                chin: chin,
                task_nr: task_nr,
            };
            addToChoiceArray();
            trial_data.et_data = JSON.stringify(tempDs);
            display_element.innerHTML = '';
            jsPsych.finishTrial(trial_data);
        }

        function addToChoiceArray() {
            let chosenAmount = null;
            let chosenDelay = null;

            if (trial.amountLeft === 1) {
                if (response.key === 38) {
                    chosenAmount = trial.option_topLeft;
                    chosenDelay = trial.option_topRight;
                } else if (response.key === 40) {
                    chosenAmount = trial.option_bottomLeft;
                    chosenDelay = trial.option_bottomRight;
                }
            } else {
                if (response.key === 38) {
                    chosenAmount = trial.option_topRight;
                    chosenDelay = trial.option_topLeft;
                } else if (response.key === 40) {
                    chosenAmount = trial.option_bottomRight;
                    chosenDelay = trial.option_bottomLeft;
                }
            }
            subjectChoices.push({
                'amount': chosenAmount,
                'delay': chosenDelay
            });
        }

        // start the response listener
        if (trial.choices !== jsPsych.NO_KEYS) {
            var keyboardListener = jsPsych.pluginAPI.getKeyboardResponse({
                callback_function: after_response,
                valid_responses: trial.choices,
                rt_method: 'performance',
                persist: false,
                allow_held_key: false
            });
        }

        // hide stimulus if stimulus_duration is set
        if (trial.stimulus_duration !== null) {
            jsPsych.pluginAPI.setTimeout(function() {
                display_element.querySelector('#taskStimulus').style.visibility = 'hidden';
            }, trial.stimulus_duration);
        }

        // end trial if trial_duration is set
        if (trial.trial_duration !== null) {
            jsPsych.pluginAPI.setTimeout(function() {
                end_trial();
            }, trial.trial_duration);
        }
    };

    return plugin;
})();
