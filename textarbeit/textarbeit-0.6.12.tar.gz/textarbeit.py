"""Das Modul 'textarbeit' bietet Routinen, um reine Texte (*.txt) zu bearbeiten.

Folgende Funktionen stellt es zur Verfügung:

Text2Liste(einDatei, ausDatei) - erstellt eine Liste aller Wörter
Liste_rein(einDatei, ausDatei) - entfernt Sonderzeichen
Liste_sortiert(einDatei, ausDatei): - gibt eine sortierte Liste aus
ListeohneDuplikate(einDatei, ausDatei) - entfernt alle Duplikate

ListeNachAnzahl(einDatei, ausDatei): gibt eine Liste geordnet nach Anzahl aus
ListeWortAnzahl(einDatei, ausDatei): gibt eine alphabetische Liste mit Anzahl aus

ZahlPunktLoeschen(einDatei, ausDatei) - 123. Hallo wird Hallo

minus3Lz(einDatei, ausDatei) - macht aus 3 Leerzeichen 1
minus2Lz(einDatei, ausDatei) - macht aus 2 Leerzeichen 1
minusLzLinks(einDatei, ausDatei) - entfernt Leerzeichen links
minusLzRechts(einDatei, ausDatei) - entfernt Leerzeichen rechts


Anwendungsbeispiel:
textarbeit.minus3Lz("/home/beat/texte.txt","/home/beat/texte2.txt")

Weitere Funktionen werden nach ausgiebigen Test hier eingebunden:
- Ersetzen von veralteten Ausdrücken
- Erstellung von Listen jeder Art
"""

#**********************Listen*********************************

def Text2Liste(einDatei, ausDatei):
     """Liest einen Text (*.txt-Datei) ein und speichert ihn als Liste
     (ein Wort pro Zeile) wieder ab.
     """
     einText = open(einDatei)
     ausText = open(ausDatei, "w")
     for line in einText:
          Woerter=line.split(" ")
          for Wort in Woerter:
               if Wort != "\n": #eliminiert leere Zeile
                    ausText.write(Wort+"\n")
     ausText.close()
     einText.close()

def Liste_rein(einDatei, ausDatei):
     """liest eine Liste (*.txt-Datei) ein, entfernt alle Sonderzeichen
     der deutschen Sprache und speichert die Liste unter dem 2. Namen 
     Wort für Wort ab.
     """
     einText = open(einDatei)
     ausText = open(ausDatei, "w")
     ZeichenTuple=("»", "«", ">", "<", "*", "^", "'", '"', "“", "”", ",", ".", \
                   ";", ":", "+", "–", "−","—", "±", "-", "_", "!", "?", "=", "@", \
                   "#", "&", "%", " ", "(", ")", "[", "]", "{", "}", "›", "‹", "`", \
                   "‘", "’", "/", "|", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "\t")
     liste = []
     for Wort in einText:
          for zeichen in ZeichenTuple:
               Wort = Wort.replace(zeichen, "")
          liste.append(Wort)
     for Wort in liste:
           if Wort != "\n": #eliminiert leere Zeile
                ausText.write(Wort)
     ausText.close()
     einText.close()

def ListeNachAnzahl(einDatei, ausDatei):
     """liest eine gereinigte Liste (*.txt-Datei) ein, zählt die Anzahl 
     verschiedener Wörter und gibt eine Liste sortiert nach Häufigkeit
     in der Form Anzahl Wort aus:
     0212 da
     0122 hier
     """
     einText = open(einDatei, "r")
     ausText = open(ausDatei, "w")
     Anzahl = dict()
     liste = []
     for Wort in einText:
          Wort = Wort.replace("\n", "")
          if Wort not in Anzahl:
               Anzahl[Wort] = 1
          else:
               Anzahl[Wort] += 1
     for key in Anzahl:
          AnzahlundWort = ("{0:04d}".format(Anzahl[key])+" "+key)
          liste.append(AnzahlundWort)
     liste.sort(key=str.lower, reverse=True)
     for Wort in liste:
          ausText.write(Wort+"\n")
     einText.close()
     ausText.close()

def ListeWortAnzahl(einDatei, ausDatei):
     """liest eine gereinigte Liste (*.txt-Datei) ein, zählt die Anzahl 
     verschiedener Wörter und gibt eine Liste sortiert nach Häufigkeit
     in der Form Wort Anzahl aus:
     da 22
     hier 21
     """
     einText = open(einDatei, "r")
     ausText = open(ausDatei, "w")
     Anzahl = dict()
     liste = []
     for Wort in einText:
          Wort = Wort.replace("\n", "")
          if Wort not in Anzahl:
               Anzahl[Wort] = 1
          else:
               Anzahl[Wort] += 1
     for key in Anzahl:
          WortundAnzahl = (key+" "+"{0:04d}".format(Anzahl[key]))
          liste.append(WortundAnzahl)
     liste.sort(key=str.lower)
     for Wort in liste:
          ausText.write(Wort+"\n")
     einText.close()
     ausText.close()

def Liste_sortiert(einDatei, ausDatei):
     """ liest eine Liste (*.txt-Datei) ein, sortiert sie (lowercase) und speichert
     die sortierte Liste unter dem zweiten Namen ab.
     Es ist zu empfehlen, diese Liste zuerst durch die Funktion
     Liste_rein(einDatei, ausDatei) von Sonderzeichen zu reinigen.
     """
     einText = open(einDatei)
     ausText = open(ausDatei, "w") 
     liste = []
     for Wort in einText:
          liste.append(Wort)
     liste.sort(key=str.lower)
     for Wort in liste:
          ausText.write(Wort)
     ausText.close()
     einText.close()

def ListeohneDuplikate(einDatei, ausDatei):
     """ liest eine Liste (*.txt-Datei) ein, wandelt sie in ein Set (ungeordnete
     Unikate) und anschliessend wieder in eine Liste um. Die neue Liste wird
     unter dem angegebenen 2. Namen gespeichert.
     """
     Liste = []
     einText = open(einDatei)
     ausText = open(ausDatei, "w")
     for wort in einText:
          Liste.append(wort)
     Liste = list(set(Liste))
     Liste.sort()
     for wort in Liste:
          ausText.write(wort)
     einText.close()
     ausText.close()

def ZahlPunktLoeschen(einDatei, ausDatei):
     """ liest eine Textdatei ein und schreibt alle Wörter
     zeilenweise in die Ausgabedatei ohne die jeweils ersten Zeichen
     (Trenner ist ". ")
     123. Hallo   wird zu:   Hallo
     """
     einText = open(einDatei)
     ausText = open(ausDatei, "w")
     for line in einText:
          Wort = line.split(". ")
          ausText.write(Wort[1])
     einText.close()
     ausText.close()

#******************Leerzeichen eliminieren************************************

def minus3Lz(einDatei, ausDatei):
    """Liest eine Textdatei ein, ersetzt 3 Leerzeichen 
    durch 1 Leerzeichen.
    """
    einText = open(einDatei)
    ausText = open(ausDatei, "w")
    for line in einText:
        Woerter=line.split("   ")
        for Wort in Woerter:
            ausText.write(" "+Wort)
    ausText.close()
    einText.close()

def minus2Lz(einDatei, ausDatei):
    """Liest eine Textdatei ein, ersetzt 2 Leerzeichen 
    durch 1 Leerzeichen.
    """
    einText = open(einDatei)
    ausText = open(ausDatei, "w")
    for line in einText:
        Woerter=line.split("  ")
        for Wort in Woerter:
            ausText.write(" "+Wort)
    ausText.close()
    einText.close()    

def minusLzLinks(einDatei, ausDatei):
    """Liest eine Textdatei ein und löscht alle Leerzeichen links.
    """
    einText = open(einDatei)
    ausText = open(ausDatei, "w")
    for line in einText:
        ausText.write(line.lstrip())
    einText.close()

def minusLzRechts(einDatei, ausDatei):
    """Liest eine Textdatei ein und löscht alle Leerzeichen rechts.
    """
    einText = open(einDatei)
    ausText = open(ausDatei, "w")
    for line in einText:
        ausText.write(line.rstrip())
    einText.close()
