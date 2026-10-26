#!/usr/bin/env bash
#
# Build the distributable APC framework kit tarball.
#
# Usage:
#   ./build-tarball.sh [OUTPUT_PATH]
#
# Default output: ~/projects/apc-framework-kit.tar.gz
#
# Packages the working tree (tracked files plus untracked non-ignored files),
# so uncommitted edits are included. .git/ and .obsidian/ are always excluded.
# Identical content produces an identical archive. Safe to run from any cwd.

set -euo pipefail

readonly DEFAULT_OUTPUT="$HOME/projects/apc-framework-kit.tar.gz"
readonly PREFIX="apc-framework-kit"

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
output="${1:-$DEFAULT_OUTPUT}"

if [[ "$output" == "-h" || "$output" == "--help" ]]; then
  sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 0
fi

cd "$repo_root"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'error: %s is not a git repository\n' "$repo_root" >&2
  exit 1
fi

output_dir="$(dirname -- "$output")"
mkdir -p -- "$output_dir"
output="$(cd -- "$output_dir" && pwd)/$(basename -- "$output")"

file_list="$(mktemp)"
archive_tmp="$(mktemp --tmpdir="$(dirname -- "$output")" .apc-tarball.XXXXXX.tar.gz)"
cleanup() { rm -f -- "$file_list" "$archive_tmp"; }
trap cleanup EXIT

# Tracked + untracked-but-not-ignored files. Null-delimited for odd names.
git ls-files -z --cached --others --exclude-standard -- \
  ':(exclude).obsidian' > "$file_list"

if [[ ! -s "$file_list" ]]; then
  printf 'error: no files found to package\n' >&2
  exit 1
fi

# Normalize timestamps to the last commit so identical content produces an
# identical archive. Falls back to epoch when the repo has no commits.
mtime="$(git log -1 --format=%ct 2>/dev/null || printf '0')"

tar --null --verbatim-files-from --files-from="$file_list" \
    --sort=name \
    --mtime="@$mtime" \
    --owner=0 --group=0 --numeric-owner \
    --format=gnu \
    --transform="s,^,$PREFIX/," \
    -cf - \
  | gzip -n -9 > "$archive_tmp"

gzip -t -- "$archive_tmp"
mv -f -- "$archive_tmp" "$output"

file_count="$(tr -cd '\0' < "$file_list" | wc -c)"
size="$(du -h -- "$output" | cut -f1)"
sha="$(sha256sum -- "$output" | cut -d' ' -f1)"

printf 'Built %s\n' "$output"
printf '  files:  %s\n' "$file_count"
printf '  size:   %s\n' "$size"
printf '  sha256: %s\n' "$sha"
