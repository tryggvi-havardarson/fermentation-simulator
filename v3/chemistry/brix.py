water_density_20C = 998.2067  # kg/m^3
from pathlib import Path

import pandas as pd

from v3.chemistry.abv import abv_calculator, gravity_calculator

v3_folder = Path(__file__).parent.parent
csv_file = v3_folder / "database" / "brix_data.csv"

df = pd.read_csv(csv_file)


def brix_to_volume(m_honey, brix_honey, brix_target):
    m_sugar = (brix_honey * m_honey) / 100
    m_total = 100 * (m_sugar / brix_target)
    m_water = m_total - m_honey

    volume_of_water_litres = m_water / water_density_20C

    return volume_of_water_litres


def linear_interpolation(x, x1, x2, y1, y2):
    y = y1 + (y2 - y1) * ((x - x1) / (x2 - x1))

    return y


def gravity_brix(x, command):

    target = x

    if command == "brix":
        column1 = "Specific Gravity 20°C"
        column2 = "Brix"

    elif command == "gravity":
        column1 = "Brix"
        column2 = "Specific Gravity 20°C"

    else:
        print("Command not valid")
        return

    exact = df[df[column1] == target]

    if not exact.empty:
        row = exact.index[0]
        return df.at[df.index[row], column2]

    else:
        below = df[df[column1] < target]
        above = df[df[column1] > target]

        if not below.empty:
            row_below = below[column1].idxmax()

        if not above.empty:
            row_above = above[column1].idxmin()

        x1 = df.at[df.index[row_below], column1]
        x2 = df.at[df.index[row_above], column1]
        y1 = df.at[df.index[row_below], column2]
        y2 = df.at[df.index[row_above], column2]

        y = linear_interpolation(x, x1, x2, y1, y2)
        return y


def target_water_volume(m_honey, brix_honey, target_abv):

    FG = 1.000

    target_OG = gravity_calculator(target_abv, FG)
    brix_target = gravity_brix(target_OG, "brix")
    volume_of_water_litres = brix_to_volume(m_honey, brix_honey, brix_target)

    print("target og:", target_OG)
    print("target brix:", brix_target)
    print("volume:", volume_of_water_litres)


def brix_to_sugar_mass(brix, m_tot):
    m_sugar = (brix / 100) * m_tot

    return m_sugar


def brix_to_tot_mass(brix, m_sugar):
    m_tot = (m_sugar / brix) * 100

    return m_tot


def target_volume(target_abv, target_volume, brix_honey):

    FG = 1.000

    target_OG = gravity_calculator(target_abv, FG)
    target_density = target_OG * water_density_20C
    target_tot_mass = target_density * target_volume
    target_brix = gravity_brix(target_OG, "brix")
    target_sugar_mass = brix_to_sugar_mass(target_brix, target_tot_mass)
    target_honey_mass = brix_to_tot_mass(brix_honey, target_sugar_mass)
    target_water_mass = target_tot_mass - target_honey_mass
    target_water_volume = target_water_mass / water_density_20C

    print(f"Target honey mass is: {target_honey_mass}g")
    print(f"Target water volume is: {target_water_volume}L")


print(abv_calculator(1.034, 1.006))
print(abv_calculator(1.0385, 1.008))
