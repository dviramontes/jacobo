# Jacobo

## Mission

Build a generative sketch library in [jank](https://book.jank-lang.org/),
a Clojure dialect with native C++ interop, using raylib for rendering.
The visual reference is a dense field of lavender outlines on near-black:
mostly touching circles, interrupted by squares, capsules, and clusters of
smaller shapes. Work toward reproducible compositions with varied scale and
local density. The initial scaffold is only a starting sketch.

## Project layout

- `src/jacobo/sketch.jank`: drawing functions reusable by sketches.
- `src/jacobo/main.jank`: window lifecycle and executable entry point.
- `Justfile`: development and native build commands.
- `docs/reference.png`: original visual direction.
- `hallo.jank`: existing hello-world experiment; preserve it.

## Workflow

- Run `just` to list recipes, `just doctor` to check prerequisites.
- Use `just run` for development and `just build` for a native executable.
- Run `just smoke` after changes to verify native linking without a window.
- Run `just lint` after source changes. clj-kondo checks Clojure forms; jank
  remains responsible for native symbols, types, and interop correctness.
- Build artifacts belong in `target/` and must stay untracked.
- Consult the jank book and installed `jank --help` before assuming JVM
  Clojure features or compiler options work; jank is alpha software.
- Keep composition logic in jank. Use C++ only where native interop needs it.
- Separate drawing from window lifecycle. Keep future random generation seeded.
- For visual changes, launch the sketch and inspect it when a display is available.
- Keep this first step small; add dependencies and abstractions as needed.
