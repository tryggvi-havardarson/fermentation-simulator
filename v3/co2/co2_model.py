import numpy as np

from v3.batch import Batch
from v3.co2 import henrys_law
from v3.database.databases import chemicals
from v3.reactor import Reactor

R = 0.08206


class CarbonDioxideModel:
    def __init__(
        self,
        reactor: Reactor,
        batch: Batch,
    ) -> None:
        self.reactor = reactor
        self.batch = batch

        self.C_aq_history = []
        self.y_CO2_history = []
        self.sim_mass_history = []
        self.kLa_history = []

        self.dt = 3.6e-3
        self.sugar_concentration = None
        self.ethanol_concentration = None
        self.fizz_velocity_constant_value = None
        self.yco2 = 0
        self.gas_transfer_speed_value = None
        self.carbon_dioxide_liquid_molarity = 0
        self.gas_production_speed = None
        self.henrys_constant = None

        self.gas_volume = reactor.volume - batch.liquid_volume
        self.w_ethanol = 0
        self.w_water = 1
        self.glucose_molarity = None
        self.total_moles = (reactor.P_tot * self.gas_volume) / (
            (self.reactor.T_set + 273.15) * R
        )

    def update_sugar_concentration(self, new_value) -> None:

        self.sugar_concentration = new_value

    def update_ethanol_concentration(self, new_value) -> None:

        self.ethanol_concentration = new_value

        
        water_mass = self.batch.water_mass
        ethanol_mass = self.mass_concentration_to_mass(self.ethanol_concentration)
        total_solvent_mass = water_mass + ethanol_mass

        self.w_water = self.mass_to_mass_fraction(water_mass, total_solvent_mass)
        self.w_ethanol = self.mass_to_mass_fraction(ethanol_mass, total_solvent_mass)

    def update_fizz_velocity_constant(
        self, Rg, K=0.5, b1=1.8, b2=2.5, alpha=0.5, beta=-0.4, gamma=0.3
    ):

        self.fizz_velocity_constant_value = (
            K
            * ((Rg) ** alpha)
            * ((1 + b1 * self.glucose_molarity) ** beta)
            * ((1 + b2 * self.w_ethanol) ** gamma)
        )

    def update_gas_transfer_speed(self) -> None:

        print(
            "kLa =", self.fizz_velocity_constant_value,
            "V =", self.batch.liquid_volume,
            "Caq =", self.carbon_dioxide_liquid_molarity,
            "kH =", self.henrys_constant,
            "yco2 =", self.yco2
        )

        self.gas_transfer_speed_value = (
            self.fizz_velocity_constant_value
            * self.batch.liquid_volume
            * (self.carbon_dioxide_liquid_molarity - (self.henrys_constant * self.yco2))
        )

    def update_yco2(self) -> None:

        dyco2_dt = (self.gas_transfer_speed_value * (1 - self.yco2)) / self.total_moles

        self.yco2 += dyco2_dt * self.dt

        self.y_CO2_history.append(self.yco2)

    def update_gas_production_speed(self, new_ethanol_value) -> None:

        if self.ethanol_concentration is not None:
            previous_ethanol_concentration = self.ethanol_concentration

            self.update_ethanol_concentration(new_ethanol_value)

            self.gas_production_speed = (
                (self.ethanol_concentration) - (previous_ethanol_concentration)
            ) / self.dt
        else:
            self.update_ethanol_concentration(new_ethanol_value)
            self.gas_production_speed = self.ethanol_concentration

        self.gas_production_speed *=((self.batch.liquid_volume)/chemicals["ethanol"]["molar_mass"])

    def update_carbon_dioxide_liquid_molarity(self) -> None:
        
        dCco2_dt = (
            self.gas_production_speed / self.batch.liquid_volume
        ) - (self.gas_transfer_speed_value / self.batch.liquid_volume)

        self.carbon_dioxide_liquid_molarity += dCco2_dt * self.dt

        self.C_aq_history.append(self.carbon_dioxide_liquid_molarity)

    def mass_concentration_to_molarity(self, mass_concentration, molar_mass) -> float:

        molarity = mass_concentration / molar_mass

        return molarity

    def mass_concentration_to_mass(self, mass_concentration) -> float:

        mass = mass_concentration * self.batch.liquid_volume

        return mass

    def mass_to_mass_fraction(
        self, mass_of_specific_solvant, total_solvent_mass
    ) -> float:

        mass_fraction = mass_of_specific_solvant / total_solvent_mass

        return mass_fraction

    def update_glucose_molarity(self) -> None:

        self.glucose_molarity = self.mass_concentration_to_molarity(
            self.sugar_concentration, chemicals["glucose"]["molar_mass"]
        )

    def update_kH(self) -> None:

        self.henrys_constant = henrys_law.kH_final(
            self.reactor.T_set+273.15, self.glucose_molarity, self.w_water, self.w_ethanol
        )

    def update_mass_transfer(self) -> None:

        M_air = (chemicals["oxygen"]["molar_mass"] * 0.21) + (
            chemicals["nitrogen"]["molar_mass"] * 0.79
        )
        M_co2 = chemicals["carbon_dioxide"]["molar_mass"]

        mass_transfer_value = self.gas_transfer_speed_value * (
            M_air * (1 - self.yco2) + M_co2 * self.yco2
        )

        mass_transfer_value *= self.dt

        if self.sim_mass_history:
            mass_transfer_value += self.sim_mass_history[-1]

        self.sim_mass_history.append(mass_transfer_value)

    def update_values(self, new_ethanol_value, new_sugar_value) -> None:

        self.update_gas_production_speed(new_ethanol_value)
        self.update_sugar_concentration(new_sugar_value)
        self.update_glucose_molarity()
        self.update_kH()

        self.update_fizz_velocity_constant(self.gas_production_speed)
        self.update_gas_transfer_speed()
        self.update_yco2()
        self.update_carbon_dioxide_liquid_molarity()
        self.update_mass_transfer()

    def plot_co2(self):
        import matplotlib.pyplot as plt

        time = np.arange(len(self.sim_mass_history)) * self.dt

        plt.plot(time, self.sim_mass_history)
        plt.xlabel("Time [h]")
        plt.ylabel("Mass escaped [g]")
        plt.title("total mass escaped")
        plt.show()