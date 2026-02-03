FROM python:3.11-slim

# Create a non-root user with a specific UID between 10000 and 20000 (Choreo requirement)
RUN addgroup --gid 10001 choreogroup && \
    adduser --disabled-password --gecos "" --uid 10001 --gid 10001 choreouser
WORKDIR /home/choreouser/app

# Copy requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the entire project (backend and frontend)
COPY . .

# Set permissions for the data directory
RUN mkdir -p backend/data && chown -R choreouser:choreogroup /home/choreouser/app

USER 10001

# Expose port 8080 (standard for Choreo)
EXPOSE 8080

# Run the app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080"]
