FROM continuumio/miniconda3

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN echo "Acquire::http::Pipeline-Depth 0;" > /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::BrokenProxy    true;" >> /etc/apt/apt.conf.d/99custom && \
    echo 'Acquire::http::Timeout "300";' > /etc/apt/apt.conf.d/99timeout
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y  --fix-missing \
    python3-venv \
    build-essential \
    && apt-get install -y --no-install-recommends gdal-bin libgdal-dev

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /workspace

RUN python -m venv /workspace/venv
ENV PATH="/workspace/venv/bin:$PATH"
ENV PATH /opt/conda/bin:$PATH

# for install latest GDAL
#RUN conda init bash && \
#    echo ". /root/.bashrc" >> /root/.bashrc && \
#    /bin/bash -c "source /root/.bashrc"
RUN conda install -c conda-forge gdal
ENV GDAL_VERSION=3.7.3
ENV GDAL_CONFIG=/usr/local/bin/gdal-config


COPY ../requirements.txt .
RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/bin/bash"]

