class Reactor:
    def __init__(self, volume: float, radius:float, T_set: float, P_tot) -> None:
        if volume <= 0:
            raise ValueError("Reactor volume must be greater than zero.")

        self.volume = volume
        self.radius = radius
        self.T_set = T_set
        self.P_tot = P_tot