NGSPICE_SRC ?= src/ngspice
NGFUNCS_CM ?= build/ngfuncs.cm

.PHONY: help test check-stock clean install-source build-cm

help:
	@printf '%s\n' \
		'Targets:' \
		'  make build-cm                     Build build/ngfuncs.cm from vendored src/ngspice.' \
		'  make test                         Run custom-model regression tests (requires build/ngfuncs.cm).' \
		'  make check-stock                  Run smoke tests that need only stock ngspice.' \
		'  make install-source               Copy code-model sources into $(NGSPICE_SRC).' \
		'  make clean                        Remove local test logs.'

test:
	@scripts/run_ngspice_tests.sh

check-stock:
	@ngspice -b tests/stock_ddt_smoke.cir

install-source:
	@scripts/install_into_ngspice_source.sh "$(NGSPICE_SRC)"

build-cm: install-source
	@$(MAKE) -C "$(NGSPICE_SRC)/src/xspice/icm" cm=ngfuncs ngfuncs/ngfuncs.cm
	@mkdir -p build
	@cp "$(NGSPICE_SRC)/src/xspice/icm/ngfuncs/ngfuncs.cm" "$(NGFUNCS_CM)"

clean:
	@rm -rf tests/output
