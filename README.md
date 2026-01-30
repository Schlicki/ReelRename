# ReelRename

<img src="ReelRename%20Logo%20.png" width="60" align="center"> ReelRename

ReelRename ist ein benutzerfreundliches Tool für Windows, um deine Film- und Seriensammlung automatisch zu organisieren. Es nutzt die Datenbank von TMDB, um korrekte Titel, Episodennummern und Veröffentlichungsjahre zu finden und deine Dateien sauber umzubenennen.

✨ Funktionen

🎬 Filme & 📺 Serien: Unterstützt beide Medienarten mit spezifischen Suchalgorithmen.

🔍 Automatische Erkennung: Analysiert Dateinamen (S01E01, 1x01, etc.) und findet die passenden Metadaten.

👀 Vorschau-Modus: Sieh dir genau an, wie die Dateien heißen werden („Vorher -> Nachher“), bevor du Änderungen vornimmst.

🎨 Artwork Downloader: Lade automatisch Poster, Fanart, Logos und Banner in hoher Qualität herunter.

🧹 Cleanup-Tools:

Löscht auf Wunsch lästige "Sample"-Dateien.

Entfernt Web-Links (.url, .html) aus den Ordnern.

📂 Ordner-Management: Kann auch den übergeordneten Ordner passend zur Serie/zum Film umbenennen.

🌍 Mehrsprachig: Verfügbar in Deutsch 🇩🇪, Englisch 🇬🇧, Spanisch 🇪🇸 und Französisch 🇫🇷.

⚙️ Anpassbar: Definiere dein eigenes Namensformat (z.B. {show} - S{s}E{e} - {title}).

🚀 Download & Installation

Du musst kein Python installieren! Lade einfach die fertige Anwendung herunter:

Klicke rechts auf Releases (oder oben auf den Reiter).

Lade die aktuelle ReelRename.exe herunter.

Verschiebe die Datei in einen Ordner deiner Wahl und starte sie per Doppelklick.

⚠️ Hinweis beim ersten Start:
Da ich als privater Entwickler keine teuren Zertifikate kaufe, wird Windows Defender (oder dein Antivirus) eventuell warnen ("Der Computer wurde durch Windows geschützt").

Klicke auf "Weitere Informationen".

Klicke auf "Trotzdem ausführen".

Das Programm ist sicher und open-source (du kannst den Code hier im Repository prüfen).

🛠️ Nutzung

API Key: Beim allerersten Start wirst du nach einem TMDB API Key gefragt. Dieser ist kostenlos. Ein Link, um ihn zu erstellen, ist in der App enthalten.

Ordner wählen: Wähle den Ordner aus, in dem deine Videodateien liegen.

Suchen: Gib den Namen der Serie oder des Films ein und klicke auf Suchen.

Auswählen: Wähle das korrekte Ergebnis aus der Liste (inkl. Poster-Vorschau).

Vorschau & Start: Überprüfe die geplante Umbenennung in der Liste und klicke auf "UMBENENNEN STARTEN".

☕ Unterstützung

Gefällt dir ReelRename? Hilft es dir, deine Sammlung sauber zu halten?
Da ich das Tool in meiner Freizeit entwickle, würde ich mich sehr über einen Kaffee freuen!

<a href="https://coindrop.to/reelrename">
<img src="https://www.google.com/search?q=https://coindrop.to/embed-btn.png" alt="Support me on CoinDrop" style="border-radius: 8px; height: 50px;">
</a>

Hier klicken um zu spenden

💻 Für Entwickler (Python Source)

Falls du den Quellcode nutzen oder weiterentwickeln möchtest, kannst du das Projekt auch manuell ausführen.

Voraussetzung

Python 3.x installiert

Bibliotheken installieren: pip install pillow

Starten

git clone [https://github.com/DEIN_USERNAME/ReelRename.git](https://github.com/DEIN_USERNAME/ReelRename.git)
cd ReelRename
python cinematch.py


Eigene .exe bauen

pip install pyinstaller
pyinstaller --onefile --noconsole --name "ReelRename" --icon="ReelRename.ico" cinematch.py


📝 Lizenz

Dieses Projekt ist unter der MIT Lizenz veröffentlicht.

Developed by Schlicki
