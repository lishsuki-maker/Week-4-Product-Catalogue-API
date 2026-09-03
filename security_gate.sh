#!/usr/bin/env bash
set -euo pipefail

log() {
    echo "$*"
}

die() {
    log "$*"
    log "Overall: FAIL"
    exit 1
}

log "Running Hadolint..."

if hadolint Dockerfile; then
    log "Hadolint: PASS"
else
    die "Hadolint: FAIL"
fi

log "Running Trivy-Config..."

if trivy config . --severity CRITICAL,HIGH --exit-code 1; then
    log "Trivy-Config: PASS"
else
    die "Trivy-Config: FAIL"
fi

log "Running Trivy-Fs Scanners..."

if trivy fs . --scanners vuln,secret --severity CRITICAL,HIGH --exit-code 1; then
    log "Trivy-Fs Scanners: PASS"
else
    die "Trivy-Fs Scanners: FAIL"
fi

log "Overall: PASS"
