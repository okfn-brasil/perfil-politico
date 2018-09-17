FROM conda/miniconda3

WORKDIR /code

COPY jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py
COPY requirements.txt requirements.txt
RUN apt-get update && \
    apt-get install -y build-essential git libicu-dev && \
    python -m pip --no-cache install -r requirements.txt && \
    python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')" && \
    polyglot download embeddings2.pt ner2.pt && \
    apt-get purge -y build-essential git && \
    rm -rf /var/lib/apt/lists/*

CMD ["jupyter", "notebook", "--no-browser", "--ip", "0.0.0.0", "--allow-root"]
