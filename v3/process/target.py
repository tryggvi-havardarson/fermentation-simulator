from v3.chemistry import abv, brix

water_density_20C = 998.2067  # kg/m^3

def target_water_volume(m_honey, brix_honey, target_abv):

    FG = 1.000

    target_OG = brix.gravity_calculator(target_abv, FG)
    brix_target = brix.gravity_brix(target_OG, "brix")
    volume_of_water_litres = brix.brix_to_volume(m_honey, brix_honey, brix_target)

    print("target og:", target_OG)
    print("target brix:", brix_target)
    print("volume:", volume_of_water_litres)


def target_volume(target_abv, target_volume, brix_honey):

    FG = 1.000

    target_OG = abv.gravity_calculator(target_abv, FG)
    target_density = target_OG * water_density_20C
    target_tot_mass = target_density * target_volume
    target_brix = brix.gravity_brix(target_OG, "brix")
    target_sugar_mass = brix.brix_to_sugar_mass(target_brix, target_tot_mass)
    target_honey_mass = brix.brix_to_tot_mass(brix_honey, target_sugar_mass)
    target_water_mass = target_tot_mass - target_honey_mass
    target_water_volume = target_water_mass / water_density_20C

    print(f"Target honey mass is: {target_honey_mass}g")
    print(f"Target water volume is: {target_water_volume}L")