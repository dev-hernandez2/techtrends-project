FROM python:2.7

EXPOSE 3111

WORKDIR /app
COPY techtrends/ .
COPY techtrends/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN python init_db.py

CMD [ "python", "app.py" ]

