from src.planner_core import generate_plan
import json

def launch_cli():
    print("\nWelcome to ATLAS, your travel planner\nTo get started, please-\n")
    destination = input("Enter your destination: ")
    budget = input("Enter your total budget (INR or USD): ")
    travelers = input("Enter number of travelers: ")
    duration = input("Trip duration (in days): ")

    print("\nGenerating your personalized itinerary...\n")
    plan = generate_plan(destination, budget, travelers, duration)
    print(plan)
    print(json.dumps(plan, indent=2, ensure_ascii=False))

    save = input("\nSave itinerary to file? (y/n): ")
    if save.lower() == 'y':
        filename = f"itinerary_{destination.replace(' ','_')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        print(f"Saved to {filename}")