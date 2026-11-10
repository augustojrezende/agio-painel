#!/bin/bash
# Agenda a exportação do painel no Mac (launchd).
#
# Dispara quando a pasta dados/tratado do agio-stablecoin muda, ou seja, logo
# depois de `agio calcular` na coleta semanal. Assim o painel sempre lê o ágio
# já recalculado, mesmo que o Mac tenha dormido no horário da coleta.
# Reserva: também roda toda terça às 10h. Se não houver dia novo, não publica.
#
# Instalar:   ./scripts/agendar_mac.sh [pasta do agio-stablecoin]
# Remover:    launchctl unload ~/Library/LaunchAgents/br.agio.painel.plist
#             rm ~/Library/LaunchAgents/br.agio.painel.plist

set -eu
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
ORIGEM="$(cd "${1:-$RAIZ/../agio-stablecoin}" && pwd)"
TRATADO="$ORIGEM/dados/tratado"
PLIST="$HOME/Library/LaunchAgents/br.agio.painel.plist"
PY="$(command -v python3)"
[ -d "$TRATADO" ] || { echo "Pasta não encontrada: $TRATADO"; exit 1; }
mkdir -p "$HOME/Library/LaunchAgents" "$RAIZ/logs"

cat >"$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>br.agio.painel</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PY</string><string>$RAIZ/scripts/exportar.py</string>
    <string>--publicar</string><string>--origem</string><string>$ORIGEM</string>
  </array>
  <key>WorkingDirectory</key><string>$RAIZ</string>
  <key>WatchPaths</key>
  <array><string>$TRATADO</string></array>
  <key>StartCalendarInterval</key>
  <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
  <key>ThrottleInterval</key><integer>300</integer>
  <key>StandardOutPath</key><string>$RAIZ/logs/exportar.log</string>
  <key>StandardErrorPath</key><string>$RAIZ/logs/exportar.log</string>
</dict>
</plist>
PL

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Exportação agendada: quando $TRATADO mudar, e toda terça às 10h como reserva."
echo "Conferir: launchctl list | grep painel"
echo "Log em: $RAIZ/logs/exportar.log"
