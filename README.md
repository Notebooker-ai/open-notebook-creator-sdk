# open-notebook-creator-sdk

The normalized plugin contract for **Open Notebook** "Creation" multimodal generators.

Each creator (flashcards, infographics, podcasts, …) lives in its own repo, depends
on this SDK, subclasses `BaseCreator`, and is exposed via the `open_notebook.creators`
entry point. Open Notebook resolves models, assembles content, runs the creator, and
renders the result — all through the DTOs and versioned schemas defined here.

## Contract

```python
from open_notebook_creator_sdk import BaseCreator, CreationRequest, CreationResult

class MyCreator(BaseCreator):
    config_model = MyConfig                      # Pydantic -> drives the UI form

    @property
    def manifest(self):
        return self.build_manifest(
            key="my_thing", name="My Thing", version="0.1.0",
            sdk_compat=">=0.1,<1", emits=["chart_spec.v1"],
            model_roles=[...],                   # capability-annotated
        )

    async def generate(self, request: CreationRequest) -> CreationResult:
        llm = request.models["text"].create_language()
        ...
        return CreationResult(status="SUCCESS", schema_id="chart_spec.v1", data={...})
```

**Rules**

- Creators are **stateless per call** — no module-global config, no shared clients.
- Return `data` that validates against the `schema_id` you declare in `emits`.
- Write files into `request.output_dir` only; return them as relative `CreationFile`s.
- Never log/persist `request.models` — credentials are excluded from serialization.

## Optional manifest fields

Beyond the required `key` / `name` / `version` / `sdk_compat` / `emits`, a manifest
may declare:

| Field | Purpose |
| --- | --- |
| `icon` | Icon identifier the frontend renders in nav and pickers. |
| `has_custom_form` | The frontend ships a bespoke config form instead of rendering `config_schema`. |
| `view` | A self-contained HTML view bundle (`CreatorView(entry="view/index.html")`) the plugin ships and the host renders in a sandboxed iframe. |
| `suggestion_hint` | Steers the host's "Suggest" button on the *additional instructions* field. |

`suggestion_hint` is a **noun phrase naming what a useful instruction for this
artifact decides** — the artifact's shape, not the content's meaning. The host
injects it into a single LLM call that drafts an example instruction from the
notebook's sources; it is never shown to the end user verbatim. Mention the
creator's real config levers (grouping, counts, themes) where they apply:

```python
return self.build_manifest(
    key="timelines", name="Timeline", version="0.3.0",
    sdk_compat=">=0.10,<1", emits=["timeline.v1"],
    suggestion_hint=(
        "which chronological thread to trace, the time span to cover, how "
        "fine-grained events should be, and how to group them into eras"
    ),
)
```

Omit it and the host falls back to a generic prompt — every field above is
optional and defaults to `None`/`False`, so older manifests keep validating.

## Versioned schemas

`schema_id` strings (`flashcards.v1`, `chart_spec.v1`, `audio.v1`) are the
cross-language contract. They are **immutable**; new behavior = new id. Generate the
frontend's TypeScript + Zod from them:

```bash
python -m open_notebook_creator_sdk.codegen path/to/creation.generated.ts
```

## Compliance

```python
from open_notebook_creator_sdk.testing import assert_creator_compliant
def test_compliance(): assert_creator_compliant(MyCreator())
```

MIT licensed.
