#!/usr/bin/env bash
# Pluto the Cat: log check. Usage: ./pluto_check.sh [path/to/BepInEx/LogOutput.log]
# Prints PASS/FAIL lines and exits non-zero on any FAIL. Safe to run while the game is closed.
LOG="${1:-$HOME/.var/app/io.github.ebkr.r2modman/config/r2modmanPlus-local/ETG/profiles/Default/BepInEx/LogOutput.log}"
[ -f "$LOG" ] || { echo "FAIL log not found: $LOG"; exit 2; }
fail=0
chk() { # chk <expect:present|absent> <label> <pattern>
  local n; n=$(grep -c -- "$3" "$LOG")
  if [ "$1" = present ]; then [ "$n" -gt 0 ] && echo "PASS $2 ($n)" || { echo "FAIL $2 (0 matches)"; fail=1; }
  else [ "$n" -eq 0 ] && echo "PASS $2" || { echo "FAIL $2 ($n matches)"; fail=1; }; fi
}
echo "log: $LOG ($(wc -l < "$LOG") lines)"
chk present "plugin loaded"            "Loading \[Pluto The Cat"
chk present "character ready"          "\[Pluto\] Pluto the Cat is ready"
chk absent  "no plugin load failure"   "\[Pluto\] Pluto the Cat failed to load"
chk absent  "no character build fail"  "FAILED to build"
chk absent  "no CharAPI error"         "\[CharAPI\] An error occured"
chk absent  "no altGun null"           "altGun is NULL"
chk absent  "no LateUpdate NRE flood"  "PlayerController..LateUpdate"
chk absent  "no CustomCharacter NRE"   "CustomCharacter.FixedUpdate"
chk absent  "no synergy failures"      "synergy .* not registered"
echo "--- lines to send back ---"
grep -n "\[Pluto\]\|CharAPI\|PlutoTheCat\|nine_lives\|kibble\|wet_food\|synerg" "$LOG" | grep -v "punchout" | head -60
echo "--- punchout names (copy verbatim) ---"
grep "\[Pluto\] punchout" "$LOG" | head -2
[ $fail -eq 0 ] && echo "RESULT: PASS" || echo "RESULT: FAIL"
exit $fail
