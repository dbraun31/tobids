'''
A collection of metadata needed to parse both GradCPT and
ExperienceSampling data
'''

# GRAD CPT

gradcpt_headers = ['cue', 'constant1', 'onset', 'stimulus_coherence',
                   'response_time', 'response', 'constant2']

gradcpt_json = {
        'cue': {
            'LongName': 'Cue image',
            'Description': 'The type of image (city/mountain) presented to participants where cities are non-targets and mountains are targets',
            'Levels': {
                '1': 'Target (mountain) nogo trial',
                '2': 'Non-target (city) go trial'
                }
            },

        'onset': {
            'Description': 'Onset time in seconds'
            },

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

        'att_resp': {
            'question_wording': 'Were you more focused on your thoughts (mental) or sensing the world or your body (phsysical)? (or if your mind was blank press the 0 key)',

            'Description': 'Determine whether your attention was on your thoughts (mental) or something tangible on your body or the environment (physical) or if you are unable to recall thinking about anything (mind blank)',

            'low_anchor': 'completely physical',
            
            'high_anchor': 'completely mental'

            },

        'att_RT': {
            'Description': 'Response time in seconds'
            },

        'att_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'att_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'past_response': {
            'question_wording': 'Were your thoughts oriented towards the past?',

            'Description': 'Determine where your thoughts were located in time',

            'low_anchor': 'not past oriented',
            
            'high_anchor': 'completely past oriented'

            },

        'past_RT': {
            'Description': 'Response time in seconds'
            },

        'past_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'past_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'fut_response': {
            'question_wording': 'Were your thoughts oriented towards the future?',

            'Description': 'Determine where your thoughts were located in time',

            'low_anchor': 'not future oriented',
            
            'high_anchor': 'completely future oriented'

            },

        'future_RT': {
            'Description': 'Response time in seconds'
            },

        'future_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'future_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'self_response': {
            'question_wording': 'Were your thoughts about yourself?',

            'Description': 'Think about whether your thoughts were focused on yourself, or matters related to you',

            'low_anchor': 'nothing about you',
            
            'high_anchor': 'completely about you'

            },

        'self_RT': {
            'Description': 'Response time in seconds'
            },

        'self_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'self_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'ppl_response': {
            'question_wording': 'Were your thoughts about others?',

            'Description': 'Think about whether your thoughts were focused on others, or matters related to others',

            'low_anchor': 'nothing about others',
            
            'high_anchor': 'completely about others'

            },

        'others_RT': {
            'Description': 'Response time in seconds'
            },

        'others_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'others_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'arou_response': {
            'question_wording': 'How activated or energized were you feeling?',

            'Description': 'Activation (or arousal) includes feelings of energy linked to emotion.',

            'low_anchor': 'completely deactivated',
            
            'high_anchor': 'completely activated'

            },

        'arou_RT': {
            'Description': 'Response time in seconds'
            },

        'arou_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'arou_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },
        

        'aff_response': {
            'question_wording': 'How positive or negative were you feeling?',

            'Description': 'How positive or negative you felt while having these thoughts',

            'low_anchor': 'completely negative',
            
            'high_anchor': 'completely positive'

            },

        'aff_RT': {
            'Description': 'Response time in seconds'
            },

        'aff_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'aff_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'eng_response': {
            'question_wording': 'How easy was it to disengage from your thoughts?',

            'Description': 'Think about how easy it was to pull yourself away from your thoughts at the onset of the probe',

            'low_anchor': 'extremely easy',
            
            'high_anchor': 'extremely hard'

            },

        'eng_RT': {
            'Description': 'Response time in seconds'
            },

        'eng_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'eng_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'mvmt_response': {
            'question_wording': 'Were your thoughts freely moving?',

            'Description': 'Think about the last few seconds before the questions popped up and whether you were focused on one thought for an extended period of time (unmoving) or if your thoughts were drifting from one thing to another without focusing on any single thought for long (freely moving).',

            'low_anchor': 'unmoving',
            
            'high_anchor': 'moving freely'

            },

        'mvmt_RT': {
            'Description': 'Response time in seconds'
            },

        'mvmt_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'mvmt_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'delib_response': {
            'question_wording': 'How intentional were your thoughts?',

            'Description': 'Think about whether you directed your attention to a certain task or thoughts with purpose or if your thoughts popped into your mind without intending to do so.',

            'low_anchor': 'completely unintentional',
            
            'high_anchor': 'completely intentional'

            },

        'delib_RT': {
            'Description': 'Response time in seconds'
            },

        'delib_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'delib_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'image_response': {
            'question_wording': 'Were your thoughts visual?',

            'Description': 'Think about whether your thoughts took the form of images',

            'low_anchor': 'completely visual',
            
            'high_anchor': 'completely non-visual'

            },

        'visual_RT': {
            'Description': 'Response time in seconds'
            },

        'visual_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'visual_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },



        'ling_response': {
            'question_wording': 'Were your thoughts verbal',

            'Description': 'Were your thoughts manifesting as a voice in your head or were your thoughts oriented as words or using language.',

            'low_anchor': 'completely verbal',
            
            'high_anchor': 'completely non-verbal'

            },

        'verbal_RT': {
            'Description': 'Response time in seconds'
            },

        'verbal_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'verbal_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            },


        'conf_response': {
            'question_wording': 'How confident are you about your ratings for this trial?',

            'Description': 'How accurately you were able to remember and categorize your thoughts by answering the questions, and how strongly you believe they reflect your last thought.',

            'low_anchor': 'completely confident',
            
            'high_anchor': 'completely unconfident'

            },

        'conf_RT': {
            'Description': 'Response time in seconds'
            },

        'conf_onset': {
            'Description': 'Onset of item wording on screen in seconds'
            },

        'conf_offset': {
            'Description': 'Offset of item wording off of screen in seconds'
            }

        }
