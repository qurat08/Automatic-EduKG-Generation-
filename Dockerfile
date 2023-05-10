FROM python:3.7-stretch

RUN pip install --upgrade pip

### Install JAVA
RUN set -eux; \
    curl -Lso /tmp/openjdk.tar.gz https://github.com/AdoptOpenJDK/openjdk10-releases/releases/download/jdk-10.0.2%2B13/OpenJDK10_x64_Linux_jdk-10.0.2%2B13.tar.gz; \
    mkdir -p /opt/java/openjdk; \
    cd /opt/java/openjdk; \
    tar -xf /tmp/openjdk.tar.gz; \
    jdir=$(dirname $(dirname $(find /opt/java/openjdk -name javac))); \
    mv ${jdir}/* /opt/java/openjdk; \
    rm -rf ${jdir} /tmp/openjdk.tar.gz;

ENV JAVA_HOME=/opt/java/openjdk \
    PATH="/opt/java/openjdk/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Download stanfordcorenlp
# RUN wget https://nlp.stanford.edu/software/stanford-corenlp-latest.zip -P /app
# RUN unzip /app/stanford-corenlp-latest.zip
# RUN rm /app/stanford-corenlp-latest.zip

COPY . /app

# Download ELMO config files to auxiliary_data folder
# RUN wget https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_weights.hdf5 -P /app/auxiliary_data
# RUN wget https://s3-us-west-2.amazonaws.com/allennlp/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_options.json -P /app/auxiliary_data

RUN pip install .

# RUN pip install Jinja2==3.0.3 itsdangerous==2.0.1
RUN pip install flask==1.1.4 Werkzeug==0.16.1 markupsafe==1.1.1

ENV PYTHONPATH /app

RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2'); from kwp_extraction.model import KeyphraseExtractor; KeyphraseExtractor(); KeyphraseExtractor('squeezebert/squeezebert-mnli')"

# RUN python -c "import nltk; nltk.download('stopwords')" 
# RUN python -c "import nltk; nltk.download('wordnet');" 
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2');" 
# RUN python -c "from kwp_extraction.model import KeyphraseExtractor; KeyphraseExtractor()"


EXPOSE 5000

CMD python api/app.py