from scipy.optimize import root_scalar


def abv_calculator(OG, FG):
    abv = ((76.08 * (OG - FG)) / (1.775 - OG)) * (FG / 0.794)

    return round(abv, ndigits=3)


def gravity_calculator(abv, FG):

    def OG_equation(OG):
        return abv - ((76.08 * (OG - FG)) / (1.775 - OG)) * (FG / 0.794)

    solution = root_scalar(OG_equation, x0=0, x1=1)

    return solution.root
