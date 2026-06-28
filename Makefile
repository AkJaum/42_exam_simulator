PYTHON ?= python3

.PHONY: run check clean

run:
	bash start_exam.sh

check:
	$(PYTHON) -m compileall simulator
	@find questions -name meta.json -print | sort | while read -r meta; do \
		$(PYTHON) -m json.tool "$$meta" >/dev/null || exit 1; \
	done
	@find questions -path '*/tests/test.sh' -print | sort | while read -r test_script; do \
		bash -n "$$test_script" || exit 1; \
	done

clean:
	find . -mindepth 1 -maxdepth 1 -type d -name 'exam_*_*' -exec rm -rf {} +
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*.tmp' \) -delete
	rm -rf .coverage htmlcov
