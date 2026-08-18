---
id: d204be47-47f7-41b2-8973-8492a94e8cf6
title: "vault-audit"
type: "note"
project: "Distillation"
tags:
  - "#note"
  - "#project"
  - "#ld/living"
  - "#stack/python"
  - "#status/shipped"
  - "#cluster/personal"
status: shipped
created: "2026-08-17"
updated: "2026-08-17"
source_path: "/Users/brunojaamaa/Desktop/distillation/(Flint) Distillation"
---

# vault-audit

**Check this vault against itself: no broken links, no orphans, frontmatter that parses, and
every repo folder either documented or explicitly excluded.** Run after any batch of note edits.

## The four gates

| Gate | Passing means |
|---|---|
| **Broken wikilinks** | Every wikilink resolves to a note in this vault, except the deliberate cross-vault links to the hub, which are allowlisted |
| **Orphans** | Every note is linked from at least one other note |
| **Frontmatter** | Every note's frontmatter parses as YAML and carries `id`, `title`, `type`, `project`, `tags`, `status`, `created`, `updated` |
| **Coverage** | Every top-level folder in the repo appears in [[(Report) Folder Audit]], either documented or listed as excluded with a reason |

## Run it

The verification script written for the initial build lives in the scratchpad rather than the
vault, because it is a tool and not a note. Rewrite it if it has been cleaned up. It must:

1. Walk every markdown file under `Mesh/`, `Sources/`, `Media/`, `Exports/` and
   `Shards/project/`. Exclude Flint's own plumbing.
2. Parse the frontmatter block between the first two `---` lines and assert the eight required
   keys.
3. **Assert every tag list item is quoted.** An unquoted `#` starts a YAML comment and silently
   empties the whole tag list, so a note can lose every tag without erroring.
4. Collect every wikilink target, strip any alias suffix, and check a note file with that name
   exists.
5. Allowlist the hub targets, currently `(Map) BRUNO HQ`.
6. Build the reverse index and report any note with no inbound link.
7. Assert every `id` is unique.

## A fifth gate, specific to this repo ⚠️

**Check that the two irreplaceable artefacts are still there**, because this vault's most
important claim is about them:

```bash
ls -la "/Users/brunojaamaa/Desktop/distillation/runs/current/best/adapters.safetensors"
du -sh "/Users/brunojaamaa/Desktop/distillation/data"
```

Expected: **3,672,013 bytes** and **5.1 MB**. If either is missing, that is not a vault problem,
it is an incident. Update [[(Note) The Deleted Student Weights]] and tell Bruno immediately.

## The known allowlist

`(Map) BRUNO HQ` lives in the hub vault at
`/Users/brunojaamaa/Desktop/Main Vault/Main/Mesh/(Map) BRUNO HQ.md`. It is linked from
[[(Map) Master Map]], [[(Guide) BRUNO HQ]] and [[(Report) Project Summary]] on purpose and
resolves only when both vaults are open.

## Then

Write the results into [[(Report) Build Log]] with the current note count and tree, and log a
`verify` op:

```bash
node "/Users/brunojaamaa/Desktop/Main Vault/Main/Shards/tools/obsidianlog.mjs" \
  --actor "claude:vault-audit" --op verify --target "(Flint) Distillation/" \
  --result "<counts>" --trigger "vault-audit" \
  --project "/Users/brunojaamaa/Desktop/distillation"
```

Finish with `flint sync`.

## Related

[[(Report) Build Log]] · [[(Report) Folder Audit]] · [[codebase-map-refresh]] ·
[[(Note) The Deleted Student Weights]] · [[(System) Flint Init]] · [[(Map) Master Map]]
