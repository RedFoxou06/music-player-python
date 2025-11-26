import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import pygame as pg
from mutagen.mp3 import MP3

# --- Configuration du Style ---
# Palette de couleurs (Thème Dark Blue/Teal)
BG_COLOR = "#2C3E50"  # Fond principal (Bleu nuit)
FG_COLOR = "#ECF0F1"  # Texte principal (Blanc cassé)
BTN_BG = "#34495E"  # Fond des boutons (Gris bleu)
BTN_HOVER = "#1ABC9C"  # Couleur au survol (Turquoise)
ACCENT_COLOR = "#16A085"  # Couleur d'accentuation pour les sliders
QUIT_BG = "#C0392B"  # Rouge pour le bouton quitter

# Polices
FONT_TITLE = ("Helvetica", 14, "bold")
FONT_MAIN = ("Helvetica", 11)
FONT_ICONS = ("Arial", 20)  # Police plus grande pour les symboles Unicode

path = ""
enpause = True
Listechanson = []
index_chan = 0
temps_total = 0



def choisir_fichier():
    global path, Listechanson, index_chan, temps_total
    nouvelle_path = filedialog.askopenfilename(title="Choisir un fichier MP3", filetypes=[("Fichier MP3", "*.mp3")])
    if nouvelle_path:
        path = nouvelle_path
        dossier = os.path.dirname(path)
        Listechanson = [os.path.join(dossier, f) for f in os.listdir(dossier) if f.endswith(".mp3")]
        Listechanson.sort()
        index_chan = Listechanson.index(path)

        mise_a_jour_titre()
        jouer_musique()


def mise_a_jour_titre():
    if path:
        nom_fichier = os.path.basename(path)
        nom_propre = os.path.splitext(nom_fichier)[0]
        label_titre.config(text=nom_propre)


def jouer_musique():
    global enpause, path, temps_total
    if path:
        enpause = False
        pg.mixer.music.load(path)
        pg.mixer.music.play()
        mise_a_jour_titre()

        try:
            audio = MP3(path)
            temps_total = audio.info.length
        except:
            temps_total = 0

        barre_temp.config(to=temps_total)
        lecteur.after(1000, obtenir_temps_total)

        btn_pause.config(text="⏸")


def obtenir_temps_total():
    if pg.mixer.music.get_busy():
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
        jouer_musique()
    else:
        label_titre.config(text="Fin de la playlist")
        pg.mixer.music.stop()
        path = ""  
        

def basculer_pause():
    global enpause
    if not path: return

    if enpause:
        pg.mixer.music.unpause()
        btn_pause.config(text="⏸") 
        enpause = False
        mise_a_jour_barre()  
    elif not enpause:
        pg.mixer.music.pause()
        btn_pause.config(text="▶")  
        enpause = True


def confirmer_quitter():
    rep = messagebox.askyesno("Quitter", "Voulez-vous fermer le lecteur ?")
    if rep:
        lecteur.quit()


def volume(valeur):
    vol = float(valeur) / 100
    pg.mixer.music.set_volume(vol)


def clic_barre_temps(event):
    if temps_total > 0 and path:
        position = event.x
        largeur = barre_temp.winfo_width()
        if largeur > 0:
            proportion = position / largeur
            nouvelle_position = proportion * temps_total
            pg.mixer.music.set_pos(nouvelle_position)
            barre_temp.set(nouvelle_position)


def verifier_fin_musique():
    if not enpause and path and not pg.mixer.music.get_busy():
        suivante()
    lecteur.after(1000, verifier_fin_musique)


def on_enter(e):
    e.widget['background'] = BTN_HOVER


def on_leave(e):
    e.widget['background'] = BTN_BG


def on_enter_quit(e):
    e.widget['background'] = "#E74C3C"


def on_leave_quit(e):
    e.widget['background'] = QUIT_BG


# -----------------------------------------------------------------------
# CONSTRUCTION DE L'INTERFACE GRAPHIQUE STYLISÉE
# -----------------------------------------------------------------------

lecteur = tk.Tk()
pg.mixer.init()

# Configuration de la fenêtre principale
lecteur.title("Lecteur MP3 Python")
lecteur.geometry("450x550")  # Taille fixe pour un meilleur rendu
lecteur.configure(bg=BG_COLOR)  # Couleur de fond de la fenêtre
try:
    lecteur.iconbitmap("music.ico")  # Si vous avez une icône. Sinon, commentez cette ligne.
except:
    pass

# 1. Zone du Titre (Haut)
frame_titre = tk.Frame(lecteur, bg=BG_COLOR, pady=30)
frame_titre.pack(fill=tk.X)

icone_musique = tk.Label(frame_titre, text="🎵", font=("Arial", 40), bg=BG_COLOR, fg=ACCENT_COLOR)
icone_musique.pack()

label_titre = tk.Label(frame_titre, text="Sélectionnez une musique...", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR,
                       wraplength=400)
label_titre.pack(pady=(10, 0))

# 2. Barre de progression (Milieu)
# Astuce : showvalue=0 cache le numéro au dessus du slider, highlightthickness=0 enlève la bordure moche au focus
barre_temp = tk.Scale(lecteur, from_=0, to=100, orient=tk.HORIZONTAL, length=380,
                      bg=BG_COLOR, fg=ACCENT_COLOR, troughcolor=BTN_BG,
                      activebackground=ACCENT_COLOR, highlightthickness=0, bd=0, showvalue=0)
barre_temp.pack(pady=20)
barre_temp.bind("<Button-1>", clic_barre_temps)

# 3. Zone des Boutons de Contrôle (Frame horizontale)
frame_controles = tk.Frame(lecteur, bg=BG_COLOR, pady=10)
frame_controles.pack()

# Configuration commune pour les boutons ronds/plats
btn_config = {
    'bg': BTN_BG,
    'fg': FG_COLOR,
    'activebackground': BTN_HOVER,
    'activeforeground': FG_COLOR,
    'font': FONT_ICONS,
    'bd': 0,  # Pas de bordure 3D
    'relief': 'flat',  # Aspect plat
    'width': 4,  # Largeur fixe pour des boutons carrés
    'height': 2,
    'cursor': 'hand2'  # Curseur main au survol
}

# Bouton Choisir (Dossier)
btn_choisir = tk.Button(frame_controles, text="📂", command=choisir_fichier, **btn_config)
btn_choisir.grid(row=0, column=0, padx=10)

# Bouton Jouer (Rejouer depuis le début) - Optionnel si choisir lance déjà
btn_jouer = tk.Button(frame_controles, text="⏮", command=jouer_musique, **btn_config)
btn_jouer.grid(row=0, column=1, padx=10)

# Bouton Pause/Reprendre (Central, un peu plus grand si on voulait, ici même taille)
btn_pause = tk.Button(frame_controles, text="⏸", command=basculer_pause, **btn_config)
btn_pause.grid(row=0, column=2, padx=10)

# Bouton Suivant
btn_suivant = tk.Button(frame_controles, text="⏭", command=suivante, **btn_config)
btn_suivant.grid(row=0, column=3, padx=10)

# Application des effets de survol sur les contrôles
for btn in [btn_choisir, btn_jouer, btn_pause, btn_suivant]:
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# 4. Zone de Volume (Frame horizontale en bas)
frame_volume = tk.Frame(lecteur, bg=BG_COLOR, pady=20)
frame_volume.pack(fill=tk.X, padx=30)

label_vol_min = tk.Label(frame_volume, text="🔈", font=FONT_MAIN, bg=BG_COLOR, fg=FG_COLOR)
label_vol_min.pack(side=tk.LEFT)

barre_vol = tk.Scale(frame_volume, from_=0, to=100, orient=tk.HORIZONTAL, command=volume,
                     bg=BG_COLOR, fg=FG_COLOR, troughcolor=BTN_BG,
                     activebackground=ACCENT_COLOR, highlightthickness=0, bd=0, showvalue=0)
barre_vol.set(50)
barre_vol.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

label_vol_max = tk.Label(frame_volume, text="🔊", font=FONT_MAIN, bg=BG_COLOR, fg=FG_COLOR)
label_vol_max.pack(side=tk.RIGHT)

# 5. Bouton Quitter (Tout en bas)
# Style différent pour le bouton quitter (rouge)
btn_quitter = tk.Button(lecteur, text="QUITTER", command=confirmer_quitter,
                        bg=QUIT_BG, fg=FG_COLOR,
                        activebackground="#E74C3C", activeforeground=FG_COLOR,
                        font=("Helvetica", 10, "bold"), bd=0, relief='flat', pady=8, width=20, cursor='hand2')
btn_quitter.pack(side=tk.BOTTOM, pady=(0, 20))

btn_quitter.bind("<Enter>", on_enter_quit)
btn_quitter.bind("<Leave>", on_leave_quit)

# Lancement des boucles de vérification
verifier_fin_musique()
lecteur.mainloop()
