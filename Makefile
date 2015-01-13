########################################################

# Makefile for re-client
#
# useful targets (not all implemented yet!):
#   make clean               -- Clean up garbage
#   make pyflakes, make pep8 -- source code checks
#   make test ----------------- run all unit tests (export LOG=true for /tmp/ logging)
#   make ci ------------------- Execute CI steps (for travis or jenkins)

########################################################

# > VARIABLE = value
#
# Normal setting of a variable - values within it are recursively
# expanded when the variable is USED, not when it's declared.
#
# > VARIABLE := value
#
# Setting of a variable with simple expansion of the values inside -
# values within it are expanded at DECLARATION time.

########################################################

# This doesn't evaluate until it's called. The -D argument is the
# directory of the target file ($@), kinda like `dirname`.
ASCII2MAN = a2x -D $(dir $@) -d manpage -f manpage $<
MANPAGES := docs/man/man1/re-client.1
NAME := re-client

RPMSPECDIR := contrib/rpm
RPMSPEC := $(RPMSPECDIR)/re-client.spec
TESTPACKAGE := reclient
SHORTNAME := reclient

# To force a rebuild of the docs run 'touch VERSION && make docs'
docs: $(MANPAGES)

# Regenerate %.1.asciidoc if %.1.asciidoc.in has been modified more
# recently than %.1.asciidoc.
%.1.asciidoc: %.1.asciidoc.in VERSION
	sed "s/%VERSION%/$(VERSION)/" $< > $@

# Regenerate %.1 if %.1.asciidoc or VERSION has been modified more
# recently than %.1. (Implicitly runs the %.1.asciidoc recipe)
%.1: %.1.asciidoc
	$(ASCII2MAN)

sdist: clean
	python setup.py sdist

tests: unittests pep8 pyflakes
	:

coverage:
	EDITOR=emacs nosetests -v --with-cover --cover-min-percentage=80 --cover-package=$(SHORTNAME) --cover-html test/

unittests:
	@echo "#############################################"
	@echo "# Running Unit Tests"
	@echo "#############################################"
	EDITOR=emacs nosetests -v

clean:
	@find . -type f -regex ".*\.py[co]$$" -delete
	@find . -type f \( -name "*~" -or -name "#*" \) -delete
	@rm -fR build dist rpm-build MANIFEST htmlcov .coverage re_client.egg-info  re-clientenv

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	pep8 --ignore=E501,E121,E124 src/$(SHORTNAME)/

pyflakes:
	@echo "#############################################"
	@echo "# Running Pyflakes Sanity Tests"
	@echo "# Note: most import errors may be ignored"
	@echo "#############################################"
	-pyflakes src/$(SHORTNAME)

rpmcommon: sdist
	@mkdir -p rpm-build
	@cp dist/*.gz rpm-build/

srpm: rpmcommon
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir $(RPMSPECDIR)" \
	--define "_sourcedir %{_topdir}" \
	-bs $(RPMSPEC)
	@echo "#############################################"
	@echo "$(NAME) SRPM is built:"
	@find rpm-build -maxdepth 2 -name '$(NAME)*src.rpm' | awk '{print "    " $$1}'
	@echo "#############################################"

rpm: rpmcommon
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir $(RPMSPECDIR)" \
	--define "_sourcedir %{_topdir}" \
	-ba $(RPMSPEC)
	@echo "#############################################"
	@echo "$(NAME) RPMs are built:"
	@find rpm-build -maxdepth 2 -name '$(NAME)*.rpm' | awk '{print "    " $$1}'
	@echo "#############################################"

virtualenv:
	@echo "#############################################"
	@echo "# Creating a virtualenv"
	@echo "#############################################"
	virtualenv $(NAME)env
	. $(NAME)env/bin/activate && pip install -r requirements.txt
	. $(NAME)env/bin/activate && pip install pep8 nose coverage mock

#       If there are any special things to install do it here
#       . $(NAME)env/bin/activate && INSTALL STUFF

ci-unittests:
	@echo "#############################################"
	@echo "# Running Unit Tests in virtualenv"
	@echo "#############################################"
	. $(NAME)env/bin/activate && nosetests -v --with-cover --cover-min-percentage=80 --cover-package=$(TESTPACKAGE) --cover-html test/

ci-list-deps:
	@echo "#############################################"
	@echo "# Listing all pip deps"
	@echo "#############################################"
	. $(NAME)env/bin/activate && pip freeze

ci-pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests in virtualenv"
	@echo "#############################################"
	. $(NAME)env/bin/activate && pep8 --ignore=E501,E121,E124 src/$(SHORTNAME)/


ci: clean virtualenv ci-list-deps ci-pep8 ci-unittests
	:
