from src.planner_core import generate_plan

def launch_cli():
    print("\n=== Agentic Travel Planner ===")
    destination = input("Enter your destination: ")
    budget = input("Enter your total budget (INR or USD): ")
    travelers = input("Enter number of travelers: ")
    duration = input("Trip duration (in days): ")

    print("\nGenerating your personalized itinerary...\n")
    plan = generate_plan(destination, budget, travelers, duration)
    print(plan)
