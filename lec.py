import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import pygame as pg
from mutagen.mp3 import MP3  # Importer pour récupérer la durée d'un MP3

path = ""
enpause = True
Listechanson = []
index_chan = 0
temps_total = 0  # Durée totale de la chanson

def choisir_fichier():
    global path, Listechanson, index_chan, temps_total
    path = filedialog.askopenfilename(title="Choisir un fichier MP3", filetypes=[("Fichier MP3", "*.mp3")])
    if path:
        dossier = os.path.dirname(path)
        Listechanson = [os.path.join(dossier, f) for f in os.listdir(dossier) if f.endswith(".mp3")]
        Listechanson.sort()
        index_chan = Listechanson.index(path)
        nom_fichier = path.split("/")[-1]  
        texte.config(text=f"Choisi : {nom_fichier}")

        # Obtenir la durée du MP3 avec mutagen
        audio = MP3(path)
        global temps_total
        temps_total = audio.info.length  # Durée en secondes

def jouer_musique():
    global enpause, path, temps_total
    if path:
        enpause = False
        pg.mixer.music.load(path)
        pg.mixer.music.play()

        # Attendre un peu pour s'assurer que la musique commence à jouer avant de récupérer la durée
        lecteur.after(1000, obtenir_temps_total)

def obtenir_temps_total():
    global temps_total
    if pg.mixer.music.get_busy():
        # La musique joue, récupérons la durée totale
        texte.config(text=f"Musique en cours de lecture : {os.path.basename(path)}")
        barre_temp.config(to=temps_total)  # Met à jour la barre de progression
        mise_a_jour_barre()  # Lance la mise à jour de la barre de progression

def mise_a_jour_barre():
    if pg.mixer.music.get_busy():
        temps_ecoule = pg.mixer.music.get_pos() / 1000  # Obtenir le temps écoulé en secondes
        barre_temp.set(temps_ecoule)  # Met à jour la barre de progression
    if not enpause and pg.mixer.music.get_busy():  # Si la musique est en cours de lecture
        lecteur.after(1000, mise_a_jour_barre)  # Vérifie toutes les secondes

def suivante():
    global index_chan, path
    index_chan += 1
    if index_chan < len(Listechanson):
        path = Listechanson[index_chan]
        jouer_musique()
    else:
        texte.config(text="Fin de la playlist")

def pause():
    global enpause
    if enpause:
        pg.mixer.music.unpause()
        texte.config(text="Musique en cours")
        enpause = False
    elif not enpause:
        pg.mixer.music.pause()
        texte.config(text="Musique en pause")
        enpause = True

def confirmer_quitter():
    rep = messagebox.askyesno("Quitter ?", "Etes-vous sûr ?")
    if rep:
        lecteur.quit()

def volume(valeur):
    vol = float(valeur) / 100
    pg.mixer.music.set_volume(vol)

# Fonction pour gérer le clic sur la barre de temps
def clic_barre_temps(event):
    if temps_total > 0:
        # Calculer la position cliquée par rapport à la largeur de la barre de temps
        position = event.x  # Position du clic dans la barre
        proportion = position / barre_temp.winfo_width()  # Proportion de la barre
        nouvelle_position = proportion * temps_total  # Convertir la proportion en secondes
        pg.mixer.music.set_pos(nouvelle_position)  # Avancer la musique à la position cliquée
        mise_a_jour_barre()  # Mettre à jour la barre après le changement de position

# Fonction pour vérifier si la musique est terminée
def verifier_fin_musique():
    if not pg.mixer.music.get_busy():  # Si la musique est terminée
        suivante()  # Passer à la chanson suivante
    else:
        lecteur.after(1000, verifier_fin_musique)  # Vérifier chaque seconde si la musique est terminée

#-----------------------------------------------------------------------

lecteur = tk.Tk()  # Crée la fenêtre
pg.mixer.init()

lecteur.title("Lecteur mp3")  # Titre
texte = tk.Label(lecteur, text="Aucun fichier sélectionné")  # Texte dans une variable
texte.pack(pady=10)  # On l'envoie sur la fenêtre

choisir = tk.Button(lecteur, text="Choisir", command=choisir_fichier)  # Bouton pour choisir
choisir.pack(pady=10)

jouer = tk.Button(lecteur, text="Jouer", command=jouer_musique)  # Bouton pour jouer
jouer.pack(pady=10)

pause = tk.Button(lecteur, text="Pause/Reprendre", command=pause)  # Bouton pour mettre en pause
pause.pack(pady=10)

quitter = tk.Button(lecteur, text="Quitter", command=confirmer_quitter)  # Bouton pour quitter
quitter.pack(pady=10)

barre_vol = tk.Scale(lecteur, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume", command=volume)
barre_vol.set(50)  # Volume par défaut à 50%
barre_vol.pack(pady=10)

barre_temp = tk.Scale(lecteur, from_=0, to=180, orient=tk.HORIZONTAL, label="Temps", length=300)
barre_temp.pack(pady=10)

barre_temp.bind("<Button-1>", clic_barre_temps)  # Lier l'événement de clic à la fonction

# Vérifier si la musique est terminée
verifier_fin_musique()

lecteur.mainloop()
