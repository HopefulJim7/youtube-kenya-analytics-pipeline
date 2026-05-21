FROM apache/airflow:3.2.1-python3.12

COPY --chown=airflow:0 airflow/requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt
