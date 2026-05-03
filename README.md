hotel
restaurant
taxi
attraction

travel-booking-chatbot/
│
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── configs/
│   ├── domains.yaml
│   ├── slots.yaml
│   ├── actions.yaml
│   └── app_config.yaml
│
├── data/
│   ├── raw/
│   │   └── multiwoz/
│   │
│   ├── processed/
│   │   ├── train.jsonl
│   │   ├── val.jsonl
│   │   └── test.jsonl
│   │
│   ├── mock_db/
│   │   ├── hotels.json
│   │   ├── restaurants.json
│   │   ├── attractions.json
│   │   └── taxis.json
│   │
│   └── samples/
│       ├── sample_dialogues.json
│       └── sample_training_examples.jsonl
│
├── notebooks/
│   ├── 01_explore_multiwoz.ipynb
│   ├── 02_check_slot_values.ipynb
│   └── 03_test_mock_tools.ipynb
│
├── src/
│   ├── __init__.py
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── load_multiwoz.py
│   │   ├── normalize_slots.py
│   │   ├── build_dialogue_states.py
│   │   └── build_turn_examples.py
│   │
│   ├── schema/
│   │   ├── __init__.py
│   │   ├── domains.py
│   │   ├── slots.py
│   │   └── actions.py
│   │
│   ├── dialogue/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── state_tracker.py
│   │   ├── policy.py
│   │   └── response_templates.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── hotel_tools.py
│   │   ├── restaurant_tools.py
│   │   ├── taxi_tools.py
│   │   ├── attraction_tools.py
│   │   └── tool_router.py
│   │
│   ├── nlu/
│   │   ├── __init__.py
│   │   ├── rule_based_nlu.py
│   │   ├── prompt_nlu.py
│   │   └── parsers.py
│   │
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── chat_engine.py
│   │   └── session_manager.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   ├── ui/
│   │   ├── streamlit_app.py
│   │   └── gradio_app.py
│   │
│   └── evaluation/
│       ├── __init__.py
│       ├── metrics.py
│       ├── evaluate_slots.py
│       ├── evaluate_dialogue_state.py
│       └── test_scenarios.json
│
├── scripts/
│   ├── download_multiwoz.sh
│   ├── preprocess_data.py
│   ├── create_mock_db.py
│   ├── run_chat_cli.py
│   └── run_api.sh
│
├── tests/
│   ├── test_slot_normalization.py
│   ├── test_state_tracker.py
│   ├── test_tools.py
│   └── test_chat_engine.py
│
└── logs/
    ├── conversations/
    └── evaluations/