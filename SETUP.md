# Setup — [GuiNunesBR](https://github.com/GuiNunesBR)

Checklist para publicar e rodar o **price-agent** na sua conta GitHub.

O projeto esta evoluindo para um agente pessoal de compras: cadastrar produtos desejados, pesquisar ofertas em fontes curadas, registrar resultados e alertar quando houver oportunidade real de compra.

## 1. Ferramentas

| Ferramenta | Para quê |
|------------|----------|
| [Python 3.11+](https://www.python.org/downloads/) | Rodar o agente |
| [Git](https://git-scm.com/) | Versionamento |
| [GitHub CLI](https://cli.github.com/) | Criar repo e push (`gh`) |
| [Brave](https://brave.com/) | Browser dos scrapers (Playwright) |
| [Notion](https://www.notion.so/) | Painel planejado para relatorios e oportunidades |

Instalar GitHub CLI no Windows:

```powershell
winget install GitHub.cli
```

## 2. Identidade Git (uma vez)

```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

Use o e-mail da conta GitHub (ou o e-mail noreply do GitHub).

## 3. Login no GitHub

```powershell
gh auth login
```

Escolha: GitHub.com → HTTPS → login no browser.

## 4. Projeto local

```powershell
cd C:\Users\joaoe\price-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
```

Edite `products.json` com os produtos atuais. No MVP futuro, esse arquivo deve evoluir para incluir nome do produto, marca, modelo, preco-alvo, palavras obrigatorias e palavras proibidas.

### Telegram (opcional)

1. Fale com [@BotFather](https://t.me/BotFather) → `/newbot` → copie o token.
2. Envie uma mensagem ao seu bot; descubra o `chat_id` com [@userinfobot](https://t.me/userinfobot) ou a API `getUpdates`.
3. Preencha no `.env`:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### Notion (planejado)

A integracao com Notion ainda sera implementada. A ideia e usar o Notion como painel central com databases para:

- produtos monitorados;
- ofertas encontradas;
- alertas enviados;
- status de compra ou descarte.

Quando a integracao for criada, o `.env` deve receber variaveis como token da integracao e IDs das databases.

## 5. Publicar no GitHub

Na pasta do projeto, com arquivos já commitados:

```powershell
gh repo create price-agent --public --source=. --remote=origin --push
```

Ou crie manualmente em https://github.com/new (owner: **GuiNunesBR**, nome: `price-agent`) e depois:

```powershell
git branch -M main
git remote add origin https://github.com/GuiNunesBR/price-agent.git
git push -u origin main
```

## 6. Agendamento diário (Windows)

Task Scheduler → diário → programa:

`C:\Users\joaoe\price-agent\.venv\Scripts\python.exe`

Argumentos:

`C:\Users\joaoe\price-agent\monitor.py`

## Brave

Os scrapers usam o Brave instalado em:

`C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`

Outro caminho? Defina `BRAVE_EXECUTABLE_PATH` no `.env`.

