from math import *

K_B = 1.380649e-23
U = 1.660539e-27

exo_mass = 1.5
exo_temp = 1000
exo_radius = 1.25

gas_masses = {
    "Hydrogen (H2)": 2.016,
    "Helium (He)": 4.002,
    "Water Vapor (H2O)": 18.015,
    "Nitrogen (N2)": 28.014,
    "Oxygen (O2)": 31.999,
    "Carbon Dioxide (CO2)": 44.01,
}

def calculate_esc_vel(mass, radius):
    esc_vel = round(11.2 * sqrt(mass/radius), 2)

    return esc_vel


def calculate_atmos_gases(temperature, esc_vels):
    results = {}

    for gas, mass in gas_masses.items():
        m = mass * U

        therm_vel = round(sqrt((3*K_B*temperature)/m),2)

        retain = esc_vels * 1000 >= (6 * therm_vel)
        results[gas] = {
            'esc_kms': round(therm_vel / 1000, 2),
            'can_retain': retain
        }
    return results

earth_retention = calculate_atmos_gases(1000, calculate_esc_vel(2, 1.25))
for gas, data in earth_retention.items():
    status = "Retained" if data["can_retain"] else "Escapes"
    print(f"{gas:20s} | Thermal Speed: {data['esc_kms']} km/s | {status}")
