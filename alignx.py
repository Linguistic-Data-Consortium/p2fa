
""" Usage:
      python3 align_tdf.py wavfile tdffile outputfile_alignment outputfile_words
"""

import re

import os
import sys

MODEL_DIR = '/app/aligner/english'
HVITE = '/app/htk/HTKTools/HVite'
HCOPY = '/app/htk/HTKTools/HCopy'

def prep_txt(trsfile, tmpbase, dictfile, textgrid, wavfile):
    dict = []
    with open(dictfile, 'r') as fid:
        for line in fid:
            dict.append(line.split()[0])

    f = open(trsfile, 'r')
    lines = f.readlines()
    f.close()

    fw = open(tmpbase + '.txt', 'w')
    unk_words = []
    all_words = []
    first = True
    tdf = False
    first_textgrid = True
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
                        if textgrid:
                            continue
                        unk_words.append(wrd.upper())
                        wrds.append('*' + wrd + '*')
                    else:
                        wrds.append(wrd)
            if (len(wrds) > 0):
                if textgrid and first_textgrid:
                    st = '0.0'
                    en = os.popen('soxi -D ' + wavfile).read().strip() 
                    first_textgrid = False
                    fw.write(st + '\t' + en + '\t' + spkr + '\t')
                elif not textgrid:
                    fw.write(st + '\t' + en + '\t' + spkr + '\t')
                for wrd in wrds:
                    fw.write(wrd + ' ')
                    all_words.append(wrd)
                if not textgrid:
                    fw.write('\n')
    if textgrid:
        fw.write('\n')
    fw.close()

    g2p = {}
    g2pf = prep_dict(tmpbase, dictfile, unk_words, g2p)

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
        fw.write(g2pf(wrd))
        fw.write('\n')
    fw.close()
    fw2.close()
    # os.system('tail ' + tmpbase + '.dict')
    return all_words

def prep_dict(tmpbase, dictfile, unk_words, g2p):
    lower = {}
    fw2 = open(tmpbase + '_unk.words', 'w')
    fw3 = open(tmpbase + '_unk.words_lower', 'w')
    for wrd in unk_words:
        fw2.write(wrd + '\n')
        # if re.match(r'^\d+$', wrd):
            # fw.write('*' + wrd + '*\tAH1\n')
        if wrd != '#':
            fw3.write(wrd.lower() + '\n')
            lower[wrd.lower()] = wrd
    fw2.close()
    fw3.close()
    os.system('phonetisaurus-apply --model /app/train/model.fst --word_list ' + tmpbase + '_unk.words_lower > ' + tmpbase + '_unk.words_with_phones')
    f = open(tmpbase + '_unk.words_with_phones', 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        # print(line)
        line_split = line.split('\t')
        ww = line_split[0].upper()
        # newline = '*' + ww + '* ' + line_split[1]
        if ww != '{LAUGH':
            # fw.write(newline)
            g2p[lower[line_split[0]]] = line_split[1]
    def f(w):
        return g2p[w]
    return f
    # fw.write('*{LAUGH*\tAH1\n')
    # fw.write('*}*\tAH1\n')
    # fw.write('*#*\tAH1\n')
    # fw.close()


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
    # os.system('cat foo.TextGrid')

def TextGrid(infile, reffile, fw, SR, all_words):
    """
    Generate a TextGrid file from a forced aignment
    infile  - the aligned transcript
    reffile - dunno
    fw      - a file-like object to write to
    SR      - the sampling rate for the audio
    """

    def output(txt):
        fw.write(txt.encode("utf-8"))

    with open(infile, "r") as f:
        lines = f.readlines()
    with open(reffile, "r") as f:
        refs = f.readlines()

    refs = all_words
    refs.reverse()
    j = 2

    phons = []
    wrds = []
    # print(refs)
    # exit()
    while lines[j] != ".\n":
        ph = lines[j].split()[2]
        # print(ph)
        if SR == 11025:
            st = (float(lines[j].split()[0]) / 10000000.0 + 0.0125) * (
                11000.0 / 11025.0
            )
            en = (float(lines[j].split()[1]) / 10000000.0 + 0.0125) * (
                11000.0 / 11025.0
            )
        else:
            st = float(lines[j].split()[0]) / 10000000.0 + 0.0125
            en = float(lines[j].split()[1]) / 10000000.0 + 0.0125
        if st != en:
            # print(4)
            phons.append([ph, round(st,4), round(en,4)])

        if len(lines[j].split()) == 5:
            wrd = lines[j].split()[4].replace("\n", "")
            # print(wrd)
            if SR == 11025:
                st = (float(lines[j].split()[0]) / 10000000.0 + 0.0125) * (
                    11000.0 / 11025.0
                )
                en = (float(lines[j].split()[1]) / 10000000.0 + 0.0125) * (
                    11000.0 / 11025.0
                )
            else:
                st = float(lines[j].split()[0]) / 10000000.0 + 0.0125
                en = float(lines[j].split()[1]) / 10000000.0 + 0.0125
            if st != en:
                if wrd == "sp":
                    # print(1)
                    wrds.append([wrd, round(st,4), round(en,4)])
                else:
                    # print(2)
                    # wrds.append([refs.pop().strip(), st, en])
                    wrds.append([refs.pop().strip().upper(), round(st,4), round(en,4)])
                    # print(wrds[-1])
            else:
                # for other samplein rate
                pass
                # print(3)

        j += 1

    # print(phons)
    # exit()
    # write the phone interval tier
    output('File type = "ooTextFile short"\n')
    output('"TextGrid"\n')
    output("\n")
    output(str(phons[0][1]) + "\n")
    output(str(phons[-1][2]) + "\n")
    output("<exists>\n")
    output("2\n")
    output('"IntervalTier"\n')
    output('"phone"\n')
    output(str(phons[0][1]) + "\n")
    output(str(phons[-1][-1]) + "\n")
    output(str(len(phons)) + "\n")
    for k in range(len(phons)):
        output(str(phons[k][1]) + "\n")
        output(str(phons[k][2]) + "\n")
        output('"' + phons[k][0] + '"' + "\n")

    # write the word interval tier
    output('"IntervalTier"\n')
    output('"word"\n')
    output(str(phons[0][1]) + "\n")
    output(str(phons[-1][-1]) + "\n")
    output(str(len(wrds)) + "\n")
    for k in range(len(wrds) - 1):
        output(str(wrds[k][1]) + "\n")
        output(str(wrds[k + 1][1]) + "\n")
        output('"' + wrds[k][0] + '"' + "\n")

    output(str(wrds[-1][1]) + "\n")
    output(str(phons[-1][2]) + "\n")
    output('"' + wrds[-1][0] + '"' + "\n")

if __name__ == '__main__':

    try:
        wavfile = sys.argv[1]
        trsfile = sys.argv[2]
        alignfile = sys.argv[3]
        wordsfile = sys.argv[4]
        if len(sys.argv) == 6:
            textgrid = sys.argv[5]
        else:
            textgrid = None

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
    all_words = prep_txt(trsfile, tmpbase, MODEL_DIR + '/dict', textgrid, wavfile)

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
        if textgrid:
            os.system(HCOPY + ' -C ' + MODEL_DIR + '/' + samprate + '/config ' +                                                 wavfile + ' ' + subtmpbase + '.plp')
        else:
            os.system(HCOPY + ' -C ' + MODEL_DIR + '/' + samprate + '/config ' + '-s ' + str(st) + ' ' + '-e ' + str(en) + ' ' + wavfile + ' ' + subtmpbase + '.plp')

        #run alignment
        if os.path.exists('/dev/null'):
            os.system(HVITE + ' -a -m -t 10000.0 10000.0 100000.0 -I ' + subtmpbase + '.mlf -H ' + MODEL_DIR + '/' + samprate + '/macros -H ' + MODEL_DIR + '/' + samprate + '/hmmdefs -i ' + subtmpbase +  '.aligned '  + tmpbase + '.dict ' + MODEL_DIR + '/monophones ' + subtmpbase + '.plp 2>&1 > /dev/null')
        else:
            os.system(HVITE + ' -a -m -t 10000.0 10000.0 100000.0 -I ' + subtmpbase + '.mlf -H ' + MODEL_DIR + '/' + samprate + '/macros -H ' + MODEL_DIR + '/' + samprate + '/hmmdefs -i ' + subtmpbase +  '.aligned '  + tmpbase + '.dict ' + MODEL_DIR + '/monophones ' + subtmpbase + '.plp')

        if textgrid:
            break

    #generate results
    genres(tmpbase, alignfile, wordsfile)
    if textgrid:
        fw = open(textgrid, 'w+b')
        TextGrid(alignfile, wordsfile, fw, samprate, all_words)
        fw.close()
    # os.system('ls -l')
    # os.system('cat temp_1_4.aligned')
    # os.system('cat temp_1.txt')
    # os.system('cat temp_1_0.aligned')
    os.system('cat foo.words')
    # os.system('cat foo.TextGrid')

    #clean up
    print('Done!')
    os.system('cp ' + tmpbase + '_unk.words' + ' ./' + trsfile.split('/')[-1].split('.')[0] + '.unks')
    print('The unk words, whose pronunciations are generated by Phonetisaurus, are saved in ./' + trsfile.split('/')[-1].split('.')[0] + '.unks')
    os.system('rm -f ' + tmpbase + '*')

