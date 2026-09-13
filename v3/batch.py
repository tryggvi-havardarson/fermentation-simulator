from v3.yeast import Yeast


class Batch:
    def __init__(
        self,
        yeast: Yeast,
        feedstock: str,
        liquid_volume: float,
        water_mass: float,
        sugar_mass: float,
        biomass_mass: float,
    ) -> None:
        self.yeast = Yeast(yeast)
        self.feedstock = feedstock
        self.liquid_volume = liquid_volume
        self.water_mass = water_mass
        self.sugar_mass = sugar_mass
        self.biomass_mass = biomass_mass

