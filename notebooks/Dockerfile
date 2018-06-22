FROM conda/miniconda3

WORKDIR /code

COPY requirements.txt requirements.txt
RUN python -m pip --no-cache install -r requirements.txt

CMD ["jupyter", "notebook", "--no-browser", "--ip", "0.0.0.0", "--allow-root"]
