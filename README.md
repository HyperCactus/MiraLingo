# Mirad Language Engine

An open-source **Mirad language learning** platform — actively developed.

This project builds tools for the [Mirad](https://en.wikibooks.org/wiki/Mirad_Grammar/print_version) constructed language: a phoneme-based text-to-speech system, a bidirectional English↔Mirad translator, and **MiraLingo** — an interactive web app for learning Mirad vocabulary through adaptive spaced repetition.

> **Status:** TTS and translator are functional. The MiraLingo web app has a working practice loop with adaptive scheduling, typed-answer recall, achievement milestones, and Mirad audio playback.

---

## What is Mirad?

Mirad (formerly Unilingua) is an artificial constructed language designed by Noubar Agopoff in 1966 for logical international communication. Its vocabulary is built from systematic rules — every letter carries semantic or grammatical value, words are derivable from roots, and opposites are predictable through vowel-switching. This makes Mirad uniquely suited for computational processing: regular morphology, deterministic phonology, and an ontology-encoded lexicon.

**Learn more about Mirad:**

- [Mirad Grammar — Wikibooks](https://en.wikibooks.org/wiki/Mirad_Grammar/print_version) — full grammar reference
- [Mirad Lexicon — Wikibooks](https://en.wikibooks.org/wiki/Mirad_Lexicon) — word roots and derivations
- [Mirad Thesaurus — Wikibooks](https://en.wikibooks.org/wiki/Mirad_Thesaurus) — semantic groupings

---

## Packages

| Package | Description | Status |
|---------|-------------|--------|
| [**packages/tts**](packages/tts/) | Phoneme-based TTS engine — tokenization, syllabification, stress, IPA, audio synthesis via eSpeak NG / Piper / MBROLA | Functional |
| [**packages/translator**](packages/translator/) | Bidirectional English↔Mirad translation using DeepInfra DeepSeek-V4-Flash, DSPy, semantic lexicon lookup, structured grammar-rule retrieval, and deterministic post-processing | Active baseline: sentence-level eval improving toward 90% |
| [**packages/webapp**](packages/webapp/) | **MiraLingo** — interactive Mirad language-learning web app with adaptive spaced repetition, typed-answer practice, achievement milestones, and Mirad audio | Working beta |

Shared reference data (lexicon, grammar documents, evaluation results) lives in [`data/`](data/).

---

## Quick Start

Requires Python 3.10+.

```bash
# Install TTS
pip install -e packages/tts/

# Install translator
pip install -e packages/translator/

# TTS: transcribe to IPA
mirad-tts "Be yuboj, ha mir gonbio yansauna gabyuxea dalzeyn." --ipa

# Translator: English → Mirad (uses DeepInfra env from .env)
python -c "
import dspy
from mirad_translator.evaluate import _make_deepinfra_lm
from mirad_translator.translate import DefaultTranslator

dspy.settings.configure(lm=_make_deepinfra_lm())
t = DefaultTranslator()
result = t.forward('you do not work at home')
print(result.mirad_text)
"
```

### MiraLingo Web App

Launch the full stack (backend + frontend) in one command:

```bash
./scripts/start_miralingo.sh
```

Open http://127.0.0.1:5173 and log in with `admin` / `admin` (development only). See the [webapp README](packages/webapp/README.md) for details.

### Docker deployment

Clone, build, and run MiraLingo with Docker Compose:

```bash
git clone https://github.com/HyperCactus/MiraLingo.git
cd MiraLingo
cp .env.example .env
# Optional for local-only test deploys: keep defaults and use admin/admin.
docker compose up --build -d
```

Open http://localhost:5173. The default Compose deployment stores SQLite data in the named `miralingo_db` volume and serves the Svelte frontend through Nginx, with API requests proxied to the FastAPI backend.

For a live site, edit `.env` before first deploy:

```bash
MIRALINGO_ENV=production
MIRALINGO_ENABLE_LOCAL_ADMIN=false
MIRALINGO_SESSION_SECRET=<long random secret>
MIRALINGO_FRONTEND_BASE_URL=https://your-domain.example
MIRALINGO_HTTP_PORT=5173
```

Put HTTPS in front with your host reverse proxy (Caddy, Traefik, Nginx, or cloud load balancer). To ship future fixes/features on the live site:

```bash
git pull --ff-only
docker compose build --pull
docker compose up -d --remove-orphans
```

See the [webapp README](packages/webapp/README.md#docker-deployment) for health checks, rollback notes, and optional Google OAuth settings.

### Experimental Docker services

```bash
# TTS via Docker
docker compose --profile experiments build tts
docker compose --profile experiments run --rm tts mirad-tts "Be yuboj" --ipa

# Optional local model services for experiments only.
# Default translator runtime uses DeepInfra, not Ollama.
docker compose --profile experiments up -d ollama
```

See individual package READMEs for full usage, API details, and configuration.

---

## Project Roadmap

1. ✅ Mirad phoneme-based TTS engine
2. 🔧 Bidirectional English↔Mirad translator (improving accuracy toward 90%)
3. ✅ MiraLingo adaptive practice web app
4. 🔧 Translator accuracy and web app polish

---

## Documentation

- [TTS Installation Guide](docs/TTS_INSTALLATION.md) — setting up eSpeak NG, Piper, MBROLA
- [Piper Integration](docs/PIPER_INTEGRATION.md) — Piper TTS backend details
- [TTS README](docs/README_PIPER.md) — Piper-specific notes
- [Data Overview](data/README.md) — reference data and evaluation results
- [Webapp README](packages/webapp/README.md) — MiraLingo full documentation

## License

MIT