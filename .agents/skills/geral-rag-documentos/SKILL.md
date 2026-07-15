---
name: geral-rag-documentos
description: Ingestão e busca semântica de documentos via RAG com pgvector. Extrai texto de PDF, DOCX, DOC, XLSX, PPTX, ODT, imagens e mais, chunkifica com overlap, gera embeddings e armazena no Supabase para busca por similaridade. Use quando o usuário quiser indexar um documento, perguntar sobre múltiplos documentos, ou buscar informação em arquivos já processados.
---

# RAG de Documentos — Ingestão + Busca Semântica

Pipeline completo: arquivo → extração → chunk (com overlap) → embedding → pgvector → busca.

## Ingestão (Script Único)

Use `scripts/rag-ingest.py` — pipeline robusto com dedup, progresso e tratamento de erros:

```bash
# Ingerir um arquivo
python3 scripts/rag-ingest.py documento.pdf

# Com chunking customizado
python3 scripts/rag-ingest.py documento.pdf --chunk-size 1500 --overlap 200

# Especificar tipo e importancia
python3 scripts/rag-ingest.py documento.pdf --type fact --importance 4

# Ingerir diretório inteiro (recursivo)
python3 scripts/rag-ingest.py diretorio/

# Dry-run (mostra o que faria sem modificar)
python3 scripts/rag-ingest.py documento.pdf --dry-run

# Limitado a pasta atual (nao recursivo)
python3 scripts/rag-ingest.py diretorio/ --no-recursive
```

O script faz automaticamente:
- Extração de texto via `file-reader.py`
- Chunking com overlap (evita perda de contexto entre chunks)
- Dedup por checksum SHA256 (não duplica chunks idênticos)
- Embedding via LiteLLM ou OpenAI
- Armazenamento no Supabase pgvector
- Progress bar (`tqdm`)
- 3 retries com backoff em caso de falha

## Ingestão Manual (Passo a Passo)

### 1. Extrair texto

```bash
python3 scripts/file-reader.py "documento.pdf" > /tmp/doc.json
```

### 2. Armazenar na memória vetorial

```bash
text=$(python3 -c "import json; d=json.load(open('/tmp/doc.json')); print(d['text'])")
python3 scripts/memory-cli.py store "$text" --type fact --importance 3
```

### 3. Para documentos grandes, use chunking manual

```bash
python3 scripts/file-reader.py "documento.pdf" 100000 > /tmp/doc.json
python3 -c "
import json
with open('/tmp/doc.json') as f:
    text = json.load(f)['text']
chunk_size = 2000
for i in range(0, len(text), chunk_size):
    print(f'---CHUNK {i//chunk_size}---')
    print(text[i:i+chunk_size])
" > /tmp/chunks.txt
```

## Busca Semântica

```bash
# Busca vetorial (embedding)
python3 scripts/memory-cli.py search "sua pergunta sobre o documento" --limit 5

# Full-text search (fallback)
python3 scripts/memory-cli.py search "termo exato" --fts

# Filtrado por tipo
python3 scripts/memory-cli.py search "pergunta" --type fact
```

## Contexto para o Agente

```bash
python3 scripts/memory-cli.py inject-context "sua pergunta aqui" --limit 5
```

Retorna bloco formatado para colocar no prompt do agente, com similaridade e importancia.

## Script Único (Legado — Ingestão Manual Completa)

```bash
python3 -c "
import sys, json, subprocess
from pathlib import Path

filepath = sys.argv[1]
r = subprocess.run(['python3', 'scripts/file-reader.py', filepath], capture_output=True, text=True)
doc = json.loads(r.stdout)
if doc.get('error'):
    print(f'Erro: {doc[\"error\"]}')
    sys.exit(1)
text = doc['text']
chunk_size = 2000
for i in range(0, len(text), chunk_size):
    chunk = text[i:i+chunk_size]
    subprocess.run(['python3', 'scripts/memory-cli.py', 'store', chunk, '--type', 'fact', '--importance', '0.7'])
print(f'✅ {doc[\"name\"]} — {doc[\"size_chars\"]} chars em {len(text)//chunk_size + 1} chunks')
" "documento.pdf"
```

## Dependências

```bash
pip install -r scripts/requirements.txt
```

## Troubleshooting

| Problema | Causa | Solução |
|---|---|---|
| `ModuleNotFoundError` | Dependência faltando | `pip install -r scripts/requirements.txt` |
| Nenhum resultado | Threshold alto | Baixe para 0.5 com `--threshold 0.5` |
| Dedup pulando chunks | Checksum já existe | Comportamento esperado (não duplica) |
| Timeout na ingestão | Documento muito grande | Aumente timeout ou use `--dry-run` primeiro |
