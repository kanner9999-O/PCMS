#!/bin/zsh
set -e
cd "${0:A:h}"
export PYTHONPATH="$PWD/src"
if curl --silent --fail http://127.0.0.1:8792/api/datasets >/dev/null; then
  open http://127.0.0.1:8792
  exit 0
fi
(sleep 2; open http://127.0.0.1:8792) &
exec python3 -m pcms serve --p01 --data "$PWD/outputs/p01-user-trial" --port 8792
