
""" Usage:
      python3 align_tdf.py wavfile tdffile outputfile_alignment outputfile_words
"""

import re

import os
import sys
from g2p_en import G2p
g2p = G2p()

MODEL_DIR = '/app/aligner/english'
HVITE = '/app/htk/HTKTools/HVite'
HCOPY = '/app/htk/HTKTools/HCopy'

def prep_txt(trsfile, tmpbase, dictfile):
    dict = []
    with open(dictfile, 'r') as fid:
        for line in fid:
            dict.append(line.split()[0])

    f = open(trsfile, 'r')
    lines = f.readlines()
    f.close()

    fw = open(tmpbase + '.txt', 'w')
    unk_words = []
    first = True
    tdf = False
    for line in lines:
        if first:
            first = False
            if re.match(r'^file;unicode', line):
                tdf = True
            continue
        if tdf and re.match(r'^;;MM', line):
            continue
        line_split = line.split('\t')
        if (len(line_split) >= 5):
            if tdf:
                st, en = line_split[2:4]
                spkr = line_split[4]
                txt = line_split[7]
            else:
                spkr, st, en = line_split[1:4]
                txt = line_split[4]
            for pun in ['*', '~', '--', ',', '.', ':', ';', '!', '?', '"', '(', ')', '+', '=']:
                txt = txt.replace(pun,  ' ')
       
            wrds = []
            for wrd in txt.split():
                if (len(wrd) >= 2) and (wrd[-1] == '-'):
                    wrd = wrd[:-1]
                if wrd[0] == "'":
                    wrd = wrd[1:]
                if (wrd not in ["'", "-", ""]):
                    if (wrd.upper() not in dict):
                        unk_words.append(wrd.upper())
                        wrds.append('*' + wrd + '*')
                    else:
                        wrds.append(wrd)
            if (len(wrds) > 0):
                fw.write(st + '\t' + en + '\t' + spkr + '\t')
                for wrd in wrds:
                    fw.write(wrd + ' ')
                fw.write('\n')
    fw.close()
    
    #add unknown words to the standard dictionary, generate a tmp dictionary for alignment 
    fw = open(tmpbase + '.dict', 'w')
    f = open(dictfile, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        fw.write(line)
    fw2 = open(tmpbase + '_unk.words', 'w')
    for wrd in unk_words:
        fw2.write(wrd + '\n')
        fw.write('*'+wrd+'*' + ' ')
        for ph in g2p(wrd):
            fw.write(' ' + ph)
        fw.write('\n')
    fw.close()
    fw2.close()

def prep_mlf(txt, tmpbase):
    fw = open(tmpbase + '.mlf', 'w')
    fw.write('#!MLF!#\n')
    fw.write('"' + tmpbase + '.lab"\n')
    fw.write('sp\n')
    for wrd in txt.split():
        fw.write(wrd.upper() + '\n')
        fw.write('sp\n')
    fw.write('.\n')
    fw.close()

def genres(tmpbase, alignfile, wordsfile):
    f = open(tmpbase + '.txt', 'r')
    lines = f.readlines()
    f.close()
    fw1 = open(alignfile, 'w')
    fw2 = open(wordsfile, 'w')
    fw1.write('#!MLF!#\n')
    fw1.write('"' + tmpbase + '.rec"\n')
    for i in range(len(lines)):
        turn_st, turn_en, spkr, txt = lines[i].split('\t')
        subtmpbase = tmpbase + '_' + str(i)
        f = open(subtmpbase + '.aligned', 'r')
        lls = f.readlines()
        f.close()
        if (len(lls) > 1):
            times = []
            j = 0
            while (j < len(lls)): 
                if (j >= 2) and (j < (len(lls)-1)):
                    new_st= int(float(turn_st)*10000000) + int(lls[j].split()[0])
                    new_en = int(float(turn_st)*10000000) + int(lls[j].split()[1])
                    fw1.write(str(new_st) + ' ' + str(new_en))
                    for mm in lls[j].strip().split()[2:]:
                        fw1.write(' ' + mm)
                    fw1.write('\n')
                if ((len(lls[j].split()) == 5) and (lls[j].split()[0] != lls[j].split()[1])):
                    wrd = lls[j].split()[-1].strip()
                    st = int(lls[j].split()[0])/10000000.0 + 0.0125 + float(turn_st)
                    k = j + 1
                    while (lls[k] != '.\n') and (len(lls[k].split()) != 5):
                        k += 1
                    en = int(lls[k-1].split()[1])/10000000.0 + 0.0125 + float(turn_st)
                    times.append([wrd, st, en])
                j += 1

            words = txt.strip().split()
            words.reverse()

            for item in times:
                if (item[0] == 'sp'):
                    fw2.write(str(item[1]) + ' ' + str(item[2]) + ' ' + item[0] + ' ' + spkr + '\n')
                else:
                    fw2.write(str(item[1]) + ' ' + str(item[2]) + ' ' + words.pop() + ' ' + spkr + '\n')
            if (words != []):
                print(lines[i], str(i) + '::not matched::' + alignfile)
        else:
            fw1.write(str(int(float(turn_st)*10000000)) + ' ' + str(int(float(turn_en)*10000000)) + ' ' + '***' + txt.strip().replace(' ', '_') + '***' + ' ' + '-1000000.0' + ' ' + '***' + txt.strip().replace(' ', '_') + '***' + '\n')
            fw2.write(turn_st + ' ' + turn_en + ' ' + '***' + txt.strip().replace(' ', '_') + '***' + ' ' + spkr + '\n')
    fw1.write('.\n')
    fw1.close()
    fw2.close()

if __name__ == '__main__':

    try:
        wavfile = sys.argv[1]
        trsfile = sys.argv[2]
        alignfile = sys.argv[3]
        wordsfile = sys.argv[4]

    except IndexError:
        print("Input errors occurred!")
        print(__doc__)
        exit(1)
  
    if 'USER' in os.environ:
        tmpbase = './' + os.environ['USER'] + '_' + str(os.getpid())
    else:
        tmpbase = './' + os.environ['USERNAME'] + '_' + str(os.getpid())
    samprate = os.popen('soxi -r ' + wavfile).read().strip() 

    #prepare clean_transcript file
    prep_txt(trsfile, tmpbase, MODEL_DIR + '/dict')

    f = open(tmpbase + '.txt', 'r')
    lines = f.readlines()
    f.close()
    for i in range(len(lines)):
        subtmpbase = tmpbase + '_' + str(i)
        st = int(float(lines[i].split('\t')[0])*10000000)
        en = int(float(lines[i].split('\t')[1])*10000000)
        txt = lines[i].split('\t')[3]
        prep_mlf(txt, subtmpbase)

        #prepare scp
        os.system(HCOPY + ' -C ' + MODEL_DIR + '/' + samprate + '/config ' + '-s ' + str(st) + ' ' + '-e ' + str(en) + ' ' + wavfile + ' ' + subtmpbase + '.plp')

        #run alignment
        if os.path.exists('/dev/null'):
            os.system(HVITE + ' -a -m -t 10000.0 10000.0 100000.0 -I ' + subtmpbase + '.mlf -H ' + MODEL_DIR + '/' + samprate + '/macros -H ' + MODEL_DIR + '/' + samprate + '/hmmdefs -i ' + subtmpbase +  '.aligned '  + tmpbase + '.dict ' + MODEL_DIR + '/monophones ' + subtmpbase + '.plp 2>&1 > /dev/null')
        else:
            os.system(HVITE + ' -a -m -t 10000.0 10000.0 100000.0 -I ' + subtmpbase + '.mlf -H ' + MODEL_DIR + '/' + samprate + '/macros -H ' + MODEL_DIR + '/' + samprate + '/hmmdefs -i ' + subtmpbase +  '.aligned '  + tmpbase + '.dict ' + MODEL_DIR + '/monophones ' + subtmpbase + '.plp')

    #generate results
    genres(tmpbase, alignfile, wordsfile)

    #clean up
    print('Done!')
    os.system('cp ' + tmpbase + '_unk.words' + ' ./' + trsfile.split('/')[-1].split('.')[0] + '.unks')
    print('The unk words, whose pronunciations are generated by g2p, are saved in ./' + trsfile.split('/')[-1].split('.')[0] + '.unks')
    os.system('rm -f ' + tmpbase + '*')
