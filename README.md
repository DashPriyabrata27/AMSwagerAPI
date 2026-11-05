Author_Misattribution_Detection/
│
├── backend/
│   │
│   └── app/
│       │
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── dependencies.py
│       │   │
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── authors.py
│       │       └── validation.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── openalex_service.py
│       │   ├── extraction_service.py
│       │   └── validation_service.py
│       │
│       ├── validators/
│       │   ├── __init__.py
│       │   ├── rule_engine.py
│       │   │
│       │   └── problems/
│       │       ├── __init__.py
│       │       ├── problem_01.py
│       │       ├── problem_02.py
│       │       ├── problem_03.py
│       │       ├── problem_04.py
│       │       ├── problem_05.py
│       │       ├── problem_06.py
│       │       ├── problem_07.py
│       │       ├── problem_08.py
│       │       ├── problem_09.py
│       │       └── problem_10.py
│       │
│       ├── scoring/
│       │   ├── __init__.py
│       │   ├── scoring_engine.py
│       │   └── weights.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── author.py
│       │   └── validation.py
│       │
│       └── utils/
│           ├── __init__.py
│           └── data_utils.py
│
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md