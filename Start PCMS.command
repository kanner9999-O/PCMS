#!/bin/zsh
cd "${0:A:h}"
export PYTHONPATH="$PWD/src"
if /usr/bin/curl -sf http://127.0.0.1:8787/api/state >/dev/null; then
  /usr/bin/open http://127.0.0.1:8787
else
  (sleep 2; /usr/bin/open http://127.0.0.1:8787) &
  python3 -m pcms serve
fi
