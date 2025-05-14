[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Vd0qjMAQ)

# 2.1 Whistle Input
## Setup
- Navigiere in den Ordner `whistle_input`
- (Erstelle und) starte dann Virtual Environment mittels `venv\scripts\activate`
- Installiere ggf. Abhängigkeiten mit `pip install -r requirements.txt`
- Starte Anwendung mit `python whistle-input.py`
- Wähle Audio Eingabegerät per Konsoleneingabe
- Pfeif!

## Beschreibung
Durch pfeifen kann man sowohl die Auswahl im Raster des Testprogramms steuern, als auch eine beliebige Anwendung außerhalb. "Nach oben Pfeifen" (Frequenz erhöht sich während des Pfeifens) betätigt die Pfeiltaste nach oben, "Nach unten Pfeifen" (Frequenz verringert sich während des Pfeifens) die Pfeiltaste nach unten.

# 2.2 Karaoke Game
## Setup
- Navigiere in den Ordner `karaoke_game`
- (Erstelle und) starte dann Virtual Environment mittels `venv\scripts\activate`
- Installiere ggf. Abhängigkeiten mit `pip install -r requirements.txt`
- Starte Spiel mit `python karaoke.py`
- Wähle Audio Eingabegerät per Konsoleneingabe
- Gib Pfad zu gewünschter MIDI-Datei an
- Sing! (oder so)

## Im Spiel
Du bist der blaue Block am linken Bildschirmrand. Seine y-Position entspricht deiner gesungenen Note. Von rechts kommen Notenblöcke auf dich zu! Singe möglichst durchweg die korrekten Töne und gleite mit deinem Spieler über die Noten. Je länger du insgesamt Töne oder Pausen triffst, desto höher ist dein Score (in %).

## Geplante, nette Dinge, für die die Zeit nicht gereicht hat...
- Logarithmische (korrekte) Darstellung der Frequenzskala (y)
- Visuelles Feedback darüber, ob man den Ton getroffen hat (z.B. Notenfarbe ändert sich)
- Toleranz auch beim Timing (sodass man nicht unmenschlich perfekt sein muss, schlicht durch Verfrühung der Notenstarts und Verzögerung des Notenstopps realisierbar)
- Punkte auch für fast getroffene Töne (sowohl bzgl. Frequenz als auch Timing)
- Restart-Option

# Schon wieder ein kleiner Disclaimer...
Mit den technischen Problemen von letzter Woche habe ich nach wie vor zu kämpfen. Erschwerend kamen Probleme mit ausgerechnet dem Mikro und Midi hinzu. Mein Laptop weigert sich von Python aus Midis abzuspielen. Um meinen Code überhaupt irgendwie halbwegs testen zu können, habe ich mich mehrfach mit Richard zusammengesetzt. Wir haben also lange Sessions gemeinsam an diesen Abgaben gearbeitet, weshalb sich diese sicherlich ziemlich ähneln. Wir hoffen, das ist in diesem Rahmen kein zu großes Problem. 
Daraus resultiert auch, dass ich die finale Version des Karaoke nicht wirklich testen konnte (ich höre ja auf dem einen PC kein Midi, der andere steikt bei Pyglet). Der Audio-Input wirkt mir auch sehr wirr und ich kann mit meiner Hardware einfach nicht beurteilen, ob es am Code oder an meinem Mikro. Der Whistle-Input hingegen läuft auch bei mir mit sehr großer Zuverlässigkeit.
