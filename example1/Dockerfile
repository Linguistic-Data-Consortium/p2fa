FROM python:2

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
COPY model model
COPY align.py align.py
WORKDIR /mount
CMD [ "python2", "/app/aligner/align.py", "foo.wav", "foo.txt", "foo.TextGrid" ]
