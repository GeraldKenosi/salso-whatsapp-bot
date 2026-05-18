# SALSO (Southern African Liaison Office) knowledge base
# All information extracted from the official website: https://www.salo.org.za

ORGANISATION = {
    "name": "The Southern African Liaison Office",
    "short_name": "SALO",
    "tagline": "International liaison, dialogue and research",
    "description": (
        "SALO is a South African-based not-for-profit civil society organisation "
        "which, through advocacy, dialogue, policy consensus and in-depth research "
        "and analysis, influences current thinking and debates on foreign policy, "
        "especially regarding African crises and conflicts."
    ),
    "founded": 2006,
    "email": "info@salo.org.za",
    "website": "https://www.salo.org.za",
    "social_media": {
        "facebook": "Southern African Liaison Office",
    },
}

PROGRAMMES = [
    {
        "title": "Building international, regional and national consensus",
        "description": "Facilitating dialogue between national, regional and international actors to build consensus on peace and security issues."
    },
    {
        "title": "Engaging, influencing SA foreign policy",
        "description": "Interpreting and influencing South Africa's foreign policy positions on African crises and conflicts."
    },
    {
        "title": "Deepening North-South partnerships",
        "description": "Strengthening partnerships between developed and developing nations for sustainable development."
    },
    {
        "title": "Deepening South-South partnerships",
        "description": "Fostering collaboration among developing countries for mutual growth and stability."
    },
    {
        "title": "Xenophobia, migration and diaspora",
        "description": "Combating xenophobia and focusing on migration and diaspora communities."
    },
    {
        "title": "Gender mainstreaming and LGBTI rights",
        "description": "Promoting women's, children's and LGBTI rights in political transitions."
    },
    {
        "title": "Climate justice and critical minerals",
        "description": "Advancing climate justice, just transition, and equitable natural resource governance with emphasis on extractives."
    },
]

FAQS = [
    {
        "question": "What does SALO stand for?",
        "answer": "SALO stands for the Southern African Liaison Office."
    },
    {
        "question": "What does SALO do?",
        "answer": (
            "SALO is a South African-based civil society organisation that works on "
            "peace, security, and foreign policy in Africa. It facilitates dialogue, "
            "conducts research, and builds consensus between governments, civil society, "
            "and international partners."
        )
    },
    {
        "question": "Where is SALO based?",
        "answer": "SALO is based in South Africa and works across Southern Africa, especially Zimbabwe, Mozambique, and Eswatini."
    },
    {
        "question": "When was SALO founded?",
        "answer": "SALO was founded in 2006."
    },
    {
        "question": "How can I contact SALO?",
        "answer": "You can email SALO at info@salo.org.za or visit the website at https://www.salo.org.za"
    },
    {
        "question": "Is SALO a government organisation?",
        "answer": "No. SALO is an independent, not-for-profit civil society organisation (NGO)."
    },
    {
        "question": "Does SALO have a youth programme?",
        "answer": "Yes. SALO has a Youth Development Programme that engages young people in dialogue, research, and advocacy."
    },
    {
        "question": "How can I stay updated on SALO's work?",
        "answer": "You can visit https://www.salo.org.za for publications, reports, news, and upcoming policy dialogues and events."
    },
    {
        "question": "Does SALO offer any training or internships?",
        "answer": "Yes, SALO offers opportunities through its Youth Development Programme. Contact info@salo.org.za for more information."
    },
    {
        "question": "How can I support SALO's work?",
        "answer": "You can support SALO by engaging with its research, attending policy dialogues, or contacting info@salo.org.za for partnership opportunities."
    },
    {
        "question": "How many staff does SALO have?",
        "answer": "SALO operates with a core team of staff and consultants supported by a Board of Directors. Visit the website for current staff listings."
    },
    {
        "question": "What is the Workers' Workforce App?",
        "answer": "The Workforce App is SALO's internal mobile app for staff and volunteers to clock attendance, submit reports, manage leave, and access resources."
    },
]

# Map keywords to FAQ indices for quick matching
FAQ_KEYWORDS = {
    "what": [0, 1, 6, 10, 11],
    "who": [0],
    "where": [2],
    "when": [3],
    "how": [4, 5, 7, 8, 9, 10],
    "does": [1, 6, 7, 10, 11],
    "salO": list(range(12)),
    "contact": [4],
    "email": [4, 8, 9],
    "youth": [6],
    "internship": [8],
    "train": [8],
    "volunteer": [8, 9],
    "job": [8],
    "support": [9],
    "donate": [9],
    "partner": [9],
    "app": [11],
    "workforce": [11],
}
