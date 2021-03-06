FROM ubuntu:18.04

ENV SHELL /bin/bash
ENV DEBIAN_FRONTEND noninteractive
ENV HOME /workspace
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN sed -i 's/archive.ubuntu.com/tw.archive.ubuntu.com/g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    python3 \
    python3-pip \
    python3-setuptools \
    vim \
    wget \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install wheel \
                 pytest \
                 pexpect \
                 tensorflow==1.14.0

COPY . /build/
# build & install mlsteam_cli
RUN cd /build && \
    python3 setup.py bdist_wheel && \
    pip3 install dist/mlsteam-*

COPY tests /workspace/tests
WORKDIR /workspace
RUN cd /workspace && \
    mkdir example && \
    cd example && \
    git clone https://github.com/myelintek/cifar10_estimator.git && \
    python3 /workspace/example/cifar10_estimator/generate_cifar10_tfrecords.py --data-dir=/workspace/cifar10
