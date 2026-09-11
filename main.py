from v3.batch import Batch
from v3.co2.co2_model import CarbonDioxideModel
from v3.fermentation_simulator import FermentationSimulator
from v3.reactor import Reactor
from v3.yeast import Yeast

#aðalega að finna betur út úr hvað sé Yeast, Batch og Reactor, líka tengja við hvort annað t.d. Batch->Yeast,
#Líka pæling með að tengja process við þetta allt
#þarf eiginlega að breyta öllu file systeminu, finnst skrítið að v1-3 og main séu saman líka með README
#gæti þurft að endur skoða öll stök files
#þarf líka að getað notað sykur eitt og sér í process 
yeast1 = Yeast("yeast_proxy")
reactor1 = Reactor(4.8, 20, 25, 1)
batch1 = Batch("rowse_squeezy_honey", 4, 3689, 450, 2.5)
carbon_dioxide_model1 = CarbonDioxideModel(reactor1, batch1)

fermentation1 = FermentationSimulator(
    reactor1, yeast1, carbon_dioxide_model1, batch1, 144
)

