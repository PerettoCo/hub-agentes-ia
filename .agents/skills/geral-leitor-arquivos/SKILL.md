---
name: geral-leitor-arquivos
description: Leitor universal de arquivos — extrai texto de PDF, DOCX, DOC, ODT, ODS, ODP, PPTX, XLSX, XLS, RTF, imagens (OCR), HTML, CSV e código-fonte. Use quando o usuário enviar ou pedir para ler qualquer arquivo binário ou documento que o Read tool não consiga processar diretamente.
---

# Leitor Universal de Arquivos

Extrai texto de qualquer formato de arquivo usando `scripts/file-reader.py`.

## Formatos Suportados

| Extensão | Formato | Motor |
|----------|---------|-------|
| `.pdf` | PDF | pypdf / pdftotext / OCR (scanned) |
| `.docx` | Word | python-docx |
| `.doc` | Word antigo | antiword / catdoc / olefile |
| `.odt` | LibreOffice Texto | odfpy |
| `.ods` | LibreOffice Planilha | odfpy |
| `.odp` | LibreOffice Apresentação | odfpy |
| `.rtf` | Rich Text Format | striprtf |
| `.pptx` | PowerPoint | python-pptx |
| `.xlsx` | Excel | openpyxl |
| `.xls` | Excel antigo | ssconvert (Gnumeric) |
| `.csv` | CSV | nativo |
| `.html` / `.htm` | HTML | HTMLParser |
| `.png` / `.jpg` / `.gif` / `.bmp` / `.tiff` / `.webp` | Imagem | Tesseract OCR (português + inglês) com pré-processamento |
| `.md` / `.txt` / `.py` / `.js` / `.ts` / etc. | Texto/código | leitura UTF-8 direta |

## Uso

```bash
python3 scripts/file-reader.py <caminho-do-arquivo> [max_chars]
```

Retorna JSON com campos: `file`, `name`, `extension`, `size_chars`, `size_bytes`, `truncated`, `text`, `error`.

## Fluxo para o Agente

1. Usuário envia ou menciona um arquivo
2. Se Read tool não conseguir ler, use:
   ```bash
   python3 scripts/file-reader.py "caminho/do/arquivo"
   ```
3. Apresente o texto extraído ao usuário
4. Se `truncated: true`, pergunte se quer ler mais de uma parte específica

## RAG — Ingestão de Documentos

Use `scripts/rag-ingest.py` para ingestão completa:

```bash
# Ingerir um arquivo
python3 scripts/rag-ingest.py documento.pdf

# Com parametros customizados
python3 scripts/rag-ingest.py documento.pdf --chunk-size 1500 --overlap 200 --type fact --importance 4

# Ingerir diretório inteiro
python3 scripts/rag-ingest.py diretorio/

# Dry-run (só mostra o que faria)
python3 scripts/rag-ingest.py documento.pdf --dry-run
```

## Dependências

```bash
pip install -r scripts/requirements.txt
```

### Sistema (apt-get)
- `tesseract-ocr tesseract-ocr-por` — OCR
- `poppler-utils` — pdftotext
- `libmagic1` — detecção MIME
- `antiword catdoc` — .doc antigo
- `ssconvert` (gnumeric) — .xls antigo (opcional)
