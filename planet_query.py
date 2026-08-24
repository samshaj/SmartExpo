import csv
import os

def load_planets(csv_filename):
    planets = []
    # Get absolute path to the CSV file relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, csv_filename)
    
    if not os.path.exists(csv_path):
        print(f"Error: Data file '{csv_filename}' not found at {csv_path}.")
        return planets

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            planets.append(row)
    return planets

def search_planets(planets, query):
    query = query.strip().lower()
    matches = []
    for p in planets:
        if query in p['name'].lower():
            matches.append(p)
    return matches

def main():
    planets = load_planets("planets.csv")
    if not planets:
        return

    print("=== Planet Data Query Tool ===")
    print("Type 'exit' or 'quit' to close the program.\n")
    
    while True:
        try:
            query = input("Enter the name (or part of the name) of the planet: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
            
        if query.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break
            
        if not query:
            print("Please enter a search query.\n")
            continue
            
        matches = search_planets(planets, query)
        
        if not matches:
            print(f"No planets found matching '{query}'.\n")
            continue
            
        print(f"Found {len(matches)} matching planet(s):\n")
        for p in matches:
            print(f"Planet: {p['name']}")
            print("-" * (len(p['name']) + 8))
            for key, value in p.items():
                if key != 'name':
                    print(f"  {key.capitalize()}: {value}")
            print()


if __name__ == "__main__":
    main()
