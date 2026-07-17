.PHONY: install install-dev doctor test lint format

install:
	conda env update -n quant -f environment.yml

install-dev:
	conda run -n quant pip install -e ".[dev]"

doctor:
	conda run -n quant python -m etf_pool doctor

test:
	conda run -n quant pytest

lint:
	conda run -n quant ruff check .
	conda run -n quant mypy src

format:
	conda run -n quant ruff format .
	conda run -n quant ruff check --fix .
