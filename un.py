#!/usr/bin/python

import re
import jieba
import codecs as cs
from wordcloud import WordCloud

def sentence_segmentation(content_str):
    sent_end = u'[。？！，：；]+'
    sent_end_set = set([u'。', u'？', u'！', u'，', u'：', u'；'])
    wrapper = set([u'\"', u'”', u'』'])
    offsetInContent = 0
    sstart = 0
    sent_array = []
    for sent_str in re.split(sent_end, content_str):
        if len(sent_str) == 0:
            continue
        if len(sent_str.strip()) == 1 and sent_str.strip() in wrapper:
            sent_array[-1] += sent_str.rstrip()
            # print sent_array[-1]
            continue
        try:
            sstart = content_str.index(sent_str[0], offsetInContent)
        except:
            print('cannot find sentence substring!!!')
            print('sentence:', sent_str)
            print('section:', content_str)
        while sstart + len(sent_str) < len(content_str) and content_str[sstart + len(sent_str)] in sent_end_set:
            sent_str += content_str[sstart + len(sent_str)]
        send = sstart + len(sent_str)
        offsetInContent = send
        if sent_str.strip() in sent_end_set:
            sent_array[-1] += sent_str
            continue
        sent_array.append(sent_str)
        # print 'sentence:', sent_str, 'start=', sstart, 'end=', send
    return sent_array


def Q2B(uchar):
    """全角转半角"""
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
        return uchar
    return chr(inside_code)  # unichr(inside_code) unichr is in Python2.


def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])


def char_transform(uchar):
    punc = set(u'—（）／．《》『』，、。？；：！……“”‘’|,.;:\'\"!+-@#$%^&*()\\=~`></?{}[]')
    num = set(
        [u'①', u'②', u'③', u'④', u'⑤', u'⑥', u'⑦', u'○', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十',
         u'百', u'千', u'万', u'亿', u'两', u' ％', u'１', u'２', u'３', u'４', u'５', u'６', u'７', u'８', u'９', u'０'])
    date = set([u'日', u'月', u'年'])
    if uchar in punc:
        return 'P'
    elif is_number(uchar) or uchar in num:
        return 'N'
    elif uchar in date:
        return 'D'
    elif is_alphabet(uchar):
        return 'E'
    elif is_other(uchar):
        return 'S'
    else:
        return 'O'

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False

def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False


def read_file(filename, representation, name_len_thresh, labeled=True):
    corpus_x = []
    corpus_y = []
    line_pointer = []
    word_cn_dict = {}
    char_cn_dict = {}
    count_dict = {'char_total': 0, 'char_cn': 0}
    urlStr = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    with cs.open(filename, 'r', encoding='utf-8') as inf:
        line_count = 0
        for line in inf:
            line_count += 1
            line = line.strip()
            if len(line) == 0:
                continue
            sentences = sentence_segmentation(line.strip())
            for sent in sentences:
                sent = stringQ2B(sent)
                elems = sent.strip().split()  # ('  ') #line.split('  ')
                # print elems
                # print sent
                if len(elems) < 1:
                    print(elems)
                    continue
                x = []
                y = []
                if representation == 'charpos':
                    # charpos = [char+str(i) for seg in jieba.cut(''.join(elems)) for i, char in enumerate(seg)]
                    charpos = []
                    jieba_output = jieba.cut(''.join(elems))
                    for seg in jieba_output:
                        if seg not in word_cn_dict:
                            if len(seg) > 1 or (len(seg) == 1 and is_chinese(seg)):
                                word_cn_dict[seg] = 1
                        else:
                            word_cn_dict[seg] += 1
                        for i, char in enumerate(seg):
                            charpos.append(char + str(i))
                            if char not in char_cn_dict:
                                if is_chinese(char):
                                    char_cn_dict[char] = len(char_cn_dict)
                pointer = 0
                for wd in elems:
                    ##Special treatment for URL##
                    wd = re.sub(urlStr, 'URL', wd)
                    if wd == 'URL':
                        x.append(wd)
                        y.append('S-word')
                        count_dict['char_total'] += 1
                        continue
                    ##EOSpecial treatment for URL##
                    for i, char in enumerate(wd):
                        rep = char_transform(char)
                        count_dict['char_total'] += 1
                        if is_chinese(char):
                            count_dict['char_cn'] += 1
                        # when rep == 'O', it's regular hanzi
                        if rep != 'O':
                            x.append(rep)
                        elif representation == 'charpos':
                            x.append(charpos[pointer])
                        else:
                            x.append(char)  # pos[pointer])
                        pointer += 1
                        if not labeled:
                            y.append('N')
                            continue
                        if len(wd) == 1:
                            y.append('S-word')
                        elif i == 0:
                            y.append('B-word')
                        elif i == len(wd) - 1:
                            y.append('E-word')
                        else:
                            y.append('I-word')
                assert len(x) == len(y)
                if len(x) < 2:
                    continue
                # print len(x), len(y)
                corpus_x.append(x)
                corpus_y.append(y)
                line_pointer.append(line_count)
    # print('read file', filename, len(corpus_x), len(corpus_y), len(line_pointer))
    return [corpus_x, corpus_y, word_cn_dict, char_cn_dict, count_dict]


def io_simple_test():
    text_path = 'test_input.txt'
    print('loading text from ', text_path)
    text_set = read_file(text_path, 'charpos', 16, False)

    print('总字符数:', text_set[4]['char_total'])
    print('总汉字数:', text_set[4]['char_cn'])
    print('共用到无重复汉字字符:', len(text_set[3]))
    print('共用到无重复汉字单词:', len(text_set[2]))

# create word cloud image for top freq words (max 10 words)
word_freq_top = sorted(text_set[2], key=text_set[2].get)
word_freq_top.reverse()
word_freq_top_drop_single = [wd for wd in word_freq_top if len(wd) > 1]
word_dict4wc = {}
for idex in range(min(10, len(word_freq_top_drop_single))):
    print(word_freq_top_drop_single[idex], ':', text_set[2][word_freq_top_drop_single[idex]])
    if word_freq_top_drop_single[idex] not in word_dict4wc:
        word_dict4wc[word_freq_top_drop_single[idex]] = text_set[2][word_freq_top_drop_single[idex]]
wc = WordCloud(font_path='STHeiti_Light.ttc', max_words=2000,
               width=1920, height=1080, background_color="black", margin=5)
wc.generate_from_frequencies(word_dict4wc)
wc.to_file('word_cloud_image_output.png')


io_simple_test()
