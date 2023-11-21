FROM python:3.11.5-bookworm

WORKDIR /app
RUN apt-get update -yqq && apt-get install -yqq --no-install-recommends sox gcc-multilib
COPY htk htk
WORKDIR /app/htk
RUN sed -i 's/  *if/\tif/' HLMTools/Makefile.in
RUN sed -i 's/dur<=0/dur<0/g' HTKLib/HRec.c
RUN ./configure --without-x --disable-hslab
RUN make all
RUN make install

WORKDIR /app/aligner
RUN pip install --user -U nltk
RUN python -m nltk.downloader "averaged_perceptron_tagger" "cmudict"
RUN pip install g2p_en
COPY model english
COPY dict.diff dict.diff
WORKDIR /app/aligner/english
RUN patch < ../dict.diff
WORKDIR /app/aligner
COPY align_tdf.py align_tdf.py
WORKDIR /mount
ENV USER=temp
CMD [ "python3", "/app/aligner/align_tdf.py", "foo.wav", "foo.tdf", "foo.words", "foo.phones" ]
