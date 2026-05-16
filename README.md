# Codexx Crypto AI Agent

MVP AI agent provider-agnostic untuk research crypto, NFT mint, airdrop, narasi market, automation report, RAG knowledge base, dan autonomous coding/research workflow. Bisa memakai Claude, DeepSeek, GLM/Zhipu, atau endpoint OpenAI-compatible lain.

> **Catatan risiko:** crypto/NFT/airdrop berisiko tinggi. Agent ini membantu riset dan membuat laporan; bukan financial advice. Selalu verifikasi ulang dari sumber resmi sebelum mengambil keputusan.

## Fitur

- **Chat agent dengan custom prompt** untuk tanya jawab dan mode analis crypto, tanpa terkunci ke satu vendor model.
- **Research crypto & NFT**: web search/scraping, template analisis early project, airdrop, NFT mint, narasi Twitter/X, dan peluang monetisasi.
- **Tool-using agent**: web fetch, scraping, eksekusi kode sandbox sederhana, workflow scheduler, email, Telegram, API call, file reader, dan RAG database.
- **RAG knowledge base**: ingest export Notion/docs, website snapshots, dan repo code ke SQLite FTS.
- **Autonomous coding/research agent**: planning multi-step, browsing/searching, edit file terbatas, run test, dan membuat draft PR report.
- **Scheduler**: kirim laporan otomatis ke Telegram/email sesuai interval.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Isi `.env` minimal:

```bash
AI_PROVIDER=anthropic
AI_MODEL=claude-3-5-sonnet-latest
ANTHROPIC_API_KEY=sk-ant-...
# Alternatif DeepSeek:
# AI_PROVIDER=deepseek
# AI_MODEL=deepseek-chat
# DEEPSEEK_API_KEY=...
# Alternatif GLM/Zhipu:
# AI_PROVIDER=glm
# AI_MODEL=glm-4-flash
# GLM_API_KEY=...
TELEGRAM_BOT_TOKEN=123:abc
TELEGRAM_CHAT_ID=123456
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASSWORD=app-password
REPORT_EMAIL_TO=target@example.com
```

Jalankan chat:

```bash
codexx-agent chat --prompt "Kamu analis crypto degen tapi tetap risk-aware"
```

Jalankan report sekali:

```bash
codexx-agent research --topic "early airdrop L2 dan AI x crypto minggu ini" --telegram
```

Ingest knowledge base:

```bash
codexx-agent ingest ./exports/notion ./docs ./src
codexx-agent ask-kb "Apa strategi research airdrop dari knowledge base?"
```

Jalankan scheduler:

```bash
codexx-agent schedule --config examples/schedule.json
```


## Provider model AI

Agent ini **bukan khusus OpenAI**. Pilih provider dari environment variable:

| Provider | `AI_PROVIDER` | API key | Default base URL | Contoh model |
| --- | --- | --- | --- | --- |
| Claude / Anthropic | `anthropic` atau `claude` | `ANTHROPIC_API_KEY` | `https://api.anthropic.com/v1` | `claude-3-5-sonnet-latest` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com/v1` | `deepseek-chat` |
| GLM / Zhipu | `glm`, `zai`, atau `zhipu` | `GLM_API_KEY` | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` |
| Provider kompatibel | `openai-compatible` | `COMPATIBLE_API_KEY` | `COMPATIBLE_BASE_URL` | sesuai provider |
| Local fallback | `local` | tidak perlu | - | - |

DeepSeek dan GLM memakai format Chat Completions OpenAI-compatible, sedangkan Claude memakai Anthropic Messages API. Jadi kalau Anda pakai Claude, DeepSeek, atau GLM, cukup set `AI_PROVIDER`, `AI_MODEL`, dan API key yang sesuai.

## Arsitektur

```text
cryptox_agent/
├── agent.py          # Orchestrator chat/research/coding
├── config.py         # Environment & runtime config
├── prompts.py        # Custom system prompt Indonesia/crypto
├── scheduler.py      # Workflow scheduler sederhana
├── rag.py            # SQLite FTS knowledge base
├── tools/            # Web, code, email, telegram, API, file tools
└── cli.py            # Command line interface
```

## Contoh schedule

Lihat [`examples/schedule.json`](examples/schedule.json). Scheduler mendukung interval detik dan dapat mengirim report ke Telegram atau email.

## Production checklist

1. Validasi model dan endpoint provider yang dipilih di staging sebelum automation mengirim report rutin.
2. Tambahkan provider search resmi (Tavily/SerpAPI/Brave) untuk kualitas hasil X/Twitter dan web.
3. Tambahkan database durable (Postgres + pgvector) bila knowledge base besar.
4. Simpan credential di secret manager, bukan file `.env` di server bersama.
5. Jalankan code interpreter dalam container terisolasi bila menerima kode dari user.
6. Tambahkan guardrail anti-scam: blacklist contract, source reputation, dan checklist official links.
7. Tambahkan observability: logs, trace, retries, dan alerting.
