from v3.batch import Batch
from v3.co2.co2_model import CarbonDioxideModel
from v3.fermentation_simulator import FermentationSimulator
from v3.reactor import Reactor
from v3.yeast import Yeast

yeast1 = Yeast("yeast_proxy")
reactor1 = Reactor(4.8, 20, 25, 1)
batch1 = Batch("rowse_squeezy_honey", 4, 3689, 450, 2.5)
carbon_dioxide_model1 = CarbonDioxideModel(reactor1, batch1)

fermentation1 = FermentationSimulator(
    reactor1, yeast1, carbon_dioxide_model1, batch1, 144
)

fermentation1.run()
