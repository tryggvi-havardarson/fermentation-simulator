from v3.batch import Batch
from v3.co2.co2_model import CarbonDioxideModel
from v3.fermentation_simulator import FermentationSimulator
from v3.reactor import Reactor

# Líka pæling með að tengja process við þetta allt
# gæti þurft að endur skoða öll stök files
# þarf líka að getað notað sykur eitt og sér í process
reactor1 = Reactor(4.8, 20, 25, 1)
batch1 = Batch("yeast_proxy", "rowse_squeezy_honey", 4, 3689, 450, 2.5)
carbon_dioxide_model1 = CarbonDioxideModel(reactor1, batch1)

fermentation1 = FermentationSimulator(reactor1, batch1, carbon_dioxide_model1, 144)

fermentation1.run()
