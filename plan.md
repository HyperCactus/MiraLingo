I want to queue the full roadmap:
Mirad phoneme based TTS engine
English/other languages to Mirad translator
Mirad language learning web-app

To archive this I would like to containerise the project with docker. and seperate the repo into 3 sections with their own documentation and everything (the current readme can go in the TTS engine section and there will be a new one later for the whole project).

For the translator component, I would like to start off with a retrieval-augmented system that:
- Takes a string of English text as input
- Uses simple keyword/exact-match retrieval (no sentence-transformers — Mirad terms may retrieve poorly in English embedding space) against indexed chunks from `data/mirad-docs/mirad_thesaurus.md` and `data/mirad-docs/mirad_lexicon.md`, which contain English→Mirad pairs with Mirad translations embedded in each chunk
- Retrieves at the **word/token level** first, then assembles context — word order and grammar in Mirad differ from English, so individual word lookups followed by assembly are more reliable than whole-sentence retrieval
- Passes the retrieved word translations plus the relevant grammar rules from `data/mirad-docs/mirad_grammer.md` (especially: vowel-contrast derivation, consonant domains, pluralization with **-i**, article **ha**, noun-modifier order, verb tenses/aspects) to an LLM along with few-shot example sentences
- All retrieval logic lives locally and offline — no external API calls for indexing or search
- **Evaluation plan (phased)**:
  1. Phase 1 — eval on Ollama only using the **44 samples** in `data/pronunciation_tests.csv` (English sentences/words → Mirad translations, with syllable count as a sanity check)
  2. Phase 2 — once the Ollama baseline is stable, use the teacher model (DeepInfra: `Qwen/Qwen3-235B-A22B-Instruct-2507`, from `.env`) for prompt optimization and dataset expansion
- The evaluation dataset will be uploaded to HuggingFace once refined

For the web app, I want a simple MVP, for the front end I want a simple, modern, user friendly UI. It should have secure Authentication and users, use relevant open-source libraries rather then doing everything from scratch, keep the stack very simple. 
It will have a few different modes:
A flashcard mode where the user is shown flashcards of common english words/phrases and need to enter the Mirad translation and see if it was correct (or press skip to see the translation without guessing if they don't know the word/phrase), and vice versa i.e. get a Mirad word and guess the english translation. When the Mirad version of a word is shown, it should also include other versions off the word, i.e. opposite, different intensity, etc. The app should track how many times the user has been shown each word/phrase and how often they get it correct, and word/phrases that they almost always get correct in recent sessions should be shown less frequently, and once the user is getting most of the current word/phrases correct, they will be show some new ones that they haven't seen before. It should start off with the most common words/phrases. Each word/phrase shown should also have a 'loudspeaker icon' speak button next to it to read aloud using the Mirad tts part of the project. You should start with samples for testing and verification and get it ready, so later I can run it to generate all translations and TTS audio samples at once rather then doing it on the fly. To get all these word/phases, use wordfreq to get most common english words, and translate them. 
For phrases/sentences, there is a dataset @data/phrases/english_sentences.csv which is tab separated English sentences that will also need translation, it is very big, you can compute a commonness score for a phrase by filtering out some basic stop words and calculating the mean word frequency of the words it contains.

The app should also have a mode to just translate any entered text using the translation part of this project, and the translated text should have a button to read aloud using the tts component of the project.

The home page after login should be a main menu section where the user can choose a mode, enter the settings menu, or see their stats/progress.

Items for later down the road: add support for other languages as the base language to learn mirad (Both implementing them in the translater and flashcards etc. and also the UI of the app (controlled by a language selection drop-down with in the settings menu)); Add icons with the word flashcards from https://www.opensymbols.org/

I want it all to be well documented, as simple as possible without sacrificing functionality, logically structured. Make frequant commits after verified changes.