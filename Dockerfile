FROM continuumio/miniconda3

ADD . .

RUN conda create -n qtEnv
RUN conda init
RUN activate qtEnv
RUN conda install pytest pyqt

CMD ["python", "./src/appMain.py"]