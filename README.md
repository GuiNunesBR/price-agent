# price-agent

Agente monitor de preços com histórico SQLite, scrapers por loja (Playwright) e alertas via Telegram.

## Estrutura

```
price-agent/
├── products.json      # produtos monitorados
├── prices.db          # histórico (gerado na primeira execução)
├── monitor.py         # agente principal
├── notifier.py        # Telegram / console
├── database.py        # SQLite
├── query.py           # consulta menor preço (evolução → RAG)
├── scrapers/
│   ├── amazon.py
│   ├── mercado_livre.py
│   └── kabum.py
└── requirements.txt
```

## Setup

Guia completo (GitHub **GuiNunesBR**, Brave, Telegram): **[SETUP.md](SETUP.md)**

```powershell
cd C:\Users\joaoe\price-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
# necessário para o motor Chromium usado com o executável do Brave
copy .env.example .env
```

Scrapers rodam no **Brave** (Chromium via Playwright), não no Chromium empacotado do Playwright.

Edite `products.json` com URLs reais e metas. Configure `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` no `.env` (opcional).

## Uso

Execução única (teste / cron manual):

```powershell
python monitor.py
```

Com agendamento diário embutido (APScheduler):

```powershell
python monitor.py --schedule
```

Consulta histórico:

```powershell
python query.py "PS5 Slim" --days 30
```

## Agendamento externo

**Windows (Task Scheduler):** diário → `python C:\Users\joaoe\price-agent\monitor.py`

**Linux (cron):** `0 9 * * * cd /caminho/price-agent && python3 monitor.py`

## Alertas

| Evento | Condição |
|--------|----------|
| Meta atingida | preço ≤ `target_price` |
| Queda relevante | ≥ 5% abaixo do último registro |
| Falha de scrape | seletor/site mudou |

## Próximos passos (arquitetura de agente)

- [ ] Dashboard com gráficos
- [ ] PostgreSQL + API
- [ ] LangGraph/CrewAI para promoções suspeitas e perguntas em linguagem natural
- [ ] Busca automática de produtos / comparador multi-loja
- [ ] Docker + CI

Os seletores CSS variam por página; ajuste em `scrapers/*.py` se um site mudar o layout.
