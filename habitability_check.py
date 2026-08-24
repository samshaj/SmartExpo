import csv
import math
import os

def load_planets(csv_filename):
    planets = []
    # Get absolute path relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, csv_filename)
    
    if not os.path.exists(csv_path):
        print(f"Error: Data file '{csv_filename}' not found at {csv_path}.")
        return planets

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert values to float for analysis
            planets.append({
                'name': row['name'],
                'luminosity': float(row['luminosity']),
                'distance': float(row['distance']),
                'radius': float(row['radius']),
                'mass': float(row['mass']),
                'eccentricity': float(row['eccentricity']),
                'albedo': float(row['albedo'])
            })
    return planets

def search_planets(planets, query):
    query = query.strip().lower()
    matches = []
    for p in planets:
        if query in p['name'].lower():
            matches.append(p)
    return matches

def check_habitability(name, star_luminosity, planet_distance, planet_radius, planet_mass, albedo):
    """Checks if an exoplanet could support liquid water and rocky surface."""

    if planet_distance <= 0:
        return "Verdict: Invalid distance (0 or negative)"
        
    energy_received = star_luminosity / (planet_distance**2)

    # Calculate "Goldilocks Zone" boundaries (in AU)
    inner_edge = math.sqrt(star_luminosity / 1.11)
    outer_edge = math.sqrt(star_luminosity / 0.36)

    # Check criteria
    in_habitable_zone = inner_edge <= planet_distance <= outer_edge
    is_rocky = 0.5 <= planet_radius <= 1.6  # Earth-like size range

    # Estimate temperature in Celsius
    temp_kelvin = 278.5 * ((energy_received * (1 - albedo)) ** 0.25)
    temp_celsius = temp_kelvin - 273.15

    # Build analysis results
    output = []
    output.append(f"\n=========================================")
    output.append(f"          ANALYSIS FOR {name.upper()}")
    output.append(f"=========================================")
    output.append(f"  Energy Received:  {energy_received:.4f}x Earth's level")
    output.append(f"  Habitable Zone:   {inner_edge:.4f} AU to {outer_edge:.4f} AU")
    output.append(f"  Est. Temperature: {temp_celsius:.1f} °C")
    output.append(f"  Rocky Planet:     {'Yes' if is_rocky else 'No'} (Radius: {planet_radius}x Earth)")
    output.append(f"  ---------------------------------------")

    # Verdict
    if in_habitable_zone and is_rocky:
        output.append("  Verdict: Potentially Habitable Rocky World!")
    elif in_habitable_zone:
        output.append("  Verdict: In the Habitable Zone, but likely a Gas Giant (Not Rocky).")
    else:
        output.append("  Verdict: Outside the Habitable Zone (too hot or too cold).")
    
    output.append(f"=========================================\n")
    return "\n".join(output)

def display_planet_data(p):
    print(f"\nRaw Data for {p['name']}:")
    print(f"  Luminosity:   {p['luminosity']}")
    print(f"  Distance:     {p['distance']} AU")
    print(f"  Radius:       {p['radius']}x Earth")
    print(f"  Mass:         {p['mass']}x Earth")
    print(f"  Eccentricity: {p['eccentricity']}")
    print(f"  Albedo:       {p['albedo']}")

def main():
    planets = load_planets("planets.csv")
    if not planets:
        return

    print("=== Planet Habitability Analysis Tool ===")
    print("Type 'exit' or 'quit' to close the program.\n")
    
    while True:
        try:
            query = input("Enter planet name to analyze: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
            
        if query.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break
            
        if not query:
            print("Please enter a planet name.\n")
            continue
            
        matches = search_planets(planets, query)
        
        if not matches:
            print(f"No planets found matching '{query}'.\n")
            continue
            
        print(f"\nFound {len(matches)} matching planet(s):")
        for p in matches:
            # 1. Display raw data
            display_planet_data(p)
            
            # 2. Run analysis and print result
            analysis_result = check_habitability(
                name=p['name'],
                star_luminosity=p['luminosity'],
                planet_distance=p['distance'],
                planet_radius=p['radius'],
                planet_mass=p['mass'],
                albedo=p['albedo']
            )
            print(analysis_result)

if __name__ == "__main__":
    main()
