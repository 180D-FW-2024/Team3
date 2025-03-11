FROM python:3.11-slim

# Clean up APT cache to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y libpq-dev gcc

# Set working directory
WORKDIR /app

# Copy necessary files (including FlaskExports.sh)
COPY ../. .

# Install dependencies
RUN pip install --no-input --no-cache-dir -r ./app/requirements.txt

# Install system packages
RUN apt-get install -y procps net-tools tzdata sqlite3

# Ensure FlaskExports.sh is executable (optional but good practice)
RUN chmod +x /app/FlaskExports.sh

# Use ENTRYPOINT to source the exports before running Flask
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source /app/FlaskExports.sh && exec quart run --host=0.0.0.0 --port=80"]

# Expose the port
EXPOSE 80