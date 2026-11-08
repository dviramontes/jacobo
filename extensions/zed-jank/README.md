# Jank for Zed (local)

A small, declarative Zed extension treating `.jank` files as Clojure syntax,
with additional highlighting for `cpp/…` symbols and `#cpp` reader tags.
No language server, Rust extension code, or jank runtime is required.

Includes bracket pairing, two-space indentation, line comment toggling,
and an outline for namespaces and definitions. Only `.jank` files are
associated with Jank; the existing Clojure extension can stay installed.

## Install locally

1. In Zed's command palette, run **zed: install dev extension**.
2. Select this directory (`extensions/zed-jank`), containing `extension.toml`.
3. Open a `.jank` file. The language selector should say **Jank**.

Zed downloads the pinned Tree-sitter grammar and its WASI build tools on
first installation, so that step needs network access. Nothing is published.
See Zed's [development instructions](https://zed.dev/docs/extensions/developing-extensions).

If a previous `file_types` setting explicitly maps `*.jank` to Clojure,
remove that association or select Jank manually. After changing the extension,
use **Rebuild** on its entry in Zed's Extensions view. Use **zed: open log**
to troubleshoot loading or query errors.

## Scope

The pinned [Clojure grammar](https://github.com/prcastro/tree-sitter-clojure/tree/38b4f8d264248b2fd09575fbce66f7c22e8929d5)
provides parsing, not compiler validation. C++ embedded in `cpp/raw` remains
a string; this version does not inject C++ highlighting into it. There are no
completion, diagnostics, formatting, or nREPL integrations. Use `just lint`
and `just smoke` in Jacobo for source checks.

The language configuration and queries use Zed's documented
[language extension format](https://zed.dev/docs/extensions/languages).
