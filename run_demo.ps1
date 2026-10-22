# Mini SQL Compiler — Quickstart PowerShell Helper for Evaluators
# Executes the curated 5-query demonstration showcase

param(
    [switch]$VerboseOutput
)

if ($VerboseOutput) {
    python demo_runner.py --verbose
} else {
    python demo_runner.py $args
}
