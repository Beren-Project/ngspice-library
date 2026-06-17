.PHONY: help test check-stock clean install-source

help:
	@printf '%s\n' \
		'Targets:' \
		'  make test                         Run custom-model regression tests (requires build/ngfuncs.cm).' \
		'  make check-stock                  Run smoke tests that need only stock ngspice.' \
		'  make install-source NGSPICE_SRC=  Copy code-model sources into an ngspice source tree.' \
		'  make clean                        Remove local test logs.'

test:
	@scripts/run_ngspice_tests.sh

check-stock:
	@ngspice -b tests/stock_ddt_smoke.cir

install-source:
	@test -n "$(NGSPICE_SRC)" || { echo 'Set NGSPICE_SRC=/path/to/ngspice-source'; exit 2; }
	@scripts/install_into_ngspice_source.sh "$(NGSPICE_SRC)"

clean:
	@rm -rf tests/output

