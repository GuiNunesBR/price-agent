# Project Scope

## Visao

O `price-agent` sera um agente pessoal de compras. Em vez de depender apenas de URLs fixas, o sistema deve receber uma intencao de compra, procurar ofertas na internet em fontes confiaveis, comparar os resultados e registrar oportunidades em um painel central.

O Notion sera tratado como o destino preferencial para relatorios e acompanhamento, funcionando como uma base de produtos desejados, ofertas encontradas e alertas.

## Problema

Comprar produtos de maior valor exige acompanhar preco por varios dias ou semanas, comparar lojas, evitar falsos descontos e decidir rapidamente quando surge uma boa oferta. Esse processo costuma ser manual, repetitivo e facil de perder.

## Proposta

Automatizar a rotina de acompanhamento:

- o usuario cadastra o produto desejado;
- o agente busca ofertas em fontes curadas;
- o sistema filtra resultados ruins ou irrelevantes;
- as ofertas sao pontuadas por oportunidade;
- os melhores achados sao registrados no Notion;
- alertas sao enviados quando uma oferta atinge o criterio configurado.

## MVP

### Entrada

Cada produto monitorado deve conter:

- nome do produto;
- marca;
- modelo, quando existir;
- categoria;
- preco-alvo;
- palavras-chave obrigatorias;
- palavras-chave proibidas;
- prioridade;
- status de monitoramento.

### Processo

O MVP deve:

- buscar ofertas em 2 ou 3 fontes iniciais;
- extrair titulo, preco, loja, link, fonte e data;
- validar se o titulo parece corresponder ao produto;
- descartar resultados com palavras proibidas;
- calcular um score simples;
- salvar resultados localmente;
- gerar alerta quando houver oportunidade.

### Saida

O MVP deve entregar:

- registro das ofertas encontradas;
- melhor preco por produto;
- alerta quando uma oferta atingir o preco-alvo;
- resumo pronto para ser enviado ou sincronizado com o Notion.

## Fontes iniciais candidatas

As fontes devem ser escolhidas pela estabilidade e qualidade dos dados. A ordem inicial sugerida:

1. Zoom ou Buscape, quando a pagina publica permitir leitura estavel.
2. Mercado Livre.
3. Amazon.
4. Kabum ou Magalu para categorias especificas.

Observacao: comparadores como Zoom e Buscape sao bons porque ja fazem parte da curadoria, mas podem ter bloqueios, mudancas de HTML ou restricoes. O projeto deve tratar cada fonte como adaptador isolado.

## Notion

O Notion deve funcionar como painel operacional.

### Database: Produtos Monitorados

Campos sugeridos:

- Nome;
- Marca;
- Modelo;
- Categoria;
- Preco-alvo;
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

### Product Agent

Normaliza os dados do produto e transforma a intencao de compra em criterios objetivos de busca.

### Search Agent

Executa buscas nas fontes configuradas e retorna candidatos.

### Price Agent

Extrai informacoes de preco, loja, link, disponibilidade e frete quando possivel.

### Opportunity Agent

Calcula score e decide se uma oferta deve virar alerta.

### Report Agent

Atualiza Notion ou gera relatorios locais quando a integracao ainda nao estiver configurada.

### Alert Agent

Envia notificacoes por Telegram no MVP e pode evoluir para e-mail, WhatsApp ou outros canais.

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

MVP com busca em poucas fontes, score simples, SQLite e Telegram.

### Fase 2

Integracao com Notion e painel de produtos/ofertas.

### Fase 3

Execucao recorrente, deduplicacao de alertas e historico mais completo.

### Fase 4

Melhoria de inteligencia: matching de produto, analise de variacoes, reputacao de loja e aprendizado com feedback.
