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
- [x] Verificare Python 3.10+: `python3 --version`
- [x] Installare pip, venv e git se non presenti: `sudo apt install -y python3-pip python3-venv git`

### Upload progetto (via git)
- [x] Creare repository **pubblico** su GitHub e fare il primo push (locale → remoto): https://github.com/arrubiu/pollinbot
- [x] Sul server, clonare il repository via HTTPS (nessuna autenticazione necessaria, repo pubblico): `git clone https://github.com/arrubiu/pollinbot.git /home/ubuntu/sergej/websites/pollinbot`
- [x] Creare venv sul server: `python3 -m venv /home/ubuntu/sergej/websites/pollinbot/venv`
- [x] Installare dipendenze: `/home/ubuntu/sergej/websites/pollinbot/venv/bin/pip install -r requirements.txt`
- [x] Installare dipendenze di sistema per Playwright (rileva automaticamente i nomi pacchetto corretti per la versione di Ubuntu): `sudo /home/ubuntu/sergej/websites/pollinbot/venv/bin/playwright install-deps chromium`
- [x] Installare il browser Playwright Chromium: `/home/ubuntu/sergej/websites/pollinbot/venv/bin/playwright install chromium`
- [x] Creare `.env` sul server con i valori reali (file non versionato, va creato a mano)

### Aggiornamenti futuri
- [ ] Per aggiornare il codice: `cd /home/ubuntu/sergej/websites/pollinbot && git pull` (per il push da locale invece, il remoto `origin` usa SSH: `git@github.com:arrubiu/pollinbot.git`)
- [ ] Se cambia `requirements.txt`: `/home/ubuntu/sergej/websites/pollinbot/venv/bin/pip install -r requirements.txt`

### Configurazione crontab
- [x] Aprire crontab: `crontab -e`
- [x] Aggiungere la riga (ogni giorno alle 8:00):
  ```
  0 8 * * * /home/ubuntu/sergej/websites/pollinbot/venv/bin/python /home/ubuntu/sergej/websites/pollinbot/main.py >> /home/ubuntu/sergej/websites/pollinbot/pollinibot.log 2>&1
  ```
- [x] Verificare con `crontab -l`
- [x] Testare esecuzione manuale dal server: `/home/ubuntu/sergej/websites/pollinbot/venv/bin/python /home/ubuntu/sergej/websites/pollinbot/main.py`
ma
## Fase 6 — Manutenzione

- [ ] Controllare il log periodicamente: `tail -f /home/ubuntu/sergej/websites/pollinbot/pollinibot.log`
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
