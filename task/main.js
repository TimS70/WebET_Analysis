let tempDs=[];
let subjectChoices = [];
let selectedOption = null;
let timeline = [];

let chinFirst = Math.floor(Math.random()+0.5);
let choiceTask_amountLeftFirst = Math.floor(Math.random()+0.5);
let subjectID = Math.round(Math.random() * 1000);
// let turkInfo = jsPsych.turk.turkInfo();

jsPsych.data.addProperties({
    subject: subjectID,
    chinFirst: chinFirst,
    choiceTask_amountLeftFirst: choiceTask_amountLeftFirst,
});

let chin = 0;
let task_nr = 0;

let calClickNr = null;
let calRepetitions = null;
let maxCalDots = null;
let cal_trialNr = null;
let tFixation = null;
let choiceTask_trialNr = null;
let NChoiceTaskTrials = null;


let pilot = 0;
if (pilot === 1) {
    calClickNr = 1;
    calRepetitions = 1;
    maxCalDots = calRepetitions * 13;
    cal_trialNr = 1;

    tFixation = 2000;
    choiceTask_trialNr = 1;
    NChoiceTaskTrials = 4;
} else {
    calClickNr = 14;
    calRepetitions = 3;
    maxCalDots = calRepetitions * 13;
    cal_trialNr = 1;

    tFixation = 5000;
    choiceTask_trialNr = 1;
    NChoiceTaskTrials = 80;
}

/****************************************************************
 * Checking Webcam (Yang & Krajbich, 2020)
 */
ensureWebcam(() => startExperiment());

function ensureWebcam(callback) {
    $('body').html('<p class="center", style="font-family:Arial, Helvetica, sans-serif">Checking webcam ...</p>');
    window.navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            stream.getTracks().forEach(track => track.stop());
            callback();
        })
        .catch(function() {
            alert('Cannot open webcam.\nIs it blocked? This app requires webcam.');
            location.reload();
        });
}

/****************************************************************
 * General Instructions
 * @type {{data: {window_width: (function(): jQuery), window_height: (function(): jQuery), assignmentID: *}, stimulus: string, type: string, choices: [number]}}
 */

let welcome = {
    type: 'html-button-response',
    stimulus:
        '<div style="position: fixed; display: inline-block; top: 20%; right: 20%; text-align: right;">' +
        '<img src="fu_logo.PNG" alt="[FU Berlin Logo]" style="width: 25%;">' +
        '</div>' +
        '<div>' +
        "<br><br>" +
        "<p><strong>Welcome, dear participant! </strong></p>" +
        "<p>Thank you for your interest in and your support for our research.<br> " +
        "This study is run by researchers at Freie Universität Berlin. </p>" +
        '</div>',
    choices: ['Click to continue'],
    on_start: () => {
        saveWebcamInfo();
    },
    data: {
        window_width: function() {return $(window).width();},
        window_height: function() {return $(window).height();},
    }
}

function saveWebcamInfo() {
    window.navigator.mediaDevices.getUserMedia({video: true})
        .then(function (stream) {

            let videoTracks = stream.getVideoTracks();
            let webcam_label = videoTracks[0].label;
            let webcam_fps = videoTracks[0].getSettings().frameRate;
            let webcam_height = videoTracks[0].getSettings().height;
            let webcam_width = videoTracks[0].getSettings().width;

            jsPsych.data.addProperties({
                webcam_label: webcam_label,
                webcam_fps: webcam_fps,
                webcam_height: webcam_height,
                webcam_width: webcam_width,
            });
        })
    ;
}

let fixation = {
    name: "fixation",
    type: 'eyetracking-fix-object',
    x_position: 0.5,
    y_position: 0.5,
    trial_duration: 1500,
    stimulus: '<div style="font-size:60px;">+</div>',
}

let break500 = {
    type: 'html-keyboard-response',
    stimulus: '',
    choices: jsPsych.NO_KEYS,
    trial_duration: 500,
}

let break1500 = {
    type: 'html-keyboard-response',
    stimulus: '',
    choices: jsPsych.NO_KEYS,
    trial_duration: 1500,
}

let break3000 = {
    type: 'html-keyboard-response',
    stimulus: '',
    choices: jsPsych.NO_KEYS,
    trial_duration: 3000,
}

let survey_prolific = {
    type: "survey-html-form",
    preamble:
        "<p>Please enter your Prolific ID. </p>",
    html:
        '<div style="text-align: left;">' +
        '<input name="prolificID" type="text" id="prolificID" placeholder="ID" style="width: 80%;" required>' +
        '</div>' +
        '<br>'
    ,
}


let instruct_monitor = {
    type: 'html-button-response',
    stimulus:
        "<p>Please, use only <strong>one monitor</strong> for this study.<br>" +
        "If necessary, switch off the other monitors.</p>",
    choices: ['Click to continue'],
}



let instruct_mobileDevices = {
    type: 'html-button-response',
    stimulus:
        "<p><strong>Please turn your mobile phone into Airplane Mode and close all CPU- or data-intensive " +
        "programs and websites!</strong><br> " +
        "(e.g. running Youtube Videos or Torrents)</p>",
    choices: ['Click to continue'],
}

let initEyeTracking = {
    type: "eyetracking-init",
    countdown: 10,
    key: 32,
    on_finish: () => {
        webgazer.clearData();
        webgazer.removeMouseEventListeners();
    }
}

let instruct_eyeTracking_light = {
    type: 'html-button-response',
    stimulus:
        '<div style="width: 45%; text-align: left; margin: auto;">' +
        "<p><strong>For a preliminary adjustment, please consider the following instructions: </strong></p>" +
        "<ol>" +
        "<li>Sit at a table and make sure that you could later rest your elbows on it. </li>" +
        "<li>Sit towards a window or lamp so that there are no shadows on your face. " +
        "You might additionally turn on a desk lamp for that. <u>Avoid</u> having a window behind you. </li>" +
        "</ol>" +
        "</div>" +
        '<img src="lightInstruct.PNG" alt="[Eye-Tracking-Instructions]" style="width: 70%;">',
    choices: ['Click to continue'],
    on_start: () => {
        webgazer.resume();
    }
}

let instruct_eyeTracking_2 = {
    stimulus:
        '<div style="width: 45%; text-align: left; margin: auto;">' +
        "<ol start='3'>" +
        "<li>Check the video and stay in the highlighted rectangle so that it becomes green. </li>" +
        "<li>Try as much as possible to follow the instructions on these pictures and avoid " +
        "moving your head. If you move too much, the calibration can fail and you might " +
        "not be able to finish the study. </li>" +
        "<li><strong>If necessary, adjust your laptop, monitor, webcam, or chair. </strong></li>" +
        "</ol>" +
        "</div>" +
        '<img src="ETInstructions.PNG" alt="[Eye-Tracking-Instructions]" style="width: 70%;">',
    type: 'html-button-response',
    choices: ['Click to continue'],
    on_start: () => {
        webgazer.resume();
    },
    on_finish: () => {
        webgazer.pause();
        webgazer.clearData();
    }
}

let instruct_chinFirst_chin = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="width: 45%; margin: auto; text-align: justify;">' +
        '<p>In order to make this measurement as accurate as possible, please rest your head on <u>one</u> of your arms, with your elbow on the desk (see image) ' +
        'You face may be covered a little bit but please keep your eyes visible. ' +
        'Get sure that you stay in the green rectangle in the video stream while doing that. If necessary, adjust your position or the monitor.</p>' +
        '<p>The idea is to keep your head at the same position at all time so that you <strong>only move your eyes</strong> when you look at the screen. </p>' +
        '</div>' +
        '<div style="text-align: center;">' +
        '<img src="chinstruction.PNG" alt="Oh, this image cannot be displayed" style="width: 15%;">' +
        '</div>' +
        '<p style="text-align: center;">Press Space to continue </p>' +
        '</div>' +
        '<br>',
    choices: [32],
    on_start: () => {
        chin = 1;
    }
}

let instruct_chinFirst_noChin = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="width: 45%; margin: auto; text-align: justify;">' +
        '<p>For the third and final task, we will calibrate again. Before that, you can take a short break, loosen your posture and relax your head a little bit. </p> ' +
        '<p><strong>This task will be conducted without the chin rest:</strong> Make  yourself comfortable in front of this monitor and keep your head in a natural position. ' +
        'Get sure that you stay in the green rectangle in the video stream while doing that. </p>' +
        '<p>However, in order to make this measurement as accurate as possible, please keep your head at the same position at all time ' +
        'so that you <strong>only move your eyes</strong> when you look at the screen. </p>' +
        '</div>' +
        '<div>' +
        '<img src="ETInstructions.PNG" alt="Oh, this image cannot be displayed" style="width: 45%;">' +
        '</div>' +
        '<p style="text-align: center;">Press Space to continue </p>' +
        '</div>',
    choices: [32],
    on_start: () => {
        webgazer.clearData();
        chin = 0;
    },
}

let instruct_chinSecond_noChin = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="width: 45%; margin: auto; text-align: justify;">' +
        '<p>For the next task, please do <strong>not</strong> rest your head on your arm but keep your head in a natural position. ' +
        'Get sure that you stay in the green rectangle in the video stream while doing that. </p>' +
        '<p>However, in order to make this measurement as accurate as possible, ' +
        'please keep your head at the same position at all time so that you <strong>only move your eyes</strong> when you look at the screen. </p>' +
        '</div>' +
        '<p style="text-align: center;">Press Space to continue </p>',
    choices: [32],
    on_start: () => {
        chin = 0;
    }
}

let instruct_chinSecond_chin = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="width: 45%; margin: auto; text-align: justify;">' +
        '<p>For the next two tasks, we will calibrate again. Before that, you can take a short break, loosen your posture and relax your head a little bit. </p>' +
        '<p>In order to make this measurement as accurate as possible, ' +
        'please rest your head on <u>one</u> of your arms, with your elbow on the desk (see image). ' +
        'Get sure that you stay in the green rectangle in the video stream while doing that. If necessary, adjust your position or the monitor.' +
        '<p>The idea is to keep your head at the same position at all time so that you <strong>only move your eyes</strong> when you look at the screen. </p>' +
        '</div>' +
        '<div style="text-align: center;">' +
        '<img src="chinstruction.PNG" alt="Oh, this image cannot be displayed" style="width: 20%;">' +
        '</div>' +
        '<p style="text-align: center;">Press Space to continue </p>',
    choices: [32],
    on_start: () => {
        webgazer.clearData();
        chin = 1;
    },
}

let instruct_dontmove = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="text-align: center; position: fixed; top: 40%; left: 10%; width: 80%;">' +

        "<p style='font-size: 30px;'><strong>Don\'t move! </strong><br></p>" +
        "<p style='font-size: 18px;'>Keep your head in the instructed position for the next task. </p><br>" +
        "<p>Press Space to continue </p>",
    choices: [32],
}

let survey_demographics = {
    type: "survey-html-form",
    preamble:
        '<p style="text-align: center;"><strong>The eye-tracking part is complete!</strong> <br>' +
        "Before we end the experiment, we have a few more questions for you. </p>" +
        "<p style=\"text-align: center;\">Please answer these demographic demographic questions. (Page 1/4) <br>" +
        "The data are <strong>completely anonymized.</strong></p>",
    html: '<div style="text-align: left;">' +
        '<table>' +
        '<tr>' +
        '<td>Birth year</td>' +
        '<td><input name="age" type="number" min="1903" max="2001" style="width: 70%;" required</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Gender</td>' +
        '<td>' +
        '<input name="gender" type="radio" id="male" value="male" required>' +
        '<label for="male">Male</label>' +
        '</td>' +
        '<td>' +
        '<input name="gender" type="radio" id="female" value="female" required>' +
        '<label for="female">Female</label>' +
        '</td>' +
        '<td>' +
        '<input name="gender" type="radio" id="diverse"  value="diverse" required>' +
        '<label for="diverse">Non-binary</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Ethnicity</td>' +
        '<td>' +
        '<input name="ethnic" type="radio" id="caucasian" value="caucasian" required>' +
        '<label for="caucasian">Caucasian</label>' +
        '</td>' +
        '<td>' +
        '<input name="ethnic" type="radio" id="black" value="black" required>' +
        '<label for="black">Black</label>' +
        '</td>' +
        '<td>' +
        '<input name="ethnic" type="radio" id="hispanic" value="hispanic" required>' +
        '<label for="hispanic">Hispanic / Latinx</label>' +
        '</td>' +
        '<td>' +
        '<input name="ethnic" type="radio" id="asian" value="asian" required>' +
        '<label for="asian">Asian</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Visual acuity</td>' +
        '<td>' +
        '<input name="sight" type="radio" id="perfectSight" value="perfectSight" required>' +
        '<label for="perfectSight">perfect sight</label>' +
        '</td>' +
        '<td>' +
        '<input name="sight" type="radio" id="glasses" value="glasses" required>' +
        '<label for="glasses">glasses (corrected)</label>' +
        '</td>' +
        '<td>' +
        '<input name="sight" type="radio" id="lenses" value="contactLenses" required>' +
        '<label for="lenses">contact lenses (corrected)</label>' +
        '</td>' +
        '<td>' +
        '<input name="sight" type="radio" id="notCorrected" value="notCorrected" required>' +
        '<label for="notCorrected">not corrected</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Kind of correction</td>' +
        '<td>' +
        '<input name="glasses" type="radio" id="noCorrection" value="noCorrection" required>' +
        '<label for="noCorrection">no correction</label>' +
        '</td>' +
        '<td>' +
        '<input name="glasses" type="radio" id="shortSight" value="shortSight" required>' +
        '<label for="shortSight">near sighted</label>' +
        '</td>' +
        '<td>' +
        '<input name="glasses" type="radio" id="longSight" value="longSight" required>' +
        '<label for="longSight">far sighted</label>' +
        '</td>' +
        '<td>' +
        '<input name="glasses" type="radio" id="progressive" value="progressive" required>' +
        '<label for="progressive">progressive</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Highest degree</td>' +
        '<td>' +
        '<input name="degree" type="radio" id="middleSchool" value="middleSchool">' +
        '<label for="middleSchool">Middle School</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td></td>' +
        '<td>' +
        '<input name="degree" type="radio" id="highSchool" value="highSchool">' +
        '<label for="highSchool">High School</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td></td>' +
        '<td>' +
        '<input name="degree" type="radio" id="college" value="college">' +
        '<label for="college">College / Undergraduate / Bachelor / similar</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td></td>' +
        '<td>' +
        '<input name="degree" type="radio" id="graduate" value="graduate">' +
        '<label for="graduate">Graduate / PhD / Master / similar</label>' +
        '</td>' +
        '</tr>' +
        '</table>' +
        '</div>' +
        '<br>'
    ,
}


let survey_makeup = {
    preamble: "Makeup (Page 2/4) <br><br>",
    type: "survey-html-form",
    html: '<div style="text-align: left;">' +
        '<table>' +
        '<tr>' +
        '<td>Eye-Shadow</td>' +
        '<td>' +
        '<input name="eyeshadow" type="radio" id="yes" value="yes">' +
        '<label for="yes">yes</label>' +
        '<input name="eyeshadow" type="radio" id="no" value="no" checked>' +
        '<label for="no">no</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Masquara</td>' +
        '<td>' +
        '<input name="masquara" type="radio" id="yes" value="yes">' +
        '<label for="yes">yes</label>' +
        '<input name="masquara" type="radio" id="no" value="no" checked>' +
        '<label for="no">no</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Eyeliner</td>' +
        '<td>' +
        '<input name="eyeliner" type="radio" id="yes" value="yes">' +
        '<label for="yes">yes</label>' +
        '<input name="eyeliner" type="radio" id="no" value="no" checked>' +
        '<label for="no">no</label>' +
        '</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Brow-Liner</td>' +
        '<td>' +
        '<input name="browliner" type="radio" id="yes" value="yes">' +
        '<label for="yes">yes</label>' +
        '<input name="browliner" type="radio" id="no" value="no" checked>' +
        '<label for="no">no</label>' +
        '</td>' +
        '</tr>' +
        '</table>' +
        '</div>' +
        '<br>'
    ,
}

let survey_verticalAlignment = {
    type: "survey-html-form",
    preamble:
        "<p>Which picture most closely resembles the vertical " +
        "relation between your eyes and the screen? (Page 3/4)</p>",
    html:
        '<div style="text-align: center;">' +
        '<img src="positions.PNG" alt="Oh, this image cannot be displayed" style="width: 45%;">' +
        '</div>' +
        '<div>' +
        '<input name="vertPosition" type="radio" id="a" value="a" required>' +
        '<label for="a">a) &nbsp &nbsp</label>' +
        '<input name="vertPosition" type="radio" id="b" value="b" required>' +
        '<label for="b">b) &nbsp &nbsp</label>' +
        '<input name="vertPosition" type="radio" id="c" value="c" required>' +
        '<label for="c">c) &nbsp &nbsp</label>' +
        '</div>' +
        '<br>'
    ,
}

let askCompliance = {
    type: "survey-html-form",
    preamble:
        '<div>' +
        '<p>(Page 4/4)</p> ' +
        "<p>Because we cannot see the video or check any " +
        "other way, please answer this question sincerely. Your response will <strong>not</strong> influence your " +
        "financial compensation or the completion of this study: </p>" +
        "</div>" +
        "<br>",
    html: '<div style="text-align: left;">' +
        "<p style='text-align: left;'><strong>Did you try to do the chin rest with your arms?</strong></p>" +
        '<input name="triedChin" type="radio" id="yes" value="yes" required>' +
        '<label for="yes">Yes, I tried &nbsp</label>' +
        '<br>' +
        '<input name="triedChin" type="radio" id="no" value="no" required>' +
        '<label for="no">No, I did not try</label>' +
        '<br><br>' +
        "<p style='text-align: left;'><strong>Could you manage to keep your head at the same position at each task?</strong></p>" +
        '<input name="keptHead" type="radio" id="yes" value="yes" required>' +
        '<label for="yes">Yes, my head stayed still most of the time</label>' +
        '<br>' +
        '<input name="keptHead" type="radio" id="no" value="no" required>' +
        '<label for="no">No, I moved quite a lot</label>' +
        '<br><br>' +
        '<input name="optionalNote" type="text" id="optionalNote" placeholder="Any further Notes" style="width:80%; height:30px;">' +
        '<br><br>' +
        '</div>'
    ,
}

let choiceTaskReward = {
    type: 'html-keyboard-response',
    stimulus: function() {
        const random = Math.floor(Math.random() * subjectChoices.length);
        selectedOption = subjectChoices[random];

        jsPsych.data.addProperties({
            chosenAmount: selectedOption.amount,
            chosenDelay: selectedOption.delay,
        });

        return '<div style=position: fixed; top: 40%; left: 10%; width: 80%;">' +
                '<p><strong>Bonus Payment</strong></p>' +
                '<p>For your Bonus Payment, we randomly selected one of ' +
                'your chosen options from the choice Task: </p>' +
                '<p style="text-align: left; font-weight: bold;">Reward: ' + selectedOption.amount + '</p>' + //convertAmount
                '<p style="text-align: left; font-weight: bold;">Delay: ' + selectedOption.delay + '</p>' + //convertDelay
                '<p>We will send you the reward via Prolific Bonus Payment with the respective delay. ' +
                'If you have any questions, do not hesitate to contact: tim.schneegans@fu-berlin.de.</p>' +
                '<p>Press Space to get your Prolific Code.</p>' +
            '</div>';
    },
    choices: [32],
}

let end = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="position: fixed; display: inline-block; top: 10%; right: 10%; text-align: right;">' +
        '<img src="fu_logo.PNG" alt="[FU Berlin Logo]" style="width: 15%;">' +
        '</div>' +
        "<div style='text-align:left; font-size: small; line-height: 1.1;'>" +
        "<p><strong>Study Title: </strong>Factors that influence the accuracy of webcam-based eye-tracking </p>" +
        "<p><strong>Project manager (also responsible for data protection in the project):</strong> Tim Schneegans, " +
        "tim.schneegans@fu-berlin.de </p>" +
        "<p><strong>Chief data protection officer of the Freie Universität Berlin: </strong>Dr. Karsten Kinast, LL.M. " +
        "datenschutz@fu-berlin.de<br>" +
        "More information: <a href='https://www.fuberlin.de/en/einrichtungen/interessenvertretungen/datenschutz/dahlem/index.html'>" +
        "https://www.fuberlin.de/en/einrichtungen/interessenvertretungen/datenschutz/dahlem/index.html</a> </p>" +
        "<p></p><strong>Berlin officer for data protection and freedom of information:</strong> mailbox@datenschutz-berlin.de<br>" +
        "More information: <a href='https://www.datenschutz-berlin.de/ueber-uns/kontakt/'>" +
        "https://www.datenschutz-berlin.de/ueber-uns/kontakt/</a> </p>" +
        '</div>' +
        '<p style="margin-bottom: 6px;"><strong>Your Prolific Code: </strong></p>' +
        '<div style="border: 5px outset #51B896;background-color: #e2fbff; text-align: center;">' +
        '<strong>82F1A4A9 </strong>' +
        '</div>' +
        '<p style="margin-bottom: 6px;">The following text is optional. Your participation will now be considered as completed. </p>' +
        '<div style="border: 3px outset rgba(163,163,163,0.49); background-color: #f1f1f1; ' +
        'padding: 10px; text-align: center; text-align:justify;">' +
        '<p style="margin-top: 0; margin-bottom: 0;"><i>What was this study about in detail? </i><br>'+
        'This study wants to understand how accurate online eye-tracking devices are and what factors ' +
        'influence their accuracy. Researchers have developed online eye-tracking tools that work with the user’s ' +
        'browser and webcam. Compared to traditional in-lab eye-tracking ' +
        'machines, they could enable researchers from various fields (e.g. decision making, attention or learning ' +
        'behavior) to carry their experiments beyond the campus and work with and therefore apply their findings ' +
        'to people from more diverse demographic backgrounds. In addition, online eye-trackers could save a lot ' +
        'of time, costs, and therefore tax money. In this study, we used the tool Webgazer.js from Prof. ' +
        'Papoutsaki and colleagues (www.webgazer.cs.brown.edu). In the fixation tasks, we were ' +
        'testing the accuracy of the gaze predictions and if an improvised chin-rest could improve the accuracy. ' +
        'In the decision tasks, we tested whether we can replicate established findings from decision making research.' +
        'For any further questions, please do not hesitate to contact tim.schneegans@fu-berlin.de </p>' +
        '</div>',
    choices: [32],
}

let enterFullscreen = {
    type: 'fullscreen',
    fullscreen_mode: true,
    message:
        "<p>This experiment has to be conducted in <strong>full screen mode</strong>. It will end automatically at " +
        "the end of the study.</p><br>",
    data: {
        window_width: function() {return $(window).width();},
        window_height: function() {return $(window).height();}
    }
}

let exitFullscreen = {
    type: 'fullscreen',
    fullscreen_mode: false,
    message: '',
}

let header_task1 = {
    type: 'html-keyboard-response',
    choices: [32],
    stimulus:
        '<div style="text-align: center; position: fixed; top: 35%; left: 10%; width: 80%;  font-size: 60px;">' +
        "<p><strong>Task 1 </strong></p>" +
        "<p style='font-size: 18px;'>Press Space to continue</p>" +
        "</div>",
    on_start: () => {
        task_nr = 1;
    }
}

let header_task2 = {
    type: 'html-keyboard-response',
    choices: [32],
    stimulus:
        '<div style="text-align: center; position: fixed; top: 35%; left: 10%; width: 80%;  font-size: 60px;">' +
        "<p><strong>Task 2 </strong></p>" +
        "<p style='font-size: 18px;'>Press Space to continue</p>" +
        "</div>",
    on_start: () => {
        task_nr = 2;
    }
}

let header_task3 = {
    type: 'html-keyboard-response',
    choices: [32],
    stimulus:
        '<div style="text-align: center; position: fixed; top: 35%; left: 10%; width: 80%;  font-size: 60px;">' +
        "<p><strong>Task 3 </strong></p>" +
        "<p style='font-size: 18px;'>Press Space to continue</p>" +
        "</div>",
    on_start: () => {
        task_nr = 3;
    }
}

let progress_10 = {
    type: 'html-keyboard-response',
    choices: [32],
    stimulus:
        '<div style="text-align: center; position: fixed; top: 35%; left: 10%; width: 80%;">' +
        '<p style="font-size: 18px;">You completed the study to </p>' +
        '<p style="font-size: 40px; margin: 10px;"><strong>10% </strong></p><br>' +
        "<p style='font-size: 18px;'>Press Space to continue</p>" +
        "</div>",
}

let progress_30 = {
    type: 'html-keyboard-response',
    choices: [32],
    stimulus:
        '<div style="text-align: center; position: fixed; top: 35%; left: 10%; width: 80%;">' +
        '<p style="font-size: 18px;">You completed the study to </p>' +
        '<p style="font-size: 40px; margin: 10px;"><strong>30% </strong></p><br>' +
        "<p style='font-size: 18px;'>Press Space to continue</p>" +
        "</div>",
}

let progress_50 = {
    type: 'html-keyboard-response',
    choices: [32],
    stimulus:
        '<div style="text-align: center; position: fixed; top: 35%; left: 10%; width: 80%;">' +
        '<p style="font-size: 18px;">You completed the study to </p>' +
        '<p style="font-size: 40px; margin: 10px;"><strong>50% </strong></p><br>' +
        "<p style='font-size: 18px;'>Press Space to continue</p>" +
        "</div>",
}

let progress_70 = {
    type: 'html-keyboard-response',
    choices: [32],
    stimulus:
        '<div style="text-align: center; position: fixed; top: 35%; left: 10%; width: 80%;">' +
        '<p style="font-size: 18px;">You completed the study to </p>' +
        '<p style="font-size: 40px; margin: 10px;"><strong>70% </strong></p><br>' +
        "<p style='font-size: 18px;'>Press Space to continue</p>" +
        "</div>",
}

let progress_90 = {
    type: 'html-keyboard-response',
    choices: [32],
    stimulus:
        '<div style="text-align: center; position: fixed; top: 35%; left: 10%; width: 80%;">' +
        '<p style="font-size: 18px;">You completed the study to </p>' +
        '<p style="font-size: 40px; margin: 10px;"><strong>90% </strong></p><br>' +
        "<p style='font-size: 18px;'>Press Space to continue</p>" +
        "</div>",
}

let hideVideo = {
    type: 'html-keyboard-response',
    stimulus: '',
    trial_duration: 100,
    on_start: () => {
        $('#webgazerVideoFeed').hide();
        $('#webgazerFaceFeedbackBox').hide();
    }
}

let showVideo = {
    type: 'html-keyboard-response',
    stimulus: '',
    trial_duration: 100,
    on_start: () => {
        $('#webgazerVideoFeed').show();
        $('#webgazerFaceFeedbackBox').show();
    }
}

let darkBackground = {
    type: 'html-keyboard-response',
    stimulus: '',
    trial_duration: 100,
    on_start: () => {
        $(".jspsych-content-wrapper").css({'background-color': 'black', 'color': 'white'});
    }
}

let whiteBackground = {
    type: 'html-keyboard-response',
    stimulus: '',
    trial_duration: 100,
    on_start: () => {
        $(".jspsych-content-wrapper").css({'background-color': 'white', 'color': 'black'});
    }
}

let hideCursor = {
    type: 'html-keyboard-response',
    stimulus: '',
    trial_duration: 100,
    on_start: () => {
        $(document.body).css('cursor', 'none');
    }
}

let showCursor = {
    type: 'html-keyboard-response',
    stimulus: '',
    trial_duration: 100,
    on_start: () => {
        $(document.body).css('cursor', 'auto');
    }
}

/***************************************************************
 * Calibration
 * @type {{randomize_order: boolean, on_start: cal_procedure.on_start, timeline: [{on_start: function(): void, on_finish: function(): void, stimulus: function(): string, type: string, choices: *, trial_duration: number}, {y_position: *, x_position: *, data: {window_width: function(): *, window_height: function(): *}, on_start: function(): void, on_finish: function(): void, clickNr: number, stimulus: string, name: string, type: string}], timeline_variables: ({x: number, y: number})[], repetitions: number}}
 */

let calInstruct = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="position: fixed; top: 30%; left: 27.5%; width: 45%; margin: auto; text-align: justify;">' +
        '<p>For calibration purposes, there will be buttons (' + calRepetitions * 13 + ' in total) appearing one after another. <strong>' +
        'Click ' + calClickNr + 'x on each button</strong> until it turns green. Then the next button will appear. ' +
        'This will take around <strong>3 minutes. </strong></p>' +
        '<p>For an accurate measurement, please <strong><u>always</u></strong> follow the mouse cursor with your eyes. </p><br>' +
        '<p style="text-align: center;">Press Space to continue</p>' +
        '</div>',
    choices: [32],
}

let calInstruct_again = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="width: 45%; margin: auto; text-align: justify;">' +
        '<div style="position: fixed; top: 30%; left: 27.5%; width: 45%; margin: auto; text-align: justify;">' +
        '<p>Before the next task, we are going to calibrate one last time. ' +
        '<strong>Click ' + calClickNr + 'x on each of the calibration buttons</strong> that ' +
        'will appear on the next page. This will take around <strong>3 minutes. </strong></p>' +
        '<p>For an accurate measurement, please <strong>always</strong> follow the mouse cursor with your eyes. </p><br>' +
        '<p style="text-align: center;">Press Space to continue</p>' +
        '</div>',
    choices: [32],
}

let calInstruct_askSure = {
    type: 'html-keyboard-response',
    stimulus: "<p><strong>Can you stay in that pose for a while?</strong></p>" +
        "<p>If not, then please adjust now in order to be comfortable.</p><br>" +
        "<p>Press Space to continue</p>",
    choices: [32],
}
let cal_positions = null;
if (pilot === 1) {
    cal_positions = [
        {x: 0.20, y: 0.80},
        {x: 0.50, y: 0.50},
        {x: 0.80, y: 0.80},
    ];
} else {
    cal_positions = [
        {x: 0.20, y: 0.20},
        {x: 0.20, y: 0.50},
        {x: 0.20, y: 0.80},

        {x: 0.35, y: 0.35},
        {x: 0.35, y: 0.65},

        {x: 0.50, y: 0.20},
        {x: 0.50, y: 0.50},
        {x: 0.50, y: 0.80},

        {x: 0.65, y: 0.35},
        {x: 0.65, y: 0.65},

        {x: 0.80, y: 0.20},
        {x: 0.80, y: 0.50},
        {x: 0.80, y: 0.80},
    ];
}

let cal_trial = {
    name: "calibration",
    type: 'eyetracking-calibration',
    x_position: jsPsych.timelineVariable('x'),
    y_position: jsPsych.timelineVariable('y'),
    stimulus: '<button ' +
        'style="' +
        'width: 50px; height: 50px;' +
        '-webkit-border-radius: 25px;' +
        '-moz-border-radius: 25px;' +
        'border-radius: 25px;' +
        'background-color: deepskyblue;' +
        'border-color: ivory;' +
        'border-style: solid;"></button>',
    clickNr: calClickNr,
    on_start: () => {
        webgazer.addMouseEventListeners();
    },
    on_finish: () => {
        webgazer.removeMouseEventListeners();
    }
}

let break1500_cal = {
    type: 'html-keyboard-response',
    stimulus: function() {
        let html='';
        if (cal_trialNr === maxCalDots) {
            cal_trialNr = 1;
        }
        if ((cal_trialNr%13 === 0) &&
            (cal_trialNr < maxCalDots-10)) {
            html +=
                '<div style="font-size:30px;">' +
                "<p><strong>" +
                Math.floor(10*cal_trialNr/maxCalDots) * 10 +
                "%</strong><br><br>Calibration complete</p>" +
                "</div>";
        }
        cal_trialNr++;
        return html;
    },
    choices: jsPsych.NO_KEYS,
    trial_duration: 1500,
}

let cal_procedure = {
    timeline: [break1500_cal, cal_trial],
    timeline_variables: cal_positions,
    randomize_order: true,
    repetitions: calRepetitions,
}

/**************************************************************
 * Fixation Task
 * @type {{stimulus: string, type: string, choices: [number]}}
 */

let fixTask_instruct = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="text-align: center; position: fixed; top: 40%; left: 10%; width: 80%;">' +
        '<p>For measurement purposes, <strong>dots</strong> (9 in total) will be appearing ' +
        'on the next page one after another. ' +
        'First, <u>look</u> at the <strong>fixation cross</strong> in the center. When the cross disappears, ' +
        '<strong>look for 5 seconds at each dot</strong> that will appear randomly on the screen.</p>' +
        '<p>Press Space to continue</p>' +
        '</div>',
    choices: [32],
}

let fixTask_instruct_again = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="text-align: center; position: fixed; top: 40%; left: 10%; width: 80%;">' +
        '<p>Just as before, please <u>look</u> at the dots that will appear on the next page. First, look at the ' +
        '<strong>fixation cross</strong> in the center and then <strong>look for 5 seconds at each dot.' +
        '</strong></p>' +
        '<p>Press Space to continue</p>' +
        '</div>',
    choices: [32],
}

let fixTask_positions = null;
if (pilot === 1) {
    fixTask_positions = [
        {x: 0.20, y: 0.20},
        {x: 0.50, y: 0.50},
        {x: 0.80, y: 0.80},
    ];
} else {
    fixTask_positions = [
        {x: 0.20, y: 0.20},
        {x: 0.20, y: 0.50},
        {x: 0.20, y: 0.80},

        {x: 0.50, y: 0.20},
        {x: 0.50, y: 0.50},
        {x: 0.50, y: 0.80},

        {x: 0.80, y: 0.20},
        {x: 0.80, y: 0.50},
        {x: 0.80, y: 0.80},
    ];

}

let fixTask_trial = {
    name: "task1",
    type: 'eyetracking-fix-object',
    x_position: jsPsych.timelineVariable('x'),
    y_position: jsPsych.timelineVariable('y'),
    trial_duration: tFixation,
    stimulus: '<button ' +
        'style="' +
        'width: 50px; height: 50px;' +
        '-webkit-border-radius: 25px;' +
        '-moz-border-radius: 25px;' +
        'border-radius: 25px;' +
        'background-color: deepskyblue;' +
        'border-color: ivory;' +
        'border-style: solid;"></button>',
}

let fixTask_procedure = {
    timeline: [break1500, fixation, break500, fixTask_trial],
    timeline_variables: fixTask_positions,
    randomize_order: true,
}

/*******************************************************************
 * Choice Task
 * @type {{stimulus: string, type: string, choices: [number]}}
 *****/

let choiceTask_instruct_1 = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="width: 45%; margin: auto; text-align: justify;">' +
        '<p>For this task, we will ask you to make <strong>repeated choices between two options</strong> on ' +
        'the top and the bottom of the screen. One side at both options contains a ' +
        '<strong>reward</strong>. The other side on both options contains a <strong>delay</strong> ' +
        'corresponding to the respective reward.</p>' +
        '<p>For example, you can decide between $5 in 180 days vs $2 today. Press the <strong>upwards arrow key ' +
        '&uarr;</strong> to choose the top option. Press the <strong>downwards arrow key &darr;</strong> for the ' +
        'bottom option.</p>' +
        '<p>There will be ' + NChoiceTaskTrials + ' choices, that will take <strong>' +
        'ca. 7 minutes in total.</strong> We will inform you about your progress.</p>' +
        '</div>' +
        '<div style="text-align: center;">' +
        '<img src="choiceTask.PNG" alt="[Choice Task Instruction]" style="width: 20%;">' +
        '</div>' +
        '<div style="text-align: center;">' +
        '<p>Press Space to continue</p>' +
        '</div>',
    choices: [32],
}

let choiceTask_instruct_2 = {
    type: 'html-keyboard-response',
    stimulus:
        '<div style="width: 45%; margin: auto; text-align: justify;">' +
        '<p>The chosen option will be assigned to a lottery pot of which one reward will be ' +
        'randomly chosen and <strong>sent to you as a bonus payment.</strong></p>' +
        '<p>Press the <strong>upwards arrow key &uarr;</strong> for the top option.<br> ' +
        '<p>Press the <strong>downwards arrow key &darr;</strong> for the bottom option.</p>' +
        '</div>' +
        '<div>' +
        '<p>Press Space to continue</p>' +
        '</div>',
    choices: [32],
}

let break1500_choice_switch_amountRight = {
    type: 'html-keyboard-response',
    stimulus: function() {
        let html='<div style="font-size:18px;">' +
            "<p>Now, the left and right side of the " +
            "amount and time information are <strong>switched, </strong><br> " +
            "with amount on the right and time on the left side.</p> " +
            "</div>";
        return html;
    },
    choices: jsPsych.NO_KEYS,
    trial_duration: 3000,
}

let break1500_choice_switch_amountLeft = {
    type: 'html-keyboard-response',
    stimulus: function() {
        let html='<div style="font-size:18px;">' +
            "<p>Now, the left and right side of the " +
            "amount and time information are <strong>switched, </strong><br> " +
            "with amount on the left and time on the right side.</p> " +
            "</div>";
        return html;
    },
    choices: jsPsych.NO_KEYS,
    trial_duration: 3000,
}

aSS = Array(10).fill().map((element, index) => 0.5 + index * 0.5);
tSS = [0]
aLL = Array(3).fill().map((element, index) => 4 + index * 0.5);
tLL = [1, 7, 15, 30, 90, 180];

let choiceTask_stimuli_full = [];
for (i_aSS=0; i_aSS<aSS.length; i_aSS++) {
    for (i_aLL = 0; i_aLL<(aLL.length); i_aLL++) {
        for (i_tLL = 0; i_tLL<(tLL.length); i_tLL++) {

            if (aSS[i_aSS] < aLL[i_aLL]) {
                let k = ((aLL[i_aLL] / aSS[i_aSS]) - 1) / tLL[i_tLL];
                if(k <= 0.333334) {
                    choiceTask_stimuli_full.push({
                        'aT': aSS[i_aSS],
                        'tT': 0,
                        'aB': aLL[i_aLL],
                        'tB': tLL[i_tLL],
                        data: {
                            'test_part': 'choiceTask',
                            'aSS': aSS[i_aSS],
                            'aLL': aLL[i_aLL],
                            'tSS': 0,
                            'tLL': tLL[i_tLL],
                            'k': k,
                            'llOnTop': 0
                        }
                    });

                    choiceTask_stimuli_full.push({
                        'aT': aLL[i_aLL],
                        'tT': tLL[i_tLL],
                        'aB': aSS[i_aSS],
                        'tB': 0,
                        data: {
                            'test_part': 'choiceTask',
                            'aSS': aSS[i_aSS],
                            'aLL': aLL[i_aLL],
                            'tSS': 0,
                            'tLL': tLL[i_tLL],
                            'k': k,
                            'llOnTop': 1
                        }
                    });
                }
            }

        }
    }
}

// https://bost.ocks.org/mike/shuffle/
function shuffle(array) {
    var m = array.length, t, i;
    while (m) {
        i = Math.floor(Math.random() * m--);
        t = array[m];
        array[m] = array[i];
        array[i] = t;
    }

    return array;
}
let choiceTask_stimuli_1 = choiceTask_stimuli_full.slice(shuffle(choiceTask_stimuli_full).length-(NChoiceTaskTrials/2));
let choiceTask_stimuli_2 = choiceTask_stimuli_full.slice(shuffle(choiceTask_stimuli_full).length-(NChoiceTaskTrials/2));

let choiceTask_trial_amountLeft = {
    type: 'eyetracking-choice',
    name: "choice",
    option_topLeft: () => {return convertAmount(
        jsPsych.timelineVariable('aT', true));
    },
    option_topRight: () => {return convertDelay(
        jsPsych.timelineVariable('tT', true)
    );
    },
    option_bottomLeft: () => {return convertAmount(
        jsPsych.timelineVariable('aB', true)
    );
    },
    option_bottomRight: () => {return convertDelay(
        jsPsych.timelineVariable('tB', true)
    );
    },
    choices: [38, 40],
    amountLeft: 1,
}

let choiceTask_trial_amountRight = {
    type: 'eyetracking-choice',
    name: "choice",
    option_topLeft: () => {return convertDelay(
        jsPsych.timelineVariable('tT', true)
    );
    },
    option_topRight: () => {return convertAmount(
        jsPsych.timelineVariable('aT', true)
    );
    },
    option_bottomLeft: () => {return convertDelay(
        jsPsych.timelineVariable('tB', true)
    );
    },
    option_bottomRight: () => {return convertAmount(
        jsPsych.timelineVariable('aB', true)
    );
    },
    choices: [38, 40],
    amountLeft: 0,
}

let break1500_choice = {
    type: 'html-keyboard-response',
    stimulus: function() {
        let html='';
        if ((choiceTask_trialNr%(NChoiceTaskTrials/5) === 0) &&
            (choiceTask_trialNr < NChoiceTaskTrials-10)) {
            html +=
                '<div style="font-size:30px;">' +
                "<p>You finished <br><br><strong>" +
                Math.floor(10*choiceTask_trialNr/NChoiceTaskTrials) * 10 +
                "%</strong></p>" +
                "</div>";
        }
        choiceTask_trialNr++;
        return html;
    },
    choices: jsPsych.NO_KEYS,
    trial_duration: 1500,
}

let choiceTask_procedure_amountLeft = {
    timeline: [break1500_choice, fixation, choiceTask_trial_amountLeft],
    timeline_variables: choiceTask_stimuli_1,
    randomize_order: true,
    on_start: () => {
        choiceTaskActive = 1;
    },
}

let choiceTask_procedure_amountRight = {
    timeline: [break1500_choice, fixation, choiceTask_trial_amountRight],
    timeline_variables: choiceTask_stimuli_2,
    randomize_order: true,
    on_start: () => {
        choiceTaskActive = 1;
    },
}

function convertAmount(myVar) {
    let a = parseFloat(myVar);
    if (a < 1) {
        a = String(Math.round(a * 100)) + " cent";
    }
    else if ((a % Math.floor(a))===0) {
        a = "$" + String(Math.round(a));
    } else {
        a = "$" + String(Math.round(a*100)/100);
    }
    return String(a);
}

function convertDelay(myVar) {
    let t = parseInt(myVar);
    if (t === 0) {
        t = "Today";
    } else if (t === 1) {
        t = "Tomorrow";
    } else if (t === 365) {
        t = "1 year";
    } else {
        t = String(t) + " days";
    }
    return t;
}

/****************************************************************
 * Compiling the timeline
 */

let calibration = {
    timeline: [
        darkBackground,
        hideVideo,
        cal_procedure, break3000,
        showVideo,
        whiteBackground
    ]
}

let fixTask = {
    timeline: [
        darkBackground,
        hideCursor,
        hideVideo,
        fixTask_procedure, break3000,
        showVideo,
        showCursor,
        whiteBackground
    ]
}

let choiceTask = null;

if (choiceTask_amountLeftFirst === 1) {
    choiceTask = {
        timeline: [
            choiceTask_instruct_1, choiceTask_instruct_2,
            darkBackground,
            hideCursor,
            hideVideo,
            choiceTask_procedure_amountLeft, break1500_choice_switch_amountRight, choiceTask_procedure_amountRight, break3000,
            showCursor,
            whiteBackground,
        ]
    }
} else {
    choiceTask = {
        timeline: [
            choiceTask_instruct_1, choiceTask_instruct_2,
            darkBackground,
            hideCursor,
            hideVideo,
            choiceTask_procedure_amountRight, break1500_choice_switch_amountLeft, choiceTask_procedure_amountLeft, break3000,
            showCursor,
            whiteBackground,
        ]
    }
}

timeline.push(
    whiteBackground,
    welcome,
    survey_prolific,
    instruct_monitor,
    instruct_mobileDevices,
    initEyeTracking,
    showVideo,
    instruct_eyeTracking_light, instruct_eyeTracking_2,
    hideVideo,
    enterFullscreen, showVideo,
);

if (chinFirst === 1) {
    timeline.push(
        instruct_chinFirst_chin, calInstruct_askSure,
        calInstruct, calibration,
        instruct_dontmove,
        header_task1, fixTask_instruct, fixTask,
        instruct_dontmove,
        progress_30,
        header_task2, choiceTask, choiceTaskReward,
        showVideo, instruct_chinFirst_noChin, hideVideo,
        calInstruct_again, calibration,
        instruct_dontmove,
        progress_70,
        header_task3, fixTask_instruct_again, fixTask
    );
} else if (chinFirst === 0) {
    timeline.push(
        instruct_chinSecond_noChin, calInstruct_askSure,
        calInstruct, calibration,
        instruct_dontmove,
        header_task1, fixTask_instruct, fixTask,
        progress_30,
        showVideo, instruct_chinSecond_chin, hideVideo,
        calInstruct_again, calibration,
        instruct_dontmove,
        header_task2, fixTask_instruct_again, fixTask,
        instruct_dontmove,
        progress_70,
        header_task3, choiceTask, choiceTaskReward,
    );
}

timeline.push(
    hideVideo,
    exitFullscreen,
    progress_90,
    survey_demographics, survey_makeup,
    survey_verticalAlignment,
    askCompliance,

    end,

);

function startExperiment() {
    jsPsych.init({
        timeline: timeline
    });
};