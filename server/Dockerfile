FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy necessary files (including FlaskExports.sh)
COPY ../. .

# Install dependencies
RUN pip install --no-input --no-cache-dir -r requirements.txt

# Install system packages
RUN apt-get update && apt-get install -y procps net-tools

# Ensure FlaskExports.sh is executable (optional but good practice)
RUN chmod +x /app/FlaskExports.sh

# Use ENTRYPOINT to source the exports before running Flask
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source /app/FlaskExports.sh && exec flask run --host=0.0.0.0 --port=5001"]

# Expose the Flask port
EXPOSE 5001