import pickle
import shutil
import datetime
from transformers import BertTokenizer

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
    inputFile = open(path,'rt',encoding='UTF8')
    lines = inputFile.readlines()
    for line in lines:
        line = line.replace("\n","")
        ptr_tokenizer = BertTokenizer.from_pretrained("pretrained/vocab_snu_char16424.txt", do_lower_case=False)
        words = ptr_tokenizer.tokenize(line)
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