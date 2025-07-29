
import argparse
import re

import os
import sys

import wave
# from json import dumps, loads
# from os import stat
from os.path import dirname, join
from shutil import move
from subprocess import DEVNULL, run
from tempfile import TemporaryDirectory, TemporaryFile

# from boto3 import resource
# from util import UtilException, get_input, get_logger, send_to_s3

# log = get_logger()


def path_to(rel_path):
    return join(dirname(__file__), rel_path)


MODEL_DIR = '/app/aligner/english'
HVITE = '/app/htk/HTKTools/HVite'
HCOPY = '/app/htk/HTKTools/HCopy'

def prep_txt(trsfile, dictfile, textgrid, dur, unkfile):
    dict = {}
    sdict = {}
    tdict = []
    tdictf = False
    with open(dictfile, 'r') as fid:
        for line in fid:
            line0 = line.split()[0]
            if line0 in dict:
                dict[line0] += line
            else:
                dict[line0] = line
            # dict[line0] = line
            if tdictf:
                tdict.append(line)
            if line == 'ZZZZ  Z Z\n':
                tdictf = True

    with open(trsfile, 'r') as f:
        lines = f.readlines()

    # fw = open(tmpbase + '.txt', 'w')
    fw = []
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
                st, en, txt, spkr = line_split[1:5]
                # txt = line_split[4]
            for pun in ['*', '~', '--', ',', '.', ':', ';', '!', '?', '"', '(', ')', '+', '=']:
                txt = txt.replace(pun,  ' ')
       
            wrds = []
            for wrd in txt.split():
                if (len(wrd) >= 2) and (wrd[-1] == '-'):
                    wrd = wrd[:-1]
                if wrd[0] == "'":
                    wrd = wrd[1:]
                if (wrd not in ["'", "-", ""]):
                    wrdu = wrd.upper()
                    if (wrdu not in dict):
                        if textgrid:
                            continue
                        unk_words.append(wrdu)
                        wrds.append('*' + wrd + '*')
                    else:
                        wrds.append(wrd)
                        sdict[wrdu] = dict[wrdu]
            if (len(wrds) > 0):
                fwl = ""
                if textgrid and first_textgrid:
                    st = '0.0'
                    en = str(dur)
                    first_textgrid = False
                    fwl += st + '\t' + en + '\t' + spkr + '\t'
                    fw.append(fwl)
                elif not textgrid:
                    fwl += st + '\t' + en + '\t' + spkr + '\t'
                for wrd in wrds:
                    fwl += wrd + ' '
                    if textgrid:
                        fw[-1] += wrd + ' '
                    all_words.append(wrd)
                if not textgrid:
                    fw.append(fwl)

    g2pf = prep_dict(unk_words)

    #add unknown words to the standard dictionary, generate a tmp dictionary for alignment 
    dict = []
    # fw = open(tmpbase + '.dict', 'w')
    # f = open(dictfile, 'r')
    # lines = f.readlines()
    # f.close()
    for line in sdict.values():
        # fw.write(line)
        dict.append(line)
    for line in tdict:
        dict.append(line)
    with open(unkfile, 'w') as fw2:
        for wrd in unk_words:
            fw2.write(wrd + '\n')
            # fw.write('*'+wrd+'*' + ' ')
            # fw.write(g2pf(wrd))
            # fw.write('\n')
            dict.append('*'+wrd+'*' + ' ' + g2pf(wrd) + '\n')

    # fw.close()
    # os.system('cat ' + unkfile)
    # print(len(dict))
    # exit()
    return all_words, dict, fw

def prep_dict(unk_words):
    g2p = {}
    lower = {}
    with TemporaryDirectory() as work_dir:
        words = join(work_dir, "unk.words")
        words_lower = join(work_dir, "unk.words_lower")
        words_with_phones = join(work_dir, "unk.words_with_phones")
        with open(words, 'w') as fw2, open(words_lower, 'w') as fw3:
            for wrd in unk_words:
                fw2.write(wrd + '\n')
                # if re.match(r'^\d+$', wrd):
                    # fw.write('*' + wrd + '*\tAH1\n')
                if wrd != '#':
                    fw3.write(wrd.lower() + '\n')
                    lower[wrd.lower()] = wrd
        os.system('phonetisaurus-apply --model /app/train/model.fst --word_list ' + words_lower + ' > ' + words_with_phones)
        with open(words_with_phones, 'r') as f:
            lines = f.readlines()
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

def prep_wav(orig_wav):
    with wave.open(orig_wav, "r") as f:
        SR = f.getframerate()
        NF = f.getnframes()
        # if SR not in [8000, 11025, 16000]:
        #     SR = 11025
        # # just resample everything; some wave files make HVite barf due to
        # # header errors. sox to the rescue!
        # tmp = orig_wav + ".tmp.wav"
        # run(["sox", orig_wav, f"-r {SR}", tmp])
        # move(tmp, orig_wav)
    return SR, (NF/SR)

def prep_mlf(txt, f):
    fw = open(f + '.mlf', 'w')
    fw.write('#!MLF!#\n')
    fw.write('"' + f + '.lab"\n')
    fw.write('sp\n')
    for wrd in txt.split():
        fw.write(wrd.upper() + '\n')
        fw.write('sp\n')
    fw.write('.\n')
    fw.close()

def genres(alignfile, wordsfile, llsa, textgrid, SR, all_words, lines):
    # f = open(tmpbase + '.txt', 'r')
    # lines = f.readlines()
    # f.close()
    fw1 = []
    fw2 = []
    fw1.append('#!MLF!#\n')
    fw1.append('"' + alignfile.split('.')[0] + '.rec"\n')
    for i in range(len(lines)):
        turn_st, turn_en, spkr, txt = lines[i].split('\t')
        turn_stf = float(turn_st)
        turn_enf = float(turn_en)
        turn_sti = int(turn_stf*10000000)
        turn_eni = int(turn_enf*10000000)
        # subtmpbase = tmpbase + '_' + str(i)
        # f = open(subtmpbase + '.aligned', 'r')
        # lls = f.readlines()
        # f.close()
        lls = llsa[i]
        if (len(lls) > 1):
            times = []
            j = 0
            while (j < len(lls)):
                llsj = lls[j].strip().split()
                # print(llsj)
                if (j >= 2) and (j < (len(lls)-1)):
                    new_st = turn_sti + int(llsj[0])
                    new_en = turn_sti + int(llsj[1])
                    fw1.append(str(new_st) + ' ' + str(new_en))
                    for mm in llsj[2:]:
                        fw1[-1] += ' ' + mm
                    fw1[-1] += '\n'
                if ((len(llsj) == 5) and (llsj[0] != llsj[1])):
                    wrd = llsj[-1]
                    st = int(llsj[0])/10000000.0 + 0.0125 + turn_stf
                    k = j + 1
                    while (lls[k] != '.\n') and (len(lls[k].split()) != 5):
                        k += 1
                    en = int(lls[k-1].split()[1])/10000000.0 + 0.0125 + turn_stf
                    times.append([wrd, st, en])
                j += 1

            words = txt.strip().split()
            words.reverse()

            for item in times:
                if (item[0] == 'sp'):
                    fw2.append(str(item[1]) + ' ' + str(item[2]) + ' ' + item[0] + ' ' + spkr + '\n')
                else:
                    fw2.append(str(item[1]) + ' ' + str(item[2]) + ' ' + words.pop() + ' ' + spkr + '\n')
            if (words != []):
                print(lines[i], str(i) + '::not matched::' + alignfile)
        else:
            fw1.append(str(turn_sti) + ' ' + str(turn_eni) + ' ' + '***' + txt.strip().replace(' ', '_') + '***' + ' ' + '-1000000.0' + ' ' + '***' + txt.strip().replace(' ', '_') + '***' + '\n')
            fw2.append(turn_st + ' ' + turn_en + ' ' + '***' + txt.strip().replace(' ', '_') + '***' + ' ' + spkr + '\n')
    fw1.append('.\n')
    with open(alignfile, 'w') as fw:
        fw.write("".join(fw1))
    with open(wordsfile, 'w') as fw:
        fw.write("".join(fw2))
    if textgrid:
        with open(textgrid, 'w+b') as fw:
            TextGrid(fw1, fw2, fw, SR, all_words)
    # os.system('cat foo.TextGrid')

def TextGrid(lines, refs, fw, SR, all_words):
    """
    Generate a TextGrid file from a forced aignment
    lines   - the aligned transcript
    refs    - the aligned words
    fw      - a file-like object to write to
    SR      - the sampling rate for the audio
    """

    def output(txt):
        fw.write(txt.encode("utf-8"))

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

def align(work_dir, wave_file, st, en, dict, txt, SR):
    # tmp_mlf, ref_mlf = prep_mlf(trs_file, work_dir)
    # prepare scp files
    # codetr_scp = join(work_dir, "codetr.scp")
    # test_scp = join(work_dir, "test.scp")
    # mlf = join(work_dir, "tmp.mlf")
    tmp = join(work_dir, "tmp")
    mdict = tmp + ".dict"
    with open(mdict, 'w') as fw:
        fw.write("".join(dict))
    # with open(tmp_mlf, 'r') as f, open(mlf, 'w') as fw:
    #     a = f.readlines()
    #     a[1] = '"' + lab + '"\n'
    #     fw.write("".join(a))
    prep_mlf(txt, tmp)
    plp = tmp + ".plp"
    # log.debug("wave_file is %s", wave_file)
    # log.debug("%s", stat(wave_file))
    # with open(codetr_scp, "w") as fw:
    #     fw.write(wave_file + " " + join(work_dir, "tmp.plp") + "\n")
    # with open(test_scp, "w") as fw:
    #     fw.write(join(work_dir, "tmp.plp") + "\n")
    # log.debug(open(codetr_scp).read())
    config = path_to(join("model", str(SR), "config"))
    macros = path_to(join("model", str(SR), "macros"))
    hmmdefs = path_to(join("model", str(SR), "hmmdefs"))
    monophones = path_to(join("model", "monophones"))

    aligned_mlf = join(work_dir, "aligned.mlf")
    # fmt: off
    hcopy = [ "HCopy", "-T", "1", "-C", config ]
    if st != None:
        hcopy += [ '-s', str(int(st*10000000)), '-e', str(int(en*10000000)) ]
    hcopy += [ wave_file, plp ]
    run(hcopy)
    run(
        [
            "HVite",
            "-T", "1",
            "-a",
            "-m",
            "-t", "10000.0", "10000.0", "100000.0",
            "-I", tmp + ".mlf",
            "-H", macros,
            "-H", hmmdefs,
            # "-S", test_scp,
            "-i", aligned_mlf,
            # "-p", "0.0",
            # "-s", "5.0",
            mdict,
            monophones,
            plp
        ],
        stderr=DEVNULL,
        stdout=DEVNULL,
    )
    # # fmt: on
    # with TemporaryFile(mode="w+b", dir=work_dir) as outfile:
    #     TextGrid(aligned_mlf, ref_mlf, outfile, SR)
    #     outfile.seek(0)
    #     # return send_to_s3(
    #     #     outfile, bucket, [wave_url, trs_url], prefix, content_type="text/plain"
    #     # )
    with open(aligned_mlf, 'r') as f:
        return f.readlines()

def align_transcript(work_dir, wavfile, trsfile, mdir, textgrid, unkfile):
    SR, dur = prep_wav(wavfile)

    #prepare clean_transcript file
    all_words, dict, lines = prep_txt(trsfile, mdir, textgrid, dur, unkfile)

    # with open(tmpbase + '.txt', 'r') as f:
    #     lines = f.readlines()
    lls = []
    for i in range(len(lines)):
        # subtmpbase = tmpbase + '_' + str(i)
        # st = int(float(lines[i].split('\t')[0])*10000000)
        # en = int(float(lines[i].split('\t')[1])*10000000)
        st, en, sp, txt = lines[i].split('\t')
        # prep_mlf(txt, subtmpbase)

        # print("".join(dict))
        # exit()
        if textgrid:
            st = None
            en = None
        else:
            st = float(st)
            en = float(en)
        llsx = align(work_dir, wavfile, st, en, dict, txt, SR)
        lls.append(llsx)
        # print(llsx)
        # exit()

        # #prepare scp
        # if textgrid:
        #     os.system(HCOPY + ' -C ' + MODEL_DIR + '/' + samprate + '/config ' +                                                 wavfile + ' ' + subtmpbase + '.plp')
        # else:
        #     os.system(HCOPY + ' -C ' + MODEL_DIR + '/' + samprate + '/config ' + '-s ' + str(st) + ' ' + '-e ' + str(en) + ' ' + wavfile + ' ' + subtmpbase + '.plp')

        # #run alignment
        # if os.path.exists('/dev/null'):
        #     os.system(HVITE + ' -a -m -t 10000.0 10000.0 100000.0 -I ' + subtmpbase + '.mlf -H ' + MODEL_DIR + '/' + samprate + '/macros -H ' + MODEL_DIR + '/' + samprate + '/hmmdefs -i ' + subtmpbase +  '.aligned '  + tmpbase + '.dict ' + MODEL_DIR + '/monophones ' + subtmpbase + '.plp 2>&1 > /dev/null')
        # else:
        #     os.system(HVITE + ' -a -m -t 10000.0 10000.0 100000.0 -I ' + subtmpbase + '.mlf -H ' + MODEL_DIR + '/' + samprate + '/macros -H ' + MODEL_DIR + '/' + samprate + '/hmmdefs -i ' + subtmpbase +  '.aligned '  + tmpbase + '.dict ' + MODEL_DIR + '/monophones ' + subtmpbase + '.plp')

        if textgrid:
            break
    # exit()
    #generate results
    # print(lines)
    # exit()
    return SR, all_words, lines, lls


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="forced aligner")
    parser.add_argument("-f", "--file", dest="filename", help="Specify a file name.")
    parser.add_argument("-g", "--textgrid", action="store_true", help="output TextGrid")
    parser.add_argument("wavfile", help="wave file")
    parser.add_argument("trsfile", help="transcript file")
    args = parser.parse_args()
    # if args.filename:
    #     print(f"File specified: {args.filename}")
    # if args.verbose:
    #     print("Verbose mode enabled.")
    # print(f"Input data: {args.input_data}")
    alignfile = args.trsfile + '.align'
    wordsfile = args.trsfile + '.words'
    unkfile = args.trsfile + '.unks'
    if args.textgrid:
        textgrid = args.trsfile + '.TextGrid'
    else:
        textgrid = None

    
    # try:
    #     wavfile = sys.argv[1]
    #     trsfile = sys.argv[2]
    #     alignfile = trsfile + '.align'
    #     wordsfile = trsfile + '.words'
    #     unkfile = trsfile + '.unks'
    #     textgrid = trsfile + '.TextGrid'
    #     textgrid = None
    #     # if len(sys.argv) == 6:
    #     #     textgrid = sys.argv[5]
    #     # else:
    #     #     textgrid = None
    #     # unkfile = trsfile.split('/')[-1].split('.')[0] + '.unks'

    # except IndexError:
    #     print("Input errors occurred!")
    #     print(__doc__)
    #     exit(1)
  
    # if 'USER' in os.environ:
    #     tmpbase = './' + os.environ['USER'] + '_' + str(os.getpid())
    # else:
    #     tmpbase = './' + os.environ['USERNAME'] + '_' + str(os.getpid())
    # samprate = os.popen('soxi -r ' + wavfile).read().strip() 
    with TemporaryDirectory() as work_dir:
            SR, all_words, lines, lls = align_transcript(work_dir, args.wavfile, args.trsfile, MODEL_DIR + '/dict', textgrid, unkfile)
    genres(alignfile, wordsfile, lls, textgrid, SR, all_words, lines)

    # os.system('ls -l')
    # os.system('cat temp_1_4.aligned')
    # os.system('cat temp_1.txt')
    # os.system('cat temp_1_0.aligned')
    # os.system('cat foo.align')
    # os.system('cat foo.TextGrid')

    #clean up
    # print('Done!')
    # os.system('cp ' + tmpbase + '_unk.words' + ' ./' + trsfile.split('/')[-1].split('.')[0] + '.unks')
    # print('The unk words, whose pronunciations are generated by Phonetisaurus, are saved in ./' + trsfile.split('/')[-1].split('.')[0] + '.unks')
    # os.system('rm -f ' + tmpbase + '*')

