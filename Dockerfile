FROM python:3.11-bookworm

COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

CMD ["python", "waldur_metrics/manage.py", "update_limits"]

