FROM python:3.12-slim

WORKDIR /app

# Install system tools
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Checkov
RUN pip install --no-cache-dir checkov

# Install TFLint
RUN curl -L https://github.com/terraform-linters/tflint/releases/download/v0.64.0/tflint_linux_amd64.zip -o /tmp/tflint.zip \
    && unzip /tmp/tflint.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/tflint \
    && rm /tmp/tflint.zip

# Install Gitleaks
RUN curl -L https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz -o /tmp/gitleaks.tar.gz \
    && tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin gitleaks \
    && chmod +x /usr/local/bin/gitleaks \
    && rm /tmp/gitleaks.tar.gz

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD gunicorn --chdir web app:app --bind 0.0.0.0:${PORT:-10000}