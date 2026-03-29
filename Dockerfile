# Use official lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies (ignoring the virtual environment)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Healthcheck to verify the container is running correctly
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the Streamlit application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
