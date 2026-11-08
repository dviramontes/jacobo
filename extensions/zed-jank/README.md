# Jank for Zed (local)

Syntax highlighting and click-to-definition for `.jank` files, with additional
highlighting for `cpp/…` symbols and `#cpp` reader tags. Includes bracket pairing,
two-space indentation, comment toggling, and an outline. The existing Clojure
extension can stay installed.

## Install locally

1. Install Python 3.9+ and clj-kondo, available on Zed's PATH. On macOS:
   `brew install python borkdude/brew/clj-kondo`.
2. Install Rust with rustup (Zed builds the small Rust extension to WebAssembly).
3. In Zed's command palette, run **zed: install dev extension**.
4. Select this directory (`extensions/zed-jank`), containing `extension.toml`.
5. Open a `.jank` file. The language selector should say **Jank**.

For an existing installation, use **Rebuild** in Zed's Extensions view, then
run **editor: restart language server** if needed. Zed downloads the pinned
Tree-sitter grammar and build tools on first installation, requiring network
access. Nothing is published. See Zed's
[development instructions](https://zed.dev/docs/extensions/developing-extensions).

If a `file_types` setting maps `*.jank` to Clojure, remove that association or
select Jank manually. Use **zed: open log** to troubleshoot loading errors.

## Go to definition

Cmd-click a symbol on macOS (Ctrl-click on Linux), or use **Go to Definition**.
For example, in Jacobo, follow `settings/settings` in `sketch.jank` to its
`def` in `settings.jank`.

The bundled `jank-definitions` language server uses clj-kondo's Clojure analysis
with explicit `.jank` filenames. It supports project `def`/`defn` definitions,
namespace aliases, explicit `:refer` imports, namespace requires, and local
bindings, including shadowing. Open buffers take priority over saved files, so
navigation follows unsaved edits. It honors the project's `.clj-kondo` config
and hooks. No jank runtime or nREPL is needed.

The server indexes `.jank` files under workspace roots on demand, skipping
hidden directories, `target`, `node_modules`, and `.venv`. Analysis is cached
until file contents change; the initial lookup can take longer in large projects.
It is intended for small jank projects. `:refer :all`, generated definitions,
external library sources, and native `cpp/…` definitions are not supported.
Analysis uses Clojure semantics, so jank-specific forms may need clj-kondo hooks.

## Scope and checks

This is a definition-only server: no completion, formatting, diagnostics, or
nREPL integrations. Embedded C++ in `cpp/raw` remains a string. The pinned
[Clojure grammar](https://github.com/prcastro/tree-sitter-clojure/tree/38b4f8d264248b2fd09575fbce66f7c22e8929d5)
provides syntax parsing, not compiler validation.

From the Jacobo repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s extensions/zed-jank/server -v
CARGO_TARGET_DIR=target/zed-jank cargo check --manifest-path extensions/zed-jank/Cargo.toml
# After rustup target add wasm32-wasip1:
CARGO_TARGET_DIR=target/zed-jank cargo build --manifest-path extensions/zed-jank/Cargo.toml --target wasm32-wasip1
just lint
just smoke
```

The Rust launcher embeds the Python server, so rebuilding also picks up server
changes. Language server registration follows Zed's
[language extension format](https://zed.dev/docs/extensions/languages).
