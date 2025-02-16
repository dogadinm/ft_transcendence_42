# Use Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose ports (Daphne runs on 8000)
EXPOSE 8000

# Run migrations and start Daphne server
# CMD ["sh", "-c", "python manage.py makemigrations transcendence && python manage.py migrate && daphne -b 0.0.0.0 -p 8000 ft_transcendence.asgi:application"]
CMD ["sh", "-c", "python manage.py makemigrations transcendence && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
