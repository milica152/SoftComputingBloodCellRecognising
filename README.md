# SoftComputingBloodCellRecognising

Pyton okruženje : 
  -Python 3.6
  -matplotlib 3.1.2
  -numpy 1.17.4
  -opencv-python 3.4.1.15
  
U programu se koriste putanje "dataset" foldera i "results" foldera te je bitno da oni ostanu na istoj putanji kao i oba .py fajla.

Program učitava slike dataseta iz istoimenog foldera, na njima pronalazi i oznacava crvenom bojom RBC, a plavom WBC i označene slike čuva u "results" folderu. U results.txt upisuje lokacije pronadjenih RBC u csv formatu kako bi kasnije mogli da se uporede sa anotacijama datim u datasetu.


blood_cell_detection.py se pokrece da bi se dobilo resenje, a evaluation.py se pokrece da bi se to resenje uporedilo sa anotacijama, i dobio recall i precision.
