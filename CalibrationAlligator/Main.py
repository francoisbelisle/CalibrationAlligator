# -*- coding: cp1252 -*-
#Ce script a comme objectif d'analyser les débits dans les fichiers KNR issus de VISSIM
#@author
#francois.belisle@wspgroup.com
#20140731

#Instruction
#Dans le répertoire courant doivent se trouver :
#   1) Fichier .CSV contenant les débits théoriques
#   1) Fichier .CSV de clés
#   2) Fichiers .KNR (au moins 2 ...)

# Output :
#   fichier sortie.txt des différences entre les valeurs moyennes des simulations et les valeurs théoriques
#   Noeud / Mvt / Débit_théorique / Débit moyen / diff moyen / diff moyen % / Écart-type / Sim 1 , Sim 2 , etc.
 
# Les écart-types pour chaque simulation se retrouvent à la fin

#TODO
# Changer la colonne STD pour l'aligner avec la différence
# les histoires de clés ... pas obliger de faire des erreurs si ça ne marche pas



f_clefs = "Test_Data\\141-19650-00_Cles_mvt_20140820.csv"
f_debits_theo_AM = "Test_Data\\141-19650-00_Estimation debits_0.1_20140909b_2021PM.csv"
 
def lire(standard_debits):
    import csv
    reader = csv.reader(open(standard_debits),delimiter=';') 
    nodes = {}
    header = next(reader, None)[2:]
    for row in reader :
        row_s = [w.strip() for w in row]
        node = row_s[1]
        vType = row_s[0]

        if node == "":
            continue

        if node not in nodes.keys(): # initialisation des dictionnaires
            nodes[node] = {}
            for head in header:
                nodes[node][head] = {}

        for i in range(2,len(row_s)):
            if row_s[i] == "" :
                nodes[node][header[i-2]][vType] = 0
            else:
                nodes[node][header[i-2]][vType] = row_s[i]
        
    return nodes

def test_lire():
    nodes = lire(f_debits_theo_AM)
    print nodes['135']['NBR']['Peds']

def redresser_mvt(node, mvtoriginal):
    node_mvt = node+mvtoriginal
    clefs = lire_clefs(f_clefs)
    if node_mvt in clefs.keys():
        return clefs[node_mvt]
    
    return mvtoriginal

def lire_clefs(clefs_f):
    import csv
    reader = csv.reader(open(clefs_f),delimiter=';') 
    clefs = {}
    next(reader, None)
    for row in reader :
        row_s = [w.strip() for w in row]
        clefs[row_s[0]] = row_s[1]
    return clefs

def test_lire_clefs():
    clefs = lire_clefs(f_clefs)
    print clefs

def traiter(knr):
    import csv
    fichier_tt = knr
    reader = csv.reader(open(fichier_tt),delimiter=';') 
    debits = []
    indexes = {}
    recording = False
    for row in reader :
        row_s = [w.strip() for w in row]
        if recording == True :
            node = row_s[indexes["NodeNo"]]
            mvt = redresser_mvt(node,row_s[indexes["Movement"]])
            vehtype = row_s[indexes["VehType"]]
            node_mvt_vehtype = node+"_"+mvt+"_"+vehtype
            debits.append(node_mvt_vehtype)

        if  recording == False and ("NodeNo" in row_s and "Movement" in row_s and "VehType" in row_s) : 
            recording = True
            for term in ["NodeNo", "Movement", "VehType"]:
                indexes[term] = row_s.index(term)

    # on traduit le dictionnaire node_mvt_vehtype en {node}{mvt}{vehtype}
    
    from collections import Counter
    debits_c = Counter(debits)
    debits_f = {}
    clefs = debits_c.keys()
    for clef in clefs:
        sc = clef.split("_")
        node = sc[0]
        mvt = sc[1]
        vehtype = sc[2]
    
        if node not in debits_f.keys():
            debits_f[node] = {}

        if mvt not in debits_f[node].keys():
            debits_f[node][mvt] = {}

        if vehtype not in debits_f[node][mvt].keys():
            debits_f[node][mvt][vehtype] = debits_c[clef]

    return (debits_f, knr)

def fast_traiter(knr):
    import csv
    fichier_tt = knr
    reader = csv.reader(open(fichier_tt),delimiter=';') 
    indexes = {}
    debits_f = {}
    recording = False
    for row in reader :
        row_s = [w.strip() for w in row]
        if recording == True :
            node = row_s[indexes["NodeNo"]]
            mvt = redresser_mvt(node,row_s[indexes["Movement"]])
            vehtype = row_s[indexes["VehType"]]

            if node not in debits_f.keys():
                debits_f[node] = {}

            if mvt not in debits_f[node].keys():
                debits_f[node][mvt] = {}

            if vehtype not in debits_f[node][mvt].keys():
                debits_f[node][mvt][vehtype] = 1
            else: 
                debits_f[node][mvt][vehtype] += 1

        if  recording == False and ("NodeNo" in row_s and "Movement" in row_s and "VehType" in row_s) : 
            recording = True
            for term in ["NodeNo", "Movement", "VehType"]:
                indexes[term] = row_s.index(term)
    
    return (debits_f, knr)

def test_traiter():
    """
    Cette fonction teste la fonction pour lire le knr
    """
    print "Test du Traitement de KNR"
    
    import glob
    knrs = glob.glob("*.knr")

    for knr in knrs:
        debits = traiter(knr)
        print debits


def imprimer(resultats, d_theo, outfile):
    """
    TODO : cette fonction ne devrait qu'imprimer les résultats de la comparaison entre d_VISSIM et d_theorique
    Le traitement n'a pas sa place ici
    """
    import scipy as sp

    noms = ["SIM_" + r[1].split(".")[0].split("_")[-1] for r in resultats]
    d_VISSIM = [r[0] for r in resultats]
    
    f = open(outfile,'w')
    nb_fichiers = len(d_VISSIM)
    entete = "Node;Mvt;Theorique;Moyen;Diff;Diff%;"
    for i in range(nb_fichiers):
        entete+= noms[i]+";"
    f.write(entete+"\n")

    nodes = d_theo.keys()
    mvts = d_theo[nodes[0]].keys()

    sim_diffs = []
    for i in range(nb_fichiers):
        sim_diffs.append([])
    
    for node in nodes:
        for mvt in mvts:

            debit_theorique = float(d_theo[node][mvt]['Volume'])
            s = node+";"+mvt+";"+str(debit_theorique)+";"
            vals = []

            for i in range(nb_fichiers):
                debit = 0
                #mvt in node pour cette simulation ?
                if mvt in d_VISSIM[i][node].keys():
                    if d_VISSIM[i][node][mvt].has_key('100'): # vraiment pas hot
                        debit += float(d_VISSIM[i][node][mvt]['100'])
                    if d_VISSIM[i][node][mvt].has_key('200'): # vraiment pas hot bis
                        debit += float(d_VISSIM[i][node][mvt]['200'])
                sim_diffs[i].append((debit, debit_theorique))
                vals.append(debit)

            debit_moyen = sum(vals)/float(nb_fichiers)
            diff_p = 0
            diff = (debit_theorique-debit_moyen)
            
            if debit_theorique != 0 :
                diff_p = abs(diff/debit_theorique)
            s+=str(debit_moyen)+";"+str(diff)+";"+str('%.2f'%(diff_p*100))+";"
            for i in range(nb_fichiers):
                s+=str(vals[i])+";"
            f.write(s+"\n")

    stds = []

    #calcul des écart-type par simulation
    s = "STD;;;;;;"
    for i in range(nb_fichiers):
        diffs = [debs[0]-debs[1] for debs in sim_diffs[i]]
        s+= str(sp.std(diffs))+";"
        
    f.write(s+"\n")  
    f.close()
    
    #représentation graphique des couples simulés_théoriques
    from matplotlib import pyplot as plt
    colors = ['b','g','r','c','m','y','k', '#b7102f', '#fda74a', '#f0371e', '#10B798', '#B79810', '#B74510', '#10B745', "#1082B7", "#B71082", "#B79910", "#08175B", "#23085B", "#5B2308", "#999999", "#2D2D2D", "#A13E0E", "#900C24", "#F3B7C2"]
    maximum = 0
    for i in range(nb_fichiers):
        
        x = [debit[0] for debit in sim_diffs[i]]
        y = [debit[1] for debit in sim_diffs[i]]
        maxi = max(x)
        if maximum < maxi:
            maximum = maxi
        import scipy.stats
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
        r2 = r_value**2
        plt.scatter(x,y, color=colors[i], label=str(noms[i]+" R^2 = "+'%.2f'%r2))

    plt.plot([0,maximum],[0,maximum], color = 'k')
    plt.axis((-5,maximum, -5, maximum))
    plt.xlabel("Debits simules")
    plt.ylabel("Debits theoriques")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1))
    plt.show()


resultats = []
def log_results(traitement):
    global resultats
    resultats.append(traitement)

def test_func(knr):
    return knr

def apply_async_with_callback():

    import glob
    knrs = glob.glob("Test_Data\\*.knr")
    outfile = "fichiers_debits.csv"
    import multiprocessing as mp
    pool = mp.Pool(processes = len(knrs))
    for knr in knrs:
        pool.apply_async(fast_traiter, args = (knr,) , callback=log_results)

    pool.close()
    pool.join()
    global resultats
    d_theo = lire(f_debits_theo_AM)
    imprimer(resultats, d_theo , outfile)

if __name__ == "__main__":
    import datetime
    debut = datetime.datetime.now()
    apply_async_with_callback()
    fin = datetime.datetime.now()
    duree = fin-debut
    print "Traiter en : " + str(duree.seconds) + " secondes"
    