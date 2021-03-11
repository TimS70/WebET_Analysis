jsPsych.plugins["eyetracking-init"] = (function() {

    var plugin = {};

    plugin.info = {
        name: "eyetracking-init",
        parameters: {
            key: {
                type: jsPsych.plugins.parameterType.KEYCODE,
                default: 32,
            },
            countdown: {
                type: jsPsych.plugins.parameterType.INT,
                default: 30,
            },
            afterLoad: {
                type: jsPsych.plugins.parameterType.STRING,
                default: '<p>Ready!<p>' +
                '<p>Check if you can see the video stream on the top left corner. If ' +
                    'you do not see a video, please try reloading the page. </p>' +
                    '<p>If you see the video stream, press Space to continue</p>'
            }
        }
    }

    plugin.trial = function(display_element, trial) {
        currentTask = trial.name;

        let t = trial.countdown;
        let w = $(window).width();
        let h = $(window).height();

        // data saving
        var trial_data = {
            window_width: w,
            window_height: h,
            chin: chin,
        };

        function initWebgazer() {
            webgazer.setRegression('ridge')
                .setGazeListener(function(data, clock) {
                    if (data == null) {
                        return;
                    }
                    tempDs.push({
                        'x': data.x/screen.width,
                        'y': data.y/screen.height,
                        't': clock,
                    });
                })
                .begin();
            webgazer.showPredictionPoints(false);
        }

        function eyetrackingReady() {
            if (!webgazer.isReady()) {
                console.log("Webgazer is not ready");
            } else {
                console.log("Webcam is ready");
            }
            if ($('#webgazerVideoFeed').length < 1) {
                console.log("Video Feed is not ready");
            } else {
                console.log("Video Feed is ready");
            }
            if ((webgazer.isReady()) && ($('#webgazerVideoFeed').length > 0)) {
                return true;
            } else {
                return false;
            }
        }

        function showStimulus() {
            display_element.innerHTML =
                '<div id="pWait" style="text-align: center; position: fixed; ' +
                'top: 40%; left: 10%; width: 80%;">' +
                '<p>Please wait for <strong>' + t + '</strong> more seconds. </p>' +
                '</div>';
        }

        function readyToContinue() {
            display_element.innerHTML =
                '<div id="pWait" style="text-align: center; position: fixed; ' +
                'top: 40%; left: 10%; width: 80%;">' +
                    '<p>' + trial.afterLoad + '</p>' +
                '</div>';

            jsPsych.pluginAPI.getKeyboardResponse({
                callback_function: after_response,
                valid_responses: [trial.key],
                rt_method: 'performance',
                persist: false,
                allow_held_key: false
            });
        }

        function after_response() {
            $('#webgazerFaceOverlay').hide();
            $('#webgazerVideoFeed').hide();
            $('#webgazerFaceFeedbackBox').hide();
            webgazer.pause();
            console.log(tempDs);
            display_element.innerHTML = '';
            jsPsych.finishTrial(trial_data);
        }

        function errorMessage() {
            display_element.innerHTML =
                '<div id="pWait" style="text-align: center; position: fixed; ' +
                'top: 15%; left: 25%; width: 50%;">' +
                '<p>Initialization failed! <br>' +
                'Please check the following: ' +
                '<div style="text-align: left;">' +
                    '<ul>' +
                    '<li>Do you have a function in webcam connected to your computer? </li>' +
                    '<li>Did you allow the browser to access this webcam? </li>' +
                    '<li>If you denied access to the webcam, please check and possibly reset ' +
                    'permission settings for this website in your browser. </li>' +
                    '<li>Did you select the correct webcam if you have more than one? </li>' +
                    '</ul>' +
                '</div>' +
                '</p>' +
                '<p>If you think that one of these points apply to you, you could try to ' +
                'reload the page <u>after</u> you fixed the respective issue. Otherwise, ' +
                'please contact the researchers.</p>' +
                '</div>'
        }

        init();

        async function init() {
            jsPsych.pluginAPI.cancelAllKeyboardResponses();

            display_element.innerHTML =
                '<div id="pWait" style="text-align: center; position: fixed; top: 40%; left: 10%; width: 80%;">' +
                    '<p>Please wait for the video stream to appear on the top left corner. ' +
                '</div>';

            let countdown = setInterval(function(){
                showStimulus()
                t -= 1;
                if (t < 1) {
                    if (eyetrackingReady()) {
                        clearInterval(countdown);
                        readyToContinue();
                        console.log("Eye-Tracking is ready to start!");
                    } else {
                        errorMessage();
                    }
                }
            }, 1000);

            initWebgazer();
        }
    };

    return plugin;
})();
