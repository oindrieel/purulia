import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oindrieel.src.pipeline import PuruliaBrain


def format_itinerary(itinerary):
    """Helper to make the itinerary JSON look pretty in the terminal."""
    output = "\n📅 **Your Trip Plan:**\n"
    for day, details in itinerary.items():
        output += f"\n   {day} ({details['Zone']} Zone):\n"
        output += f"     🌅 Morning:   {details['Morning']}\n"
        output += f"     ☀️ Afternoon: {details['Afternoon']}\n"
        output += f"     🌙 Evening:   {details['Evening']}\n"
    return output


def start_chat():
    print("⏳ Initializing Purulia AI Assistant...")
    brain = PuruliaBrain()

    print("\n" + "=" * 50)
    print("🤖 PURULIA TOURISM ASSISTANT READY")
    print("   Try asking:")
    print("   - 'Tell me about the history of masks'")
    print("   - 'I like waterfalls and nature'")
    print("   - 'Plan a 2 day trip for history lovers'")
    print("   (Type 'exit' to quit)")
    print("=" * 50 + "\n")

    while True:
        try:
            user_input = input("👤 You: ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("🤖 Bot: Enjoy your trip to Purulia! Goodbye!")
                break

            if not user_input:
                continue

            response = brain.process_query(user_input)

            print("🤖 Bot:", end=" ")

            if response.get("type") == "info":
                print(f"**{response['subject']}**")
                print(f"       {response['text']}")

            elif response.get("type") == "recommendation":
                print("Here are some places matching your interests:")
                for place in response['places']:
                    print(f"       • {place}")

            elif response.get("type") == "plan":
                print(format_itinerary(response['itinerary']))

            elif response.get("error"):
                print(f"😕 {response['error']}")

            else:
                print("I'm not sure how to handle that yet.")

            print("-" * 30)

        except KeyboardInterrupt:
            print("\n🤖 Bot: Force close detected. Bye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    start_chat()