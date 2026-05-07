import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from chat.chat_engine import ChatEngine


# I need to find a cheap hotel in the north with parking 
# Book it for 2 people on Friday for 3 nights.

def main():
    chat = ChatEngine(nlu_mode="llm")
    # chat = ChatEngine(nlu_mode="rule_based")

    print("Travel Booking Chatbot")
    print("Type 'exit' to quit.")
    print("-" * 40)

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() in {"exit", "quit"}:
            print("Bot: Goodbye!")
            break

        result = chat.process_message(user_message)

        print(f"Bot: {result['response']}")

        # Debug info while developing
        print("\n[debug]")
        print("Intent:", result["nlu_result"].get("intent"))
        print("Policy:", result["policy_decision"])
        print("State:", result["dialogue_state"])
        print("-" * 40)


if __name__ == "__main__":
    main()