import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import pygame as pg
from mutagen.mp3 import MP3  

path = ""
enpause = True
Listechanson = []
index_chan = 0
temps_total = 0 

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

        audio = MP3(path)
        temps_total = audio.info.length 

def jouer_musique():
    global enpause, path, temps_total
    if path:
        enpause = False
        pg.mixer.music.load(path)
        pg.mixer.music.play()

        lecteur.after(1000, obtenir_temps_total)

def obtenir_temps_total():
    global temps_total
    if pg.mixer.music.get_busy():
        texte.config(text=f"Musique en cours de lecture : {os.path.basename(path)}")
        barre_temp.config(to=temps_total) 
        mise_a_jour_barre()  

def mise_a_jour_barre():
    if pg.mixer.music.get_busy():
        temps_ecoule = pg.mixer.music.get_pos() / 1000 
        barre_temp.set(temps_ecoule) 
    if not enpause and pg.mixer.music.get_busy(): 
        lecteur.after(1000, mise_a_jour_barre)  

def suivante():
    global index_chan, path
    index_chan += 1
    if index_chan < len(Listechanson):
        path = Listechanson[index_chan]
        try:
            audio = MP3(path)
            global temps_total
            temps_total = audio.info.length
        except:
            pass
        jouer_musique()
    else:
        texte.config(text="Fin de la playlist")

def basculer_pause():
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

def clic_barre_temps(event):
    if temps_total > 0:
        position = event.x 
        proportion = position / barre_temp.winfo_width()  
        nouvelle_position = proportion * temps_total 
        pg.mixer.music.set_pos(nouvelle_position)
        mise_a_jour_barre()  

def verifier_fin_musique():
    if not enpause and path and not pg.mixer.music.get_busy(): 
        suivante() 
    else:
        lecteur.after(1000, verifier_fin_musique)  

lecteur = tk.Tk()  
pg.mixer.init()

lecteur.title("Lecteur mp3")  
texte = tk.Label(lecteur, text="Aucun fichier sélectionné") 
texte.pack(pady=10)  

choisir = tk.Button(lecteur, text="Choisir", command=choisir_fichier)
choisir.pack(pady=10)

jouer = tk.Button(lecteur, text="Jouer", command=jouer_musique) 
jouer.pack(pady=10)

pause = tk.Button(lecteur, text="Pause/Reprendre", command=basculer_pause) 
pause.pack(pady=10)

quitter = tk.Button(lecteur, text="Quitter", command=confirmer_quitter)  
quitter.pack(pady=10)

barre_vol = tk.Scale(lecteur, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume", command=volume)
barre_vol.set(50)  
barre_vol.pack(pady=10)

barre_temp = tk.Scale(lecteur, from_=0, to=180, orient=tk.HORIZONTAL, label="Temps", length=300)
barre_temp.pack(pady=10)

barre_temp.bind("<Button-1>", clic_barre_temps)  

verifier_fin_musique()

lecteur.mainloop()
