# Automated benefit discovery

This pipeline starts from normalized procedure and law JSON. It creates a
review queue; it does not write Neo4j during discovery. Only records explicitly
marked `approved` are imported.

## Discovery stages

1. **Recall candidate sections.** General legal-expression cue groups scan all
   normalized law sections for entitlements, payments/support, exemptions or
   reductions, and priority/guarantees. Broad phrases are accepted only in a
   benefit-related heading. Child sections under a benefit heading are included
   because conditions and amounts are often stated separately. Cue matches are
   recorded for review; they are only a recall filter.
2. **Classify and extract.** Gemini Flash classifies sections in batches of eight
   using a Pydantic structured-output schema. Categories distinguish benefit
   rules, eligibility, amounts/duration, application steps, exceptions,
   cross-references, irrelevant text, and insufficient context. Extracted quotes
   must occur verbatim in the source section or the extraction is discarded.
3. **Match to procedures.** Extracted benefit concepts are ranked with BM25 over
   procedure fields and verified benefit text. The top 30 positive-scoring
   benefits and benefits sharing a `life_event` are passed to Gemini for pair
   checking. BM25 is a ranking signal, not a probability; a shared life event
   adds a candidate but does not add score.
4. **Review.** Candidate pairs are grouped by normalized benefit title, ranked
   using transparent retrieval signals, and written as one JSON object per line
   with `status: pending`. Reviewers may set `approved` or `rejected`, edit the
   title/aliases, and refine evidence. Only approved records with known procedure,
   section, and non-empty quote are accepted by the importer.

The default Gemini model is `gemini-3.8-flash`; override it with
`GEMINI_BENEFIT_MODEL`. The pipeline uses `GEMINI_API_KEY` (or `GOOGLE_API_KEY`)
and no vector database or embedding model. Extracted field values carry quotes
that are checked against the source section. Section extractions and pair checks
are cached in `data/benefit_relation/discovery.cache.jsonl` by input content,
model, and prompt version. Increment `PROMPT_VERSION` when changing extraction
or matching instructions.

## Run

Generate a review file from normalized law and procedure records:

```powershell
python -m db.graph.discover_benefits --top-k 30
```

For a small trial, use `--max-sections 20`. This caps classification after
candidate recall and can omit candidates, so do not use it for a complete run.

Edit `data/benefit_relation/discovery_review.jsonl` and set reviewed records to
`approved` or `rejected`. The generator preserves review status when candidate
evidence is unchanged, plus the canonical title and aliases; changed evidence
returns the candidate to `pending`. To merge two reviewed concepts,
set them to the same canonical `benefit_id` and title. Import the approved records together with the existing
procedure/law graph:

```powershell
python -m db.graph.neo4j_import --reviewed-benefits data/benefit_relation/discovery_review.jsonl
```

When `--reviewed-benefits` is supplied, the importer replaces previously
generated `benefit_discovery` relationships from that review queue and leaves
manual `RELATED_TO_BENEFIT` edges intact. Do not use `--reset` unless the full
Neo4j graph should be deleted and rebuilt.

## Graph shape

Approved records create:

```text
(:Procedure)-[:HAS_RELATED_BENEFIT {review_status: "approved"}]->(:Benefit)
(:Benefit)-[:SUPPORTED_BY {quote, evidence_id}]->(:LawSection)
```

The RAG graph retriever reads these reviewed links alongside the legacy manual
procedure-to-section links. A related benefit is a suggestion; eligibility for
an individual remains unknown until the relevant personal facts and legal
conditions have been checked.
