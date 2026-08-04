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
    "istruttore direttivo tecnico",
    "lavori pubblici",
    "edilizia",
    "patrimonio",
    "infrastrutture",
    "manutenzione",
    "impianti",
    "urbanistica"
]


PAROLE_ESCLUSE = [
    "tecnico amministrativo",
    "personale tecnico amministrativo",
    "area tecnico amministrativa",
    "settore tecnico amministrativo",
    "ufficio tecnico amministrativo"
]


PAROLE_PAGINA_INFORMATIVA = [
    "settore ",
    "ufficio ",
    "area ",
    "servizio ",
    "struttura "
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



def classifica(testo):

    testo = testo.lower()


    for parola in PAROLE_ESCLUSE:
        if parola in testo:
            return None


    if "tempo pieno e indeterminato" in testo or "tempo indeterminato" in testo:
        return {
            "tipo": "tempo_indeterminato",
            "priorita": 5
        }


    if "tempo determinato" in testo:
        return {
            "tipo": "tempo_determinato",
            "priorita": 3
        }


    if "mobilità" in testo or "mobilita" in testo:
        return {
            "tipo": "mobilita",
            "priorita": 2
        }


    if (
        "concorso" in testo
        or "selezione" in testo
        or "interpello" in testo
    ):
        return {
            "tipo": "concorso_generico",
            "priorita": 4
        }


    return None



def analizza_link(ente, titolo, url):

    testo = titolo.lower()


    for parola in PAROLE_PAGINA_INFORMATIVA:
        if testo.startswith(parola):
            return None


    for parola in PAROLE_ESCLUSE:
        if parola in testo:
            return None


    parole_bando = [
        p for p in PAROLE_BANDO
        if p in testo
    ]


    parole_tecniche = [
        p for p in PAROLE_TECNICHE
        if p in testo
    ]


    if not parole_bando or not parole_tecniche:
        return None


    categoria = classifica(testo)


    if categoria is None:
        return None


    return {
        "ente": ente["nome"],
        "titolo": titolo,
        "link": url,
        "tipo": categoria["tipo"],
        "priorita": categoria["priorita"],
        "bando": parole_bando,
        "tecnico": parole_tecniche,
        "data": datetime.now().strftime("%d/%m/%Y")
    }



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


    risultati_totali.sort(
        key=lambda x: x["priorita"],
        reverse=True
    )


    salva_risultati(
        risultati_totali
    )


    print(
        f"Risultati trovati: {len(risultati_totali)}"
    )


    print(
        json.dumps(
            risultati_totali,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
