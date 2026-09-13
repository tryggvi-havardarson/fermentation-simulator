import numpy as np
from v3 import utils
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

        self.dt = 3.6e-3

        self.y_co2 = 0
        self.co2_liquid_molarity = 0
        self.ethanol_mass_fraction = 0
        self.water_mass_fraction = 1
        self.sugar_concentration = None
        self.ethanol_concentration = None
        self.glucose_molarity = None

        self.kLa = None
        self.henrys_constant = None
        self.co2_transfer_rate = None
        self.co2_production_rate = None

        self.gas_volume = reactor.volume - batch.liquid_volume
        self.total_moles = (reactor.P_tot * self.gas_volume) / (
            utils.celsius_to_kelvin(self.reactor.T_set) * R
        )

        self.co2_liquid_molarity_history = []
        self.y_co2_history = []
        self.cumulative_escaped_mass_history = []
        self.kLa_history = []

    def update_sugar_concentration(self, new_value) -> None:

        self.sugar_concentration = new_value

    def update_ethanol_concentration(self, new_value) -> None:

        self.ethanol_concentration = new_value

    def update_solvent_mass_fractions(self) -> None:

        water_mass = self.batch.water_mass
        ethanol_mass = utils.mass_concentration_to_mass(
            self.ethanol_concentration, self.batch.liquid_volume
        )
        total_solvent_mass = water_mass + ethanol_mass

        self.water_mass_fraction = utils.mass_to_mass_fraction(
            water_mass, total_solvent_mass
        )
        self.ethanol_mass_fraction = utils.mass_to_mass_fraction(
            ethanol_mass, total_solvent_mass
        )

    def update_kLa(
        self, Rg, K=0.5, b1=1.8, b2=2.5, alpha=0.5, beta=-0.4, gamma=0.3
    ) -> None:

        self.kLa = (
            K
            * ((Rg) ** alpha)
            * ((1 + b1 * self.glucose_molarity) ** beta)
            * ((1 + b2 * self.ethanol_mass_fraction) ** gamma)
        )

    def update_co2_transfer_rate(self) -> None:

        print(
            "kLa =",
            self.kLa,
            "V =",
            self.batch.liquid_volume,
            "Caq =",
            self.co2_liquid_molarity,
            "kH =",
            self.henrys_constant,
            "yco2 =",
            self.y_co2,
        )

        self.co2_transfer_rate = (
            self.kLa
            * self.batch.liquid_volume
            * (self.co2_liquid_molarity - (self.henrys_constant * self.y_co2))
        )

    def update_yco2(self) -> None:

        dyco2_dt = (self.co2_transfer_rate * (1 - self.y_co2)) / self.total_moles

        self.y_co2 += dyco2_dt * self.dt

        self.y_co2_history.append(self.y_co2)

    def update_co2_production_rate(self, new_ethanol_value) -> None:

        # updata tvisvar, kannski betra að gera öðruvísi eða nota filler
        if self.ethanol_concentration is not None:
            previous_ethanol_concentration = self.ethanol_concentration

            self.update_ethanol_concentration(new_ethanol_value)

            self.co2_production_rate = (
                (self.ethanol_concentration) - (previous_ethanol_concentration)
            ) / self.dt
        else:
            self.update_ethanol_concentration(new_ethanol_value)
            self.co2_production_rate = self.ethanol_concentration

        self.co2_production_rate *= (self.batch.liquid_volume) / chemicals["ethanol"][
            "molar_mass"
        ]

    def update_co2_liquid_molarity(self) -> None:

        dCco2_dt = (
            self.co2_production_rate - self.co2_transfer_rate
        ) / self.batch.liquid_volume

        self.co2_liquid_molarity += dCco2_dt * self.dt

        self.co2_liquid_molarity_history.append(self.co2_liquid_molarity)

    def update_glucose_molarity(self) -> None:

        self.glucose_molarity = utils.mass_concentration_to_molarity(
            self.sugar_concentration, chemicals["glucose"]["molar_mass"]
        )

    def update_kH(self) -> None:

        self.henrys_constant = henrys_law.calculate_kH_final(
            utils.celsius_to_kelvin(self.reactor.T_set),
            self.glucose_molarity,
            self.water_mass_fraction,
            self.ethanol_mass_fraction,
        )

    # ákveða hvernig ég vill hafa heildar massatap og/eða co2 massa tap
    def update_escaped_mass_transfer(self) -> None:

        M_air = (chemicals["oxygen"]["molar_mass"] * 0.21) + (
            chemicals["nitrogen"]["molar_mass"] * 0.79
        )
        M_co2 = chemicals["carbon_dioxide"]["molar_mass"]

        mass_transfer_value = self.co2_transfer_rate * (
            M_air * (1 - self.y_co2) + M_co2 * self.y_co2
        )

        mass_transfer_value *= self.dt

        if self.cumulative_escaped_mass_history:
            mass_transfer_value += self.cumulative_escaped_mass_history[-1]

        self.cumulative_escaped_mass_history.append(mass_transfer_value)

    # sýnist ok en þarf að fara betur yfir
    def update_values(self, new_ethanol_value, new_sugar_value) -> None:

        self.update_co2_production_rate(new_ethanol_value)
        self.update_sugar_concentration(new_sugar_value)
        self.update_solvent_mass_fractions()
        self.update_glucose_molarity()
        self.update_kH()

        self.update_kLa(self.co2_production_rate)
        self.update_co2_transfer_rate()
        self.update_yco2()
        self.update_co2_liquid_molarity()
        self.update_escaped_mass_transfer()

    # ógeðslegt plott, þarf að gera betra sem sýnir réttar upplýsingar, líklega best að hafa method sem returnar listum líka
    def plot_co2(self):
        import matplotlib.pyplot as plt

        time = np.arange(len(self.cumulative_escaped_mass_history)) * self.dt

        plt.plot(time, self.cumulative_escaped_mass_history)
        plt.xlabel("Time [h]")
        plt.ylabel("Mass escaped [g]")
        plt.title("total mass escaped")
        plt.show()
