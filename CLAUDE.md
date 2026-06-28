# CLAUDE.md — RIP-Agent

## Projet

RAG agentique eval-first sur des documents de concession télécom publique (DSP/RIP).
Stack : Python 3.12 · FastAPI · pgvector · SentenceTransformers · LiteLLM · OpenTelemetry.

## Architecture

```
src/rip_agent/
  config.py          Settings pydantic-settings (source de vérité, injectable)
  tokenization.py    count_tokens / split_by_tokens via tiktoken cl100k_base
  db.py              default_connection_factory(dsn) → psycopg, injectable
  telemetry.py       setup_telemetry / get_tracer
  schemas/           Contrats Pydantic — immuables, pas de logique
  ingestion/         discovery → parser → chunking → embedder → store → pipeline
  retrieval/         bm25 · dense · hybrid (RRF) · pipeline
  generation/        context · llm · prompts · pipeline
  rag/               RAGPipeline = retrieval + generation (point d'entrée unique)
  evaluation/        loader · judge · metrics/ · runner
  api/               FastAPI main · routes · deps
```

**Règle d'or** : `RAGPipeline.answer(question)` est utilisé à l'identique par l'API et par l'eval — ne jamais créer un chemin de code alternatif.

## Prochaine phase — Long-Context RAG avec arbre de sections

L'objectif est de passer d'un chunking plat à un **arbre hiérarchique** :

```
Document
  └─ Section (H1)
       ├─ Sous-section (H2)
       │    ├─ Chunk leaf 1
       │    └─ Chunk leaf 2
       └─ Sous-section (H2)
            └─ Chunk leaf 3
```

Pattern "small-to-big" : retrieval sur les feuilles (petits chunks), expansion vers le parent pour la génération (plus grand contexte). Stocké en DB avec `parent_id` + `node_type` (section | leaf). Un nœud section a `text` = concaténation de ses enfants (pour le cas où on veut un contexte plein).

Nouveaux modules à créer :
- `ingestion/tree.py` — `build_document_tree(document) -> DocumentNode`
- `schemas/document.py` — `DocumentNode` (id, parent_id, level, node_type, text, …)
- `retrieval/expand.py` — `expand_to_parent(chunks, store) -> list[RetrievedChunk]`
- Migration DB : table `doc_nodes` avec `parent_id UUID REFERENCES doc_nodes(id)`

## Standards de code

### Encapsulation
- Chaque module expose une interface minimale ; les détails SQL, les formats intermédiaires, les helpers locaux restent privés (`_nom`).
- Les classes ne partagent pas d'état mutable entre elles — elles reçoivent leurs dépendances par constructeur.
- Les fonctions pures (chunking, fusion RRF, sélection de contexte) ne lisent pas Settings directement — Settings leur est passé en argument ou injecté.

### Injection de dépendances
Toutes les dépendances lourdes ou I/O sont injectables :
- `connection_factory` pour psycopg
- `model` pour SentenceTransformer
- `llm_client` pour LiteLLM
- `parse_pdf_fn`, `chunk_document_fn` pour les pipelines d'orchestration
- `split_fn`, `token_counter` pour le chunking

**Ne jamais** importer et appeler directement un client réseau ou un modèle au niveau module — ça brise les tests.

### Imports
- Les imports lourds (sentence_transformers, llama_parse, tiktoken) sont lazy-importés dans les méthodes ou propriétés qui en ont besoin, jamais au top-level d'un module.
- Ordre : stdlib → third-party → local (`rip_agent.*`).

### Typage
- Tout est typé : signatures complètes, pas de `Any` sauf aux frontières DB/réseau.
- Utiliser les types de `collections.abc` (`Callable`, `Sequence`, `Mapping`) plutôt que `typing`.
- Pydantic v2 pour tous les contrats de données.

### Commentaires
- Aucun commentaire sauf si le **pourquoi** est non-évident (contrainte cachée, invariant subtil, contournement d'un bug connu).
- Pas de docstrings descriptifs qui répètent le nom de la fonction.

### Logging / Observabilité
- Chaque étage émet des spans OpenTelemetry via `get_tracer(__name__)`.
- Attributs de span : noms préfixés par l'étage (`ingestion.*`, `retrieval.*`, `generation.*`, `evaluation.*`).
- Pas de `print()` — spans ou logs structurés uniquement.

## Standards de tests

### Localisation
- Tous les tests unitaires dans `tests/unit/test_<module>.py`.
- Un fichier de test par module source.

### Règles
- Aucun test unitaire ne parle à Postgres, LlamaParse, SentenceTransformers ou LiteLLM.
- Les collaborateurs externes sont toujours remplacés par des faux injectés (lambdas, objets simples, pas de `mock.patch`).
- Les tests vérifient le comportement observable (sorties, effets sur les faux), pas l'implémentation interne.
- Les tests d'intégration (marqués `@pytest.mark.integration`) sont séparés et peuvent toucher une vraie DB.
- Chaque test est autonome : pas de fixtures globales complexes, pas de state partagé entre tests.

### Nommage
`test_<ce_que_ça_fait>_<dans_quelle_condition>` — lisible sans connaître le code.

## Workflow Git

Toute modification suit le flux : **issue GitHub → branche → PR → merge main**.

```bash
# 1. Créer l'issue (décrit le QUOI et le POURQUOI)
gh issue create --title "..." --body "..."

# 2. Créer la branche depuis main (nommée d'après l'issue)
git checkout main && git pull
git checkout -b feat/<sujet>          # ou fix/ refactor/ test/ docs/

# 3. Développer, committer (messages en anglais, impératif)
git add <fichiers ciblés>             # jamais git add -A
git commit -m "feat(scope): description courte"

# 4. Pousser et ouvrir la PR en référençant l'issue
git push -u origin feat/<sujet>
gh pr create --title "..." --body "Closes #<n>"

# 5. Merger (squash ou merge commit selon la taille)
gh pr merge --merge               # ou --squash pour les petits fix
git checkout main && git pull
```

**Règles :**
- Un commit par unité logique — pas de "wip" ou "fix fix fix".
- Toujours cibler des fichiers précis dans `git add`, jamais `.` ou `-A`.
- La PR ferme l'issue avec `Closes #n` dans le body.
- Jamais de push direct sur `main`.

## Commandes utiles

```bash
# Lancer les tests unitaires seuls
uv run pytest tests/unit/

# Linter + types
uv run ruff check .
uv run mypy src

# Ingestion
uv run python scripts/run_ingestion.py --source sample_corpus/docs/

# API
uv run uvicorn rip_agent.api.main:app --reload

# DB seule
docker compose up -d db
```

## Ce qu'il ne faut pas faire

- Ne pas ajouter de feature non demandée : bug fix ≠ refacto du module entier.
- Ne pas créer de CLAUDE.md, README, ou docs sauf si explicitement demandé.
- Ne pas skipper les hooks ou le typage pour aller plus vite.
- Ne pas dupliquer la logique entre l'API et l'eval — `RAGPipeline` est le point d'entrée commun.
- Ne pas stocker de secrets dans le code — `.env` uniquement, jamais versionné.
