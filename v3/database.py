yeast_database = {
    "yeast_proxy": {
        "Ks": 0.18,  # g/L glucose
        "Y_xs": 0.097,  # g dry biomass / g glucose
        "T_min": 3.08,  # °C
        "T_opt": 30.03,  # °C
        "T_max": 41.21,  # °C
        "mu_opt": 0.368,  # h^-1
    }
}

chemicals = {
    "glucose": {"chemical_formula": "C6H12O6", "molar_mass": 180.16},
    "ethanol": {"chemical_formula": "C2H5OH", "molar_mass": 46.07},
    "carbon_dioxide": {"chemical_formula": "CO2", "molar_mass": 44.01},
    "water": {"chemical_formula": "H2O", "molar_mass": 18.02},
}

feedstock_database = {
    "gestus_acacia": {
        "density": 1.326,# g/mL
        "sugar_mass_concentration": 0.760,# g sugar/100g honey
        "price_per_kilogram": 1997#isk/kg
    },

    "rowse_squeezy_honey": {
        "density": None,
        "sugar_mass_concentration": 0.808,
        "price_per_kilogram": 1154
    }
}