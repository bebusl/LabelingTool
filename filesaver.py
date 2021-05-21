import pickle
import shutil
import datetime
from transformers import AutoTokenizer
import re
import emoji
from soynlp.normalizer import repeat_normalize

emojis = ''.join(emoji.UNICODE_EMOJI.keys())
pattern = re.compile(f'[^ .,?!/@$%~％·∼()\x00-\x7Fㄱ-ㅣ가-힣{emojis}]+')
url_pattern = re.compile(
    r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')

def clean(x):
    x = pattern.sub(' ', x)
    x = url_pattern.sub('', x)
    x = x.strip()
    x = repeat_normalize(x, num_repeats=2)
    return x

def save_backup():
    suffix=datetime.datetime.now().strftime("%m%d_%H%M%S")
    try:
        shutil.copyfile("./autoSave/autosave_labels.pickle", "./autoSave/%s_labels.pickle"%suffix)
        shutil.copyfile("./autoSave/autosave_reviews.pickle", "./autoSave/%s_reviews.pickle"%suffix) ##새 파일 불러올때 자동 백업
    except:
        pass


def fileLoad(path="./sample.txt"):
    save_backup()
    reviews=[]
    inputFile = open(path,'r')
    lines = inputFile.readlines()

    tokenizer = AutoTokenizer.from_pretrained("beomi/kcbert-large")

    for line in lines:
        line = clean(line.replace("\n",""))
        print(line)
        words = tokenizer.tokenize(line)
        print(words)
        words = [word.replace("#", "") for word in words]
        reviews.append(words)
        #여기서 words를 화면에 쫘라락 보여주고, 거기서 선택할 수 있게 한 담에 result.txt에 저장시켜야 함.
    inputFile.close()
    with open('./.idx','w',encoding="UTF8") as f:
        f.write("0")
    return reviews


def saveFile(reviews,labels,path="./result.txt"):
    reviews=reviews
    labels=labels
    outputFile=open(path,'w')
    for idx,review in enumerate(reviews):
        outputFile.write(' '.join(review))
        outputFile.write('####')
        for label in range(len(labels[idx])):
            outputFile.write("%s=%s"%(review[label],labels[idx][label]))
        outputFile.write('\n')

    outputFile.close()


def autoSave(reviews,labels,idx):
    with open('./autoSave/autosave_reviews.pickle','wb') as f:
        pickle.dump(reviews, f, pickle.HIGHEST_PROTOCOL)
    with open('./autoSave/autosave_labels.pickle','wb') as f:
        pickle.dump(labels, f, pickle.HIGHEST_PROTOCOL)
    with open('./.idx','w',encoding="UTF8") as f:
        f.write(str(idx))

def autoSaveLoad():
    with open('./autoSave/autosave_reviews.pickle','rb') as f:
        data=pickle.load(f)
    with open('./autoSave/autosave_labels.pickle','rb') as f:
        label=pickle.load(f)

    with open('./.idx','r',encoding="UTF8") as f:
        idx=int(f.readline())

    return data,label,idx