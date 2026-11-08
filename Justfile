set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# List available commands.
default:
    @just --list

# Lint jank sources with the project's Clojure compatibility configuration.
lint:
    bash scripts/lint.sh

# Format jank sources and tests (requires cljfmt).
fmt:
    cljfmt fix --file-pattern '\.jank$' src tests hallo.jank

# Check the compiler and raylib installation.
doctor:
    jank check-health
    @bash scripts/jank.sh --help >/dev/null

# Compile a native executable to target/jacobo.
build:
    bash scripts/jank.sh --target-dir target --name jacobo compile jacobo.main

# Run the sketch through jank (Escape closes the window).
run:
    bash scripts/jank.sh run-main jacobo.main

# Reload initial-state and draw! independently on save; R resets sketch state.
dev:
    bash scripts/jank.sh run-main jacobo.live

# Check reload-on-save behavior without opening a window.
test-live:
    mkdir -p target
    bash scripts/jank.sh run tests/live_reload.jank

# Open the sketch with an editor-connectable nREPL (0 selects a free port).
repl port="0":
    bash scripts/jank.sh --port {{quote(port)}} run-main jacobo.dev

# Build and check raylib linking without opening a window.
smoke: build
    ./target/jacobo --smoke

# Remove generated build artifacts.
clean:
    rm -rf target
