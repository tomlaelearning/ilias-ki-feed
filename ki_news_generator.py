import feedparser
from feedgen.feed import FeedGenerator
import datetime
import pytz

# --- KONFIGURATION ---

# 1. RSS-Feeds, die durchsucht werden sollen (Quellen)
QUELL_FEEDS = [
    'https://www.e-teaching.org/rss/news',
    'https://hochschulforumdigitalisierung.de/feed/',
    'https://www.forschung-und-lehre.de/rss',
    'https://www.heise.de/rss/heise-atom.xml' # Heise für allgemeine Tech-News
]

# 2. Schlagworte, nach denen gesucht werden soll (Groß-/Kleinschreibung wird ignoriert)
SUCHBEGRIFFE = [
    'ki', 'künstliche intelligenz', 'chatgpt', 'llm', 
    'scopus', 'copilot', 'prompt', 'generative ai', 'machine learning'
]

# --- HAUPTPROGRAMM ---

def generiere_ki_feed():
    print("Starte KI-News-Scout...")
    
    # Neuen, eigenen Feed initialisieren (Dieser wird später in ILIAS eingebunden)
    fg = FeedGenerator()
    fg.title('KI in der Hochschullehre - FH Dortmund')
    fg.description('Automatischer Newsfeed rund um Künstliche Intelligenz in Forschung und Lehre.')
    fg.link(href='https://www.fh-dortmund.de', rel='alternate')
    fg.language('de')
    
    gesammelte_eintraege = []

    # Alle Quellen durchsuchen
    for url in QUELL_FEEDS:
        print(f"Durchsuche Feed: {url}")
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            # Text aus Titel und Zusammenfassung holen (kleingeschrieben für einfache Suche)
            titel = entry.title.lower() if hasattr(entry, 'title') else ''
            beschreibung = entry.description.lower() if hasattr(entry, 'description') else ''
            
            # Prüfen, ob eines der Schlagworte vorkommt
            treffer = any(begriff in titel or begriff in beschreibung for begriff in SUCHBEGRIFFE)
            
            # "ki" als ganzes Wort suchen, um falsche Treffer wie "Mar(ki)erung" zu vermeiden
            # Für eine simple Lösung reicht uns hier eine grobe Prüfung:
            if ' ki ' in f" {titel} " or ' ki ' in f" {beschreibung} ":
                treffer = True

            if treffer:
                gesammelte_eintraege.append(entry)

    # Gefilterte Einträge zu unserem neuen Feed hinzufügen
    for eintrag in gesammelte_eintraege:
        fe = fg.add_entry()
        fe.title(eintrag.title)
        fe.link(href=eintrag.link)
        
        # Beschreibung übernehmen (falls vorhanden)
        if hasattr(eintrag, 'description'):
            fe.description(eintrag.description)
            
        # Datum übernehmen oder aktuelles Datum setzen, falls keins vorhanden
        if hasattr(eintrag, 'published_parsed') and eintrag.published_parsed:
            # Umwandlung des Zeitformats für den Feed
            dt = datetime.datetime(*eintrag.published_parsed[:6])
            dt = pytz.utc.localize(dt)
            fe.pubDate(dt)
        else:
            fe.pubDate(datetime.datetime.now(pytz.utc))

    # XML-Datei speichern
    dateiname = 'ki_news.xml'
    fg.rss_file(dateiname)
    print(f"Fertig! {len(gesammelte_eintraege)} KI-relevante Artikel gefunden und in '{dateiname}' gespeichert.")

if __name__ == '__main__':
    generiere_ki_feed()
