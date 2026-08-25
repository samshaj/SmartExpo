import csv
import os
import math

def calculate_comprehensive_esi(radius_earth, density_earth, escape_vel_earth, temp_kelvin):
    """Calculates the Global Earth-Similarity Index (ESI) using 4 key factors."""
    esi_r = (1 - abs((radius_earth - 1.0) / (radius_earth + 1.0))) ** 0.57
    esi_d = (1 - abs((density_earth - 1.0) / (density_earth + 1.0))) ** 1.07
    esi_v = (1 - abs((escape_vel_earth - 1.0) / (escape_vel_earth + 1.0))) ** 0.70
    esi_t = (1 - abs((temp_kelvin - 288.0) / (temp_kelvin + 288.0))) ** 5.58

    interior_esi = math.sqrt(esi_r * esi_d)
    surface_esi = math.sqrt(esi_v * esi_t)
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
                    print(f"  {key.capitalize().replace('_', ' ')}: {value}")
            
            # Print calculated ESI and Orbital Period
            try:
                lum = float(p['luminosity'])
                sma = float(p['semi_major_axis'])
                rad = float(p['radius'])
                mass = float(p['mass'])
                density = float(p['density'])
                albedo = float(p['albedo'])
                
                # Calculations
                energy_received = lum / (sma ** 2)
                t_eq_kelvin = 278.5 * ((energy_received * (1 - albedo)) ** 0.25)
                delta_t = estimate_greenhouse_warming(mass, rad, t_eq_kelvin)
                temp_kelvin = t_eq_kelvin + delta_t
                temp_celsius = temp_kelvin - 273.15
                star_mass = lum ** 0.25
                escape_vel = math.sqrt(mass / rad) if rad > 0 else 0.0
                
                esi = calculate_comprehensive_esi(rad, density, escape_vel, temp_kelvin)
                period_years, period_days = calculate_orbital_period(sma, star_mass)
                
                gravity = calculate_surface_gravity(mass, rad)
                tidal_locked = check_tidal_locking(sma, star_mass)
                planet_type = classify_planet_type(rad, density)
                
                print(f"  Planet Type: {planet_type}")
                print(f"  Estimated Temperature: {temp_celsius:.1f} °C ({temp_kelvin:.1f} K)")
                print(f"  Orbital Period: {period_years:.2f} Earth years ({period_days:.1f} days)")
                print(f"  Escape Velocity: {escape_vel:.2f}x Earth's")
                print(f"  Surface Gravity: {gravity:.2f}x Earth's")
                print(f"  Tidally Locked: {'Yes' if tidal_locked else 'No'}")
                print(f"  Global ESI: {esi['Global_ESI']:.3f} (Interior: {esi['Interior_ESI']:.3f}, Surface: {esi['Surface_ESI']:.3f})")
            except Exception as e:
                pass
            print()


if __name__ == "__main__":
    main()
