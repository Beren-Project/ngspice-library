#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 /path/to/ngspice-source" >&2
    exit 2
fi

src_root=$1
icm_dir="$src_root/src/xspice/icm"
devdefs="$src_root/src/include/ngspice/devdefs.h"
write_ifs="$src_root/src/xspice/cmpp/writ_ifs.c"

if [ ! -d "$icm_dir" ]; then
    echo "not an ngspice source tree: missing $icm_dir" >&2
    exit 2
fi

if [ ! -f "$devdefs" ] || [ ! -f "$write_ifs" ]; then
    echo "not an ngspice source tree: missing XSPICE build headers/generator" >&2
    exit 2
fi

dest="$icm_dir/ngfuncs"
mkdir -p "$dest"
cp -R src/xspice/icm/ngfuncs/. "$dest/"

makefile="$icm_dir/GNUmakefile.in"
if [ -f "$makefile" ] && ! grep -Eq '(^|[[:space:]])ngfuncs($|[[:space:]])' "$makefile"; then
    tmp="${makefile}.ngfuncs.tmp"
    sed '0,/^CMDIRS[[:space:]]*=/{s/^CMDIRS[[:space:]]*=.*/& ngfuncs/}' "$makefile" > "$tmp"
    mv "$tmp" "$makefile"
fi

if grep -q 'int \*DEVinstSize' "$devdefs" && \
   grep -q 'DEVbindCSC)(GENmodel' "$devdefs" && \
   perl -0ne 'exit(/DEVinstSize.*#ifdef KLU/s ? 0 : 1)' "$devdefs"; then
    perl -0pi -e 's/    int \*DEVinstSize;    \/\* size of an instance \*\/\n    int \*DEVmodSize;     \/\* size of a model \*\/\n\n#ifdef KLU\n    int \(\*DEVbindCSC\)\(GENmodel \*, CKTcircuit \*\);\n        \/\* routine to convert Sparse linked list to Real CSC array \*\/\n    int \(\*DEVbindCSCComplex\)\(GENmodel \*, CKTcircuit \*\);\n        \/\* routine to convert Real CSC array to Complex CSC array \*\/\n    int \(\*DEVbindCSCComplexToReal\)\(GENmodel \*, CKTcircuit \*\);\n        \/\* routine to convert Complex CSC array to Real CSC array \*\/\n#endif\n/#ifdef KLU\n    int (*DEVbindCSC)(GENmodel *, CKTcircuit *);\n        \/* routine to convert Sparse linked list to Real CSC array *\/\n    int (*DEVbindCSCComplex)(GENmodel *, CKTcircuit *);\n        \/* routine to convert Real CSC array to Complex CSC array *\/\n    int (*DEVbindCSCComplexToReal)(GENmodel *, CKTcircuit *);\n        \/* routine to convert Complex CSC array to Real CSC array *\/\n#endif\n\n    int *DEVinstSize;    \/* size of an instance *\/\n    int *DEVmodSize;     \/* size of a model *\/\n/s' "$devdefs"
fi

if grep -q '"    \.DEVbindCSC = MIFbindCSC' "$write_ifs"; then
    perl -0pi -e 's/"    \.DEVbindCSC = MIFbindCSC,\\n"\n            "    \.DEVbindCSCComplex = MIFbindCSCComplex,\\n"\n            "    \.DEVbindCSCComplexToReal = MIFbindCSCComplexToReal,\\n"/"    .DEVbindCSC = NULL,\\n"\n            "    .DEVbindCSCComplex = NULL,\\n"\n            "    .DEVbindCSCComplexToReal = NULL,\\n"/s' "$write_ifs"
fi

echo "Installed ngfuncs source into $dest"
echo "Now rebuild ngspice and copy the resulting ngfuncs.cm into this repo's build/ directory."
