class batch:
    def __init__(
        self,
        feedstock: str,
        liquid_volume: float,
        sugar_mass: float,
        biomass_mass: float,
    ) -> None:
        self.feedstock = feedstock
        self.liquid_volume = liquid_volume
        self.sugar_mass = sugar_mass
