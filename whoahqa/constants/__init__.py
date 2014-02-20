CLINIC_IDENTIFIER = 'facility_info/clinic_id'
CHARACTERISTIC = 'facility_info/HS_char'
XFORM_ID = '_xform_id_string'

# Client Tool Constants
ADOLESCENT_CLIENT = 'adolescent_quality_assementEnSp'
HEALTH_CARE_PROVIDER = 'health_care_provider_interview_EnSp'
SUPPORT_STAFF = 'support_staff_interview_EnSp'
HEALTH_FACILITY_MANAGER = 'health_facility_manager_interview_EnSp'
OUTREACH_WORKER = 'outreach_worker_interview_EnSp'
COMMUNITY_MEMBER = 'community_member_interview_EnSp'
ADOLESCENT_IN_COMMUNITY = 'adolescent_in_community_tool_EnSp'
OBSERVATION_GUIDE = 'observation_guide_EnSp'

# Clinic registration
CLINIC_REGISTRATION = 'clinic_registration'

CLIENT_TOOLS = [
    (ADOLESCENT_CLIENT, u"AC"),
    (HEALTH_CARE_PROVIDER, u"HC"),
    (SUPPORT_STAFF, u"SS"),
    (HEALTH_FACILITY_MANAGER, u"M"),
    (OUTREACH_WORKER, u"OW"),
    (COMMUNITY_MEMBER, u"CM"),
    (ADOLESCENT_IN_COMMUNITY, u"A in C"),
    (OBSERVATION_GUIDE, u"OG")
]

ONE = 'one'
TWO = 'two'
THREE = 'three'
FOUR = 'four'
FIVE = 'five'
SIX = 'six'
SEVEN = 'seven'
EIGHT = 'eight'
NINE = 'nine'
TEN = 'ten'
ELEVEN = 'eleven'
TWELVE = 'twelve'
THIRTEEN = 'thirteen'
FOURTEEN = 'fourteen'
FIFTEEN = 'fifteen'
SIXTEEN = 'sixteen'
SEVENTEEN = 'seventeen'
EIGHTEEN = 'eighteen'
NINETEEN = 'nineteen'
TWENTY = 'twenty'

CHARACTERISTICS = [
    (ONE, u"Policies and procedures are in place that do not restrict the "
          u" provision of health services on any terms"),
    (TWO, u"Health-care providers treat all adolescent clients with equal"
          u" care and respect, regardless of status"),
    (THREE, u"Support staff treat all adolescent clients with equal care"
            u" and respect, regardless of status"),
    (FOUR, u"Policies and procedures are in place that ensure that health"
           u" services are either free or affordable to adolescents"),
    (FIVE, u"The point of health service delivery has convenient hours of"
           u" operation"),
    (SIX, u"Adolescents are well-informed about the range of available"
          u" reproductive health services and how to obtain them"),
    (SEVEN, u"Community members understand the benefits that adolescents"
            u" will gain by obtaining the health services they need,"
            u" and support their provision"),
    (EIGHT, u"Some health services and health-related commodities are"
            u" provided to adolescents in the community by selected"
            u" community members, outreach workers and adolescents"
            u" themselves"),
    (NINE, u"Policies and procedures are in place that guarantee client"
           u" confidentiality"),
    (TEN, u"The point of health service delivery ensures privacy"),
    (ELEVEN, u"Health-care providers are non-judgemental, considerate and"
             u" easy to relate to"),
    (TWELVE, u"The point of health service delivery ensures consultations"
             u" occur in a short waiting time. with or without an"
             u" appointment, and (where necessary) with referral"),
    (THIRTEEN, u"The point of health service delivery has an appealing"
               u" and clean environment"),
    (FOURTEEN, u"The point of health service delivery provides information"
               u" and education through a variety of channels"),
    (FIFTEEN, u"Adolescents are actively involved in designing, assessing"
              u" and providing health services"),
    (SIXTEEN, u"The required package of health care is provided to fulfil"
              u" the needs of all adolescents either at the point of health"
              u" service delivery or through referral linkages"),
    (SEVENTEEN, u"Health-care providers have the required competencies to"
                u" work with adolescents and to provide them with the"
                u" required health services"),
    (EIGHTEEN, u"Health-care providers use evidence-based protocols and"
               u" guidelines to provide health services"),
    (NINETEEN, u"Health-care providers are able to dedicate sufficient time"
               u" to work effectively with their adolescent clients"),
    (TWENTY, u"The point of health service delivery has the required"
             u" equipment, supplies and basic services necessary to deliver"
             u" the required health services")
]

CHARACTERISTIC_MAPPING = {
    ONE: {
        ADOLESCENT_CLIENT: (
            'characteristic_one/ch1_q1',
            'characteristic_one/ch1_q2'
        ),
        HEALTH_CARE_PROVIDER: (
            'characteristic_one/ch1_q1',
        ),
        HEALTH_FACILITY_MANAGER: (
            'characteristic_one/ch1_q1',
        ),
        ADOLESCENT_IN_COMMUNITY: (
            'characteristic_one/ch1_q1',
        )
    },
    TWO: {
        ADOLESCENT_CLIENT: (
            'characteristic_two/ch2_q1',
            'characteristic_two/ch2_q2'
        ),
        HEALTH_CARE_PROVIDER: (
            'characteristic_two/ch2_q1',
        ),
        ADOLESCENT_IN_COMMUNITY: (
            'characteristic_two/ch2_q1',
        )
    },
    THREE: {
        ADOLESCENT_CLIENT: (
            'characteristic_three/ch3_q1',
            'characteristic_three/ch3_q2',
            'characteristic_three/ch3_q3',
            'characteristic_three/ch3_q4'
        ),
        SUPPORT_STAFF: {
            'characteristic_three/ch3_q1',
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_three/ch3_q1',
        }
    },
    FOUR: {
        ADOLESCENT_CLIENT: (
            'characteristic_four/ch4_q1',
            'characteristic_four/ch4_q1_yes',
            'characteristic_four/ch4_q1_yes2'
        ),
        HEALTH_FACILITY_MANAGER: {
            'characteristic_four/ch4_q1',
            'characteristic_four/ch4_q2'
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_four/ch4_q1'
        }
    },
    FIVE: {
        ADOLESCENT_CLIENT: (
            'characteristic_five/ch5_q2',
        ),
        HEALTH_FACILITY_MANAGER: {
            'characteristic_five/ch5_q1',
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_five/ch5_q1',
        }
    },
    SIX: {
        ADOLESCENT_CLIENT: {
            'characteristic_six/ch6_q1',
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_six/ch6_q1',
        }
    },
    SEVEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_seven/ch7_q1',
            'characteristic_seven/ch7_q2',
            'characteristic_seven/ch7_q3'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_seven/ch7_q1',
        },
        COMMUNITY_MEMBER: {
            'characteristic_seven/ch7_q1',
            'characteristic_seven/ch7_q2',
            'characteristic_seven/ch7_q3',
            'characteristic_seven/ch7_q4'
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_seven/ch7_q1',
            'characteristic_seven/ch7_q2',
            'characteristic_seven/ch7_q3'
        }
    },
    EIGHT: {
        ADOLESCENT_CLIENT: {
            'characteristic_eight/ch8_q1'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_eight/ch8_q1'
        },
        OUTREACH_WORKER: {
            'characteristic_eight/ch8_q1',
        },
        ADOLESCENT_IN_COMMUNITY: {
            'characteristic_eight/ch8_q1',
            'characteristic_eight/ch8_q2'
        }
    },
    NINE: {
        ADOLESCENT_CLIENT: {
            'characteristic_nine/ch9_q1',
            'characteristic_nine/ch9_q2',
            'characteristic_nine/ch9_q3',
            'characteristic_nine/ch9_q4'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_nine/ch9_q1'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_nine/ch9_q1'
        },
        OBSERVATION_GUIDE: {
            'characteristic_nine/ch9_q1'
        }
    },
    TEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_ten/ch10_q1',
            'characteristic_ten/ch10_q2',
            'characteristic_ten/ch10_q3',
            'characteristic_ten/ch10_q4'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_ten/ch10_q1',
            'characteristic_ten/ch10_q2'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_ten/ch10_q1'
        },
        OBSERVATION_GUIDE: {
            'characteristic_ten/ch10_q1',
            'characteristic_ten/ch10_q2',
            'characteristic_ten/ch10_q3'
        }
    },
    ELEVEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_eleven/ch11_q1',
            'characteristic_eleven/ch11_q2',
            'characteristic_eleven/ch11_q3',
            'characteristic_eleven/ch11_q4'
        },
        OBSERVATION_GUIDE: {
            'characteristic_eleven/ch11_q1',
            'characteristic_eleven/ch11_q2',
            'characteristic_eleven/ch11_q3',
            'characteristic_eleven/ch11_q4'
        }
    },
    TWELVE: {
        ADOLESCENT_CLIENT: {
            'characteristic_twelve/ch12_q1',
            'characteristic_twelve/ch12_q2',
            'characteristic_twelve/ch12_q3'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_twelve/ch12_q1',
            'characteristic_twelve/ch12_q2'
        },
        SUPPORT_STAFF: {
            'characteristic_twelve/ch12_q1',
            'characteristic_twelve/ch12_q2',
        },
        OBSERVATION_GUIDE: {
            'characteristic_twelve/ch12_q1'
        }
    },
    THIRTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_thirteen/ch13_q1',
            'characteristic_thirteen/ch13_q2',
            'characteristic_thirteen/ch13_q3',
            'characteristic_thirteen/ch13_q4',
            'characteristic_thirteen/ch13_q5',
            'characteristic_thirteen/ch13_q6'
        },
        OBSERVATION_GUIDE: {
            'characteristic_thirteen/ch13_q1',
            'characteristic_thirteen/ch13_q2',
            'characteristic_thirteen/ch13_q3',
            'characteristic_thirteen/ch13_q4',
            'characteristic_thirteen/ch13_q5',
            'characteristic_thirteen/ch13_q6',
            'characteristic_thirteen/ch13_q7',
            'characteristic_thirteen/ch13_q8',
            'characteristic_thirteen/ch13_q9'
        }
    },
    FOURTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_fourteen/ch14_q1',
            'characteristic_fourteen/ch14_q2',
            'characteristic_fourteen/ch14_q3',
            'characteristic_fourteen/ch14_q4'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_fourteen/ch14_q1'
        },
        OBSERVATION_GUIDE: {
            'characteristic_fourteen/ch14_q1',
            'characteristic_fourteen/ch14_q2'
        }
    },
    FIFTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_fifteen/ch15_q1',
            'characteristic_fifteen/ch15_q2'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_fifteen/ch15_q1',
            'characteristic_fifteen/ch15_q2'
        }
    },
    SIXTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_sixteen/ch16_q1',
            'characteristic_sixteen/ch16_q2'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_sixteen/ch16_q1',
            'characteristic_sixteen/ch16_q2',
            'characteristic_sixteen/ch16_q3',
            'characteristic_sixteen/ch16_q4',
            'characteristic_sixteen/ch16_q5',
            'characteristic_sixteen/ch16_q6',
            'characteristic_sixteen/ch16_q7',
            'characteristic_sixteen/ch16_q8',
            'characteristic_sixteen/ch16_q9',
            'characteristic_sixteen/ch16_q10',
            'characteristic_sixteen/ch16_q11',
            'characteristic_sixteen/ch16_q12',
            'characteristic_sixteen/ch16_q13',
            'characteristic_sixteen/ch16_q14'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_sixteen/ch16_q1',
            'characteristic_sixteen/ch16_q2',
            'characteristic_sixteen/ch16_q3',
            'characteristic_sixteen/ch16_q4',
            'characteristic_sixteen/ch16_q5',
            'characteristic_sixteen/ch16_q6',
            'characteristic_sixteen/ch16_q7',
            'characteristic_sixteen/ch16_q8',
            'characteristic_sixteen/ch16_q9',
            'characteristic_sixteen/ch16_q10',
            'characteristic_sixteen/ch16_q11',
            'characteristic_sixteen/ch16_q12',
            'characteristic_sixteen/ch16_q13',
            'characteristic_sixteen/ch16_q14'
        }
    },
    SEVENTEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_seventeen/ch17_q1',
            'characteristic_seventeen/ch17_q2',
            'characteristic_seventeen/ch17_q3',
            'characteristic_seventeen/ch17_q4',
            'characteristic_seventeen/ch17_q5',
            'characteristic_seventeen/ch17_q6'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_seventeen/ch17_q1',
            'characteristic_seventeen/ch17_q2',
            'characteristic_seventeen/ch17_q3',
            'characteristic_seventeen/ch17_q4',
            'characteristic_seventeen/ch17_q5',
            'characteristic_seventeen/ch17_q6',
            'characteristic_seventeen/ch17_q7',
            'characteristic_seventeen/ch17_q8',
            'characteristic_seventeen/ch17_q9',
            'characteristic_seventeen/ch17_q10',
            'characteristic_seventeen/ch17_q11',
            'characteristic_seventeen/ch17_q12',
            'characteristic_seventeen/ch17_q13',
            'characteristic_seventeen/ch17_q14',
            'characteristic_seventeen/ch17_q15'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_seventeen/ch17_q1',
            'characteristic_seventeen/ch17_q2',
            'characteristic_seventeen/ch17_q3',
            'characteristic_seventeen/ch17_q4',
            'characteristic_seventeen/ch17_q5',
            'characteristic_seventeen/ch17_q6',
            'characteristic_seventeen/ch17_q7',
            'characteristic_seventeen/ch17_q8',
            'characteristic_seventeen/ch17_q9',
            'characteristic_seventeen/ch17_q10',
            'characteristic_seventeen/ch17_q11',
            'characteristic_seventeen/ch17_q12',
            'characteristic_seventeen/ch17_q13'
        },
        OBSERVATION_GUIDE: {
            'characteristic_seventeen/ch17_q1',
            'characteristic_seventeen/ch17_q2',
            'characteristic_seventeen/ch17_q3',
            'characteristic_seventeen/ch17_q4',
            'characteristic_seventeen/ch17_q5',
            'characteristic_seventeen/ch17_q6',
            'characteristic_seventeen/ch17_q7',
            'characteristic_seventeen/ch17_q8',
            'characteristic_seventeen/ch17_q9',
            'characteristic_seventeen/ch17_q10',
            'characteristic_seventeen/ch17_q11',
            'characteristic_seventeen/ch17_q12',
            'characteristic_seventeen/ch17_q13',
            'characteristic_seventeen/ch17_q14',
            'characteristic_seventeen/ch17_q15',
            'characteristic_seventeen/ch17_q16',
            'characteristic_seventeen/ch17_q17'
        }
    },
    EIGHTEEN: {
        HEALTH_CARE_PROVIDER: {
            'characteristic_eighteen/ch18_q1',
            'characteristic_eighteen/ch18_q2',
            'characteristic_eighteen/ch18_q3',
            'characteristic_eighteen/ch18_q4',
            'characteristic_eighteen/ch18_q5',
            'characteristic_eighteen/ch18_q6',
            'characteristic_eighteen/ch18_q7',
            'characteristic_eighteen/ch18_q8',
            'characteristic_eighteen/ch18_q9',
            'characteristic_eighteen/ch18_q10',
            'characteristic_eighteen/ch18_q11',
            'characteristic_eighteen/ch18_q12',
            'characteristic_eighteen/ch18_q13'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_eighteen/ch18_q1',
            'characteristic_eighteen/ch18_q2',
            'characteristic_eighteen/ch18_q3',
            'characteristic_eighteen/ch18_q4',
            'characteristic_eighteen/ch18_q5',
            'characteristic_eighteen/ch18_q6',
            'characteristic_eighteen/ch18_q7',
            'characteristic_eighteen/ch18_q8',
            'characteristic_eighteen/ch18_q9',
            'characteristic_eighteen/ch18_q10',
            'characteristic_eighteen/ch18_q11',
            'characteristic_eighteen/ch18_q12',
            'characteristic_eighteen/ch18_q13'
        },
        OBSERVATION_GUIDE: {
            'characteristic_eighteen/ch18_q1',
            'characteristic_eighteen/ch18_q2',
            'characteristic_eighteen/ch18_q3',
            'characteristic_eighteen/ch18_q4',
            'characteristic_eighteen/ch18_q5',
            'characteristic_eighteen/ch18_q6',
            'characteristic_eighteen/ch18_q7',
            'characteristic_eighteen/ch18_q8',
            'characteristic_eighteen/ch18_q9',
            'characteristic_eighteen/ch18_q10',
            'characteristic_eighteen/ch18_q11',
            'characteristic_eighteen/ch18_q12',
            'characteristic_eighteen/ch18_q13'
        }
    },
    NINETEEN: {
        ADOLESCENT_CLIENT: {
            'characteristic_nineteen/ch19_q1',
            'characteristic_nineteen/ch19_q2'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_nineteen/ch19_q1',
            'characteristic_nineteen/ch19_q2'
        }
    },
    TWENTY: {
        ADOLESCENT_CLIENT: {
            'characteristic_twenty/ch20_q1'
        },
        HEALTH_CARE_PROVIDER: {
            'characteristic_twenty/ch20_q1',
            'characteristic_twenty/ch20_q2',
            'characteristic_twenty/ch20_q3',
            'characteristic_twenty/ch20_q4'
        },
        HEALTH_FACILITY_MANAGER: {
            'characteristic_twenty/ch20_q1',
            'characteristic_twenty/ch20_q2',
            'characteristic_twenty/ch20_q3'
        },
        OBSERVATION_GUIDE: {
            'characteristic_twenty/ch20_q1',
            'characteristic_twenty/ch20_q2'
        }
    }
}