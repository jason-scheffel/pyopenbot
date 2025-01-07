.PHONY: help
help:
	@echo "Targets:"
	@echo "  help  - Display this message"
	@echo "  run   - Run main.py"

.PHONY: run
run:
	uv run src/openbot/main.py
