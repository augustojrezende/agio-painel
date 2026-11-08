#!/bin/bash
# Agenda a exportação semanal do painel no Mac (launchd): toda segunda às 21h,
# uma hora depois da coleta do agio-stablecoin (segunda, 20h).
# Se o Mac estiver dormindo nesse horário, roda quando ele acordar.
#
# Instalar:   ./scripts/agendar_mac.sh
# Remover:    launchctl unload ~/Library/LaunchAgents/br.agio.painel.plist
#             rm ~/Library/LaunchAgents/br.agio.painel.plist

set -eu
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/br.agio.painel.plist"
PY="$(command -v python3)"
mkdir -p "$HOME/Library/LaunchAgents" "$RAIZ/logs"

cat >"$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>br.agio.painel</string>
  <key>ProgramArguments</key>
  <array><string>$PY</string><string>$RAIZ/scripts/exportar.py</string><string>--publicar</string></array>
  <key>WorkingDirectory</key><string>$RAIZ</string>
  <key>StartCalendarInterval</key>
  <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$RAIZ/logs/exportar.log</string>
  <key>StandardErrorPath</key><string>$RAIZ/logs/exportar.log</string>
</dict>
</plist>
PL

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Exportação agendada: toda segunda às 21h."
echo "Conferir: launchctl list | grep painel"
echo "Log em: $RAIZ/logs/exportar.log"
