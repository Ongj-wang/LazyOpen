_lazyopen_complete() {
  local cur prev cword
  _init_completion || return

  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD - 1]}"

  case "$prev" in
    -open|-folder|-del)
      local script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
      local list_file="${LAZYOPEN_LIST_FILE:-$(cd -- "$script_dir/.." && pwd)/lazylist.txt}"
      if [[ -f "$list_file" ]]; then
        local names=()
        while IFS='|' read -r name _; do
          if [[ -n "$name" ]]; then
            names+=("$name")
          fi
        done < "$list_file"
        COMPREPLY=( $(compgen -W "${names[*]}" -- "$cur") )
      fi
      ;;
    *)
      COMPREPLY=( $(compgen -W "-open -folder -del -list -add -help" -- "$cur") )
      ;;
  esac
}

complete -F _lazyopen_complete lazyopen lazyopen.exe
