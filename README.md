CalibrationAlligator
====================
Ce script a comme objectif d'analyser les débits dans les fichiers KNR issus de VISSIM et 
de les comparer graphiquement avec les valeurs théoriques
@author
francois.belisle@wspgroup.com
20140731, mise à jour 20141105

#Instruction
#Dans le répertoire courant doivent se trouver :
#   1) Fichier .CSV contenant les débits théoriques
#   1) Fichier .CSV de clés
#   2) Fichiers .KNR (au moins 2 ...)
#   3) Fichiers de clé .txt pour redresser les mouvements

Les fichiers doivent être identifiés dans le script ; je modifierai éventuellement cececi.

# Output :
#   1) fichier sortie.txt des différences entre les valeurs moyennes des simulations et les valeurs théoriques
#       Noeud / Mvt / Débit_théorique / Débit moyen / diff moyen / diff moyen % / Écart-type / Sim 1 , Sim 2 , etc.
#       Les écart-types pour chaque simulation se retrouvent à la fin
#   2) Le graphique illustrant l'adéquation entre les résultats simulés et les débits théoriques
