#!/bin/bash
#
# Session Manager - Main Entry Point
# Manages OpenClaw sessions and sub-agents
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Source utility functions
source "$SCRIPT_DIR/lib/common.sh"

# Command dispatch
case "${1:-}" in
    list|ls)
        shift
        "$SCRIPT_DIR/cmd/list.sh" "$@"
        ;;
    status|st)
        shift
        "$SCRIPT_DIR/cmd/status.sh" "$@"
        ;;
    history|hist)
        shift
        "$SCRIPT_DIR/cmd/history.sh" "$@"
        ;;
    spawn|new|create)
        shift
        "$SCRIPT_DIR/cmd/spawn.sh" "$@"
        ;;
    cleanup|clean)
        shift
        "$SCRIPT_DIR/cmd/cleanup.sh" "$@"
        ;;
    resources|res|top)
        shift
        "$SCRIPT_DIR/cmd/resources.sh" "$@"
        ;;
    watch|monitor)
        shift
        "$SCRIPT_DIR/cmd/watch.sh" "$@"
        ;;
    kill|stop|terminate)
        shift
        "$SCRIPT_DIR/cmd/kill.sh" "$@"
        ;;
    info|details)
        shift
        "$SCRIPT_DIR/cmd/info.sh" "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [[ -z "${1:-}" ]]; then
            show_help
        else
            echo "Unknown command: $1"
            echo ""
            show_help
            exit 1
        fi
        ;;
esac
