# ---------------------------------------------------------
# [  INCLUDES  ]
# override to whatever works on your system

PIPENV := pipenv

include ./Makefile.in.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# override to whatever works on your system

APPLICATION := main.asgi:app
ENTRYPOINT := $(PYTHON) $(DIR_SRC)/main/runner.py

include ./Makefile.targets.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# keep your targets here

.PHONY: migrate
migrate::
	$(MANAGEMENT) migrations --apply

