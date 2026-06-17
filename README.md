# ngspice function block helpers

This project provides LTspice-style transient function blocks for ngspice using
custom XSPICE code models plus friendly `.subckt` wrappers.

The initial library targets:

- resettable integration with pulse, rising-edge, or falling-edge reset
- modulo integration
- edge-triggered sample-and-hold
- derivative wrapper around ngspice's built-in `d_dt`
- resettable integration with anti-windup

The local ngspice package supplies the runtime XSPICE libraries, but this
machine's Debian/Ubuntu `ngspice-dev` package does not include `cmpp`, the
code-model preprocessor needed to build a `.cm` library directly from this
workspace. Use an ngspice source tree to compile `ngfuncs.cm`.

## Layout

- `src/xspice/icm/ngfuncs/` - XSPICE code-model library source
- `lib/ngfuncs.lib` - user-facing `.subckt` wrappers
- `examples/` - runnable example decks after `build/ngfuncs.cm` exists
- `tests/` - ngspice regression decks and test runner
- `scripts/` - helper scripts for source-tree installation and checks
- `docs/` - design and usage notes
- `build/` - expected location for generated `ngfuncs.cm`

## Build

1. Get an ngspice source tree matching your installed version when possible.
2. Copy this project library into the source tree:

   ```sh
   scripts/install_into_ngspice_source.sh /path/to/ngspice-source
   ```

   The installer also applies a small compatibility patch for the Ubuntu
   ngspice-45.2 runtime used on this machine: dynamic XSPICE `SPICEdev`
   structures need the KLU callback slots before the instance/model size
   fields, and generated custom models leave those KLU bind callbacks null.

3. Build ngspice from that source tree using its normal configure/make flow.
4. Copy the produced `ngfuncs.cm` into this repository:

   ```sh
   mkdir -p build
   cp /path/to/ngspice-build/src/xspice/icm/ngfuncs/ngfuncs.cm build/ngfuncs.cm
   ```

5. Run the tests:

   ```sh
   make test
   ```

On this machine the working local source tree is `src/ngspice`, and the built
library is copied to `build/ngfuncs.cm`.

## Use

Load the code model before circuit parsing and include the wrapper library:

```spice
.control
pre_codemodel build/ngfuncs.cm
.endc

.include lib/ngfuncs.lib
```

Then instantiate blocks such as:

```spice
XINT in reset out NG_INT_RISE params: ic=0 gain=1 vth=0.5
XMOD in phase NG_INT_MOD params: ic=0 gain=1 modulus=1
XSAMP signal clk held NG_SAMPLE_RISE params: ic=0 vth=0.5
XDDT in slope NG_DDT params: gain=1
```
