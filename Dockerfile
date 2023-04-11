FROM python:3.10-alpine
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt 
EXPOSE 4000
COPY . .
CMD [ "python", "main.py" ]

