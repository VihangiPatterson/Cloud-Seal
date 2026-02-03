FROM python:3.11-slim

# Create a non-root user with a specific UID between 10000 and 20000 (Choreo requirement)
RUN addgroup --gid 10001 choreogroup && \
    adduser --disabled-password --gecos "" --uid 10001 --gid 10001 choreouser
WORKDIR /home/choreouser/app

# Copy the entire project
COPY . .

# Set permissions
RUN mkdir -p backend/data && chown -R choreouser:choreogroup /home/choreouser/app

# Switch to backend directory for execution
WORKDIR /home/choreouser/app/backend

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

USER 10001

# Expose port 8080 (standard for Choreo)
EXPOSE 8080

# Run the app from the backend directory (ensures 'import config' works)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
