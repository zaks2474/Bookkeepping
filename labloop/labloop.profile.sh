# Lab Loop PATH configuration
# ============================
# Add this to your ~/.bashrc or ~/.zshrc:
#
#   source /home/zaks/bookkeeping/labloop/labloop.profile.sh
#
# Or add this line:
#
#   export PATH="$PATH:/home/zaks/bookkeeping/labloop/bin"

# Add npm global binaries (claude, codex)
# Prefer user-owned npm global bin; keep root path as fallback.
if [[ -d "/home/zaks/.npm-global/bin" ]]; then
  export PATH="/home/zaks/.npm-global/bin:$PATH"
fi
if [[ -d "/root/.npm-global/bin" ]]; then
  export PATH="$PATH:/root/.npm-global/bin"
fi

# Add labloop binaries
export PATH="$PATH:/home/zaks/bookkeeping/labloop/bin"

# Optional aliases
alias ll='labloop'
alias llnew='labloop new'
alias llrun='labloop run'
alias llstatus='labloop status'
alias lllist='labloop list'
