#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LINUX_DIR="$SCRIPT_DIR/linux"
COMPLETION_DIR="$LINUX_DIR/AutoRegistration"

cd "$SCRIPT_DIR"

echo "[1/3] Installing wrapper script to ~/.local/bin..."
mkdir -p "$HOME/.local/bin"
cp -f "$LINUX_DIR/lazyopen" "$HOME/.local/bin/lazyopen"
chmod +x "$HOME/.local/bin/lazyopen"

echo "[2/3] Installing shell completion..."
if [ -f "$HOME/.bashrc" ] && ! grep -Fq 'lazyopen-completion.bash' "$HOME/.bashrc"; then
  printf '\n# LazyOpen shell completion\nif [ -f "%s/lazyopen-completion.bash" ]; then\n  . "%s/lazyopen-completion.bash"\nfi\n' "$COMPLETION_DIR" "$COMPLETION_DIR" >> "$HOME/.bashrc"
fi

if [ -f "$HOME/.zshrc" ] && ! grep -Fq 'lazyopen-completion.zsh' "$HOME/.zshrc"; then
  printf '\n# LazyOpen shell completion\nif [ -f "%s/lazyopen-completion.zsh" ]; then\n  . "%s/lazyopen-completion.zsh"\nfi\n' "$COMPLETION_DIR" "$COMPLETION_DIR" >> "$HOME/.zshrc"
fi

echo "[3/3] Finalizing PATH..."
if ! grep -Fq '$HOME/.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
fi
if ! grep -Fq '$HOME/.local/bin' "$HOME/.zshrc" 2>/dev/null; then
  printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.zshrc"
fi

echo "Deployment complete. Open a new shell or run:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo "  source ~/.bashrc  # or source ~/.zshrc"
