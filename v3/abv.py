water_density_20C = 998.2067  # kg/m^3
import pandas as pd
from scipy.optimize import root_scalar


def abv_calculator(OG, FG):
    abv = ((76.08 * (OG - FG)) / (1.775 - OG)) * (FG / 0.794)

    return round(abv, ndigits=3)


def gravity_calculator(abv, FG=1):

    def OG_equation(OG):
        return abv - ((76.08 * (OG - FG)) / (1.775 - OG)) * (FG / 0.794)

    solution = root_scalar(OG_equation, x0=0, x1=1)

    return solution.root


def brix_to_volume(m_honey, brix_honey, brix_target):
    m_sugar = (brix_honey * m_honey) / 100
    m_total = 100 * (m_sugar / brix_target)
    m_water = m_total - m_honey

    volume_of_water_litres = m_water / water_density_20C

    return volume_of_water_litres


def linear_interpolation(x, x1, x2, y1, y2):
    y = y1 + (y2 - y1) * ((x - x1) / (x2 - x1))

    return y


def gravity_to_brix(x):
    df = pd.read_csv(
        "C:/Users/trygg/OneDrive/Documents/GitHub/fermentation-simulator/v3/brix_data.csv"
    )

    target = x

    exact = df[df["Specific Gravity 20°C"] == target]

    if not exact.empty:
        row = exact.index[0]
        return df.at[df.index[row], "Brix"]

    else:
        below = df[df["Specific Gravity 20°C"] < target]
        above = df[df["Specific Gravity 20°C"] > target]

        if not below.empty:
            row_below = below["Specific Gravity 20°C"].idxmax()

        if not above.empty:
            row_above = above["Specific Gravity 20°C"].idxmin()

        x1 = df.at[df.index[row_below], "Specific Gravity 20°C"]
        x2 = df.at[df.index[row_above], "Specific Gravity 20°C"]
        y1 = df.at[df.index[row_below], "Brix"]
        y2 = df.at[df.index[row_above], "Brix"]

        y = linear_interpolation(x, x1, x2, y1, y2)
        return y


def target_water_volume(m_honey, brix_honey, target_abv):
    target_OG = gravity_calculator(target_abv)
    brix_target = gravity_to_brix(target_OG)
    volume_of_water_litres = brix_to_volume(m_honey, brix_honey, brix_target)

    print("target og:", target_OG)
    print("target brix:", brix_target)
    print("volume:", volume_of_water_litres)


print(target_water_volume(1000, 82, 5))
