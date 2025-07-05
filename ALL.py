import EPCI
import os

#os.system("python barometre_EPCI_2025_big_percent.py "+"MEL")

for key, value in EPCI.all.items():
    os.system("python barometre_EPCI.py "+key+" 2025 taux")
    os.system("python barometre_EPCI.py "+key+" 2021 taux")
    os.system("python barometre_EPCI.py "+key+" 2025 reponses")
    os.system("python barometre_EPCI.py "+key+" 2021 reponses")
    os.system("python barometre_EPCI_2025_logo.py "+key)
