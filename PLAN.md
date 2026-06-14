# PolliniBot — Checklist di Realizzazione

## Fase 1 — Creazione Bot Telegram

- [x] Aprire Telegram e cercare `@BotFather`
- [x] Inviare `/newbot` e seguire le istruzioni (scegliere nome e username)
- [x] Copiare il **token API** ricevuto (formato: `123456789:AAF...`)
- [x] Creare o aprire il gruppo Telegram dove mandare i report
- [x] Aggiungere il bot come membro del gruppo
- [x] Recuperare il **chat ID** del gruppo:
  - Inviare un messaggio al gruppo, poi aprire `https://api.telegram.org/bot<TOKEN>/getUpdates`
  - Il `chat.id` dei gruppi è un numero negativo (es. `-1001234567890`)
- [x] Salvare token e chat ID in un file `.env` (non committare mai questo file)

## Fase 2 — Struttura del Progetto

- [x] Creare la struttura directory
- [x] Creare `.gitignore`
- [x] Creare `.env.example`
- [x] Creare `requirements.txt`

## Fase 3 — Implementazione

- [x] `pollen.py` — categorizzazione p/m³ → basso/medio/alto con soglie ISPRA
- [x] `scrapers/ispra.py` — scraper ISPRA con requests + BeautifulSoup
- [x] `scrapers/threebmeteo.py` — scraper 3bmeteo con Playwright headless
- [x] `telegram_sender.py` — formattazione e invio messaggio
- [x] `main.py` — entry point con dependency check, orchestrazione

## Fase 4 — Test Locale

- [x] Creare ambiente virtuale: `python3 -m venv venv && source venv/bin/activate`
- [x] Installare dipendenze: `pip install -r requirements.txt`
- [x] Installare browser Playwright: `playwright install chromium`
- [x] Copiare `.env.example` in `.env` e inserire token e chat ID reali
- [x] Eseguire `python main.py` e verificare che il messaggio arrivi su Telegram
- [x] Verificare che i dati ISPRA siano corretti e aggiornati
- [x] Verificare che 3bmeteo venga scrapato correttamente

## Fase 5 — Deploy su Ubuntu Server

### Prerequisiti server
- [ ] Verificare Python 3.10+: `python3 --version`
- [ ] Installare pip se non presente: `sudo apt install python3-pip`
- [ ] Installare dipendenze sistema per Playwright:
  ```bash
  sudo apt install -y libglib2.0-0 libnss3 libnspr4 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdrm2 libdbus-1-3 libxcb1 \
    libxkbcommon0 libx11-6 libxcomposite1 libxdamage1 libxext6 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
  ```

### Upload progetto (via git)
- [ ] Creare repository **pubblico** su GitHub e fare il primo push (locale → remoto)
- [ ] Sul server, clonare il repository via HTTPS (nessuna autenticazione necessaria, repo pubblico): `git clone https://github.com/<utente>/pollinibot.git /opt/pollinibot`
- [ ] Creare venv sul server: `python3 -m venv /opt/pollinibot/venv`
- [ ] Installare dipendenze: `/opt/pollinibot/venv/bin/pip install -r requirements.txt`
- [ ] Installare Playwright chromium: `/opt/pollinibot/venv/bin/playwright install chromium`
- [ ] Creare `.env` sul server con i valori reali (file non versionato, va creato a mano)

### Aggiornamenti futuri
- [ ] Per aggiornare il codice: `cd /opt/pollinibot && git pull`
- [ ] Se cambia `requirements.txt`: `/opt/pollinibot/venv/bin/pip install -r requirements.txt`

### Configurazione crontab
- [ ] Aprire crontab: `crontab -e`
- [ ] Aggiungere la riga (ogni giorno alle 8:00):
  ```
  0 8 * * * /opt/pollinibot/venv/bin/python /opt/pollinibot/main.py >> /var/log/pollinibot.log 2>&1
  ```
- [ ] Verificare con `crontab -l`
- [ ] Testare esecuzione manuale dal server: `/opt/pollinibot/venv/bin/python /opt/pollinibot/main.py`
ma
## Fase 6 — Manutenzione

- [ ] Controllare il log periodicamente: `tail -f /var/log/pollinibot.log`
- [ ] Aggiornare i selettori HTML se ISPRA o 3bmeteo cambiano struttura della pagina

---

## Note Rapide

**Recuperare chat ID gruppo Telegram:**
```
https://api.telegram.org/bot<TOKEN>/getUpdates
```
Dopo aver inviato un messaggio nel gruppo, cercare `"chat":{"id":-XXXXXXXXXX}`.

**Soglie categorizzazione (p/m³):**
| Polline | Assente | Basso | Medio | Alto |
|---------|---------|-------|-------|------|
| Compositae | 0–2 | 3–9 | 10–29 | ≥30 |
| Urticaceae | 0–2 | 3–19 | 20–79 | ≥80 |
| Cupressaceae/Taxaceae | 0–2 | 3–14 | 15–49 | ≥50 |
