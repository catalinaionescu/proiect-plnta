Descrierea proiectului
Prezentul repository contine implementarea unei aplicatii software in limbajul Python, destinata analizei automate a textului medical. Proiectul propune un sistem de "triaj digital" primar, care permite preluarea simptomelor descrise de pacienti in limbaj natural (prin voce sau text) si incadrarea acestora intr-o categorie medicala, alaturi de calcularea unui scor de severitate.
Sistemul nu este conceput pentru a inlocui consultul medical de specialitate, ci are rolul de a facilita prioritizarea cazurilor in situatii de supraaglomerare, directionand corect pacientii in functie de simptomatologie.

Metodologie si justificare tehnica
Spre deosebire de modelele complexe de invatare automata (Deep Learning) care functioneaza pe principiul "cutiei negre", acest proiect utilizeaza o abordare de tip "Rule-Based", bazata pe un Lexicon definit manual.
Aceasta alegere tehnica asigura un nivel ridicat de transparenta si explicabilitate (metoda "white box"). Astfel, in orice moment, decizia sistemului poate fi justificata prin identificarea exacta a cuvintelor care au declansat un anumit diagnostic preliminar, aspect considerat critic in domeniul medical.

Functionalitati principale
Achizitie multimodala: Sistemul proceseaza intrari atat in format text (de la tastatura), cat si vocal (preluare live de la microfon sau din fisiere audio inregistrate).
Procesare NLP si preprocesare: Textul brut este curatat prin tehnici de tokenizare, eliminare a punctuatiei si case folding, in vederea analizei.
Scoring de severitate: Termenii identificati in discursul pacientului sunt mapati pe o scara de severitate de la 1 (usor) la 3 (urgenta medicala). Sistemul calculeaza rezultatul final folosind principiul "worst-case scenario" - prezenta unui singur simptom critic ridica severitatea intregului caz la nivelul maxim.
Filtrare a continutului: Aplicatia include un modul de monitorizare a limbajului, care opreste analiza daca detecteaza cuvinte licentioase sau inadecvate.
Feedback mixt: Rezultatele evaluarii sunt comunicate atat vizual pe ecran, cat si auditiv, prin generarea unui raspuns vocal sintetizat.

Arhitectura si tehnologii utilizate
Aplicatia este structurata dupa o arhitectura de tip "Pipeline", datele trecand unidirectional prin patru module principale: Modulul de Input, Modulul de Preprocesare, Motorul de Analiza (Core Engine) si Modulul de Output.

Limbaj de programare: Python

SpeechRecognition: Pentru componenta de Speech-to-Text (integrat cu Google Web Speech API).

pyttsx3: Pentru componenta de sinteza vocala offline (Text-to-Speech).

Structura de date: Lexiconul este implementat sub forma de Hash Map (dictionar Python) pentru a asigura o complexitate de cautare minima si executie rapida pe procesoare standard.

Limitari si dezvoltari viitoare
In stadiul curent, proiectul demonstreaza functionalitatea conceptului pe un lexicon de baza. Pentru a putea fi implementat intr-un mediu clinic real, se propun urmatoarele directii de cercetare si dezvoltare:

Rezolvarea lipsei de context gramatical (in special tratarea negatiilor, astfel incat sistemul sa faca diferenta intre "ma doare" si "nu ma doare").

Integrarea cu ontologii medicale standardizate (precum SNOMED-CT) pentru a mari exponential numarul de simptome recunoscute.

Implementarea unui modul de analiza a sentimentelor direct pe semnalul audio, pentru a detecta nivelul de stres sau panica din vocea pacientului.
