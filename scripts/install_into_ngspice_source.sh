#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 /path/to/ngspice-source" >&2
    exit 2
fi

src_root=$1
icm_dir="$src_root/src/xspice/icm"

if [ ! -d "$icm_dir" ]; then
    echo "not an ngspice source tree: missing $icm_dir" >&2
    exit 2
fi

dest="$icm_dir/ngfuncs"
mkdir -p "$dest"
cp -R src/xspice/icm/ngfuncs/. "$dest/"

for makefile in "$icm_dir/GNUmakefile" "$icm_dir/GNUmakefile.in"; do
    if [ -f "$makefile" ] && ! grep -Eq '(^|[[:space:]])ngfuncs($|[[:space:]])' "$makefile"; then
        tmp="${makefile}.ngfuncs.tmp"
        sed '0,/^CMDIRS[[:space:]]*=/{s/^CMDIRS[[:space:]]*=.*/& ngfuncs/}' "$makefile" > "$tmp"
        mv "$tmp" "$makefile"
    fi
done

echo "Installed ngfuncs source into $dest"
echo "Now run: make build-cm"
