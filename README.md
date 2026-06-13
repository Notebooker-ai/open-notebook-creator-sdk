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
