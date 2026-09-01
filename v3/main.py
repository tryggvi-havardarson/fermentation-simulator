from fermentation_simulator import FermentationSimulator
from reactor import Reactor
from yeast import Yeast

yeast1 = Yeast("yeast_proxy")
reactor1 = Reactor(4.8, 25)

fermentation1 = FermentationSimulator(reactor1, yeast1, 700, 2.5, 144)

fermentation1.run()
