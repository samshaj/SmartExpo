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
                'distance': float(row['semi_major_axis']),
                'radius': float(row['radius']),
                'mass': float(row['mass']),
                'density': float(row['density']),
                'eccentricity': float(row['eccentricity']),
                'albedo': float(row['albedo'])
            })
    return planets

def calculate_comprehensive_esi(radius_earth, density_earth, escape_vel_earth, temp_kelvin):
    """Calculates the Global Earth-Similarity Index (ESI) using 4 key factors."""
    # 1. Individual property similarity sub-scores using standard weights
    esi_r = (1 - abs((radius_earth - 1.0) / (radius_earth + 1.0))) ** 0.57
    esi_d = (1 - abs((density_earth - 1.0) / (density_earth + 1.0))) ** 1.07
    esi_v = (1 - abs((escape_vel_earth - 1.0) / (escape_vel_earth + 1.0))) ** 0.70
    esi_t = (1 - abs((temp_kelvin - 288.0) / (temp_kelvin + 288.0))) ** 5.58

    # 2. Interior ESI (Radius + Density)
    interior_esi = math.sqrt(esi_r * esi_d)

    # 3. Surface ESI (Escape Velocity + Temperature)
    surface_esi = math.sqrt(esi_v * esi_t)

    # 4. Global ESI (Geometric mean of Interior and Surface)
    global_esi = math.sqrt(interior_esi * surface_esi)

    return {
        "Interior_ESI": round(interior_esi, 3),
        "Surface_ESI": round(surface_esi, 3),
        "Global_ESI": round(global_esi, 3),
    }

def calculate_orbital_period(semi_major_axis_au, star_mass_solar):
    """Calculates orbital period in Earth years and days using Kepler's 3rd Law."""
    if star_mass_solar <= 0 or semi_major_axis_au <= 0:
        return 0.0, 0.0
    period_years = math.sqrt((semi_major_axis_au**3) / star_mass_solar)
    period_days = period_years * 365.25
    return period_years, period_days

def calculate_surface_gravity(mass_earth, radius_earth):
    """Calculates surface gravity relative to Earth (1.0 = 9.8 m/s^2)."""
    if radius_earth <= 0:
        return 0.0
    return round(mass_earth / (radius_earth**2), 2)

def check_tidal_locking(semi_major_axis_au, star_mass_solar):
    """Flags if a planet is likely tidally locked to its host star."""
    # M-dwarf stars with close-in planets are prime targets for tidal locking
    return semi_major_axis_au < 0.1 and star_mass_solar < 0.6

def classify_planet_type(radius_earth, density_earth):
    """Categorizes planet structure based on bulk density and size."""
    if radius_earth > 1.6 or density_earth < 0.3:
        return "Gas Giant / Sub-Neptune"
    elif density_earth >= 0.8 and radius_earth <= 1.6:
        return "Rocky Terrestrial"
    else:
        return "Possible Water World / Ocean Planet"

def estimate_greenhouse_warming(
    mass_earth: float, radius_earth: float, t_eq_kelvin: float
) -> float:
    """Dynamically estimates greenhouse temperature boost (Delta T in Kelvin/Celsius)

    based on mass, radius, and equilibrium temperature.
    """
    if radius_earth <= 0:
        return 0.0
    # 1. Surface gravity relative to Earth (g = M / R^2)
    surface_gravity = mass_earth / (radius_earth**2)

    # 2. Determine atmospheric thickness multiplier based on planet size and gravity
    if radius_earth < 0.5 or surface_gravity < 0.2:
        # Bare rock / thin atmosphere regime (e.g., Moon, Mercury, Mars)
        atmo_factor = 0.1
    elif radius_earth <= 1.6:
        # Rocky terrestrial regime (Earth baseline: g=1.0, R=1.0 -> factor=1.0)
        atmo_factor = (surface_gravity*0.6) + (radius_earth*0.4)
    else:
        # Sub-Neptune / Gas envelope regime (thick runaway atmosphere)
        atmo_factor = 3.5 * ((radius_earth / 1.6) ** 1.5)

    # 3. Scale Earth's baseline greenhouse warming (33.3 K) by atmosphere factor
    # and re-radiation flux (higher T_eq drives stronger thermal re-radiation)
    flux_scaling = (t_eq_kelvin / 255.0) ** 0.5
    delta_t = 33.3 * atmo_factor * flux_scaling

    return round(delta_t, 1)

def search_planets(planets, query):
    query = query.strip().lower()
    matches = []
    for p in planets:
        if query in p['name'].lower():
            matches.append(p)
    return matches

def check_habitability(name, star_luminosity, planet_distance, planet_radius, planet_mass, density, albedo):
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

    # Estimate temperature in Celsius and Kelvin (including dynamic greenhouse warming)
    t_eq_kelvin = 278.5 * ((energy_received * (1 - albedo)) ** 0.25)
    delta_t = estimate_greenhouse_warming(planet_mass, planet_radius, t_eq_kelvin)
    temp_kelvin = t_eq_kelvin + delta_t
    temp_celsius = temp_kelvin - 273.15

    # Estimate star mass from luminosity (M_star = L^0.25)
    star_mass = star_luminosity ** 0.25

    # Compute ESI and Orbital Period
    escape_vel = math.sqrt(planet_mass / planet_radius) if planet_radius > 0 else 0.0
    esi = calculate_comprehensive_esi(planet_radius, density, escape_vel, temp_kelvin)
    period_years, period_days = calculate_orbital_period(planet_distance, star_mass)

    # Additional calculations
    gravity = calculate_surface_gravity(planet_mass, planet_radius)
    tidal_locked = check_tidal_locking(planet_distance, star_mass)
    planet_type = classify_planet_type(planet_radius, density)

    # Build analysis results
    output = []
    output.append(f"\n=========================================")
    output.append(f"          ANALYSIS FOR {name.upper()}")
    output.append(f"=========================================")
    output.append(f"  Planet Type:      {planet_type}")
    output.append(f"  Energy Received:  {energy_received:.4f}x Earth's level")
    output.append(f"  Habitable Zone:   {inner_edge:.4f} AU to {outer_edge:.4f} AU")
    output.append(f"  Est. Temperature: {temp_celsius:.1f} °C ({temp_kelvin:.1f} K)")
    output.append(f"  Rocky Planet:     {'Yes' if is_rocky else 'No'} (Radius: {planet_radius}x Earth)")
    output.append(f"  ---------------------------------------")
    output.append(f"  Orbital Period:   {period_years:.2f} Earth years ({period_days:.1f} days)")
    output.append(f"  Escape Velocity:  {escape_vel:.2f}x Earth's level")
    output.append(f"  Surface Gravity:  {gravity:.2f}x Earth's level")
    output.append(f"  Tidally Locked:   {'Yes' if tidal_locked else 'No'}")
    output.append(f"  ---------------------------------------")
    output.append(f"  Earth Similarity Index (ESI) Breakdown:")
    output.append(f"    Interior ESI:   {esi['Interior_ESI']:.3f}")
    output.append(f"    Surface ESI:    {esi['Surface_ESI']:.3f}")
    output.append(f"    Global ESI:     {esi['Global_ESI']:.3f}")
    output.append(f"  ---------------------------------------")

    # Verdict
    if in_habitable_zone and is_rocky and -20 <= temp_celsius <= 100:
        output.append("  Verdict: Potentially Habitable Rocky World!")
    elif in_habitable_zone and is_rocky and temp_celsius > 100:
        output.append("  Verdict: In the Habitable Zone, but temperature is Too Hot for Life.")
    elif in_habitable_zone and is_rocky and temp_celsius < -20:
        output.append("  Verdict: In the Habitable Zone, but temperature is Too Cold for Life.")
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
    print(f"  Density:      {p['density']}x Earth")
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
                density=p['density'],
                albedo=p['albedo']
            )
            print(analysis_result)

if __name__ == "__main__":
    main()
