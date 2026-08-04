import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin


ENTI_FILE = "enti.json"
RISULTATI_FILE = "risultati.json"


PAROLE_BANDO = [
    "concorso",
    "selezione",
    "interpello",
    "assunzione",
    "mobilità",
    "mobilita",
    "bando",
    "avviso",
    "graduatoria"
]


PAROLE_TECNICHE = [
    "architetto",
    "ingegnere",
    "funzionario tecnico",
    "istruttore tecnico",
    "tecnico",
    "lavori pubblici",
    "edilizia",
    "patrimonio",
    "infrastrutture"
]


def carica_enti():
    with open(ENTI_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def salva_risultati(dati):
    with open(RISULTATI_FILE, "w", encoding="utf-8") as f:
        json.dump(
            dati,
            f,
            indent=2,
            ensure_ascii=False
        )


def analizza_link(ente, titolo, url):

    testo = titolo.lower()

    parole_bando_trovate = [
        p for p in PAROLE_BANDO
        if p in testo
    ]

    parole_tecniche_trovate = [
        p for p in PAROLE_TECNICHE
        if p in testo
    ]


    if parole_bando_trovate and parole_tecniche_trovate:

        return {
            "ente": ente["nome"],
            "titolo": titolo,
            "link": url,
            "bando": parole_bando_trovate,
            "tecnico": parole_tecniche_trovate,
            "data": datetime.now().strftime("%d/%m/%Y")
        }


    return None


def controlla_pagina(ente):

    print(f"Controllo: {ente['nome']}")

    risultati = []

    try:

        risposta = requests.get(
            ente["url"],
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=20
        )


        soup = BeautifulSoup(
            risposta.text,
            "html.parser"
        )


        for link in soup.find_all("a", href=True):

            titolo = link.get_text(
                " ",
                strip=True
            )


            if not titolo:
                continue


            url = urljoin(
                ente["url"],
                link["href"]
            )


            risultato = analizza_link(
                ente,
                titolo,
                url
            )


            if risultato:
                risultati.append(risultato)


    except Exception as e:

        print(
            f"Errore {ente['nome']}: {e}"
        )


    return risultati



def main():

    print("Avvio RadarPA")

    enti = carica_enti()

    risultati_totali = []


    for ente in enti:

        risultati = controlla_pagina(ente)

        risultati_totali.extend(risultati)


    salva_risultati(
        risultati_totali
    )


    print(
        f"Risultati trovati: {len(risultati_totali)}"
    )


    for risultato in risultati_totali:

        print(
            risultato["ente"],
            "-",
            risultato["titolo"]
        )


if __name__ == "__main__":
    main()
