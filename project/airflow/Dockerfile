# Base image
FROM apache/airflow:3.0.0

# Definir variables de entorno
ENV AIRFLOW_HOME=/opt/airflow
#ENV CLOUD_SDK_VERSION=322.0.0
ENV CLOUD_SDK_VERSION=470.0.0
ENV GCLOUD_HOME=/home/google-cloud-sdk
ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"

# Cambiar a root para instalaciones del sistema
USER root

# Instalar paquetes del sistema
RUN apt-get update -qq && apt-get install -y \
    vim \
    curl \
    gnupg \
    apt-transport-https \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Cloud SDK
RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
        --bash-completion=false \
        --path-update=false \
        --usage-reporting=false \
        --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version

# Copiar y usar requirements.txt (como airflow)
COPY requirements.txt /

# Crear carpeta de trabajo y copiar scripts
WORKDIR $AIRFLOW_HOME
COPY scripts scripts
RUN chmod +x scripts

# Volver al usuario airflow para pip install
USER airflow

RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres \
    apache-airflow-providers-amazon \
    apache-airflow-providers-google

RUN pip install --no-cache-dir -r /requirements.txt

# Establecer usuario final
USER ${AIRFLOW_UID}
