import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

ENTI_FILE = "enti.json"
RISULTATI_FILE = "risultati.json"


def carica_enti():
    with open(ENTI_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def salva_risultati(dati):
    with open(RISULTATI_FILE, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)


def controlla_pagina(ente):

    print(f"Controllo: {ente['nome']}")

    risultati = []

    try:

        risposta = requests.get(
            ente["url"],
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )

        soup = BeautifulSoup(risposta.text, "html.parser")

        for link in soup.find_all("a", href=True):

            titolo = link.get_text(" ", strip=True)

            if not titolo:
                continue

            testo = titolo.lower()

            trovate = []

            for parola in ente.get("parole", []):

                if parola.lower() in testo:
                    trovate.append(parola)

            if trovate:

                href = link["href"]

                if href.startswith("/"):
                    href = ente["url"].rstrip("/") + href

                risultati.append({
                    "ente": ente["nome"],
                    "titolo": titolo,
                    "link": href,
                    "parole": trovate,
                    "data": datetime.now().strftime("%d/%m/%Y")
                })

    except Exception as e:

        print(f"Errore {ente['nome']}: {e}")

    return risultati


def main():

    print("Avvio TecnicoAlert")

    enti = carica_enti()

    tutti = []

    for ente in enti:

        risultati = controlla_pagina(ente)

        tutti.extend(risultati)

    salva_risultati(tutti)

    print(f"Risultati trovati: {len(tutti)}")

    for r in tutti:

        print(r["ente"], "-", r["titolo"])


if __name__ == "__main__":
    main()
