# AGENTS.md

Instructions for agents modifying **the APC Framework Kit itself**. This repo
distributes the framework; it is not a project that has adopted it. Do not
apply adopter-project paths (`docs/context/`, `docs/tasks/`, etc.) here.

Read `README.md` and `COLLABORATOR-GUIDE.md` before changing behavior.

## What ships

- `setup-apc-framework.py` — scaffolder that instantiates the kit into a target project.
- `templates/` — source templates, all suffixed `.template`.
- Root docs: `README.md`, `COLLABORATOR-GUIDE.md`, `STANDALONE-ADOPTION-PROMPT.md`.
- `build-tarball.sh` — builds the distributable archive.

## Rules

1. **Preserve template placeholders.** Keep `{{PLACEHOLDER}}` tokens intact when
   editing `templates/`. The scaffolder replaces them; removing or renaming one
   breaks generation.
2. **Keep duplicated docs in sync.** `COLLABORATOR-GUIDE.md` ↔
   `templates/docs/guide/COLLABORATOR-GUIDE.md.template` and
   `STANDALONE-ADOPTION-PROMPT.md` ↔
   `templates/docs/prompts/STANDALONE-ADOPTION-PROMPT.md.template` must not drift.
3. **Test the scaffolder.** After changing `setup-apc-framework.py` or any
   template, run it into a throwaway directory and verify the generated project.
   Never test inside this repo.
4. **Do not commit or push unless the operator asks.**

## Tarball contract

After any change to the kit:

1. Decide whether `build-tarball.sh` needs updating:
   - New shippable file: no change; it is picked up automatically.
   - New file/dir that must NOT ship: add it to the exclusion pathspec.
   - Renamed repo folder or archive prefix: update `PREFIX`.
2. Run `./build-tarball.sh` from the repo root.
3. Report the archive path, file count, size, and SHA-256.

The working tree is packaged, so uncommitted edits are included. `.git/` and
`.obsidian/` are always excluded. See README §8 for details.
