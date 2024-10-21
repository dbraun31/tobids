'''
A collection of metadata needed to parse both GradCPT and
ExperienceSampling data
'''

# GRAD CPT

gradcpt_headers = ['cue', 'constant1', 'timestamp', 'stimulus_coherence',
                   'response_time', 'response', 'constant2']

gradcpt_json = {
        'onset': {
            'Description': 'Onset time in seconds when stimulus on current trial is at 1% coherence. Timelocked to fMRI scan start.'
            },
        'duration': {
            'Description': 'Duration of trial in seconds.'
            },
        'cue': {
            'LongName': 'Cue image',
            'Description': 'The type of image (city/mountain) presented to participants where cities are non-targets and mountains are targets',
            'Levels': {
                '1': 'Target (mountain) nogo trial',
                '2': 'Non-target (city) go trial'
                }
            },

        'timestamp': {
            'Description': 'The timestamp recorded from the GradCPT Matlab script on each trial.'},


        'stimulus_coherence': {
            'Description': 'The coherence of the image to be judged on trial N as compared to trial N-1.'
            },

        'response_time': {
            'Description': 'Response time in seconds calculated as the amount of time that has elapsed from when the N-1 image was at 100% coherence to the time of the response made by the participant.'
            },

        'response': {
            'LongName': 'Coded response from the participant',
            'Description': 'Whether a commission response was correct / incorrect or whether a response was omitted.',
            'Levels': {
                '1': 'Correct commission response',
                '0': 'No response',
                '-1': 'Incorrect commission response'
                }
            }
        }

                

# EXPERIENCE SAMPLING

es_json = {
        'onset': 'Onset of item wording on screen in cumulative seconds since start of scan.',
        'duration': 'Duration of item wording on screen in seconds since start of scan.',
        'offset': 'Offset of item wording on screen in cumulative seconds since start of scan.',
        'trial': 'The number ID of experience sampling probe in ascending order.',
        'item': {
            'aff': {
                'question_wording': 'How positive or negative were you feeling?',
                'description': 'How positive or negative you felt while having these thoughts.',
                'low_anchor': 'completely negative',
                'high_anchor': 'completely positive'},

            'arou': {
                'question_wording': 'How activated or energized were you feeling?',
                'description': 'Activation (or arousal) includes feelings of energy linked to emotion.',
                'low_anchor': 'completely deactivated',
                'high_anchor': 'completely activated'},

            'att' : {
                'question_wording': 'Were you more focused on your thoughts (mental) or sensing the world or your body (phsysical)? (or if your mind was blank press the 0 key)',
                'description': 'Determine whether your attention was on your thoughts (mental) or something tangible on your body or the environment (physical) or if you are unable to recall thinking about anything (mind blank).',
                'low_anchor': 'completely physical',
                'high_anchor': 'completely mental'},

            'conf': {
                'question_wording': 'How confident are you about your ratings for this trial?',
                'description': 'How accurately you were able to remember and categorize your thoughts by answering the questions, and how strongly you believe they reflect your last thought.',
                'low_anchor': 'completely unconfident',
                'high_anchor': 'completely confident'},
            'delib': {
                'question_wording': 'How intentional were your thoughts?',
                'description': 'Think about whether you directed your attention to a certain task or thoughts with purpose or if your thoughts popped into your mind without intending to do so.',
                'low_anchor': 'completely unintentional',
                'high_anchor': 'completely intentional'},
            'eng': {
                'question_wording': 'How easy was it to disengage from your thoughts?',
                'description': 'Think about how easy it was to pull yourself away from your thoughts at the onset of the probe.',
                'low_anchor': 'extremely easy',
                'high_anchor': 'extremely difficult'},
            'fut': {
                'question_wording': 'Were your thoughts oriented towards the future?',
                'description': 'Determine where your thoughts were located in time.',
                'low_anchor': 'not future oriented',
                'high_anchor': 'completely future oriented'},
            'image': {
                'question_wording': 'Were your thoughts visual?',
                'description': 'Think about whether your thoughts took the form of images.',
                'low_anchor': 'completely visual',
                'high_anchor': 'completely non-visual'},
            'ling': {
                'question_wording': 'Were your thoughts verbal?',
                'description': 'Were your thoughts manifesting as a voice in your head or were your thoughts oriented as words or using language?',
                'low_anchor': 'completely verbal',
                'high_anchor': 'completely non-verbal'},
            'mvmt': {
                'question_wording': 'Were your thoughts freely moving?',
                'description': 'Think about the last few seconds before the questions popped up and whether you were focused on one thought for an extended period of time (unmoving) or if your thoughts were drifting from one thing to another without focusing on any single thought for long (freely moving).',
                'low_anchor': 'unmoving',
                'high_anchor': 'moving freely'},
            'past': {
                'question_wording': 'Were your thoughts oriented towards the past?',
                'description': 'Determine where your thoughts were located in time.',
                'low_anchor': 'not past oriented',
                'high_anchor': 'completely past oriented'},
            'ppl': {
                'question_wording': 'Were your thoughts about others?',
                'description': 'Think about whether your thoughts were focused on others, or matters related to others.',
                'low_anchor': 'nothing about others',
                'high_anchor': 'completely about others'},
            'self': {
                'question_wording': 'Were your thoughts about yourself?',
                'description': 'Think about whether your thoughts were focused on yourself, or matters related to you.',
                'low_anchor': 'nothing about you',
                'high_anchor': 'completely about you'}
            },

        'offset': 'Offset of wording from screen in cumulative seconds.',
        'response': 'Response made by participant on the scale',
        'event_type': 'If a real-time fMRI study, whether this probe triggered by a brain event or a timeout.'
}
         



