# Sourced by the bash scripts (expects $ROOT). Loads .env for LOCAL runs only,
# never overriding a variable that is already set - an explicit environment
# variable always wins. Cloud routines have no .env.
if [[ -f "$ROOT/.env" ]]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%$'\r'}"
        [[ "$line" =~ ^[[:space:]]*([A-Z_][A-Z0-9_]*)=(.*)$ ]] || continue
        k="${BASH_REMATCH[1]}"
        v="${BASH_REMATCH[2]}"
        v="${v%\"}"
        v="${v#\"}"
        [[ -n "${!k+x}" ]] || export "$k=$v"
    done < "$ROOT/.env"
fi
