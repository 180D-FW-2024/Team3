FROM continuumio/miniconda3

WORKDIR /

COPY / /

RUN conda config --add channels conda-forge

RUN conda env create -f environment.yaml

RUN conda init bash

RUN conda activate Raspitouille

RUN ./flaskexports.sh

RUN flask run