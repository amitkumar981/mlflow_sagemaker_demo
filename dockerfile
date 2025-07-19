# Base Python image
FROM python:3.11-slim

# Working directory
WORKDIR /opt/ml

# Install OS-level dependencies
RUN apt-get update && apt-get install -y libgomp1 && apt-get clean

# Copy requirements and install Python packages
COPY docker_requirements.txt .
RUN pip install --upgrade pip && pip install -r docker_requirements.txt

# SageMaker requires these folders
RUN mkdir -p /opt/ml/model /opt/ml/input /opt/ml/output /opt/ml/code

# Copy necessary files
COPY src /opt/ml/code/src
COPY model_info.json /opt/ml/code/model_info.json
COPY data/raw/swiggy_sample.csv /opt/ml/code/data/raw/swiggy_sample.csv
COPY serve.py /opt/ml/code/serve.py
COPY monitoring/prod_logger.py /opt/ml/code/monitoring/prod_logger.py

# Switch to code dir (SageMaker uses this during inference)
WORKDIR /opt/ml/code

# Expose port (optional, good for local testing)
EXPOSE 8080

# Define entrypoint for serving
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

# Copy entrypoint
COPY entrypoint.sh /opt/ml/code/entrypoint.sh
RUN chmod +x /opt/ml/code/entrypoint.sh

# Use custom shell entrypoint
ENTRYPOINT ["/opt/ml/code/entrypoint.sh"]







