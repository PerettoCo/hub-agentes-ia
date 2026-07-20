# DB_SCHEMA — Banco de Dados (Supabase DADOS)

Schema de referência para o agente traduzir perguntas em linguagem natural para SQL (PostgREST).
Tabela fato principal: **DBClientes** (clientes).

## Tabelas e colunas principais

### DBClientes (TABELA FATO — clientes)

cardid, title, nomedaempresa, cnpj, cidade, uf, nomedoprincipalstakeholder, contatodostakeholder, emaildostakeholder, razaosocial, corretagem, faturamentoanual, tier, etiquetastatus, currentphasename, setor, subsetor, segmento, canaldevendas, modelodevendas, modelodenegocio, nomedocloser, moeda, poderfinanceiro, portfolio, nivelconsciencia, inadimplencia, situacao, contrato_url, datadeinicio, datadoprimeiropagamento, data_churn, motivo_churn, google_drive_folder, ekyte_id

### DBSquads (squads/times)

cardid, title, departamento, headdri, emaildohead, match_keywords, is_apoio, space_id_squads, id_pipefy

### DBPessoas (colaboradores)

cardid, title, funcao, equipe, datadeinicio, senioridade, status, nomecompleto, emailv4company, cpf, cnpj, whatsappbusiness, razaosocial, remuneracaoinicial, remuneracaovigente, chavepix, space_id, meet_recordings_id

### 11Service (serviços/vendas)

cardid, title, cliente12, datadeiniciopagamento, categoriavendida, juros, valorjuros, pessoalenvolvido, squads, quantotempoduraraesseprojeto, clientedatabase, modelodecobranca, produtosgestaodemidia, valorgestaodemidia, produtoscriativos, valorcriativos, produtoscrmmarketing, valorcrmmarketing, produtoscomerciais, valorcomerciais, produtostech, valortech, produtoscontent, valorcontent, produtoswebdesing, valorwebdesing, produtosassessoria, valorassessoria, datadechurn, squad, squad1, squad2, squad3, datainicio

### 121Kickoff (kickoff comercial)

cardid, title, empresacompany, cidadeestado, segmentodonegocio, nome, cargo, qualofaturamentomensalmedio, qualeoticketmedio, margem_contribuicao_pct, categoria, icp, percepcaomarca, tomdevoz, website, whoareyourmaincompetitors

### 121KickoffEE (kickoff EE)

id, created_at, faturamento_mensal, segmento_negocio, objetivos, modelo_vendas, produto_servico, descricao_clientes, concorrentes, margem_contribuicao_pct, investimento_midia_paga_brl, qtd_leads_mes, qtd_oportunidades_mes, qtd_pedidos_mes, data_envio, nome_cliente, dbcliente_id

### 50TranscricaoCheckin (transcricoes de check-in)

codigo, titulo, criado_em, atualizado_em, squad, cliente, indice_aderencia_ao_roteiro_metodo, indice_rigor_analitico_dados_conteudo, indice_lideranca_gestao_de_expectativa_futuro, check_in, dores_latentes, visao_sobre_o_projeto, avaliacao_positiva_do_projeto, sugestao_de_melhoria, oportunidades_de_upsell, riscos_e_obstaculos, recomendacoes_finais, resumo, indice_atendimento, indice_satisfacao_do_cliente, indice_tecnico, space_id_cliente, funcionario_email

### f_gerenciador_meta (campanhas Meta Ads)

id, ad_id, adset_id, campaign_id, account_id, data_semana, data_fim, custo, impressoes, cliques, reach, ctr, cpc, leads, omni_purchase, value_omni_purchase, resultados, resultado_indicador, cpm, cpp, frequency

### f_gerenciador_google_ad (Google Ads - anuncios)

id, customer_id, campaign_id, ad_group_id, ad_id, data_semana, campaign_name, ad_group_name, ad_status, custo, impressoes, cliques, ctr, average_cpc, conversions, conversions_value, cost_per_conversion, roas, all_conversions

### f_gerenciador_google_campanha (Google Ads - campanhas)

id, customer_id, campaign_id, data_semana, campaign_name, channel_type, campaign_status, bidding_strategy_type, custo, impressoes, cliques, ctr, average_cpc, conversions, conversions_value, cost_per_conversion, roas

### f_gerenciador_google_pmax (Google Ads - PMax)

id, customer_id, campaign_id, asset_group_id, data_semana, campaign_name, asset_group_name, asset_group_status, custo, impressoes, cliques, ctr, conversions, conversions_value, roas

## Convencoes de traducao (portugues -> coluna)

- "ativo/ativos" -> `etiquetastatus = 'Ativo'`
- "faturamento" -> `faturamentoanual`
- "estado/UF" -> `uf` (use sigla de 2 letras: SP, RJ, RS, PR...)
- "squad" -> `squads` (DBClientes) ou tabela `DBSquads`
- "check-in" -> tabela `50TranscricaoCheckin`, filtre por `cliente` (use ILIKE)
- "campanhas" -> `f_gerenciador_meta` / `f_gerenciador_google_*`
- "pessoa/colaborador" -> tabela `DBPessoas`
- "servico" -> tabela `11Service`

## Limites do SQL suportado

- Suporta: `SELECT`, `WHERE` (com `AND`/`OR`), `ORDER BY col ASC|DESC`, `LIMIT n`, `count(*)`
- NAO suporta: `JOIN`, `GROUP BY`, subqueries, funcoes de agregacao exceto `count(*)`
- Texto sempre entre aspas simples: `WHERE uf='SP'`
- Use `count(*)` para contagens (ex: `SELECT count(*) FROM DBClientes WHERE etiquetastatus='Ativo'`)
- Sempre inclua `LIMIT` (padrao 20, maximo 100)

## Exemplos

```sql
SELECT count(*) FROM DBClientes WHERE etiquetastatus='Ativo';
SELECT nomedaempresa, faturamentoanual FROM DBClientes WHERE uf='SP' ORDER BY faturamentoanual DESC LIMIT 10;
SELECT * FROM 50TranscricaoCheckin WHERE cliente ILIKE '%Dettaglio%' LIMIT 5;
SELECT nomedaempresa, cidade, uf FROM DBClientes WHERE setor='Tecnologia' LIMIT 20;
```
