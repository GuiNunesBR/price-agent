# price-agent

Agente pessoal de compras para monitorar produtos desejados, pesquisar precos em fontes curadas e avisar quando aparecer uma oportunidade real de compra.

O projeto esta evoluindo de um monitor de URLs especificas para um sistema mais amplo: voce cadastra um produto, define criterios de busca e preco-alvo, e o agente procura ofertas em fontes como marketplaces e comparadores de preco. Os resultados devem ser registrados em um local central, com Notion como destino preferencial para o painel de acompanhamento.

## Objetivo

Transformar buscas manuais de preco em um fluxo recorrente:

1. Cadastrar produtos desejados.
2. Buscar ofertas em fontes confiaveis.
3. Comparar preco, loja, link e aderencia ao produto.
4. Identificar oportunidades abaixo do preco-alvo ou com bom score.
5. Registrar resultados no Notion.
6. Enviar alerta quando houver uma oportunidade relevante.

Exemplo de entrada:

```text
Produto: Geladeira Electrolux Inverter modelo XYZ
Preco-alvo: R$ 3.200
Palavras obrigatorias: Electrolux, Inverter, XYZ
Palavras proibidas: usado, recondicionado
Prioridade: alta
```

## Estado atual

A base atual ja possui:

- historico SQLite;
- scrapers por loja com Playwright/Brave;
- alertas via Telegram ou console;
- cadastro simples em `products.json`;
- consulta de historico por `query.py`.

Essa base sera reorganizada para suportar descoberta de ofertas, comparacao entre fontes e relatorios no Notion.

## Arquitetura planejada

Os "agentes" comecam como modulos simples e podem evoluir para orquestracao mais inteligente depois:

| Modulo | Responsabilidade |
|--------|------------------|
| Product Agent | Normalizar produto, marca, modelo, palavras obrigatorias e proibidas |
| Search Agent | Buscar candidatos em fontes curadas como Zoom, Buscape, Amazon, Mercado Livre e outras |
| Price Agent | Extrair preco, loja, frete quando possivel, link e disponibilidade |
| Opportunity Agent | Calcular score e decidir se existe oportunidade |
| Report Agent | Registrar achados no Notion e gerar resumo |
| Alert Agent | Enviar alerta por Telegram, e-mail ou outro canal |

## Fases

### Fase 1: MVP funcional

- Cadastrar produto, preco-alvo e palavras-chave.
- Buscar em 2 ou 3 fontes iniciais.
- Extrair titulo, preco, loja, link e fonte.
- Filtrar falsos positivos basicos.
- Gerar score simples.
- Salvar resultado em SQLite.
- Alertar via Telegram quando `preco <= preco-alvo`.

### Fase 2: Notion como painel

- Criar integracao com Notion API.
- Registrar produtos monitorados.
- Registrar ofertas encontradas.
- Marcar status: nova, boa, ignorada, comprada.
- Manter ultima verificacao e melhor preco.

### Fase 3: Automacao recorrente

- Rodar em agenda diaria ou por intervalo.
- Evitar alertas duplicados.
- Atualizar historico de preco.
- Gerar resumo periodico no Notion.

### Fase 4: Inteligencia de compra

- Melhorar correspondencia entre busca e produto real.
- Comparar variacoes de modelo.
- Considerar reputacao da loja e frete.
- Aprender com ofertas ignoradas.
- Responder perguntas sobre historico e melhores oportunidades.

## Estrutura atual

```text
price-agent/
|-- products.json      # produtos monitorados atualmente
|-- prices.db          # historico gerado na primeira execucao
|-- monitor.py         # agente principal atual
|-- notifier.py        # Telegram / console
|-- database.py        # SQLite
|-- query.py           # consulta menor preco
|-- scrapers/
|   |-- amazon.py
|   |-- mercado_livre.py
|   |-- kabum.py
|   |-- browser.py
|   `-- page.py
|-- PROJECT_SCOPE.md   # escopo e roadmap do novo produto
|-- SETUP.md
`-- requirements.txt
```

## Setup

Guia completo: [SETUP.md](SETUP.md)

```powershell
cd C:\Users\joaoe\price-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
```

Scrapers rodam no Brave via Playwright. Se o Brave estiver em outro caminho, configure `BRAVE_EXECUTABLE_PATH` no `.env`.

## Uso atual

Execucao unica:

```powershell
python monitor.py
```

Com agendamento embutido:

```powershell
python monitor.py --schedule
```

Consulta historico:

```powershell
python query.py "PS5 Slim" --days 30
```

## Proximos passos imediatos

- Definir o formato novo de `products.json`.
- Escolher as primeiras fontes de busca.
- Criar modelo de dados para ofertas encontradas.
- Preparar integracao com Notion.
- Separar os modulos internos por responsabilidade.
