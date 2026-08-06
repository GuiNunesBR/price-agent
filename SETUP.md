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
cd price-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
python setup_db.py
```

Edite `products.json` com os produtos atuais. O formato atual inclui nome do produto, marca, modelo, faixa de preco, palavras obrigatorias, palavras proibidas e fontes desejadas.

Para recriar ou atualizar os produtos cadastrados no SQLite depois de editar `products.json`, rode:

```powershell
python setup_db.py
```

### Telegram (opcional)

O alvo futuro e notificacao push por aplicativo proprio; ate la, o Telegram e o canal de alerta no celular. Sem token configurado, os alertas saem no console.

1. Fale com [@BotFather](https://t.me/BotFather) → `/newbot` → copie o token.
2. Envie uma mensagem ao seu bot; descubra o `chat_id` com [@userinfobot](https://t.me/userinfobot) ou a API `getUpdates`.
3. Preencha no `.env`:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### Painel (planejado)

O painel de acompanhamento sera um aplicativo proprio consumindo os dados do SQLite:

- produtos monitorados;
- ofertas encontradas;
- alertas enviados;
- status de compra ou descarte.

Detalhes do modelo de dados em [PROJECT_SCOPE.md](PROJECT_SCOPE.md).

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

`<pasta do projeto>\.venv\Scripts\python.exe`

Argumentos:

`<pasta do projeto>\monitor.py`

## Brave

Os scrapers usam o Brave instalado em:

`C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`

Outro caminho? Defina `BRAVE_EXECUTABLE_PATH` no `.env`.

