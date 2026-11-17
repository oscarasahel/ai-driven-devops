# Jenkins con las herramientas del pipeline. Versiones de herramientas fijadas.
FROM jenkins/jenkins:2.580.2-lts-jdk21@sha256:74401de6a6f92e1afe1b02d1c8e3d0c33f263bfb5275dd8813f9150355f2367b

USER root
ARG CHECKOV_VERSION=3.2.255
ARG AWSCLI_VERSION=2.22.0

RUN apt-get update \
 && apt-get install -y --no-install-recommends unzip curl ca-certificates python3 python3-venv git jq \
 && rm -rf /var/lib/apt/lists/*

# Terraform, TFLint y Trivy se copian de las imágenes oficiales con versión fijada (binarios estáticos).
# Las descargas directas de las releases de Trivy devolvían 404 al construir (2026-11-16).
COPY --from=hashicorp/terraform:1.9.8 /bin/terraform /usr/local/bin/terraform
COPY --from=ghcr.io/terraform-linters/tflint:v0.53.0 /usr/local/bin/tflint /usr/local/bin/tflint
COPY --from=aquasec/trivy:0.58.1 /usr/local/bin/trivy /usr/local/bin/trivy

RUN curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWSCLI_VERSION}.zip" -o /tmp/awscli.zip  && unzip -q /tmp/awscli.zip -d /tmp && /tmp/aws/install && rm -rf /tmp/aws /tmp/awscli.zip

# Checkov 3.2.x depende de rustworkx 0.13, sin ruedas para Python 3.13 (el de la imagen base): se usa Python 3.12 aislado con uv.
RUN python3 -m venv /opt/uv && /opt/uv/bin/pip install --no-cache-dir uv  && UV_PYTHON_INSTALL_DIR=/opt/python /opt/uv/bin/uv venv --python 3.12 /opt/checkov  && VIRTUAL_ENV=/opt/checkov /opt/uv/bin/uv pip install --no-cache "checkov==${CHECKOV_VERSION}"  && ln -s /opt/checkov/bin/checkov /usr/local/bin/checkov && checkov --version

USER jenkins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
    CASC_JENKINS_CONFIG=/usr/share/jenkins/casc
COPY casc/ /usr/share/jenkins/casc/
