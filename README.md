# Hybrid Fine-Tuned LLM Travel Booking Chatbot

## Project Overview

This project implements a **task-oriented travel booking chatbot** that supports four domains:

- hotel
- restaurant
- taxi
- attraction

The chatbot processes user messages along with the current dialogue state and predicts structured JSON containing:

```json
{
  "domain": "...",
  "intent": "...",
  "slots": {...},
  "next_action": "...",
  "missing_slots": [...]
}
```

The final system can:

- search mock travel databases
- book hotels/restaurants/taxis
- ask users for missing information
- fallback for unsupported requests

The project compares three systems:

1. Rule-based baseline
2. Prompt-only Mistral baseline
3. LoRA/QLoRA fine-tuned Mistral model

---

# Table of Contents

1. Project Goal
2. Rule-Based Baseline
3. Dataset Processing Pipeline
4. Supervised Fine-Tuning (SFT)
5. Fine-Tuning Notebook
6. Prompt-Only Baseline
7. Loaded Fine-Tuned Model Evaluation
8. Hybrid Chatbot Pipeline
9. Web Demo
10. How to Run
11. Project Evolution
12. Final Contribution

---

# 1. Project Goal

The objective of this project is to build a **hybrid intelligent travel assistant** capable of handling realistic travel-booking conversations using:

- dialogue state tracking
- slot extraction
- policy prediction
- mock API grounding
- LLM-based structured prediction

The chatbot combines:

- a fine-tuned Large Language Model (LLM)
- deterministic validation logic
- tool-based execution

to create a reliable end-to-end conversational system.

---

# 2. Rule-Based Baseline

## Why the Rule-Based Baseline Was Built

The rule-based chatbot was developed first as a baseline system using:

- keyword matching
- regular expressions
- slot dictionaries
- deterministic missing-slot checks
- mock API tool calls

The purpose was to evaluate how far handcrafted dialogue systems can go before introducing fine-tuned LLMs.

### Example Supported Queries

```text
I need a cheap hotel in the north.
Book it for 2 people on Friday for 3 nights.
```

### Limitations

The rule-based system struggles with:

- paraphrased language
- implicit references
- flexible phrasing
- attraction name searches
- ambiguous time extraction

Examples:

```text
I’m looking for somewhere affordable to stay up north.
I’d like somewhere to eat around the city centre.
```

---

## Rule-Based Source Code Structure

Main files:

```text
src/chat/chat_engine.py
src/dialogue/state_tracker.py
src/dialogue/policy.py
src/dialogue/response_templates.py
src/tools/tool_router.py
src/tools/
src/nlu/
```

---

## Rule-Based Chatbot Flow

```text
User message
→ rule-based NLU
→ normalized intent/slots
→ dialogue state update
→ policy decision
→ mock tool call
→ chatbot response
```

---

## Mock Databases

The chatbot uses local JSON databases:

```text
data/mock_db/hotels.json
data/mock_db/restaurants.json
data/mock_db/attractions.json
data/mock_db/taxis.json
```

---

## Running the Rule-Based Chatbot

Run the CLI chatbot:

```bash
python run_chat_cli.py
```

The chatbot is initialized using:

```python
chat = ChatEngine(nlu_mode="rule_based")
```

A `reset` command was added:

```python
if user_message.lower() == "reset":
    chat = ChatEngine(nlu_mode="rule_based")
    print("Bot: Dialogue state reset.")
    continue
```

This ensures dialogue states do not carry across test cases.

---

## Manual Testing

The rule-based chatbot was tested on:

1. hotel search
2. multi-turn hotel booking
3. restaurant search
4. restaurant booking
5. missing-slot hotel booking
6. taxi booking
7. taxi missing slots
8. attraction type search
9. attraction name search

The results showed strong performance on direct prompts but weaker performance on paraphrased or flexible language.

This motivated the transition to an LLM-based approach.

---

# 3. Dataset Processing Pipeline

## Dataset Used

The project uses the **MultiWOZ** dataset filtered to supported domains:

- hotel
- restaurant
- taxi
- attraction

Unsupported domains such as:

- train
- hospital
- police

were removed.

---

## Stage 1: Normalize Slots and Intents

File:

```text
main.py
```

Purpose:

- normalize slot names
- normalize slot values
- assign intents and domains
- remove unsupported domains

Examples:

```text
pricerange → price_range
leaveat → leave_at
arriveby → arrive_by
bookpeople → people
dontcare → any
not mentioned → None
```

---

## Stage 2: Build Dialogue States

File:

```text
build_states_from_normalized.py
```

Purpose:

- create dialogue-state training examples
- track booking slots
- track search slots
- support multi-turn references

Example:

```text
Turn 1:
I need a cheap hotel in the north.

State:
hotel.search_slots = {
  price_range: cheap,
  area: north
}

Turn 2:
Book it for 2 people on Friday for 3 nights.
```

The state tracker preserves previous hotel information while adding booking details.

---

## Stage 3: Apply Policy Labels

File:

```text
apply_policy_to_datasets.py
```

Purpose:

- compute `next_action`
- compute `missing_slots`
- determine tool-routing actions

Example actions:

```text
search_hotel
book_hotel
search_restaurant
book_restaurant
book_taxi
search_attraction
ask_missing_slot
fallback
```

---

## Stage 4: Apply Tools

File:

```text
apply_tools_to_datasets.py
```

Purpose:

- connect policy outputs to tools
- simulate booking/search APIs
- generate tool-grounded examples

---

# 4. Supervised Fine-Tuning (SFT)

## SFT Dataset Files

```text
train_sft.jsonl
dev_sft.jsonl
test_sft.jsonl
```

Usage:

```text
train_sft.jsonl → training
dev_sft.jsonl → validation
test_sft.jsonl → held-out testing
```

---

## SFT Example Format

Each example follows chat-style instruction tuning:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "..."
    },
    {
      "role": "user",
      "content": "User message...\nCurrent dialogue state..."
    },
    {
      "role": "assistant",
      "content": "{target JSON}"
    }
  ]
}
```

The model is trained to output strictly structured JSON.

---

# 5. Fine-Tuning Notebook

## Notebook

```text
nlp-project-code-3k-samples-final.ipynb
```

---

## Purpose

This notebook:

- loads the SFT datasets
- loads the base Mistral model
- configures LoRA/QLoRA
- trains the adapter
- evaluates the model
- saves the adapter

---

## Base Model

```text
mistralai/Mistral-7B-Instruct-v0.3
```

---

## Why LoRA/QLoRA Was Used

Full fine-tuning of a 7B model is computationally expensive.

LoRA/QLoRA trains only lightweight adapter layers instead of all parameters, making training feasible on limited hardware.

The final trained system is:

```text
Mistral-7B-Instruct-v0.3 + LoRA adapter
```

---

## Fine-Tuning Notebook Execution Order

```text
1. Environment setup
2. Imports and paths
3. Load SFT datasets
4. Load tokenizer/model
5. Configure LoRA/QLoRA
6. Configure trainer
7. Train adapter
8. Save adapter
9. Run inference
10. Define parser/repair functions
11. Evaluate model
12. Save metrics
```

---

## Saved Adapter

Training produces:

```text
latest_model_with_full_dataset/
├── adapter_config.json
└── adapter_model.safetensors
```

This adapter is reused later without retraining.

---

# 6. Prompt-Only LLM Baseline

## Purpose

A prompt-only baseline was created using:

```text
Mistral-7B-Instruct-v0.3
```

without the LoRA adapter.

The same prompt format and evaluation pipeline were used.

---

## Findings

The prompt-only model:

### Performed well on:

- broad domain detection
- general intent understanding

### Performed poorly on:

- strict slot extraction
- structured JSON consistency
- task completion reliability

This demonstrated the value of fine-tuning.

---

# 7. Loaded Fine-Tuned Model Evaluation

## Notebook

```text
nlp-project-code-testing-full-with-advanced-metrics-generic.ipynb
```

---

## Purpose

This notebook:

- loads the saved LoRA adapter
- evaluates the trained model
- computes advanced metrics
- runs chatbot demos
- avoids retraining

This is the recommended notebook for evaluation and submission.

---

## Required Inputs

The notebook requires:

```text
1. latest_model_with_full_dataset/
2. src/
3. hotels.json
4. restaurants.json
5. attractions.json
6. taxis.json
7. evaluation_prompts.json
8. test_sft.jsonl
```

and Hugging Face access to:

```text
mistralai/Mistral-7B-Instruct-v0.3
```

---

## Evaluation Notebook Execution Order

```text
1. Install packages
2. Import libraries
3. Define paths
4. Authenticate Hugging Face
5. Copy mock DB files
6. Add src to Python path
7. Import tools
8. Load Mistral model
9. Load LoRA adapter
10. Define inference functions
11. Define parser/repair logic
12. Load evaluation prompts
13. Run evaluations
14. Run held-out test evaluation
15. Compute metrics
16. Run manual chatbot demo
```

---

## Custom Evaluation Prompts

The custom evaluation set includes:

- hotel search
- hotel booking
- restaurant search
- restaurant booking
- taxi booking
- attraction search
- missing-slot cases
- multi-turn conversations

The evaluation tests:

```text
model prediction
→ normalization
→ repair
→ state update
→ policy decision
→ tool call
→ chatbot response
```

---

## Held-Out Test Evaluation

The held-out `test_sft.jsonl` evaluation produced:

```text
Exact-match structured output accuracy: 75%
Slot precision: 91.14%
Slot recall: 87.27%
Slot F1: 89.16%
```

This demonstrated strong structured prediction capability.

---

# 8. Hybrid Chatbot Pipeline

## Final Chatbot Flow

```text
User message
→ current dialogue state
→ prompt builder
→ fine-tuned Mistral + LoRA
→ raw JSON prediction
→ JSON parser
→ normalization
→ repair and validation layer
→ dialogue state update
→ policy decision
→ tool router
→ mock API result
→ chatbot response
```

---

## Role of the Fine-Tuned LLM

The LLM predicts:

- domain
- intent
- slots
- next_action
- missing_slots

---

## Role of Deterministic Validation

The rule-based layer:

- normalizes slot names/values
- repairs malformed outputs
- validates booking requirements
- prevents invalid tool calls
- updates dialogue state
- routes requests to tools

This creates a robust hybrid architecture.

---

# 9. Web Demo

## Architecture

The web demo consists of:

1. Kaggle backend notebook
2. Streamlit frontend

---

## Backend Notebook

Notebook:

```text
nlp-project-code-demo.ipynb
```

Purpose:

- load the fine-tuned model
- create chatbot pipeline
- expose Flask API
- generate ngrok public URL

---

## Backend Execution Order

```text
1. Install packages
2. Import libraries
3. Define paths
4. Add src to Python path
5. Copy mock DB files
6. Load model
7. Load LoRA adapter
8. Define chatbot pipeline
9. Start Flask server
10. Launch ngrok
```

Example generated URL:

```text
https://xxxxx.ngrok-free.dev
```

---

## Streamlit Frontend

File:

```text
streamlit_app.py
```

Run locally:

```bash
streamlit run streamlit_app.py
```

The frontend connects to the Flask API and displays:

- chatbot response
- normalized model output
- policy decision
- tool result
- dialogue state
- raw model output

---

## Backend API Endpoints

```text
GET  /health
POST /chat
POST /reset
```

Example response:

```json
{
  "response": "...",
  "normalized_output": {...},
  "policy_decision": {...},
  "tool_result": {...},
  "dialogue_state": {...},
  "raw_model_output": "..."
}
```

---

# 10. How to Run

## Run the Evaluation Notebook

Steps:

```text
1. Open the Kaggle evaluation notebook.
2. Attach required datasets/models.
3. Run all cells top to bottom.
4. Review metrics and chatbot outputs.
```

No retraining is required.

---

## Run the Web Demo

Steps:

```text
1. Open the Kaggle demo notebook.
2. Run all cells.
3. Copy the ngrok public URL.
4. Start Streamlit locally:
   streamlit run streamlit_app.py
5. Paste the ngrok URL into the Streamlit sidebar.
6. Start chatting.
```

---

## Example Prompts

```text
I need a cheap hotel in the north with free parking.
Find me an Italian restaurant in the centre.
Book a table for 2 people on Friday at 7 pm.
I need a taxi from the hotel to the train station by 7 pm.
Find me a museum to visit in the centre.
```

---

# 11. Project Evolution

The project evolved through the following stages:

```text
1. Built rule-based chatbot
2. Created preprocessing pipeline
3. Built dialogue-state datasets
4. Added policy and tool grounding
5. Created train/dev/test SFT files
6. Fine-tuned Mistral with LoRA
7. Expanded dataset to ~3000 examples
8. Added evaluation prompts
9. Added held-out testing
10. Added repair/validation layer
11. Added advanced metrics
12. Built prompt-only baseline
13. Built Streamlit web demo
```

---

# 12. Final Contribution

The final system includes:

- rule-based baseline
- prompt-only LLM baseline
- fine-tuned Mistral model
- LoRA/QLoRA training
- dialogue state tracking
- slot normalization
- missing-slot validation
- mock booking APIs
- custom evaluation prompts
- held-out evaluation
- advanced metrics
- Streamlit web demo

---

# Final Conclusion

The project demonstrates that:

```text
Fine-tuned LLMs significantly improve structured dialogue prediction and slot extraction compared to prompt-only generation, while deterministic validation layers improve reliability and robustness before tool execution.
```

The final system is best described as:

```text
A hybrid fine-tuned LLM travel booking chatbot with rule-based validation and mock API grounding.
```