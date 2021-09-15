.PHONY : githook
githook: init dependencies

.PHONY : all
all : init dev_dependencies dependencies os package

OS := $(shell uname -s | tr A-Z a-z)
linux_python = /usr/bin/python3
linux_pip = /usr/local/bin/pip3

.PHONY : init
init :
ifeq ($(OS), darwin)
	pip install -r requirements.txt
endif
ifeq ($(OS), linux)
	$(linux_pip) install -r requirements.txt --user
endif

.PHONY : dependencies
dependencies :
ifeq ($(OS), darwin)
	pip install .
endif
ifeq ($(OS), linux)
	$(linux_pip) install . --user
endif

.PHONY : dev_dependencies
dev_dependencies :
ifeq ($(OS), darwin)
	pip install -e ./
endif
ifeq ($(OS), linux)
	$(linux_pip) install -e ./  --user
endif

.PHONY : dev
dev: init dev_dependencies

.PHONY : package
package :
ifeq ($(OS), darwin)
	python setup.py sdist bdist_wheel
endif
ifeq ($(OS), linux)
	$(linux_python) setup.py sdist bdist_wheel
endif

.PHONY : deploy_local
deploy_local: package
	gsutil cp dist/rsyslog_cee*.tar.gz gs://welcome_local/code/rsyslog_cee-0.1.0.tar.gz

.PHONY : deploy_d2
deploy_d2: package
	gsutil cp dist/rsyslog_cee*.tar.gz gs://welcome_d2/code/rsyslog_cee-0.1.0.tar.gz

.PHONY : deploy_beta
deploy_beta: package
	gsutil cp dist/rsyslog_cee*.tar.gz gs://welcome_beta/code/rsyslog_cee-0.1.0.tar.gz

.PHONY : deploy_prod
deploy_prod: package
	gsutil cp dist/rsyslog_cee*.tar.gz gs://welcome_prod/code/rsyslog_cee-0.1.0.tar.gz

.PHONY : deploy_gcs
deploy_gcs: deploy_local deploy_d2 deploy_beta deploy_prod

.PHONY : os
os :
	@echo $(OS)


