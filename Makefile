RHTEST_HOME := $(PWD)
export RHTEST_HOME
PYTHONPATH := $(RHTEST_HOME)/lib/supports:$(RHTEST_HOME)/lib:$(RHTEST_HOME)/testmodules
export PYTHONPATH
RHTEST_DEBUG := 1
export RHTEST_DEBUG

all:
	@echo "Run it as 'make test'"

test: client web launcher
	@echo "PASSED"

web:
	./bin/rhtest -i int.openshift.redhat.com UI.web.case_138787

client: domain app sshkey

domain:
	./bin/rhtest -R -G -i int.openshift.redhat.com RT.job_related.create_domain

app:
	./bin/rhtest -R -G -i int.openshift.redhat.com RT.cartridge.embed_mysql_to_jboss

sshkey:
	./bin/rhtest -R -G -i int.openshift.redhat.com RT.client.add_remove_mult_ssh_keys
	./bin/rhtest -R -G -i int.openshift.redhat.com RT.client.add_sshkey
	./bin/rhtest -R -G -i int.openshift.redhat.com RT.client.delete_ssh_key_per_keyname
	./bin/rhtest -R -G -i int.openshift.redhat.com RT.client.rhc_wrapper_ssh


launcher:
	#./bin/launcher.py --debug -g quickstart -A int.openshift.redhat.com

setup:
	@echo "TODO"

update_client:
	./bin/update_rhc_client.py

doc:
	make -f Makefile.sphinx html upload
