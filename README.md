# Jacobo

A generative sketch library written in [jank](https://book.jank-lang.org/),
a Clojure dialect with native C++ interop, and rendered with
[raylib](https://www.raylib.com/).

The first milestone is a working native build and a simple sketch: lavender
circles, squares, and small clusters on a near-black canvas. The reference
sets the direction for richer packing, capsules, and variation in scale.

![Visual reference](docs/reference.png)

## Setup

On Apple Silicon macOS with Homebrew:

```sh
brew install jank-lang/jank/jank just raylib
brew install borkdude/brew/clj-kondo
just doctor
just lint
just build
just smoke
just run
```

For live editing, run `just dev` instead of `just run`, then save changes in
Zed as described in [Live reload in Zed](#live-reload-in-zed).
The optional [nREPL workflow](#live-sketch-repl) remains available with `just repl`.

`just build` produces `target/jacobo`; run it directly to open the sketch.
Press Escape or close the window to exit. `just smoke` builds and checks native
linking without opening a window. `just clean` removes build outputs.

The scaffold uses the jank CLI directly, with no JVM or Leiningen dependency.
For another raylib installation, set `RAYLIB_PREFIX` to a prefix containing
`include/raylib.h` and `lib/`. Other platforms are not yet verified.

## Layout

- `src/jacobo/sketch.jank` — reusable rendering functions.
- `src/jacobo/main.jank` — window lifecycle and entry point.
- `src/jacobo/dev.jank` — development nREPL and recoverable drawing callback.
- `scripts/jank.sh` — native include/library discovery and compiler invocation.
- `AGENTS.md` — mission and contributor workflow.

## Linting

For Zed, the local [Jank extension](extensions/zed-jank/README.md) adds `.jank`
syntax highlighting, bracket matching, indentation, and a definition outline.
Install it using **zed: install dev extension**, selecting `extensions/zed-jank`.

`just lint` explicitly discovers `.jank` files under `src/` and includes
`hallo.jank`, checking them together as Clojure. Directory scans in clj-kondo
currently skip this extension. The setup was verified with clj-kondo 2026.10.26.

`.clj-kondo/config.edn` exempts the native `cpp` namespace from unresolved
namespace warnings. A small hook removes only `:include` clauses from the
linter's view of `ns`; ordinary namespace checks remain enabled. This does
not modify the source or affect compilation.

C++ names, native signatures, and jank-specific type conversions still need
`just build` and runtime verification. Additional jank special forms may need
more hooks as the project grows. Editors must recognize `.jank` as Clojure
and invoke clj-kondo in Clojure mode to use this configuration.

## Live reload in Zed

Run `just dev`, edit `src/jacobo/sketch.jank`, and save. Stop an older sketch
window first so you are looking at the live version. The sketch has two
lifecycle functions in one file:

```clojure
(defn initial-state []
  {:radius 23 :ink [120 2 225 255]})

(defn draw! [state]
  ;; Draw using (:radius state), (:ink state), etc.
  nil)
```

`initial-state` runs after the window opens and returns the state passed to every
`draw!` call. Put colors, dimensions, or seeded composition generation in
`initial-state`. `draw!`'s return value is ignored; use an atom in your state if the
sketch needs mutable animation state.

- Save a change to `initial-state`: reload it and rebuild state, keeping `draw!` compiled.
- Save a change to `draw!`: reload it while preserving the current state.
- Change both: reload both, then rebuild state once.
- Press **R** in the live window to rerun `initial-state` and reset state. Escape closes it.

Only changed lifecycle forms are evaluated, using jank's reader source ranges.
The file is checked every 50 ms and requires two matching reads before reload.
Changes to helper definitions, imports, window dimensions, or other files require
restarting `just dev`. Top-level comments and whitespace between forms do not
trigger recompilation; edits inside a function do.

Reload and state initialization failures keep the previous function bindings and state. Fix
and save again to retry. Initialization side effects (such as native resource allocation
or mutating an existing atom) cannot be rolled back. Runtime drawing errors
are caught so another edit can recover. Keep initialization resource management simple.

All lifecycle calls run on the rendering thread. Initial-state edits still compile the
small `initial-state` function; they avoid recompiling the larger drawing function.
Drawing-code edits still incur native compilation and can pause the window.
In a local running-window check, an initial-state-only edit took about 136 ms including
compilation and execution, excluding save detection; the drawing function was
preserved. State initialization can take longer as composition generation grows.
`just test-live` checks selective reload, state preservation, reset, and recovery.

## Live sketch REPL

From the project root, launch the sketch and its local nREPL server:

```sh
just repl
```

Keep that process running, then connect your editor's nREPL client to
`127.0.0.1` using the printed port or the project's `.nrepl-port` file.
To request a specific port, launch with:

```sh
just repl 5555
```

This command runs the window and server; it does not show a terminal REPL prompt.

Open `src/jacobo/sketch.jank`, change the geometry in `draw!`, then
evaluate that function in the `jacobo.sketch` namespace. The next frames use
the new definition. Evaluating the whole buffer through nREPL also works.
For example, evaluate this in that namespace to temporarily clear the canvas:

```clojure
(defn draw! [_state]
  (cpp/ClearBackground (cpp/Color 20 10 40 255))
  nil)
```

After evaluating a new `initial-state`, evaluate `(jacobo.dev/request-reset!)` to queue
a state reset on the rendering thread. Re-evaluate the original `draw!` to
restore the pattern. Saving
alone does not reload code. Window dimensions are read when the window opens,
so changes to `width` and `height` require restarting `just repl`.

Raylib drawing and window calls stay on the main thread. Define functions
through nREPL, but do not call `initial-state`, `draw!`, `reset-sketch!`, `run-sketch!`, or raylib graphics
functions directly from the editor's evaluation thread. Ordinary drawing
exceptions are caught so you can fix and re-evaluate a broken function;
`@jacobo.dev/last-error` reports the failure state (native crashes cannot be
recovered this way).

Press Escape, close the window, or evaluate `(jacobo.dev/stop!)` to end the
sketch. Start one REPL per project directory so `.nrepl-port` identifies the
right process. The development server uses jank's bundled nREPL API, verified
with the installed jank 0.1 alpha, and may need updates with future releases.

jank is alpha software; compiler compatibility should be checked against the
installed `jank --help`. See the [jank book](https://book.jank-lang.org/) for
language and C++ interop guidance.
