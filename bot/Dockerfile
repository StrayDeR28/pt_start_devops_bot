FROM python:3.9
WORKDIR /bot
COPY . .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 1000
CMD ["python", "bot.py"]