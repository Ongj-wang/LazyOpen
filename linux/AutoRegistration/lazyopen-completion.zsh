#compdef lazyopen lazyopen.exe

_lazyopen_complete() {
  local -a names
  local script_dir="${${(%):-%N}:h}"
  local list_file="${LAZYOPEN_LIST_FILE:-$(cd -- "$script_dir/.." && pwd)/lazylist.txt}"

  if [[ "$words[CURRENT-1]" == "-open" || "$words[CURRENT-1]" == "-folder" || "$words[CURRENT-1]" == "-del" ]]; then
    if [[ -f "$list_file" ]]; then
      while IFS='|' read -r name _; do
        if [[ -n "$name" ]]; then
          names+=("$name")
        fi
      done < "$list_file"
    fi
    compadd -a names
  else
    compadd -a - "-open" "-folder" "-del" "-list" "-add"
  fi
}

compdef _lazyopen_complete lazyopen lazyopen.exe
