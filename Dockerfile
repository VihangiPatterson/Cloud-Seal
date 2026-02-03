FROM python:3.11-slim

# Create a non-root user for security (Choreo best practice)
RUN adduser --disabled-password --gecos "" choreouser
WORKDIR /home/choreouser/app

# Copy requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the entire project (backend and frontend)
COPY . .

# Set permissions for the data directory
RUN mkdir -p backend/data && chown -R choreouser:choreouser /home/choreouser/app

USER choreouser

# Expose port 8080 (standard for Choreo)
EXPOSE 8080

# Run the app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080"]
