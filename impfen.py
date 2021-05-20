"""Checken ob ein Impftermin verfuegbar ist
"""
import sys
import time
import logging
import argparse
import textwrap
import pushsafer

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from urllib3.connectionpool import log as urllibLogger
from playsound import playsound


class StuckedException(Exception):
    """
    Eigene Exception falls, es nicht weiter kommt
    """
    pass


def send_push_nachricht(message: str, pushsafer_code: str, title: str = "Termin Verfuegbar!"):
    """Sendet mithilfe von Pushsafer eine Nachricht

    Args:
        message (str): Nachricht die in der App angezeigt werden soll
        pushsafer_code (str): Key fuer das Profil
        title (str, optional): Titel der Nachricht. Defaults to "Termin Verfuegbar!".
    """

    # all
    device = "a"
    # Alarm
    icon = 2
    # Buzzer
    sound = 8
    # 3mal
    vibration = 3
    # nicht automatisch loeschen
    ttl = 0
    # Hoechste
    priority = 2
    # nach 60 erneut senden bis gesehen oder expire in sec
    retry = 60
    # stoppen erneutes zustellen in sec
    expire = 60
    # nicht antworten koennen
    answer = 0

    url = ""
    url_title = ""
    image1 = ""
    image2 = ""
    image3 = ""

    pushsafer.init(pushsafer_code)
    pushsafer.Client().send_message(message, title, device, icon, sound, vibration, url, url_title, ttl, priority, retry, expire, answer, image1, image2, image3)


def init_argument_parser() -> argparse.ArgumentParser:
    """Erstellen des Parsers mit allen Argumenten

    Returns:
        argparse.ArgumentParser: Fertig eingestellter Parser
    """

    parser = argparse.ArgumentParser(description="Mithilfe von Chrome automatisch nach Termine suchen",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent("""\
                                            Ein normaler Aufruf kann zB folgendermasen sein:
                                            - .\\Check_Impftermin.exe --NOTuserinteractive -c "XXXX-XXXX-XXXX" -p "88045" -b "Baden-Württemberg"
                                            - .\\Check_Impftermin.exe --NOTuserinteractive -c "XXXX-XXXX-XXXX" -p "88045" -b "Baden-Württemberg" --wait 5
                                            - .\\Check_Impftermin.exe --NOTuserinteractive -c "XXXX-XXXX-XXXX" -p "88045" -b "Baden-Württemberg" --soundpath "D:\\i\\love\\meccas.mp3"
                                            - .\\Check_Impftermin.exe --NOTuserinteractive -c "XXXX-XXXX-XXXX" -p "88045" -b "Baden-Württemberg" --pushsaferCode "XXXXXXXXXXXXXXXXX" """))

    parser.add_argument("--NOTuserinteractive",
                        help="Wird dies mit angegeben, wird NICHT in der cmd nach den erforderlichen Parameter gefragt",
                        action='store_true')

    parser.add_argument("-c", "--code",
                        help="Vermittlungscode für den Standort",
                        default=None)

    parser.add_argument("-p", "--plz",
                        help="Postleizahl vom Impfzentrum",
                        default=None)

    parser.add_argument("-b", "--bundesland",
                        help="Bundesland",
                        default=None)

    parser.add_argument("-d", "--driver",
                        help="Pfad zum Chromedriver [Default: .\\data\\chromedriver.exe]",
                        default=".\\data\\chromedriver.exe")

    parser.add_argument("--minimized",
                        help="Chrome ist immer minimiert - BUGGGI!!! -> Disabled function",
                        action='store_true')

    parser.add_argument("--soundpath",
                        help="Pfad zur Sound-Datei die bei einem treffer abgespielt wird. [Default: .\\data\\horn.wav]",
                        default=".\\data\\horn.wav")

    parser.add_argument("--pushsaferCode",
                        help="Code für die Pushsafer App, WENN vorhanden",
                        default=None)

    parser.add_argument("--wait",
                        help="Wie lange in Sekunden gewartet werden soll, bis die Seite erfolgreich geladen wurde [Default: 4sec]",
                        type=int,
                        default=4)

    parser.add_argument("--zyklus",
                        help="""Wie lange in Sekunden nach einem fehlgeschalgenen Versuch gewartet werden soll, bis die Seite erneut aufgerufen wird [Default: 120sec] -
                                Macht es nicht zu klein, ihr wollt ja kein Denie of Service attacke starten...""",
                        type=int,
                        default=120)

    parser.add_argument("--debug",
                        help="Speichert zusaetzlich screenshots zum debuggen",
                        action='store_true')

    return parser


def create_screenshot(driver: webdriver.Chrome, name: str):
    """Speichert einen Screenshot vom Browser

    Args:
        driver (webdriver.Chrome): webdriver
        name (str): Name des Screenshots, angehaengt wird das anktuelle Datum mit minuten
    """

    driver.save_screenshot(f".\\{name}_{time.strftime('%d-%m_%H-%M-%S')}.png")


def get_arguments_from_user() -> list:
    """Holt interaktiv vom User die notwendigen Informationen
    Impf-Code, Plz, Bundesland

    Returns:
        list: Liste fuer den Argument Parser
    """

    print("Für weitere Konfiguration bitte das Programm direkt über eine Konsole starten.\nMit -h können alle Argumente aufgelistet werden\n")
    code = input("Impf-Code: ")
    plz = input("PLZ: ")
    bundesland = input("Bundesland des Zentrums (zB Baden-Württemberg): ")

    arguments = ["-c", code, "-p", plz, "-b", bundesland]
    return arguments


def play_sound(path: str, anzahl: int = 3):
    """Spielt einen Ton ab

    Args:
        path (str): Pfad zur Sounddatei
        anzahl (int, optional): Wie oft soll der Ton abgespielt werden. Defaults to 3.
    """

    while anzahl:
        playsound(path)
        anzahl -= 1


def print_countdown(seconds: int, message: str = "Erneut versuchen in..."):
    """Gibt in einer Zeile einen entsprechenden Coundown aus im Format:
    {message} {min}:{sek} min

    Args:
        seconds (int): Wie lange soll gewartet werden
        message (str, optional): Nachricht vor dem Countdown. Defaults to "Erneut versuchen in...".
    """

    while seconds:
        mins, secs = divmod(seconds, 60)
        timer = '{} {:02d}:{:02d} min'.format(message, mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        seconds -= 1


def impfzentrum_waehlen(bundesland: str, plz: str, driver: webdriver.Chrome):
    """Wahelt das Impfzentrum auf der Startseite aus

    Args:
        bundesland (str): Bundesland muss im Drop-Down Menue verfuegbar sein
        plz (str): Plz des Impfzentrums
        driver (webdriver.Chrome): webdriver
    """

    # Button holen
    submit_button = driver.find_element_by_xpath("/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[4]/button")

    # Cookies aktzeptieren
    accept_cooki(driver)

    # Richtige Daten auswaehlen
    click_bundesland(bundesland, driver)
    click_impfzentrum(plz, driver)

    submit_button.submit()


def vermittlungscode_eingeben(code: str, driver: webdriver.Chrome, wait: int):
    """Gibt den Impf-Code auf der entsprechenden Seite ein

    Args:
        code (str): Impf-Code
        driver (webdriver.Chrome): webdriver
        wait (int): Wie lange soll gewartet werden, bis die erste Aktionen ausgefuerht werden

    Raises:
        StuckedException: Eigene Exception die geworfden wird, wenn der "suchen" Button einen Fehler wirft
    """

    # Cookies aktzeptieren
    accept_cooki(driver)

    # Action chain fuer spaeter
    actions = webdriver.ActionChains(driver)

    # Vermittlungscode bereits vorhanden -> ja
    # Warte auf evtl. Warteraum 1h - 60 * 60 sekunden
    code_vorhanden_xpath = "//span[contains(text(),'Ja')]"
    code_vorhanden = WebDriverWait(driver, 60 * 60).until(expected_conditions.element_to_be_clickable((By.XPATH, code_vorhanden_xpath)))
    code_vorhanden.click()

    # Auswahl des ersten Code-Input-Feldes
    input_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/" \
        "div/div/app-corona-vaccination/div[3]/div/div/div/div[1]/app-corona-vaccination-yes/" \
        "form[1]/div[1]/label/app-ets-input-code/div/div[1]/label/input"
    input_field = WebDriverWait(driver, 1).until(expected_conditions.element_to_be_clickable((By.XPATH, input_xpath)))
    input_field.click()

    # Vermittlungscode eingeben
    time.sleep(1)
    actions.send_keys(code)
    actions.perform()

    # Auf die Seite klicken
    actions.move_by_offset(1, 1)
    actions.click()
    actions.move_by_offset(2, 2)
    actions.click()
    actions.perform()

    # Termin suchen
    suchen_button_xpath = "//button[contains(text(),'suchen')]"
    suchen_button = WebDriverWait(driver, wait).until(expected_conditions.element_to_be_clickable((By.XPATH, suchen_button_xpath)))
    suchen_button.click()

    time.sleep(1)

    counter = 0

    # "Fehler" auf der Seite
    while driver.page_source.find("Fehler") != -1:
        counter += 1

        # Fehlernachricht schreiben
        fehler = driver.find_element_by_xpath("//span[contains(text(),'Fehler')]")
        logging.debug("Fehler Nr: %s - %s", counter, fehler.text)

        # Nach 5 versuchen Exception werfen
        if counter > 5:
            logging.debug("Exception StuckedException wird geworfen - Versuch Nr %s", counter)
            raise StuckedException

        print_countdown(30)

        # Auf die Seite klicken
        actions.move_by_offset(1, 1)
        actions.click()
        actions.move_by_offset(2, 2)
        actions.click()
        actions.perform()

        # Termin suchen
        suchen_button_xpath = "//button[contains(text(),'suchen')]"
        suchen_button = WebDriverWait(driver, wait).until(expected_conditions.element_to_be_clickable((By.XPATH, suchen_button_xpath)))
        suchen_button.click()

        print_countdown(3)


def click_bundesland(bundesland: str, driver: webdriver.Chrome):
    """Waehle das entsprechende Bundesland im Drop-Down Menue auf der Startseite

    Args:
        bundesland (str): Entsprechendes Bundesland des Impfzentrums
        driver (webdriver.Chrome): webdriver
    """

    bundeslaender_waehlen = driver.find_element_by_xpath(
        "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[3]/app-corona-vaccination-center/div[1]/label/span[2]/span[1]/span")
    bundeslaender_waehlen.click()

    moeglichkeiten = driver.find_elements_by_xpath("//ul/*")

    for moeglichkeit in moeglichkeiten:
        if moeglichkeit.text == bundesland:
            moeglichkeit.click()
            return


def click_impfzentrum(plz: str, driver: webdriver.Chrome):
    """Waehle das Impfzentrum anhand der Plz im Drop-Down Menue auf der Startseite

    Args:
        plz (str): Plz des Impfzentrums
        driver (webdriver.Chrome): webdriver
    """

    impfzentren_waehlen = driver.find_element_by_xpath(
        "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[3]/app-corona-vaccination-center/div[2]/label/span[2]/span[1]/span")
    impfzentren_waehlen.click()

    moeglichkeiten = driver.find_elements_by_xpath("//ul/*")

    for moeglichkeit in moeglichkeiten:
        if moeglichkeit.text[0:5] == plz:
            moeglichkeit.click()
            return


def termin_suchen(driver: webdriver.Chrome):
    """Auf suchen Button klicken

    Args:
        driver (webdriver.Chrome): webdriver
    """

    driver.find_element_by_xpath("//button[contains(text(),'suchen')]").click()


def accept_cooki(driver: webdriver.Chrome):
    """Cookies mithilfe der class cookies-info-close akzeptieren

    Args:
        driver (webdriver.Chrome): webdriver
    """

    driver.find_element_by_xpath("//a[contains(@class, 'cookies-info-close')]").click()


def check_queue(driver: webdriver.Chrome):
    """Schaut ob man im Wartebereich ist und versucht diesen zu skippen

    Args:
        driver (webdriver.Chrome): webdriver
    """
    # Cookie holen
    queue_cookie = driver.get_cookie("akavpwr_User_allowed")

    # Neuer Cookie erstellen falls vorhanden
    if queue_cookie:
        logging.debug("Warteraum - Try skipping")
        queue_cookie["name"] = "akavpau_User_allowed"
        driver.add_cookie(queue_cookie)

        # Seite neu laden
        driver.refresh()


def main():
    """
    Main

    Startet das ganze Programm
    """

    # --- Setup Chrome Optionen ---
    options = webdriver.ChromeOptions()
    # Browser wird nach beenden des Programmes nicht beendet
    options.add_experimental_option("detach", True)
    # Falsche Warnemldung unterdruecken (Bluetooth error)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # --- Setup Argumente ---
    parser = init_argument_parser()
    arguments = parser.parse_args()

    if not arguments.NOTuserinteractive:
        arguments = parser.parse_args(get_arguments_from_user())

    code = arguments.code
    plz = arguments.plz
    bundesland = arguments.bundesland
    driver_path = arguments.driver
    minimized = arguments.minimized
    sound = arguments.soundpath
    pushsafer_code = arguments.pushsaferCode
    wait = arguments.wait
    zyklus = arguments.zyklus
    debug = arguments.debug

    url = "https://www.impfterminservice.de/impftermine"

    # --- Setup Logger ---
    seleniumLogger.setLevel(logging.WARNING)
    urllibLogger.setLevel(logging.WARNING)

    file_handler = logging.FileHandler(f"debug-{plz}.log")
    file_handler.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)

    logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(lineno)d: %(message)s',
                        handlers=[
                            file_handler,
                            stream_handler
                        ],
                        level=logging.DEBUG)

    # --- Start Nachricht ---
    logging.info("=== START ===")
    logging.info("Code: %s", code)
    logging.info("PLZ: %s", plz)
    logging.info("Bundesland: %s", bundesland)
    logging.info("Treiber: %s", driver_path)
    logging.info("Minimiert: %s", minimized)
    logging.info("Sound Pfad: %s", sound)
    logging.info("Warte auf Seite: %s sek.", wait)
    logging.info("Zyklus: %s sek.", zyklus)
    logging.info("url: %s", url)
    logging.info("debug: %s", debug)
    logging.info("=============")

    while True:
        # --- Erstelle Driver ---
        driver = webdriver.Chrome(driver_path, options=options)

        if minimized:
            logging.debug("Minimize Funktion ausser Betrieb")
            # driver.minimize_window()

        # --- Starte Aufrufe der Webseiten
        try:
            # Startseite
            driver.get(url)
            print_countdown(wait, "Warte auf Seite... ")

            # Impfzentrum waehlen
            impfzentrum_waehlen(bundesland, plz, driver)
            print_countdown(wait, "Warte auf Seite... ")

            # evtl. Warteraum skippen
            check_queue(driver)
            print_countdown(wait, "Warte auf Seite... ")

            # Code eingeben
            vermittlungscode_eingeben(code, driver, wait)
            print_countdown(wait, "Warte auf Seite... ")

            # Termin suchen
            termin_suchen(driver)
            print_countdown(wait+15, "Warte auf Seite... ")

            if driver.page_source.find("Fehler") != -1:
                raise Exception

        # --- Fehlerbehandlung wenn Element nicht gefunden worden ist ---
        except NoSuchElementException as error:
            if driver.page_source.find("Warteraum") != -1:
                logging.warning("Seite befindet sich im Warteraum - Pause von %s sek wird eingelegt", zyklus)
            else:
                if debug:
                    create_screenshot(driver, "debug_NoSuchElementException")

                logging.warning("Element zum klicken konnte nicht gefunden werden, bitte prüfen - Pause von %s sek wird eingelegt", zyklus)
                logging.debug("Error message: ", exc_info=error)

            driver.quit()
            print_countdown(zyklus)

        # --- Neustart wenn das Programm zu viele Anfragen hat ---
        except StuckedException as error:
            logging.info("Programm wird aufgrund von vielen Fehlveruchen neu gestartet - evtl. Zyklus hochsetzten")
            logging.info("Längere Pause von 5min wird eingelegt um das Problem zu beheben")
            driver.quit()
            print_countdown(60*5)

        # --- Fehler werden von WebDriverWait erzeugt ---
        except (ElementClickInterceptedException, TimeoutException) as error:
            if debug:
                create_screenshot(driver, "debug_ElementClickInterceptedException")

            logging.info("Element zum klicken konnte nicht gefunden werden")
            logging.debug("Fehler: ", exc_info=error)
            driver.quit()
            print_countdown(zyklus)

        except KeyboardInterrupt as error:
            logging.info("Programm beenden", exc_info=error)
            driver.quit()
            sys.exit(0)

        # --- Beenden wenn es ein unbekannter Fehler ist ---
        except Exception as error:
            if debug:
                create_screenshot(driver, "debug_allgemeine_Exception")

            logging.critical("Unerwarteter Fehler!", exc_info=error)
            driver.quit()
            print_countdown(60*5, "Starte neu in...")

        # --- Seiten konnten erfolgreich aufgerufen werden. Checken ob Termin verfügbar ---
        else:
            if driver.page_source.find("keine Termine") == -1:
                if debug:
                    create_screenshot(driver, "debug_termin_gefunden")

                logging.info("Termin gefunden! - %s", plz)

                if pushsafer_code:
                    send_push_nachricht(f"Termine verfügbar!!! - {plz}", pushsafer_code)
                    logging.info("Pushbenachrichtigung gesendet")

                play_sound(sound)
                logging.info("Sound abgespielt")

                input("Zum Beenden Enter drücken...")
                sys.exit(0)

            else:
                driver.close()
                logging.info("Kein Termin gefunden - Browser geschlossen - erneuter Versuch in %s Sekunden", zyklus)
                print_countdown(zyklus)


if __name__ == '__main__':
    main()
