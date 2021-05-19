# Was was macht das Programm?
Es checkt so lange in einem gewissen Intervall (Standard 2min), ob ein Impftermin verfügbar ist, bis eben einer gefunden wurde uns spielt anschließend eine Sounddatei ab.
Zusätzlich besteht die Option, eine Pushbenachrichtigung auf sein Handy zu bekommen (hierfür wird Pushsafer verwendet).

<b>Es bucht nicht automatisch einen Termin!</b>

Als Buchungseite wird [www.impfterminservice.de](https://www.impfterminservice.de/) verwendet

# Warum?

Ich bin ein ausgelernter Anwendungsentwickler und haben vor kurzem ein Duales Studium begonnen. Ich wollte mal ein Programm entwicklen, was wirklich einen Nutzen hat und promt kamen meinem Großeltern auf mich zu und haben gefragt ob ich nicht einen Termin für sie besorgen kann. Daher kam dann der gedanke zum Programm, da ich nicht 24/7 auf dieser Webseite einen Termin suchen wollte.

# Ist euch das Datum egal?

Natürlich bin ich nicht der einzige der so ein Art Programm erstellt hat. Wenn euch der Termin egal ist und ihr einfach nur geipft werden wollt, dann empfehle ich euch [vaccipy](https://github.com/iamnotturner/vaccipy)!

Ist auch deutlich Professioneller als meins hier :D

# Anwendung

Folgende Informationen werden benötigt:
- "Impf-Code" zB. "XYZW-YXZW-XYZW"
- Plz. des Impfzentrums z.B. "88045" für Friedrichshafen Messe
- Bundesland des Impfzentrums zB. "Baden-Württemberg"

## "Einfache Anwendung ohne IT Kenntnisse"

Um mein Programm benutzten zu können müsst ihr [Google Chrome](https://www.neowin.net/news/google-chrome-900443093-offline-installer/) installiert haben. Ich habe die Version 90.0.4430.93 verwendet. Dies ist unter anderem soweit wichtig, da bei einer anderen Version der Treiber unter umständen angepasst werden muss.

----------

Als erstes müsst ihr natürlich das Programm herunterladen. Dafür ladet einfach hier den Ordner *[dist](https://link)* herunter oder könnt diesen [Link](https://cloud.floskinner.ddnss.de/s/onbXdm4wXc59z7W) hier zu meiner Cloud verwenden, wo direkt nur der Inhalt von *dist* ist.

Evtl. wird das Programm von eurem Rechner als Virus gesehen... Keine Ahnung warum, ich vermute weil es kein Softwarezertifikat hat... Aber Ihr könnt den Code ja selbst inspizieren, es ist kein Virus :)

Als nächstes könnt ihr bereits schon das Programm starten. Dafür öffnet ihr einfach den Ordner und klickt auf "Check_Impftermin.exe"

Danach müsst ihr folgende Infos eingeben:
1. Impf-Code – Euren individuellen Vermittlungscode
2. PLZ: Postleizahl des Standortes von eurem Vermittlungscode z.B. 88045 für Friedrichshafen Messe
3. Bundesland: Bundesland vom Impfzentrum

Bestätigen tut ihr jeweils mit "Enter" <br>
Anschließend sollte das Fenster ungefähr so aussehen:

![cmd_start](https://wordpress.floskinner.ddnss.de/wp-content/uploads/2021/05/start.png)

Nun Läuft das Programm und ruft automatisch die Seite auf und sucht nach einem Impftermin.

## Starten mit Parameter

Möchte man noch ein paar Parameter ändern, muss man das Programm über die cmd starten. Um einen Hilfetext zu bekommen kann die Option -h mit angeben.<br>
Wichtig ist hier der Parameter **--NOTuserinteractive**

Hier ne Kurze Erklärung:
<table>
  <tr>
    <th>Konfig</th>
    <th>Beschreibung</th>
  </tr>
  <tr>
    <td>Code</td>
    <td>Vermittlungscode / "Impf-Code"</td>
  </tr>
  <tr>
    <td>PLZ</td>
    <td>Postleizahl des Impfzentrums</td>
  </tr>
  <tr>
    <td>Bundesland</td>
    <td>Bundesland des Impfzentrums</td>
  </tr>
  <tr>
    <td>Treiber</td>
    <td>Treiber für den Browser der verwendet wird</td>
  </tr>
  <tr>
    <td>Sound Pfad</td>
    <td>Pfad zur Datei, die bei einem Treffer abgespielt wird</td>
  </tr>
  <tr>
    <td>Pushsafer Code</td>
    <td>Key für die Pushsafer App / euer Account Key</td>
  </tr>
  <tr>
    <td>Warte auf Seite</td>
    <td>Wie lange auf eine Seite gewartet werden soll, bis sie vollständig geladen ist</td>
  </tr>
  <tr>
    <td>Zyklus</td>
    <td>Wie schnell ein neuer Versuch gestartet werden soll</td>
  </tr>
  <tr>
    <td>debug</td>
    <td>Speichert zusaetzlich screenshots zum debuggen"</td>
  </tr>
</table>

<br>

...Natürlich kann man es auch direkt über Python starten



# Pushsafer / Nachricht aufs Handy

[Pushsafer](https://www.pushsafer.com) wird verwendet, um Pushbenachrichtigungen an das Handy zu senden. Dafür müsst ihr euch die App “Pushsafer” installieren:
- [Google Play Store](https://play.google.com/store/apps/details?id=de.appzer.Pushsafer)
- [Apple Store](https://apps.apple.com/de/app/pushsafer/id1096581405)

Anschließend könnt ihr mithilfe des Parameters --pushsaferCode euren Pushsafer Keys (privater Schlüssel) mit übergeben und eine Nachricht mit höchster Priorität wird an alle regestrierten Geräte gesendet.

# Termin gefunden :O

Wurde ein Termin gefunden, wird ein der angegebene Ton 3 mal abgespielt (siehe *data/horn.wav*). Danach habt ihr 10min Zeit einen Termin auszuwählen und ihn verbindlich zu buchen:

![first](https://wordpress.floskinner.ddnss.de/wp-content/uploads/2021/05/Gefunden-2.png)

# Bisschen schönere Anleitung

Durch das Projekt bin ich auch dazu gekommen meine eigene Cloud und Wordpress in meinem Heimnetz aufzusetzten. Daher ist hier auch eine etwas [schönere Anleitung](https://wordpress.floskinner.ddnss.de/impftermin-automatisch-reservieren) mit Bildchen :)

# Zum Abschluss...

Bitte missbraucht mein Program nicht. Ich habe es erstellt, um selber etwas zu lernen und um andere zu helfen. Nicht um i welchen fremden ein Tool zu geben die sich damit Termine besorgen und diese auf eBay verkaufen :(