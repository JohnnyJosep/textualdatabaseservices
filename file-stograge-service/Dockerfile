FROM continuumio/miniconda3:4.10.3-alpine

WORKDIR /app

ENV TFG_ROOT_FOLDER=/home/fs

# crate conda environment from yaml file
COPY ./environment.yml .
RUN conda install -c conda-forge flask-restful --yes
RUN conda install -c conda-forge flask-apispec --yes
RUN conda env create -f environment.yml

# override default shell and use bash
SHELL ["conda", "run", "-n", "env", "/bin/bash", "-c"]

# activate conda environment and chek if works
# RUN conda activate env
RUN echo "Makin sure flask is installed correctly..."
RUN python -c "import flask"

# run
COPY ./main.py .
ENTRYPOINT ["conda", "run", "-n", "env", "python", "main.py"]

EXPOSE 80