import numpy as np

from v3 import kinetics, plotting
from v3.batch import Batch
from v3.co2.co2_model import CarbonDioxideModel
from v3.database import databases
from v3.reactor import Reactor
from v3.yeast import Yeast

chemicals = databases.chemicals


class FermentationSimulator:
    def __init__(
        self,
        reactor: Reactor,
        yeast: Yeast,
        carbon_dioxided_model: CarbonDioxideModel,
        batch: Batch,
        simulation_time: float,
    ) -> None:
        if batch.sugar_mass < 0:
            raise ValueError("Sugar mass cannot be negative.")

        if batch.biomass_mass < 0:
            raise ValueError("Biomass cannot be negative.")

        if simulation_time <= 0:
            raise ValueError("Simulation time must be greater than zero.")

        self.reactor = reactor
        self.yeast = yeast
        self.carbon_dioxided_model = carbon_dioxided_model
        self.batch = batch
        self.biomass_mass = batch.biomass_mass
        self.sugar_mass = batch.sugar_mass
        self.simulation_time = simulation_time

        self.dt = 0.001
        self.fermentation_time = 0

        self.mu_max = None
        self.biomass_concentration = None
        self.sugar_concentration = None
        self.ethanol_concentration = None

    def mass_to_concentration(self, mass: float) -> float:
        return mass / self.batch.liquid_volume

    def euler(self, Xn: float, Sn: float, mu_max: float) -> tuple:
        En = 0
        S0 = Sn
        count = 0

        biomass_mass = [Xn]
        sugar_concentration = [Sn]
        ethanol_concentration = [En]

        self.carbon_dioxided_model.update_values(En, Sn)
        
        while count < (self.simulation_time / self.dt) and Sn > 1e-9:
            X = Xn + (self.dt * (Xn * mu_max * Sn)) / (self.yeast.Ks + Sn)
            S = Sn - (self.dt * (mu_max * Xn * Sn)) / (
                self.yeast.Y_xs * (self.yeast.Ks + Sn)
            )

            Xn = X
            Sn = max(S, 0)

            glucose_to_ethanol = (S0 - Sn) * (1 - self.yeast.Y_xs)

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

        sugar_concentration = self.mass_to_concentration(self.sugar_mass)
        biomass_concentration = self.mass_to_concentration(self.biomass_mass)
        self.mu_max = kinetics.rosso_cardinal(
            self.reactor.T_set,
            self.yeast.T_min,
            self.yeast.T_max,
            self.yeast.T_opt,
            self.yeast.mu_opt,
        )

        (
            self.biomass_concentration,
            self.sugar_concentration,
            self.ethanol_concentration,
            self.fermentation_time,
            
        ) = self.euler(biomass_concentration, sugar_concentration, self.mu_max)


    def print_status(self) -> None:
        print(f"""
        ======================================================================
                                FERMENTATION SIMULATION
        ======================================================================

        Batch
        ----------------------------------------------------------------------
        Volume                : {self.batch.liquid_volume} L
        Temperature           : {self.reactor.T_set} °C


        Yeast
        ----------------------------------------------------------------------
        Strain                : {self.yeast.name}
        Maximum growth (μmax) : {self.mu_max:.3f} h⁻¹
        Ks                    : {self.yeast.Ks} g/L


        Simulation
        ----------------------------------------------------------------------
        Requested time        : {self.simulation_time:.2f} h
        Fermentation time     : {self.fermentation_time:.2f} h
        Sugar conversion      : {((self.sugar_mass - self.sugar_concentration[-1]) / self.sugar_mass) * 100:.1f} %


        Component Mass Balance
        ----------------------------------------------------------------------
        Component              Initial (g)        Final (g)
        ----------------------------------------------------------------------
        Biomass             {self.biomass_mass:12.2f}   {self.batch.liquid_volume * self.biomass_concentration[-1]:12.2f}
        Sugar               {self.sugar_mass:12.2f}   {self.batch.liquid_volume * self.sugar_concentration[-1]:12.2f}
        Ethanol             {0:12.2f}   {self.batch.liquid_volume * self.ethanol_concentration[-1]:12.2f}
        Carbon dioxide      {0:12.2f}   {((self.batch.liquid_volume * self.ethanol_concentration[-1]) / (chemicals["ethanol"]["molar_mass"])) * chemicals["carbon_dioxide"]["molar_mass"]:12.2f}
        ----------------------------------------------------------------------
        """)

    def run(self) -> None:
        print("Simulation is now running")

        self.prepare()
        plotting.draw_fermentation_graph(self.dt,self.biomass_concentration,self.sugar_concentration,self.ethanol_concentration)
        self.print_status()
