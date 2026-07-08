# Arquitetura dos Agentes de Relatório, Evolução e Conteúdo

## Visão Geral

```
                    ┌──────────────────────────────────────────┐
                    │           OPENCODE AGENT ORCHESTRA        │
                    │          (23 subagentes · 65 skills)      │
                    └──────────────────────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
   ┌────────────────┐      ┌──────────────────┐      ┌──────────────────┐
   │ @relatorios-   │      │ @evolucao-       │      │ @pipeline-       │
   │ trafego        │      │ checkins         │      │ conteudo         │
   │ (Ag. #11)      │      │ (Ag. #23)        │      │ (Ag. #12)        │
   └───────┬────────┘      └───────┬──────────┘      └───────┬──────────┘
           │                       │                          │
           ▼                       ▼                          ▼
   ┌───────────────┐     ┌─────────────────┐      ┌──────────────────┐
   │ Python Script │     │ Mission Control │      │  Python Script   │
   │ relatorio_    │     │ historico-      │      │  pipeline_       │
   │ trafego.py    │     │ checkins.md     │      │  conteudo.py     │
   └───────┬───────┘     └────────┬────────┘      └───────┬──────────┘
           │                      │                        │
           ▼                      ▼                        ▼
   ┌───────────────┐     ┌─────────────────┐      ┌──────────────────┐
   │ connectors.py │     │  Mission Ctrl   │      │  DriveConnector  │
   │ (3 canais +   │     │  (5 arquivos    │      │  GmailConnector  │
   │  Drive/Gmail) │     │   atômicos)     │      │  Claude API      │
   └───────────────┘     └─────────────────┘      └──────────────────┘
```

---

## 1. Agente de Relatórios de Tráfego (gt-relatorios-trafego)

### Árvore de Decisão Completa

```
RELATÓRIO DE TRÁFEGO
│
├─ [ESCOPO] Qual(is) cliente(s)?
│  ├─ Um cliente específico → --cliente "Nome"
│  └─ Todos os clientes → --all
│
├─ [PERÍODO] Qual janela?
│  ├─ 7 dias (semanal — default)
│  ├─ 30 dias (mensal)
│  └─ 90 dias (trimestral)
│
├─ [PLATAFORMAS] Auto-detect por cliente
│  ├─ google_ads_customer_id != null → GoogleAdsConnector
│  ├─ meta_ad_account_id != null → MetaConnector
│  ├─ bing_ads_customer_id != null → BingAdsConnector
│  └─ ga4_property_id != null → GA4Connector (contexto)
│
├─ [FORMATO] Como entregar?
│  ├─ html → Visual cards com cores por ROAS, KPIs por cliente/plataforma
│  ├─ json → Dados estruturados para consumo por sistemas/API
│  └─ terminal → Preview rápido no console
│
├─ [ANÁLISE IA] Claude enriquece?
│  ├─ Sim → Gera resumo executivo + anomalias + recomendações
│  └─ Não → Dados brutos processados
│
├─ [ENTREGA] Onde salvar?
│  ├─ Local → --out ./reports/
│  ├─ Email → --email destinatario (via GmailConnector)
│  └─ Google Drive → --drive (via DriveConnector, estrutura automática)
│
└─ [ANOMALIAS] Detectadas automaticamente?
   ├─ ROAS < 1.5x → 🔴 Crítico (CHAS gerado)
   ├─ ROAS 1.5x-3x → 🟡 Atenção
   ├─ ROAS > 3x → 🟢 Saudável
   ├─ Pace de verba > 20% → 🟡 Gasto fora da curva
   └─ Conversões em queda > 15% → 🔴 Alerta de performance
```

### Arquitetura de Dados

```python
# clientes.json — schema estendido
{
  "nome": "Cliente A",
  "google_ads_customer_id": "123-456-7890",  # Google Ads
  "meta_ad_account_id": "act_123456789",      # Meta Ads
  "bing_ads_customer_id": "123456",           # Bing Ads (opcional)
  "bing_ads_account_id": "654321",            # Bing Ads Account ID
  "ga4_property_id": "properties/123456789",  # GA4 (opcional, contexto)
  "verba_mensal": 5000,                       # Para cálculo de pace
  "vertical": "ecommerce",
  "drive_root_folder_id": null                # Pasta raiz no Drive
}
```

### Pipeline de Dados

```
Google Ads API (google-ads SDK)
  → GoogleAdsConnector.get_performance(customer_id, days)
  → { investimento, conversoes, receita, roas, cpc, cpa, cliques }
       ↓
Meta Ads API (facebook-business SDK)
  → MetaConnector.get_performance(ad_account_id, days)
  → { investimento, conversoes, receita, roas, cpa, ctr, cpm, frequencia }
       ↓
Bing Ads API (bingads SDK)
  → BingAdsConnector.get_performance(days)
  → { investimento, conversoes, receita, roas, cpc, cpa }
       ↓
GA4 API (google-analytics-data)
  → GA4Connector.get_performance(property_id, days)
  → { sessoes, conversoes, taxa_conversao, por_canal }
       ↓
Consolidação → totaliza_consolidado()
  → { investimento, receita, roas_geral, cpl_geral, conversoes }
       ↓
Entrega → HTML | JSON | Terminal | Email | Drive
```

### Recursos Necessários

| Recurso | Status | Onde obter |
|---------|--------|-----------|
| Google Ads Developer Token | ✅ Já existe em `connectors.py` | console.cloud.google.com → APIs → Google Ads API |
| Meta App ID + Token | ✅ Já existe em `connectors.py` | developers.facebook.com → App → Marketing API |
| Bing Ads Developer Token | ✅ Criado (BingAdsConnector) | ads.microsoft.com → Tools → API Access |
| GA4 Property ID | ✅ Já existe em `connectors.py` | analytics.google.com → Admin → Property Settings |
| Google Drive OAuth | ✅ Criado (DriveConnector) | console.cloud.google.com → APIs → Google Drive API |
| Gmail OAuth | ✅ Já existe em `connectors.py` | console.cloud.google.com → APIs → Gmail API |
| Anthropic API Key | ✅ Já existe (função `claude()`) | console.anthropic.com |
| Bing Ads SDK | ⚠️ Adicionar ao requirements.txt | `pip install bingads` |

### Comandos de Uso

```bash
# Relatório semanal de todos os clientes (terminal)
python3 v4-automations/scripts/gt/relatorio_trafego.py --all --days 7 --format terminal

# Relatório mensal de um cliente (HTML + email)
python3 v4-automations/scripts/gt/relatorio_trafego.py \
  --cliente "Cliente A" --days 30 --format html \
  --email gt@v4company.com

# Relatório com análise IA + Drive
python3 v4-automations/scripts/gt/relatorio_trafego.py \
  --cliente "Cliente A" --days 7 --format json \
  --claude --drive --out ./reports

# Relatório trimestral comparativo
python3 v4-automations/scripts/gt/relatorio_trafego.py \
  --all --days 90 --format html --claude --email diretor@v4company.com
```

---

## 2. Agente de Evolução entre Check-ins (account-evolucao-checkins)

### Árvore de Decisão Completa

```
EVOLUÇÃO DE CHECK-INS
│
├─ [CLIENTE] Qual?
│  └─ Localiza em squads/{squad}/clientes/{cliente}/mission-control/
│
├─ [DADOS] O que analisar?
│  ├─ Combinados → combinados.md (pendentes vs feitos, tempo médio)
│  ├─ Apostas → apostas-vivas.md + seção de histórico (ciclo de vida)
│  ├─ Personas → personas-call.md (evolução dos stakeholders)
│  ├─ ROPRE → checkins/*-review.md (qualidade das calls)
│  └─ Tudo (recomendado)
│
├─ [PERÍODO]
│  ├─ Último mês
│  ├─ Último quarter
│  └─ Todo histórico
│
├─ [MÉTRICAS] Calculadas automaticamente
│  ├─ Taxa de cumprimento de combinados (%)
│  ├─ Tempo médio de resolução (dias)
│  ├─ Top arrastados (combinados em 3+ check-ins)
│  ├─ Ciclo de apostas (vivas → confirmadas/mortas → novas)
│  ├─ Evolução de personas (gatilhos, tom, engajamento)
│  ├─ Série ROPRE (forte/médio/fraco/ausente por call)
│  └─ Score de Saúde Composto (0-100)
│
└─ [ALERTAS] Detectados automaticamente
   ├─ Combinado crônico → mesma task pendente em 3+ calls
   ├─ Aposta que nunca morre → viva há 2+ quarters
   ├─ Persona silenciada → stakeholder sumiu das calls
   └─ ROPRE em declínio → qualidade caindo nas últimas 3 calls
```

### Score de Saúde — Fórmula

| Componente | Peso | Fonte | Cálculo |
|---|---|---|---|
| Cumprimento de combinados | 30% | `combinados.md` | (feitos / total) * 100 |
| Vitalidade das apostas | 25% | `apostas-vivas.md` | (novas + confirmadas) / total * 100 |
| Qualidade ROPRE média | 25% | `checkins/*-review.md` | Média (Forte=3, Médio=2, Fraco=1) |
| Ritmo de check-ins | 20% | `historico-checkins.md` | calls reais / calls esperadas * 100 |

**Faixas:**
- 80-100: 🟢 Saudável
- 60-79: 🟡 Atenção
- < 60: 🔴 Crítico

### Estrutura de Dados Lida

```
squads/{squad}/clientes/{cliente}/mission-control/
├── combinados.md              # Tabela: Pendentes / Em andamento / Feitos
├── apostas-vivas.md           # 4 campos: aposta, por que, como mata, plano B
│                              # + seção "Histórico de apostas" no final
├── personas-call.md           # Por stakeholder: voz, gatilhos, padrões, frases
├── historico-checkins.md      # Calls reais com data, tipo, resumo, link
└── historico-preparacoes.md   # Ensaios (separado de calls reais)

squads/{squad}/clientes/{cliente}/checkins/
├── YYYY-MM-DD-review.md       # Review pós-call (diagnóstico ROPRE + ataques)
└── YYYY-MM-DD-prep-roleplay.md # Preparação pré-call
```

---

## 3. Agente de Pipeline de Conteúdo (copy-pipeline-conteudo)

### Árvore de Decisão Completa

```
PIPELINE DE CONTEÚDO
│
├─ [CLIENTE] Qual?
│
├─ [CALENDÁRIO] Já existe?
│  ├─ Não → Gerar via Claude
│  │  ├─ Quantas semanas? (default: 4)
│  │  ├─ Mix: blog_post + email_marketing
│  │  └─ Salvar no Drive? Sim/Não
│  │
│  └─ Sim → Qual item do calendário produzir?
│
├─ [PRODUÇÃO] Qual formato?
│  ├─ blog_post → Claude gera:
│  │  ├─ Título + meta description (160 chars)
│  │  ├─ Introdução (2-3 parágrafos)
│  │  ├─ 3-4 seções H2 com conteúdo
│  │  ├─ Conclusão + CTA
│  │  └─ Tempo de leitura estimado
│  │
│  └─ email_marketing → Claude gera:
│     ├─ 3 opções de subject line
│     ├─ Preheader text
│     ├─ Corpo (2-3 parágrafos)
│     ├─ CTA button + link de destino
│     └─ PS line
│
├─ [STATUS] Ciclo de vida do item
│  ├─ rascunho → criado no calendário
│  ├─ para_aprovacao → JSON salvo no Drive
│  └─ aprovado → status alterado (humano aprova via --aprovar)
│
├─ [ARMAZENAMENTO] Google Drive
│  ├─ Conteudo V4/
│  │  └─ {cliente}/
│  │     ├─ Calendarios/
│  │     │  └─ calendario-editorial-{data}.json
│  │     └─ {YYYY-MM}/
│  │        ├─ blog-post-{titulo}-{data}.json
│  │        └─ email-marketing-{titulo}-{data}.json
│
└─ [NOTIFICAÇÃO] Obrigatória
   ├─ Email para aprovador com link do Drive
   └─ Template: "[Aprovação] {título} — {cliente}"
```

### Pipeline de Produção

```
1. calendario() → Claude gera 4 semanas de tópicos
   → Salva em Drive: Conteudo V4/{cliente}/Calendarios/
   → Exibe no terminal para o usuário escolher
       ↓
2. produzir(indice) → Claude gera conteúdo completo
   → Salva JSON em Drive: Conteudo V4/{cliente}/{YYYY-MM}/
   → Status: "para_aprovacao"
   → Envia email para aprovador com link
       ↓
3. [Humano revisa no Drive]
       ↓
4. aprovar(fileId) → Status vira "aprovado"
   → JSON final disponível para consumo
```

### Estrutura dos JSONs no Drive

```json
// Blog post aprovado
{
  "titulo": "Como reduzir CPA em 40% com segmentação por público",
  "meta_description": "Aprenda 3 estratégias comprovadas...",
  "introducao": "Se você está pagando caro por clique...",
  "secoes": [
    {"subtitulo": "1. Segmentação por intenção", "conteudo": "..."},
    {"subtitulo": "2. Exclusão de públicos gastadores", "conteudo": "..."}
  ],
  "conclusao": "Aplicando essas 3 estratégias...",
  "cta": "Baixe nosso guia completo de segmentação",
  "tempo_leitura": 5,
  "formato": "blog_post",
  "status": "aprovado",
  "aprovado_em": "2026-05-22"
}

// Email marketing aprovado
{
  "titulo": "Newsletter: Cases de ROAS que multiplicaram",
  "subject_lines": [
    "3 clientes que bateram 5x ROAS (e como)",
    "O segredo do ROAS 5x que ninguém conta",
    "[Case] Como eles triplicaram o ROAS em 30 dias"
  ],
  "preheader": "Dados reais de campanhas que funcionaram",
  "corpo": "Nesta edição, vamos analisar...",
  "cta": {"texto": "Ver cases completos", "hint": "/blog/cases-roas"},
  "ps": "PS: Na próxima semana, estratégia para Q3",
  "formato": "email_marketing",
  "status": "aprovado",
  "aprovado_em": "2026-05-22"
}
```

---

## Integração entre os 3 Agentes

```
                    ┌─────────────────────────────┐
                    │       MISSION CONTROL        │
                    │  (combinados, apostas,       │
                    │   personas, historico)        │
                    └──────────┬──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────────┐ ┌────────────┐ ┌──────────────┐
    │ @relatorios-    │ │ @evolucao- │ │ @pipeline-   │
    │ trafego         │ │ checkins   │ │ conteudo     │
    │                 │ │            │ │              │
    │ Dados de mídia  │ │ Score de   │ │ Calendário   │
    │ alimentam       │ │ saúde +    │ │ editorial +  │
    │ check-ins e     │ │ alertas    │ │ blog/email   │
    │ apostas         │ │ alimentam  │ │ viram        │
    │                 │ │ account    │ │ conteudo     │
    └─────────────────┘ └────────────┘ └──────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
           ┌────────────────┐  ┌─────────────────────┐
           │ Google Drive   │  │ Email (Gmail)        │
           │ Relatorios V4/ │  │ Relatorios semanais  │
           │ Conteudo V4/   │  │ Notificacoes de      │
           │                │  │ aprovacao de conteudo│
           └────────────────┘  └─────────────────────┘
```

---

## Checklist de Configuração para Operação

### 1. Credenciais (`v4-automations/config/.env`)

```env
# Google
GOOGLE_ADS_DEVELOPER_TOKEN=seu_token
GOOGLE_ADS_CLIENT_ID=seu_client_id
GOOGLE_ADS_CLIENT_SECRET=seu_client_secret
GOOGLE_ADS_REFRESH_TOKEN=seu_refresh_token

# Meta
META_APP_ID=seu_app_id
META_APP_SECRET=seu_app_secret
META_ACCESS_TOKEN=seu_access_token

# Bing Ads
BING_ADS_DEVELOPER_TOKEN=seu_token
BING_ADS_CLIENT_ID=seu_client_id
BING_ADS_CLIENT_SECRET=seu_client_secret
BING_ADS_REFRESH_TOKEN=seu_refresh_token
BING_ADS_CUSTOMER_ID=seu_customer_id
BING_ADS_ACCOUNT_ID=seu_account_id

# Geral
ANTHROPIC_API_KEY=sk-ant-...
GMAIL_SENDER=agente@v4company.com
EMAIL_GT=gt@v4company.com
EMAIL_AM=am@v4company.com
```

### 2. OAuth Google (`v4-automations/config/credentials.json`)

Necessário para Gmail + Drive + GA4. Gerar em console.cloud.google.com:
- APIs: Gmail API, Google Drive API, Google Analytics Data API, Google Ads API
- Escopos: `gmail.send`, `gmail.readonly`, `drive`, `analytics.readonly`, `adwords`

### 3. Instalação

```bash
cd v4-automations
pip install -r setup/requirements.txt
python setup/auth_google.py  # Gera token.json (1x)
```

### 4. Bing Ads — Observação Importante

O conector Bing Ads foi criado, mas **depende do SDK `bingads`** que pode precisar de configuração adicional:
- O SDK `bingads` (Microsoft Advertising SDK for Python) requer autenticação OAuth com Azure AD
- O Developer Token é obtido em `https://ads.microsoft.com/ → Tools → API Access`
- O Customer ID e Account ID estão na URL quando você acessa a conta no Microsoft Ads

O conector já está estruturado com o padrão correto; se o SDK não estiver disponível, o relatório simplesmente pula Bing Ads e segue com Google + Meta.

### 5. Google Drive — Pasta Raiz

Para o `--drive` funcionar, o primeiro uso vai garantir a criação automática da hierarquia:
```
Relatorios V4/
  Trafego/
    2026-05/
      relatorio-trafego-2026-05-22.json
      relatorio-trafego-2026-05-22.html
Conteudo V4/
  {cliente}/
    Calendarios/
    {YYYY-MM}/
```

Passe `--drive-folder <ID>` se quiser usar uma pasta raiz específica. Se não passar, cria na raiz do Drive.
