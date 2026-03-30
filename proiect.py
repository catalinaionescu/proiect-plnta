import speech_recognition as sr
import pyttsx3
import os
import time

# ==========================================
# partea de date (lexiconul)
# dictionar cu termenii medicali, categoria si scorul lor
# ==========================================
LEXICON = {
    # --- aparat urinar ---
    "urina":      {"cat": "urinar", "scor": 1},
    "usturime":   {"cat": "urinar", "scor": 2},
    "rinichi":    {"cat": "urinar", "scor": 2},
    "vezica":     {"cat": "urinar", "scor": 1},
    "sange":      {"cat": "urinar", "scor": 3},  # scor 3 inseamna grav

    # --- aparat respirator ---
    "tuse":       {"cat": "respirator", "scor": 1},
    "aer":        {"cat": "respirator", "scor": 2},
    "sufoc":      {"cat": "respirator", "scor": 3}, # urgenta maxima
    "lesin":      {"cat": "respirator", "scor": 3},
    "respir":     {"cat": "respirator", "scor": 2},
    "piept":      {"cat": "respirator", "scor": 2},
    "plamani":    {"cat": "respirator", "scor": 2},

    # --- aparat digestiv ---
    "stomac":     {"cat": "digestiv", "scor": 1},
    "greata":     {"cat": "digestiv", "scor": 1},
    "varsaturi":  {"cat": "digestiv", "scor": 2},
    "burta":      {"cat": "digestiv", "scor": 1},
    "ficat":      {"cat": "digestiv", "scor": 2},

    # --- filtru limbaj (injuraturi) ---
    "prost":      {"cat": "limbaj_inadecvat", "scor": -1},
    "idiot":      {"cat": "limbaj_inadecvat", "scor": -1},
    "bataie":     {"cat": "limbaj_inadecvat", "scor": -1},
    "multumesc":  {"cat": "emotie_pozitiva", "scor": 0},
    "frica":      {"cat": "emotie_negativa", "scor": 0},

    # --- cuvinte care cresc gravitatea ---
    # astea maresc scorul indiferent de boala
    "tare":       {"cat": "indicator_de_severitate", "scor": 2},
    "insuportabil":{"cat": "indicator_de_severitate", "scor": 3},
    "urgent":     {"cat": "indicator_de_severitate", "scor": 3}
}

# initializare motor voce pentru raspuns
engine = pyttsx3.init()
engine.setProperty('rate', 150) # setare viteza vorbire mai mica sa se inteleaga

def speak_and_print(text):
    """functie care afiseaza textul si il zice vocal"""
    print(f"\n[SISTEM]: {text}")
    engine.say(text)
    engine.runAndWait()

# ==========================================
# pasul 1: preluarea datelor (input)
# meniu pentru alegerea modului de introducere date
# ==========================================
def get_input():
    print("\n--- MENIU DATE INTRARE ---")
    print("1. Microfon")
    print("2. Tastatura")
    print("3. Fisier audio")
    opt = input("Alegeti optiunea (1/2/3): ")

    recognizer = sr.Recognizer() # obiectul care asculta
    text_colectat = ""

    if opt == "1":
        # activare microfon
        with sr.Microphone() as source:
            print("[MICROFON]: Calibrez zgomotul de fundal... (Liniste 1 secunda)")
            # calibrare zgomot fundal
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # setare pauza 2 secunde ca sa nu se opreasca cand respir
            recognizer.pause_threshold = 2.0 
            
            print("[MICROFON]: Ascult... (Vorbiti acum, aveti timp!)")
            
            try:
                # asculta maxim 15 secunde
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                
                print("Procesez vocea...")
                # trimitere audio la google pentru text
                text_colectat = recognizer.recognize_google(audio, language="ro-RO")
            except sr.WaitTimeoutError:
                print("Nu s-a detectat voce (timeout).")
                return None
            except Exception as e:
                print("Eroare microfon sau conexiune internet:", e)
                return None
    
    elif opt == "2":
        text_colectat = input("[TASTATURA]: Introduceti textul: ")

    elif opt == "3":
        # citire din fisier wav
        cale_fisier = input("Introduceti numele fisierului (ex: test.wav): ")
        if os.path.exists(cale_fisier):
            with sr.AudioFile(cale_fisier) as source:
                print("Procesez fisierul audio...")
                audio = recognizer.record(source)
                try:
                    text_colectat = recognizer.recognize_google(audio, language="ro-RO")
                except:
                    print("Nu am putut transcrie fisierul.")
                    return None
        else:
            print("Fisierul nu exista!")
            return None
    else:
        return None

    print(f"--> INPUT COLECTAT: {text_colectat}")
    return text_colectat

# ==========================================
# pasul 2: curatarea textului (preprocesare)
# ==========================================
def preprocess_text(text):
    """
    pregatire text pentru analiza
    eliminare diacritice si punctuatie
    """
    text = text.lower() # transformare in litere mici
    
    # 1. inlocuire diacritice cu litere normale ca sa le gaseasca in dictionar
    diacritice = {
        "ă": "a", "â": "a", "î": "i", "ș": "s", "ț": "t"
    }
    for k, v in diacritice.items():
        text = text.replace(k, v)

    # 2. eliminare semne de punctuatie
    semne = [".", ",", "!", "?", ";"]
    for semn in semne:
        text = text.replace(semn, "")
        
    words = text.split() # impartire propozitie in cuvinte
    return words

# ==========================================
# pasul 3 & 4: cautare si calcul scor
# ==========================================
def analyze_lexicon(words):
    # dictionar pentru numararea scorurilor pe categorii
    scoruri_categorii = {
        "urinar": 0,
        "respirator": 0,
        "digestiv": 0,
        "limbaj_inadecvat": 0
    }
    max_severitate = 1 # nivelul de baza
    termeni_gasiti = []

    # parcurgere fiecare cuvant din input
    for word in words:
        # verificare daca cuvantul incepe cu termenul din dictionar
        # folosim startswith ca sa mearga si pentru plurale (rinichii)
        match = None
        for term, data in LEXICON.items():
            if word.startswith(term): 
                match = (term, data)
                break
        
        # daca s-a gasit cuvantul
        if match:
            term, data = match
            cat = data['cat']
            scor = data['scor']
            termeni_gasiti.append(f"{term}({cat})")

            # 1. adaugare punct la categoria gasita
            if cat in scoruri_categorii:
                scoruri_categorii[cat] += 1 
            
            # 2. actualizare severitate maxima daca e cazul
            if scor > 0 and scor > max_severitate:
                max_severitate = scor
            
            # 3. numarare cuvinte urate
            if cat == "limbaj_inadecvat":
                scoruri_categorii["limbaj_inadecvat"] += 1

    return scoruri_categorii, max_severitate, termeni_gasiti

# ==========================================
# pasul 5: decizia finala
# ==========================================
def interpret_result(scoruri, severitate, termeni):
    # verificare prioritara pentru limbaj urat
    if scoruri["limbaj_inadecvat"] > 0:
        return "Detectez un limbaj nepotrivit. Va rugam sa mentineti un ton respectuos."

    # calculare categoria cu punctaj maxim
    del scoruri["limbaj_inadecvat"] # scoatere filtru din calcul
    categorie_dominanta = max(scoruri, key=scoruri.get)
    valoare_max = scoruri[categorie_dominanta]

    # daca nu s-au gasit simptome
    if valoare_max == 0:
        return "Nu am detectat simptome medicale cunoscute in baza de date."

    # construire mesaj final
    mesaj = f"Pe baza termenilor identificati ({', '.join(termeni)}), "
    mesaj += f"detectez ca este vorba de o afectiune a aparatului {categorie_dominanta.upper()}. "

    # adaugare sfat in functie de severitate
    if severitate == 3:
        mesaj += "Simptomele indica o urgenta (Severitate 3). Va recomandam sa sunati la 112."
    elif severitate == 2:
        mesaj += "Simptomele par moderate (Severitate 2). Programati o consultatie."
    else:
        mesaj += "Simptomele par usoare (Severitate 1)."

    return mesaj

# --- bucla principala ---
# rulare continua pana la oprire
if __name__ == "__main__":
    speak_and_print("Sistem de analiza medicala.")
    
    while True:
        # pasul 1: ascultare
        text_input = get_input()
        
        if text_input:
            speak_and_print(f"Am receptionat: {text_input}")
            
            # pasul 2: curatare
            cuvinte = preprocess_text(text_input)
            
            # pasul 3 & 4: analiza
            scoruri, severitate, termeni = analyze_lexicon(cuvinte)
            
            # pasul 5: verdict
            rezultat_final = interpret_result(scoruri, severitate, termeni)
            
            # afisare si vocalizare rezultat
            speak_and_print(rezultat_final)
        else:
            print("Nu s-au primit date valide.")
            
        cont = input("\nContinuam? (da/nu): ")
        if cont.lower() != 'da':
            break