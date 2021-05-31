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
#주소
def clean(x):
    x = pattern.sub(' ', x)# pattern = 위에 나온 ., ?!/@...ㄱ-ㅣ가-힣{emojis}가 한글, 영어, 띄어쓰기, 일부 특수 문자 등을 제외하고 모두 제거. (한자, 일본어 등 삭제)
    x = url_pattern.sub('', x) #url 주소 있으면 지워줌 https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*) - 의미있는거
    x = x.strip()#그걸 스페이스 바 단위로 자름.
    x = repeat_normalize(x, num_repeats=2) # 무의미하게 반복되는 것들을 정리
    #print(x)

    return x

def save_backup():
    suffix=datetime.datetime.now().strftime("%m%d_%H%M%S")
    try:
        shutil.copyfile("./autoSave/autosave_labels.pickle", "./autoSave/%s_labels.pickle"%suffix)
        shutil.copyfile("./autoSave/autosave_reviews.pickle", "./autoSave/%s_reviews.pickle"%suffix)
        shutil.copyfile("./autoSave/autosave_original.pickle", "./autoSave/%s_original.pickle"%suffix) ##새 파일 불러올때 자동 백업
    except:
        pass


def fileLoad(path="./sample.txt"):
    save_backup()
    reviews=[]
    original=[]
    inputFile = open(path,'r',encoding="UTF8")
    lines = inputFile.readlines()

    tokenizer = AutoTokenizer.from_pretrained("beomi/kcbert-large")

    for line in lines:
        line = clean(line.replace("\n",""))
        #print(line)
        words = tokenizer.tokenize(line)
        #print(words)
        words = [word.replace("#", "") for word in words]
        original.append(line)
        reviews.append(words)

    inputFile.close()
    with open('./.idx','w',encoding="UTF8") as f:
        f.write("0")
    return original,reviews


def saveFile(original,reviews,labels,idx,path="./result.txt"):
    reviews=reviews
    labels=labels
    outputFile=open(path,'w')
    for i in range(idx+1):
        outputFile.write(original[i])
        outputFile.write('####')
        for label in range(len(labels[i])):
            outputFile.write("%s=%s"%(reviews[i][label],labels[i][label]))
        outputFile.write('\n')

    outputFile.close()


def autoSave(original,reviews,labels,idx):
    with open('./autoSave/autosave_original.pickle','wb') as f:
        pickle.dump(original, f, pickle.HIGHEST_PROTOCOL)
    with open('./autoSave/autosave_reviews.pickle','wb') as f:
        pickle.dump(reviews, f, pickle.HIGHEST_PROTOCOL)
    with open('./autoSave/autosave_labels.pickle','wb') as f:
        pickle.dump(labels, f, pickle.HIGHEST_PROTOCOL)
    with open('./.idx','w',encoding="UTF8") as f:
        f.write(str(idx))

def autoSaveLoad():
    with open('./autoSave/autosave_original.pickle','rb') as f:
        original=pickle.load(f)
    with open('./autoSave/autosave_reviews.pickle','rb') as f:
        data=pickle.load(f)
    with open('./autoSave/autosave_labels.pickle','rb') as f:
        label=pickle.load(f)

    with open('./.idx','r',encoding="UTF8") as f:
        idx=int(f.readline())

    return original,data,label,idx