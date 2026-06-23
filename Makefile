NGSPICE_SRC ?= src/ngspice
NGFUNCS_CM ?= build/ngfuncs.cm
TEST_REPORT ?= tests/output/report/index.html

.PHONY: help test test-report check-stock clean install-source build-cm

help:
	@printf '%s\n' \
		'Targets:' \
		'  make build-cm                     Build build/ngfuncs.cm from vendored src/ngspice.' \
		'  make test                         Run custom-model regression tests and write an HTML report.' \
		'  make test-report                  Same as make test; report path is $(TEST_REPORT).' \
		'  make check-stock                  Run smoke tests that need only stock ngspice.' \
		'  make install-source               Copy code-model sources into $(NGSPICE_SRC).' \
		'  make clean                        Remove local test logs.'

test: test-report

test-report:
	@scripts/make_test_report.py --cm "$(NGFUNCS_CM)" --output "$(TEST_REPORT)"

check-stock:
	@ngspice -b tests/stock_ddt_smoke.cir
	@ngspice -b tests/stock_comparator_smoke.cir

install-source:
	@scripts/install_into_ngspice_source.sh "$(NGSPICE_SRC)"

build-cm: install-source
	@$(MAKE) -C "$(NGSPICE_SRC)/src/xspice/icm" cm=ngfuncs ngfuncs/ngfuncs.cm
	@mkdir -p build
	@cp "$(NGSPICE_SRC)/src/xspice/icm/ngfuncs/ngfuncs.cm" "$(NGFUNCS_CM)"

clean:
	@rm -rf tests/output
