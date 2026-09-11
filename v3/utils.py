def mass_to_concentration(mass, liquid_volume) -> float:
        
    return mass / liquid_volume

def celsius_to_kelvin(T):

    Temperature_in_kelvin = T+273.15

    return Temperature_in_kelvin

def mass_concentration_to_molarity(mass_concentration, molar_mass) -> float:

        molarity = mass_concentration / molar_mass

        return molarity

def mass_concentration_to_mass(mass_concentration, liquid_volume) -> float:

        mass = mass_concentration * liquid_volume

        return mass

def mass_to_mass_fraction(mass_of_specific_solvant, total_solvent_mass) -> float:

    mass_fraction = mass_of_specific_solvant / total_solvent_mass

    return mass_fraction
