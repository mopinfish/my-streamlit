shell:
	pipenv shell
run:
	streamlit run app.py
install:
#	pipenv install
#	pip install --no-cache-dir -r requirements.txt
	pipenv install -r requirements.txt
freeze:
	pip freeze > requirements.txt
lock:
	pipenv lock
