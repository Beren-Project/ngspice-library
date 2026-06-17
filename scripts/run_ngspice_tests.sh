#!/usr/bin/env sh
set -eu

cm=${NGFUNCS_CM:-build/ngfuncs.cm}

if [ ! -f "$cm" ]; then
    echo "Missing $cm" >&2
    echo "Build ngfuncs.cm from an ngspice source tree, then copy it to build/ngfuncs.cm." >&2
    exit 2
fi

mkdir -p tests/output

status=0
for deck in tests/test_*.cir; do
    log="tests/output/$(basename "$deck" .cir).log"
    echo "running $deck"
    if ngspice -b "$deck" > "$log" 2>&1 && grep -q "TEST PASS" "$log"; then
        echo "pass $deck"
    else
        echo "fail $deck; see $log" >&2
        status=1
    fi
done

exit "$status"

