def abv_calculator(OG, FG):
    abv = ((76.08 * (OG - FG)) / (1.775 - OG)) * (FG / 0.794)

    return round(abv, ndigits=3)


def gravity_calculator(abv, FG):
    x = (76.08 * FG) / 0.794

    OG = (1.775 * abv + x * FG) / (abv + x)

    return OG
