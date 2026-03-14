import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import uuid

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Self-Assessment: Empowering Leadership", layout="centered")

# --- COSTANTI E DATI ---
DIMENSIONI = {
    "Guida con l'esempio": list(range(1, 6)),
    "Decisione partecipata": list(range(6, 12)), # L'item 11 sarà rovesciato
    "Team Coaching": list(range(12, 23)),
    "Informazione": list(range(23, 29)),
    "Coinvolgimento": list(range(29, 39))
}

DOMANDE = [
    "1. Il leader attraverso le sue azioni deve stabilire standard elevati di performance lavorativa per il gruppo.",
    "2. Il leader deve lavorare più duramente che può.",
    "3. Il leader con il suo modo di comportarsi deve essere un buon esempio per tutto il gruppo.",
    "4. Il leader guida il gruppo attraverso l’esempio che dà.",
    "5. Il leader deve lavorare tanto duramente quanto ogni membro del gruppo che guida.",
    "6. Il leader deve dare la possibilità a tutti i membri del gruppo di esprimere le proprie opinioni.",
    "7. Il leader deve incoraggiare le persone del gruppo ad esprimere idee e suggerimenti.",
    "8. Il leader deve utilizza i suggerimenti provenienti dai membri del gruppo per prendere decisioni che riguardano il gruppo stesso.",
    "9. Il leader deve ascoltare le idee e i suggerimenti provenienti dai membri del gruppo.",
    "10. Il leader deve prendere in considerazione le idee del gruppo anche quando non è d’accordo con esse.",
    "11. Il leader deve prende decisioni che si basano unicamente sulle sue idee (R).",
    "12. Il leader incoraggia i membri del gruppo a condividere le informazioni.",
    "13. Il leader propone suggerimenti per migliorare i risultati del gruppo.",
    "14. Il leader deve incoraggiare i membri del gruppo a risolvere insieme i problemi.",
    "15. Il leader deve aiutare il gruppo a prendere consapevolezza delle aree in cui ci sarebbe bisogno di maggiore formazione.",
    "16. Il leader deve aiutare tutti i membri del gruppo.",
    "17. Il leader deve insegnare al gruppo a risolvere i problemi in modo autonomo.",
    "18. Il leader deve prestare attenzione agli sforzi del gruppo.",
    "19. Quando il gruppo lavora bene, il leader lo deve riconoscere apertamente.",
    "20. Il leader deve sostenere gli sforzi del gruppo.",
    "21. Il leader deve aiutare il gruppo a focalizzarsi sui propri obiettivi.",
    "22. Il leader deve aiutare lo sviluppo di buone relazioni tra i membri del gruppo.",
    "23. Il leader deve spiegare le decisioni prese dall’azienda.",
    "24. Il leader deve spiegare gli obiettivi dell’azienda.",
    "25. Il leader deve chiarire la funzione del gruppo all’interno dell’azienda.",
    "26. Il leader deve chiarire al gruppo gli obiettivi delle politiche dell’azienda.",
    "27. Il leader deve spiegare al gruppo quali sono le regole e le aspettative sul lavoro.",
    "28. Il leader deve spiegare al gruppo le sue decisioni ed azioni.",
    "29. Il leader si interessa ai problemi personali dei membri del gruppo.",
    "30. Il leader mostra attenzione per il benessere dei membri del gruppo.",
    "31. Il leader deve trattare i membri del gruppo senza fare differenze.",
    "32. Il leader deve dedicare del tempo per discutere con calma i problemi dei singoli membri del gruppo.",
    "33. Il leader deve mostrare interesse per i successi dei membri del gruppo.",
    "34. Il leader deve essere vicino al gruppo.",
    "35. Il leader deve tenere molto ai membri del gruppo.",
    "36. Il leader deve essere al corrente di ogni lavoro che il gruppo sta svolgendo.",
    "37. Il leader fornisce risposte oneste e obiettive ai membri del gruppo.",
    "38. Il leader deve trovare il tempo per conversare con i membri del gruppo.",
    "39. Se pensi al tuo superiore diretto, quanto la sua leadership corrisponde al modello?",
    "40. Se pensi alla tua leadership, quanto ti pare di mettere in pratica le indicazioni del modello?"
]

OPZIONI = {"Per niente d'accordo": 1, "Poco d'accordo": 2, "Abbastanza d'accordo": 3, "Molto d'accordo": 4, "Del tutto d'accordo": 5}

# --- FUNZIONI ---
def interpreta_punteggio(punteggio):
    if punteggio < 2: 
        return "Basso"
    elif 2 <= punteggio < 3: 
        return "Medio-basso"
    elif 3 <= punteggio <= 4: 
        return "Medio-alto"
    else: 
        return "Alto"

def crea_radar_chart(dati, labels, media_complessiva):
    # Chiude il cerchio del radar per la corretta visualizzazione
    dati = list(dati)
    dati.append(dati[0])
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles.append(angles[0])

    # Determina il colore di riempimento in base al punteggio medio
    if media_complessiva < 2.5:
        colore_fill = 'red'
    elif 2.5 <= media_complessiva <= 3.5:
        colore_fill = 'yellow'
    else:
        colore_fill = 'green'

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # Riempimento interno con colore dinamico
    ax.fill(angles, dati, color=colore_fill, alpha=0.45)
    
    # Linea esterna fissa sul blu scuro per mantenere il bordo pulito (coerente col brand)
    ax.plot(angles, dati, color='#004C99', linewidth=2)
    
    ax.set_yticklabels(['1', '2', '3', '4', '5
