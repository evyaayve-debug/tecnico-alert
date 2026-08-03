import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime


ENTI_FILE = "enti.json"
SEEN_FILE = "seen.json"
RISULTATI_FILE = "risultati.json"


def carica_enti():
    with open(ENTI_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def carica_visti():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


def salva_visti(dati):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            dati,
            f,
            indent=2,
            ensure_ascii=False
        )


def salva_risultati(dati):
    with open(RISULTATI_FILE, "w", encoding="utf-8") as f:
        json.dump(
            dati,
            f,
            indent=2,
            ensure_ascii=False
        )


def controlla_pagina(ente):

    print(f"Controllo: {ente['nome']}")

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

        testo = soup.get_text(
            " ",
            strip=True
        ).lower()

        trovate = []

        for parola in ente.get("parole", []):
            if parola.lower() in testo:
                trovate.append(parola)

        if trovate:
            return {
                "ente": ente["nome"],
                "url": ente["url"],
                "parole": trovate,
                "data": datetime.now().strftime("%d/%m/%Y")
            }

    except Exception as e:

        print(
            f"Errore {ente['nome']}: {e}"
        )

    return None


def main():

    print("Avvio TecnicoAlert")

    enti = carica_enti()

    risultati = []

    for ente in enti:

        risultato = controlla_pagina(ente)

        if risultato:
            risultati.append(risultato)


    salva_risultati(risultati)


    print(
        f"Nuovi risultati: {len(risultati)}"
    )


    for risultato in risultati:

        print(
            risultato["ente"],
            risultato["parole"]
        )


if __name__ == "__main__":
    main()
