shell:
	pipenv shell
run:
	streamlit main app.py
install:
#	pipenv install
#	pip install --no-cache-dir -r requirements.txt
	pipenv install -r requirements.txt -r requirements-dev.txt
freeze:
	pip freeze > requirements.txt
lock:
	pipenv lock
resolve_dependencies:
	make install & make freeze & make lock

# コードフォーマット
fmt:
	black .
# Lintチェック
lint:
	ruff check .
# 型チェック
check:
	mypy .
# テスト実行
test:
	pytest -v --tb=short --disable-warnings tests/