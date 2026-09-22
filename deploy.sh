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
# Ensure the installed wrapper points to this project root (avoid looking for main.py under $HOME/.local)
sed -i "s|PROJECT_ROOT=.*|PROJECT_ROOT=\"$SCRIPT_DIR\"|" "$HOME/.local/bin/lazyopen" || true

# Install completion and lazylist to user-local share so deployments are relocatable
echo "[1.1/3] Installing completion and list to ~/.local/share/lazyopen..."
SHARE_DIR="$HOME/.local/share/lazyopen"
mkdir -p "$SHARE_DIR"
cp -f "$COMPLETION_DIR/lazyopen-completion.bash" "$SHARE_DIR/" 2>/dev/null || true
cp -f "$COMPLETION_DIR/lazyopen-completion.zsh" "$SHARE_DIR/" 2>/dev/null || true
# When installing the completion scripts, patch them so their default
# `list_file` points to this project's `lazylist.txt` (keeps completion
# consistent with the deployed project path even if the share dir is moved).
if [ -f "$SHARE_DIR/lazyopen-completion.bash" ]; then
  sed -i "s|local list_file=.*|local list_file=\"$SCRIPT_DIR/lazylist.txt\"|" "$SHARE_DIR/lazyopen-completion.bash" || true
fi
if [ -f "$SHARE_DIR/lazyopen-completion.zsh" ]; then
  sed -i "s|local list_file=.*|local list_file=\"$SCRIPT_DIR/lazylist.txt\"|" "$SHARE_DIR/lazyopen-completion.zsh" || true
fi
# Do not copy project's lazylist.txt into the share directory.
# Keep completions installed in the share dir but have them reference the
# project's lazylist path (patched earlier). Preserve read permissions.
chmod -R a+r "$SHARE_DIR" || true

echo "[2/3] Installing shell completion..."
COMPLETION_FILE="$SHARE_DIR/lazyopen-completion.bash"
MARKER="# LazyOpen shell completion"
if [ -f "$HOME/.bashrc" ] && grep -Fq "$COMPLETION_FILE" "$HOME/.bashrc"; then
  # Source the completion from the user-local share directory
  echo "LazyOpen completion already installed in ~/.bashrc"
else
  if grep -Fq "$MARKER" "$HOME/.bashrc"; then
    # Update the existing completion line
    echo "Updating LazyOpen completion in ~/.bashrc"
    sed -i "/$MARKER/,+3d" "$HOME/.bashrc"
  fi
  printf '\n%s\nif [ -f "%s" ]; then\n  . "%s"\nfi\n' \
    "$MARKER" "$COMPLETION_FILE" "$COMPLETION_FILE" >> "$HOME/.bashrc"
  echo "LazyOpen completion installed in ~/.bashrc"
fi

if [ -f "$HOME/.zshrc" ] && ! grep -Fq 'lazyopen-completion.zsh' "$HOME/.zshrc"; then
  printf '\n# LazyOpen shell completion\nif [ -f "%s/lazyopen-completion.zsh" ]; then\n  . "%s/lazyopen-completion.zsh"\nfi\n' "$SHARE_DIR" "$SHARE_DIR" >> "$HOME/.zshrc"
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
