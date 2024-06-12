FROM python:3.10.8-slim-buster

# Copy the code directory from the host to /app in the container
ADD ./app /app
ADD ./tests /tests
ADD ./config.py /config.py
ADD ./flask-cards.py /flask-cards.py
ADD ./run.py /run.py

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
# Copy the requirements.txt file into the container
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 3000

# Define environment variable
ENV FLASK_APP=run.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
