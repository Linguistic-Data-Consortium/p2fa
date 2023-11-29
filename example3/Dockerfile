FROM python:3.11.5-bookworm

RUN apt-get update -yqq && apt-get install -yqq --no-install-recommends sox gcc-multilib gfortran autoconf-archive 
WORKDIR /app
COPY htk htk
WORKDIR /app/htk
RUN sed -i 's/  *if/\tif/' HLMTools/Makefile.in
RUN sed -i 's/dur<=0/dur<0/g' HTKLib/HRec.c
RUN ./configure --without-x --disable-hslab
RUN make all
RUN make install
WORKDIR /app
RUN wget http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.7.2.tar.gz
RUN tar -xvzf openfst-1.7.2.tar.gz
WORKDIR /app/openfst-1.7.2
RUN ./configure --enable-static --enable-shared --enable-far --enable-ngram-fsts
RUN make -j
RUN make install
WORKDIR /app
RUN git clone https://github.com/mitlm/mitlm.git
WORKDIR /app/mitlm
RUN autoreconf -i
RUN ./configure
RUN make
RUN make install
RUN ldconfig -v
WORKDIR /app
RUN git clone https://github.com/AdolfVonKleist/Phonetisaurus.git
WORKDIR /app/Phonetisaurus
RUN pip install pybindgen
RUN ./configure --enable-python
RUN make
RUN make install
WORKDIR /app/Phonetisaurus/python
RUN cp ../.libs/Phonetisaurus.so .
RUN python setup.py install
WORKDIR /app
RUN wget https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict
RUN cat cmudict.dict | perl -pe 's/\([0-9]+\)//; s/\s+/ /g; s/^\s+//; s/\s+$//; @_ = split (/\s+/); $w = shift (@_); $_ = $w."\t".join (" ", @_)."\n";' > cmudict.formatted.dict
RUN phonetisaurus-train --lexicon cmudict.formatted.dict --seq2_del --verbose
WORKDIR /app/aligner
COPY model english
COPY dict.diff dict.diff
WORKDIR /app/aligner/english
RUN patch < ../dict.diff
WORKDIR /app/aligner
COPY align_tdf_ph.py align_tdf.py
WORKDIR /mount
ENV USER=temp
CMD [ "python", "/app/aligner/align_tdf.py", "foo.wav", "foo.tdf", "foo.words", "foo.phones" ]
# CMD [ "phonetisaurus-apply", "--model", "/app/train/model.fst", "--word_list", "input.txt" ]
