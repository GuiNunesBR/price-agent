# Project Scope

## Visao

O `price-agent` sera um agente pessoal de compras. Em vez de depender apenas de URLs fixas, o sistema deve receber uma intencao de compra, procurar ofertas na internet em fontes confiaveis, comparar os resultados e registrar oportunidades em um painel central.

O destino final planejado e um aplicativo proprio: painel de produtos desejados, ofertas encontradas e alertas, com notificacao push no celular. Ate o app existir, o acompanhamento fica no SQLite local e os alertas saem por Telegram ou console.

## Problema

Comprar produtos de maior valor exige acompanhar preco por varios dias ou semanas, comparar lojas, evitar falsos descontos e decidir rapidamente quando surge uma boa oferta. Esse processo costuma ser manual, repetitivo e facil de perder.

## Proposta

Automatizar a rotina de acompanhamento:

- o usuario cadastra o produto desejado;
- o agente busca ofertas em fontes curadas;
- o sistema filtra resultados ruins ou irrelevantes;
- as ofertas sao pontuadas por oportunidade;
- os melhores achados sao registrados num painel central;
- alertas sao enviados quando uma oferta atinge o criterio configurado.

## Estado atual

Diagrama completo no [README](README.md#arquitetura-atual). O que ja funciona:

- `monitor.py` le `products.json`, roteia por host da URL (Amazon, Mercado Livre, Kabum) e salva historico no SQLite;
- falha em um produto nao derruba os outros (try/except por item no loop);
- alerta por preco <= alvo ou queda >= 15% vs ultimo preco;
- notifier com fallback: sem token do Telegram, cai pro console;
- agendamento diario embutido via APScheduler (`--schedule`).

Gaps mapeados na revisao de arquitetura:

- **Erro de scrape nao persiste** — vai so pro log no console; a tabela `alerts` existe mas o fluxo automatico nao grava nela. Nao da pra consultar depois "quais scrapers falharam essa semana".
- **Tabela `prices` chaveada so pelo nome do produto** — mistura lojas no mesmo historico; a regra dos 15% pode comparar preco da Amazon com preco da Kabum. Decisao pendente: adicionar coluna `store` em `prices` OU derivar o historico da tabela `offers` (que ja tem loja/fonte).
- **Score so existe no caminho manual** — `opportunity.py` e importado apenas por `record_offer.py`; o monitor automatico nao pontua oferta nenhuma. `offers` e `alerts` so sao alimentadas manualmente.
- **Massa de teste pendente** — sem URLs reais cadastradas em `products.json` e sem token do Telegram configurado; a primeira execucao ponta a ponta ainda nao foi validada.

## MVP

### Entrada

Cada produto monitorado deve conter:

- nome do produto;
- marca;
- modelo, quando existir;
- categoria;
- faixa de preco para alerta;
- palavras-chave obrigatorias;
- palavras-chave proibidas;
- prioridade;
- status de monitoramento.

### Processo

O MVP deve:

- buscar ofertas nas fontes iniciais priorizadas;
- extrair titulo, preco, loja, link, fonte e data;
- validar se o titulo parece corresponder ao produto;
- descartar resultados com palavras proibidas;
- calcular um score simples;
- salvar resultados localmente;
- gerar alerta quando o preco estiver dentro da faixa configurada ou cair 15% em relacao ao menor preco anterior.

### Saida

O MVP deve entregar:

- registro das ofertas encontradas;
- melhor preco por produto;
- preco medio por produto;
- alerta quando uma oferta entrar na faixa configurada;
- resumo pronto para alimentar o painel.

## Fontes iniciais candidatas

As fontes devem ser escolhidas pela estabilidade e qualidade dos dados. A ordem inicial sugerida:

1. Zoom.
2. Buscape.
3. JaCotei.
4. Mercado Livre.
5. Amazon.
6. Casas Bahia.
7. Magalu.
8. Kabum.
9. Shopee.

Observacao: comparadores como Zoom e Buscape sao bons porque ja fazem parte da curadoria, mas podem ter bloqueios, mudancas de HTML ou restricoes. O projeto deve tratar cada fonte como adaptador isolado.

## Painel (aplicativo proprio)

O painel operacional sera um aplicativo proprio, consumindo os mesmos dados do SQLite (e Postgres no futuro). O modelo de dados abaixo vale independente da interface:

### Database: Produtos Monitorados

Campos sugeridos:

- Nome;
- Marca;
- Modelo;
- Categoria;
- Faixa de preco;
- Prioridade;
- Status;
- Ultima verificacao;
- Melhor preco atual.

### Database: Ofertas Encontradas

Campos sugeridos:

- Produto relacionado;
- Titulo encontrado;
- Loja;
- Fonte;
- Preco;
- Link;
- Score;
- Data da captura;
- Status: nova, boa, ignorada, comprada.

### Database: Alertas

Campos sugeridos:

- Produto;
- Oferta relacionada;
- Canal;
- Data;
- Mensagem;
- Resultado.

## Modulos planejados

Hoje o `monitor.py` concentra os papeis de Price Agent e Alert Agent; a separacao abaixo e o alvo, nao o estado atual.

### Product Agent

Normaliza os dados do produto e transforma a intencao de compra em criterios objetivos de busca.

### Search Agent

Executa buscas nas fontes configuradas e retorna candidatos.

### Price Agent

Extrai informacoes de preco, loja, link, disponibilidade e frete quando possivel.

### Opportunity Agent

Calcula score e decide se uma oferta deve virar alerta. Base ja existe em `opportunity.py` (usado hoje so por `record_offer.py`); falta ligar no fluxo automatico.

### Report Agent

Alimenta o painel ou gera relatorios locais enquanto o app nao existir.

### Alert Agent

Envia notificacoes por Telegram no MVP e evolui para push no aplicativo proprio.

## Score inicial

O score pode comecar simples:

- preco abaixo do alvo;
- desconto em relacao ao menor preco conhecido;
- correspondencia forte com marca/modelo;
- ausencia de palavras proibidas;
- fonte confiavel.

## Fora do escopo inicial

Para manter o MVP pequeno, ficam fora da primeira fase:

- prever tendencia futura de preco;
- comparar especificacoes tecnicas profundas;
- comprar automaticamente;
- buscar em toda a internet sem fontes definidas;
- usar orquestracao multiagente pesada antes do fluxo basico funcionar.

## Roadmap

### Fase 1

MVP com cadastro em `products.json`, SQLite, historico de ofertas e score simples. Telegram fica fora do MVP inicial.

### Fase 2

Painel de produtos/ofertas — comeca com relatorio local, evolui para o aplicativo proprio.

### Fase 3

Execucao recorrente, deduplicacao de alertas e historico mais completo.

### Fase 4

Melhoria de inteligencia: matching de produto, analise de variacoes, reputacao de loja e aprendizado com feedback.

## Trilha de engenharia

Evolucao da infraestrutura do projeto, em fases curtas:

- **Fase A — arquitetura documentada** FEITO - 06/08 diagrama Mermaid no README, gaps de persistencia mapeados.
- **Fase B — execucao agendada no GitHub Actions** (cron), substituindo a dependencia de maquina ligada.
- **Fase C — Dockerfile + docker-compose** para rodar em qualquer ambiente.
- **Fase D — analise do historico de precos com pandas**: tendencia, queda atipica, melhor momento de compra.
- **Fase E — SQLite -> Postgres** com consultas analiticas.

## Ideias futuras

- Persistir falhas de scrape na tabela `alerts` (ou tabela propria) para acompanhar a saude dos scrapers ao longo do tempo.
- Ligar o `opportunity.py` no fluxo automatico do monitor, gravando score em `offers`.
