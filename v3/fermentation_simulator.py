import numpy as np
from v3 import kinetics, plotting, utils
from v3.batch import Batch
from v3.co2.co2_model import CarbonDioxideModel
from v3.database import databases
from v3.reactor import Reactor

chemicals = databases.chemicals
#líklegast best að fara betur yfir öll nöfn, t.d. hafa alltaf sykur eða substrate
#ekki sáttur með self úr batch og reactor

class FermentationSimulator:
    def __init__(
        self,
        reactor: Reactor,
        batch: Batch,
        carbon_dioxided_model: CarbonDioxideModel,
        simulation_time: float,
    ) -> None:
        if batch.sugar_mass < 0:
            raise ValueError("Sugar mass cannot be negative.")

        if batch.biomass_mass < 0:
            raise ValueError("Biomass cannot be negative.")

        if simulation_time <= 0:
            raise ValueError("Simulation time must be greater than zero.")

        self.reactor = reactor
        self.carbon_dioxided_model = carbon_dioxided_model
        self.batch = batch
        self.biomass_mass = batch.biomass_mass
        self.sugar_mass = batch.sugar_mass
        self.simulation_time = simulation_time

        self.dt = 3.6e-3
        self.fermentation_time = 0

        self.mu_max = None
        self.biomass_concentration = None
        self.sugar_concentration = None
        self.ethanol_concentration = None

    def euler(self, Xn: float, Sn: float, mu_max: float) -> tuple:
        En = 0
        S0 = Sn
        count = 0

        biomass_mass = [Xn]
        sugar_concentration = [Sn]
        ethanol_concentration = [En]

        self.carbon_dioxided_model.update_values(En, Sn)

        while count < (self.simulation_time / self.dt) and Sn > 1e-6:
            X = Xn + (self.dt * (Xn * mu_max * Sn)) / (self.batch.yeast.Ks + Sn)
            S = Sn - (self.dt * (mu_max * Xn * Sn)) / (
                self.batch.yeast.Y_xs * (self.batch.yeast.Ks + Sn)
            )

            Xn = X
            Sn = max(S, 0)

            glucose_to_ethanol = (S0 - Sn) * (1 - self.batch.yeast.Y_xs)

            En = (
                2
                * glucose_to_ethanol
                * (
                    chemicals["ethanol"]["molar_mass"]
                    / chemicals["glucose"]["molar_mass"]
                )
            )

            self.carbon_dioxided_model.update_values(En, Sn)

            biomass_mass.append(Xn)
            sugar_concentration.append(Sn)
            ethanol_concentration.append(En)

            count += 1

        return (
            np.array(biomass_mass),
            np.array(sugar_concentration),
            np.array(ethanol_concentration),
            count * self.dt,
        )

    def prepare(self) -> None:

        sugar_concentration = utils.mass_to_concentration(self.sugar_mass, self.batch.liquid_volume)
        biomass_concentration = utils.mass_to_concentration(self.biomass_mass, self.batch.liquid_volume)

        self.mu_max = kinetics.rosso_cardinal(
            self.reactor.T_set,
            self.batch.yeast.T_min,
            self.batch.yeast.T_max,
            self.batch.yeast.T_opt,
            self.batch.yeast.mu_opt,
        )

        (
            self.biomass_concentration,
            self.sugar_concentration,
            self.ethanol_concentration,
            self.fermentation_time,
        ) = self.euler(biomass_concentration, sugar_concentration, self.mu_max)

#bæta við co2 massa
    def print_status(self) -> None:
        def print_status(self) -> None:
            print(f"""
======================================================================
                    FERMENTATION SIMULATION
======================================================================

Reactor
----------------------------------------------------------------------
Volume                : {self.reactor.volume:.2f} L
Temperature setpoint  : {self.reactor.T_set:.2f} °C
Total pressure        : {self.reactor.P_tot:.2f}


Yeast
----------------------------------------------------------------------
Strain                : {self.batch.yeast.name}
Maximum growth (μmax) : {self.mu_max:.3f} h⁻¹
Ks                    : {self.batch.yeast.Ks} g/L


Batch
----------------------------------------------------------------------
Liquid volume         : {self.batch.liquid_volume:.2f} L
Sugar mass            : {self.batch.sugar_mass:.2f} g
Biomass mass          : {self.batch.biomass_mass:.2f} g


Simulation
----------------------------------------------------------------------
Requested time        : {self.simulation_time:.2f} h
Fermentation time     : {self.fermentation_time:.2f} h
Sugar conversion      : {((self.sugar_mass - self.sugar_concentration[-1]) / self.sugar_mass) * 100:.1f} %
CO₂ mass escaped      : {''}

======================================================================
""")

#jafnvel runna co2 í gegnum þetta eða búa til nýjan klasa sem rönnar allt
    def run(self) -> None:
        print("Simulation is now running")

        self.prepare()
        plotting.draw_fermentation_graph(
            self.dt,
            self.biomass_concentration,
            self.sugar_concentration,
            self.ethanol_concentration,
        )
        self.carbon_dioxided_model.plot_co2()
        self.print_status()
