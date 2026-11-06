set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# List available commands.
default:
    @just --list

# Lint jank sources with the project's Clojure compatibility configuration.
lint:
    bash scripts/lint.sh

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

# Build and check raylib linking without opening a window.
smoke: build
    ./target/jacobo --smoke

# Remove generated build artifacts.
clean:
    rm -rf target
