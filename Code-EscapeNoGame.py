import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import soundfile as sf

"""---------------------------------MESSAGE TO BINAIRE---------------------------------"""
def Message():
    type_fichier = int(input("Veuillez selectionner le type de fichier :\n 1) Message texte\n 2) Fichier texte\n"))

    # SI C'EST UN MESSAGE
    if type_fichier == 1:
        message = input("Veuillez entrer votre message : entre 5 et 10 caractères.   ")
        # VERIFIE SI LE MESSAGE CONTIENT ENTRE 5 A 10 CARACTERES
        assert 5 <= len(message) <= 10, "Votre message doit contenir entre 5 et 10 caractères"
        
        binaire = ''.join(format(ord(car), '08b') for car in message)   # TRANSFORME LE MESSAGE EN BINAIRE AVEC LA TABLE ASCII
        return binaire
     
    # SI C'EST UN FICHIER TXT
    if type_fichier == 2: 
        nom_fichier = input("Entrez le nom du fichier (sans l'extension)\n")    
        with open(f"examples/{nom_fichier}.txt", "r") as file:
            fichier = file.read()
        
        binaire = ''.join(format(ord(car), '08b') for car in fichier)  # TRANSFORME LE FICHIER EN BINAIRE AVEC LA TABLE ASCII
        return binaire


"""---------------------------------ENCODAGE MANCHESTER---------------------------------"""
def enco_manchester(bits):
    manchester = []   # STOCK LE RESULTAT DE L'ENCODAGE  
    
    for i in bits:    # PARCOURS LE MESSAGE BINAIRE
        if i == '1':  # SI i = 1, ON AJOUTE DANS L'ORDRE 1 PUIS -1
            manchester.append(1)
            manchester.append(-1)
        elif i == '0':  # SI i = 0, ON AJOUTE DANS L'ORDRE -1 PUIS 1
            manchester.append(-1)
            manchester.append(1)
            
    return manchester


"""---------------------------------DECODAGE MANCHESTER---------------------------------"""
def deco_manchester(bits):
    manchester = ''        # STOCK LE RESULTAT DU DECODAGE
    for i in range(0, len(bits), 2):  
        if (bits[i] == 1 and bits[i+1] == -1):   
            manchester += '1'
        if (bits[i] == -1 and bits[i+1] == 1):
            manchester += '0'
         
    return manchester


"""---------------------------------BINAIRE TO MESSAGE---------------------------------"""
def binaire_vers_texte(binaire):
    # SEPARE LA CHAINE BINAIRE EN MORCEAUX DE 8 BITS
    octets = [binaire[i:i+8] for i in range(0, len(binaire), 8)]
    # CONVERTIT CHAQUE MORCEAU (OCTET) EN CARACTERE ASCII
    texte = ''.join(chr(int(octet, 2)) for octet in octets)
    print("Le message est : ", texte)


"""---------------------------------CODE PRINCIPAL---------------------------------"""
def main():
    bits = Message()
    print("Le message en binaire est : ", bits)

    encodage_manchester = enco_manchester(bits)
    print("Codage Manchester :", encodage_manchester)

    # VARIABLES 
    baud = 300                            # DEBIT (bit/s)
    Fe = 22_050                           # FREQUENCE D'ECHANTILLONAGE
    Nbits = len(encodage_manchester)      # NOMBRE DE BITS 
    Ns = int(Fe/baud)                     # Nombre de symboles par bit
    N = int(Nbits * Ns)                   # Nombre total d'échantillons
    # VECTEUR TEMPS
    t = np.arange(0, N/Fe, 1/Fe)  

    # DUPLICATION DU MESSAGE
    msg_bit_duplique = np.repeat(encodage_manchester, Ns)

    # GENERATION DE LA PORTEUSE
    Ap = 1
    Fp = 2_000
    Porteuse = Ap * np.sin(2 * np.pi * Fp * t)

    # CALCUL DE LA MODULATION ASK
    ASK = msg_bit_duplique * Porteuse

    # AFFICHAGES
    plt.figure(figsize=(10,2))   
    plt.plot(t[0:2_000], msg_bit_duplique[0:2_000])  
    plt.title("Message binaire codé Manchester")

    plt.figure(figsize=(10,2))
    plt.plot(t[0:2_000], Porteuse[0:2_000])
    plt.title("Porteuse")

    plt.figure(figsize=(10,2))
    plt.plot(t[0:2_000], ASK[0:2_000])
    plt.title("Modulation ASK du message binaire codé Manchester")

    plt.show()  

    # SIMULATION DU SIGNAL AUDIO
    print("\nLecture du signal modulé (attention au volume !) ...")
    sd.play(ASK, Fe)
    sd.wait()

    # DEMODULATION
    Produit = ASK * Porteuse
    res = [int(np.trapz(Produit[i:i+Ns])) for i in range(0, N, Ns)] 
    msg_demodule_ASK = [1 if r > 0 else -1 for r in res]

    print("\nSignal démodulé (ASK):", msg_demodule_ASK)

    # CALCUL DES ERREURS
    Erreur = [encodage_manchester[k] == msg_demodule_ASK[k] for k in range(len(encodage_manchester))]
    print("\nErreur de reception :", Erreur)

    # CORRECTION (remplacement par les bons bits si erreur)
    for i in range(len(Erreur)):
        if not Erreur[i]:
            msg_demodule_ASK[i] = encodage_manchester[i]
            print("Correction du bit ", i, " → ", msg_demodule_ASK[i])

    # DECODAGE
    decodage_manchester = deco_manchester(msg_demodule_ASK)
    print("Décodage Manchester : ", decodage_manchester)

    # RETOUR AU MESSAGE
    binaire_vers_texte(decodage_manchester)


if __name__ == "__main__":
    main()
