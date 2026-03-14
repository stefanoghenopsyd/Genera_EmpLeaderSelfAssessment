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
    "1. Un leader attraverso le sue azioni dovrebbe stabilire standard elevati di performance lavorativa per il gruppo.",
    "2. Un leader dovrebbe lavorare più duramente che può.",
    "3. Un leader con il suo modo di comportarsi deve essere un buon esempio per tutto il gruppo.",
    "4. Un leader guida il gruppo innanzitutto attraverso l’esempio che dà.",
    "5. Un leader dovrebbe lavorare tanto duramente quanto ogni membro del gruppo che guida.",
    "6. Un leader dovrebbe dare la possibilità a tutti i membri del gruppo di esprimere le proprie opinioni.",
    "7. Un leader dovrebbe incoraggiare le persone del gruppo ad esprimere idee e suggerimenti.",
    "8. Un leader dovrebbe utilizzare i suggerimenti provenienti dai membri del gruppo per prendere decisioni che riguardano il gruppo stesso.",
    "9. Un leader deve ascoltare le idee e i suggerimenti provenienti dai membri del gruppo.",
    "10. Un leader dovrebbe prendere in considerazione le idee del gruppo anche quando non è d’accordo con esse.",
    "11. Un leader dovrebbe prende decisioni che si basano unicamente sulle sue idee.",
    "12. Un leader dovrebbe incoraggiare i membri del gruppo a condividere le informazioni.",
    "13. Un leader dovrebbe proporre suggerimenti per migliorare i risultati del gruppo.",
    "14. Un leader dovrebbe incoraggiare i membri del gruppo a risolvere i problemi insieme.",
    "15. Un leader deve aiutare il gruppo a prendere consapevolezza delle aree in cui c'è bisogno di maggiore formazione.",
    "16. Un leader dovrebbe aiutare tutti i membri del gruppo.",
    "17. Un leader dovrebbe aiutare al gruppo a risolvere autonomamente i problemi.",
    "18. Un leader dovrebbe prestare attenzione agli sforzi del gruppo.",
    "19. Quando il gruppo lavora bene, un leader deve riconoscerlo apertamente.",
    "20. Un leader dovrebbe sostenere gli sforzi del gruppo.",
    "21. Un leader dovrebbe aiutare il gruppo a focalizzarsi sui propri obiettivi.",
    "22. Un leader dovrebbe aiutare lo sviluppo di buone relazioni tra i membri del gruppo.",
    "23. Un leader deve spiegare le decisioni prese dall’azienda.",
    "24. Un leader deve spiegare gli obiettivi dell’azienda.",
    "25. Un leader deve chiarire la funzione del gruppo all’interno dell’azienda.",
    "26. Un leader deve chiarire al gruppo gli obiettivi delle politiche dell’azienda.",
    "27. Un leader deve spiegare al gruppo quali sono le regole e le aspettative sul lavoro.",
    "28. Un leader deve spiegare al gruppo le sue decisioni ed azioni.",
    "29. Un leader dovrebbe mostrarsi interessato ai problemi personali dei membri del gruppo.",
    "30. Un leader dovrebbe mostrare attenzione verso il benessere dei membri del gruppo.",
    "31. Un leader dovrebbe trattare i membri del gruppo senza fare differenze.",
    "32. Un leader dovrebbe trovare del tempo per discutere con calma i problemi dei singoli membri del gruppo.",
    "33. Un leader dovrebbe mostrare interesse per i successi dei membri del gruppo.",
    "34. Un leader dovrebbe sentirsi ed essere sentito vicino al gruppo.",
    "35. Un leader dovrebbe dimostrare di tenere molto ai membri del gruppo.",
    "36. Un leader dovrebbe essere al corrente del lavoro che il gruppo sta svolgendo.",
    "37. Un leader deve fornire risposte oneste e obiettive ai membri del gruppo.",
    "38. Un leader deve trovare il tempo per conversare con i membri del gruppo.",
    "39. Se pensi al tuo superiore diretto, quanto il suo stile leadership corrisponde a quanto indicato finora?",
    "40. Se pensi alla tua leadership, quanto ti pare di mettere in pratica quanto indicato finora?"
]

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
    dati = list(dati)
    dati.append(dati[0])
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles.append(angles[0])

    if media_complessiva < 2.5:
        colore_fill = 'red'
    elif 2.5 <= media_complessiva <= 3.5:
        colore_fill = 'yellow'
    else:
        colore_fill = 'green'

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    ax.fill(angles, dati, color=colore_fill, alpha=0.45)
    ax.plot(angles, dati, color='#004C99', linewidth=2)
    
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.set_ylim(0, 5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    
    return fig

def salva_su_drive(dati_riga):
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("Risultati_Empowering_Leadership").sheet1
        sheet.append_row(dati_riga)
        return True
    except Exception as e:
        print(f"Errore di salvataggio: {e}")
        return False

# --- MAIN APP ---
def main():
    try:
        st.image("GENERA Logo Colore.png", use_container_width=True)
    except:
        st.warning("Immagine logo non trovata. Assicurati che 'GENERA Logo Colore.png' sia nella repository.")
    
    st.markdown("<h1 style='text-align: center;'>Autovalutazione: Empowering Leadership</h1>", unsafe_allow_html=True)

    # SEZIONE 1: Introduzione
    st.header("Introduzione")
    st.markdown("""
    Il modello di **Empowering Leadership** sviluppato da Arnold et al. (2000) è uno dei pilastri della moderna psicologia del lavoro e delle organizzazioni. Sposta il focus dall’esercizio della leadership dal "capo che decide" al "coach che abilita".
    La leadership quindi non riguarda tanto il controllo, quanto il trasferimento di potere e autonomia ai collaboratori per migliorare la loro autoefficacia e performance. Arnold e i suoi colleghi hanno identificato cinque categorie specifiche:
    
    1. **Leading by Example (Dare l'esempio):** Il leader mostra coerenza tra parole e azioni. Lavora duramente e dimostra impegno.
    2. **Participative Decision Making (Processo decisionale partecipativo):** Il leader incoraggia i collaboratori a esprimere idee e suggerimenti.
    3. **Coaching (Formazione e guida):** Il leader aiuta i membri del team a sviluppare le proprie competenze.
    4. **Informing (Informare):** La trasparenza è fondamentale. Il leader condivide informazioni rilevanti.
    5. **Showing Concern (Mostrare interesse):** La dimensione umana. Il leader si prende cura del benessere dei collaboratori.
    
    L'obiettivo finale è generare **empowerment psicologico**: Significato, Competenza, Autodeterminazione, Impatto.
    
    **Obiettivo del test:** valutare la propria propensione verso uno stile di leadership empowering.
    """)
    
    st.markdown("<p style='font-size: 0.8em; background-color: #FFFF99; padding: 5px; border-radius: 5px;'>Proseguendo nella compilazione acconsento a che i dati raccolti potranno essere utilizzati in forma aggregata esclusivamente per finalità statistiche.</p>", unsafe_allow_html=True)

    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    if not st.session_state.submitted:
        with st.form("questionario_form"):
            # SEZIONE 2: Informazioni Socio-anagrafiche
            st.header("Informazioni socio-anagrafiche")
            nome = st.text_input("Nome o Nickname")
            
            col1, col2 = st.columns(2)
            with col1:
                genere = st.selectbox("Genere", ["Maschile", "Femminile", "Non binario", "Non risponde"])
            with col2:
                eta = st.selectbox("Età", ["Fino a 20 anni", "21-30 anni", "31-40 anni", "41-50 anni", "51-60 anni", "61-70 anni", "Più di 70 anni"])
                
            col3, col4 = st.columns(2)
            with col3:
                studio = st.selectbox("Titolo di studio", ["Licenza media", "Qualifica professionale", "Diploma di maturità", "Laurea triennale", "Laurea magistrale (o ciclo unico)", "Titolo post lauream"])
            with col4:
                job = st.selectbox("Job", ["Imprenditore", "Top manager", "Middle manager", "Impiegato", "Operaio", "Tirocinante", "Libero professionista"])

            # SEZIONE 3: Test
            st.header("Test")
            st.markdown("Sposta il cursore sulla linea per indicare il tuo grado di accordo o la frequenza (da 1 a 5). Il cursore parte da un valore neutro (3).")
            
            risposte = {}
            for i, domanda in enumerate(DOMANDE):
                num_item = i + 1
                st.markdown(f"<div style='margin-top: 20px;'><strong>{domanda}</strong></div>", unsafe_allow_html=True)
                
                # Differenziazione delle etichette (1-38 vs 39-40)
                if num_item <= 38:
                    label_sx = "1 = Per niente d'accordo"
                    label_dx = "5 = Del tutto d'accordo"
                else:
                    label_sx = "1 = Mai"
                    label_dx = "5 = Sempre"
                
                # Etichette visive personalizzate posizionate sopra lo slider
                st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; font-size: 0.85em; color: #555; margin-bottom: -15px;'>
                        <span>{label_sx}</span>
                        <span>{label_dx}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Slider vero e proprio
                scelta = st.slider(
                    f"nascosto_{num_item}", 
                    min_value=1, 
                    max_value=5, 
                    value=3, 
                    step=1, 
                    key=f"q_{num_item}", 
                    label_visibility="collapsed"
                )
                risposte[num_item] = scelta

            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("Invia e Scopri i Risultati")

        if submit_button:
            if not nome:
                st.error("Per favore, inserisci un nome o nickname per procedere.")
            else:
                st.session_state.submitted = True
                st.session_state.dati_utente = [str(uuid.uuid4()), genere, eta, studio, job]
                st.session_state.risposte = risposte
                st.rerun()

    # SEZIONE 4: Feedback
    if st.session_state.submitted:
        st.header("I tuoi Risultati")
        
        risp = st.session_state.risposte
        
        # Calcolo Punteggi
        valore_11 = 6 - risp[11]
        
        punteggi_dim = {}
        for dim, items in DIMENSIONI.items():
            totale_dim = 0
            for item in items:
                if item == 11:
                    totale_dim += valore_11
                else:
                    totale_dim += risp[item]
            punteggi_dim[dim] = totale_dim / len(items)

        valori_38 = [risp[i] for i in range(1, 39) if i != 11] + [valore_11]
        media_complessiva = sum(valori_38) / 38
        
        punteggio_39 = risp[39]
        punteggio_40 = risp[40]

        dim_forza = max(punteggi_dim, key=punteggi_dim.get)
        dim_sviluppo = min(punteggi_dim, key=punteggi_dim.get)

        riga_db = st.session_state.dati_utente + [risp[i] for i in range(1, 41)]
        salvato = salva_su_drive(riga_db)
        if not salvato:
            st.warning("I risultati sono stati generati, ma si è verificato un problema nel salvataggio sul server. Puoi comunque consultare il tuo profilo qui sotto.")

        st.subheader("Profilo Grafico")
        labels = list(punteggi_dim.keys())
        values = list(punteggi_dim.values())
        
        fig = crea_radar_chart(values, labels, media_complessiva)
        st.pyplot(fig)

        st.subheader("Feedback Narrativo")
        st.write(f"**Punteggio Medio Complessivo:** {media_complessiva:.2f}/5 (Livello: {interpreta_punteggio(media_complessiva)})")
        
        st.markdown("### Dettaglio Dimensioni")
        for dim, score in punteggi_dim.items():
            st.write(f"- **{dim}:** {score:.2f} (Livello: {interpreta_punteggio(score)})")
            
        st.markdown("### Percezione della Leadership")
        st.write(f"- **Leadership subita (superiore diretto):** {punteggio_39} (Livello: {interpreta_punteggio(punteggio_39)})")
        st.write(f"- **Leadership agita (autopercezione):** {punteggio_40} (Livello: {interpreta_punteggio(punteggio_40)})")
        
        st.markdown("### Suggerimenti d'azione")
        st.success(f"🌟 **Punto di Forza:** La tua area più forte è **{dim_forza}** ({punteggi_dim[dim_forza]:.2f}). Continua a far leva su questo comportamento, rappresenta un pilastro del tuo stile relazionale sul lavoro.")
        st.warning(f"📈 **Area di Sviluppo:** L'area con margine di miglioramento è **{dim_sviluppo}** ({punteggi_dim[dim_sviluppo]:.2f}). Prova a concentrarti su azioni quotidiane per potenziare questa dimensione, come descritto nell'introduzione del modello.")

        if st.button("Compila un nuovo test"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray; font-size: 0.9em;'>Powered by GÉNERA</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
