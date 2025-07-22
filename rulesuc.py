def valida_pratica_scuola_unicredit(dati_pratica):
    errori = []

    # 1. Contanti non ammessi
    if dati_pratica.get("contanti"):
        errori.append("Pagamento in contanti non ammesso.")

    # 2. Importo non può superare quanto pagato (es: importo dichiarato 200, ma ricevuta dice 150)
    if dati_pratica.get("importo_richiesto") > dati_pratica.get("importo_pagato", 0):
        errori.append("Importo richiesto superiore al pagamento effettuato.")

    # 3. Causale deve essere tra le ammesse
    causali_ammissibili = [
        "tasse scolastiche", "retta e quota di iscrizione", "mensa",
        "libri", "pre e post scuola", "gite scolastiche"
    ]
    if dati_pratica.get("causale") not in causali_ammissibili:
        errori.append("Causale non valida.")

    # 4. Anno pagamento valido
    anno = dati_pratica.get("anno")
    data_pagamento = dati_pratica.get("data_pagamento")
    if anno and data_pagamento:
        anno_valido = (
            str(anno) in data_pagamento or  # es: 2025
            any(mese in data_pagamento for mese in ["10", "11", "12"]) and str(int(anno)-1) in data_pagamento
        )
        if not anno_valido:
            errori.append("Data di pagamento fuori dal periodo ammesso.")

    return errori
