run:
	streamlit main app.py
install:
	pip3 install -r requirements.txt -r requirements-dev.txt
#freeze:
#	pip3 freeze > requirements.txt
#lock:
#	pipenv lock
#resolve_dependencies:
#	make install & make freeze & make lock

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