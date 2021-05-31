import sys
from PyQt5.QtWidgets import QProgressBar,QAbstractItemView,QTableWidget,QTableWidgetItem,QApplication, QWidget,QPushButton, QDesktopWidget
import PyQt5.QtCore as QtCore
from filesaver import fileLoad, saveFile,autoSave,autoSaveLoad

ORIGINAL_REVIEWS = []
REVIEWS = []
REVIEW_LABEL=[]
REVIEWS_SIZE= 0
RESULT_PATH='./result.txt'

POS='T-POS'
NEG='T-NEG'
NEU='T-NEU'
NATURAL='O'


class MyApp(QWidget):
    def __init__(self, idx=0):
        super().__init__()
        self.idx=idx
        self.initUI()

    ## UI 초기화
    def initUI(self):
        self.pbar=QProgressBar(self)
        self.pbar.setGeometry(650,200,300,40)
        self.pbar.setMaximum(REVIEWS_SIZE-1)
        self.pbar.setValue(self.idx)
        self.pbar.setFormat("%i/%d"%(self.pbar.value()+1,self.pbar.maximum()+1))
        ## 프로그래스 바
        self.tableWidget=QTableWidget(self)
        self.tableWidget.move(50,50)
        self.tableWidget.resize(1500,130)
        self.tableWidget.setRowCount(2)
        self.tableWidget.setColumnCount(len(REVIEWS[0]))
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.viewport().installEventFilter(self)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.cellClicked.connect(self.__mycell_clicked)
        self.setTableWidgetData()
        ## 문장 보여지는 영역
        prevBtn=QPushButton('Prev',self)
        prevBtn.move(500,205)
        prevBtn.clicked.connect(self.getPrevReview)
        passBtn=QPushButton('Pass',self)
        passBtn.move(1450,180)
        passBtn.clicked.connect(self.passReview)
        nextBtn=QPushButton('Next',self)
        nextBtn.move(1000,205)
        nextBtn.clicked.connect(self.getNextReview)
        saveBtn = QPushButton('Save', self)
        saveBtn.move(1450, 300)
        saveBtn.clicked.connect(self.saveResult)
        ## 버튼들 (prev, next, save, pass)
        self.setWindowTitle('Cap11 LabelingTool')
        self.resize(1600,350)
        self.center()
        self.show()

    # 셀 왼쪽 클릭 했을 때 index O인 상태면 => POS로 나머지 상태였으면 => O로(선택 해제.)
    def __mycell_clicked(self,row,col):
        before=REVIEW_LABEL[self.idx][col]
        if before != NATURAL:
            REVIEW_LABEL[self.idx][col] = NATURAL
        else:
            REVIEW_LABEL[self.idx][col] = POS
        self.setTableWidgetData()


    # 셀 클릭 이벤트 핸들러. 한 번 왼쪽 클릭으로 잡아주고 - 우 클릭/휠클릭 해야 함.

    def eventFilter(self,source, event):
        col=self.tableWidget.currentColumn()
        if (event.type()==QtCore.QEvent.MouseButtonPress and event.buttons() == QtCore.Qt.RightButton):
            REVIEW_LABEL[self.idx][col]=NEG
            self.setTableWidgetData()
        elif(event.type()==QtCore.QEvent.MouseButtonPress and event.buttons() == QtCore.Qt.MidButton):
            REVIEW_LABEL[self.idx][col] = NEU
            self.setTableWidgetData()
        return QtCore.QObject.event(source, event)
    # 다음 리뷰 불러옴
    def getNextReview(self):
        self.idx+=1
        if(self.idx%5==0):
            autoSave(ORIGINAL_REVIEWS,REVIEWS,REVIEW_LABEL,self.idx)
        self.idx=self.idx%REVIEWS_SIZE
        self.pbar.setFormat("%i/%d"%(self.idx+1,self.pbar.maximum()+1))
        self.setTableWidgetData()

    # 전 리뷰 불러옴
    def getPrevReview(self):
        self.idx-=1
        self.idx=self.idx%REVIEWS_SIZE
        self.pbar.setFormat("%i/%d"%(self.idx+1,self.pbar.maximum()+1))

        self.setTableWidgetData()

    # 리뷰 패스 - 키워드 없는 문장일 경우
    def passReview(self):
        del ORIGINAL_REVIEWS[self.idx]
        del REVIEWS[self.idx]
        del REVIEW_LABEL[self.idx]

        global REVIEWS_SIZE
        REVIEWS_SIZE=len(REVIEWS)
        self.pbar.setMaximum(REVIEWS_SIZE-1)
        self.idx = self.idx % REVIEWS_SIZE
        self.pbar.setFormat("%i/%d" % (self.idx+1, self.pbar.maximum()+1))

        self.setTableWidgetData()

 
    # 저장 버튼 눌렀을 때 핸들러
    def saveResult(self):
        autoSave(ORIGINAL_REVIEWS ,REVIEWS, REVIEW_LABEL,self.idx)
        saveFile(ORIGINAL_REVIEWS ,REVIEWS, REVIEW_LABEL,self.idx, RESULT_NAME)

    def setTableWidgetData(self):
        self.tableWidget.setColumnCount(len(REVIEWS[self.idx]))
        self.pbar.setValue(self.idx)

        for idx, word in enumerate(REVIEWS[self.idx]):
            status=REVIEW_LABEL[self.idx][idx]
            newItem=QTableWidgetItem(word)
            color=QtCore.Qt.white
            if status==NEU:
                color=QtCore.Qt.gray
            elif status==POS:
                color=QtCore.Qt.green
            elif status==NEG:
                color=QtCore.Qt.red

            newItem.setBackground(color)

            self.tableWidget.setItem(0,idx,newItem)
            self.tableWidget.setItem(1,idx,QTableWidgetItem(status))
 
    # 창 중앙에 띄울 때 필요한 거.
    def center(self):
        qr = self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)


def init():
    global REVIEWS
    global REVIEWS_SIZE
    global REVIEW_LABEL
    global ORIGINAL_REVIEWS
    global RESULT_NAME
    print("""
        1.자동 저장 파일(.pickle) 로드하기
        2.새로운 파일 열기(***경고! 새 파일을 열면 기존에 자동 저장된 내용 날아가니 백업해두는 걸 추천!!(autoSave폴더에 있는 거)****)

        번호를 입력해주세요.
    """)
    select=input()

    if(int(select)==1):
        ORIGINAL_REVIEWS,REVIEWS,REVIEW_LABEL,idx=autoSaveLoad()
        REVIEWS_SIZE=len(REVIEWS)
    elif(int(select)==2):
        print("""------------------------------------------------------------------------------
        새 파일의 경로를 입력해주세요(파일 이름까지 포함, 미입력시 ./sample.txt파일을 들고 옵니다.)
        새 파일을 열면 기존에 자동 저장된 내용 날아가니 백업해두는 걸 추천!!(autoSave폴더에 있는 거)
        ex)C:\\Users\\bbcba\\Desktop\\Project\\Labeling\\input.txt (절대경로) 
            .\\input.txt(상대경로)
        ------------------------------------------------------------------------------
        파일경로:
        """)
        path=input()
        
        ORIGINAL_REVIEWS,REVIEWS=fileLoad(path) if len(path)!=0 else fileLoad()
        REVIEWS_SIZE= len(REVIEWS)
        for i in range(REVIEWS_SIZE):
            REVIEW_LABEL.append([NATURAL]*len(REVIEWS[i]))
        idx=0
    else:
        exit
    print("""

    ------------------------------------------------------------------------------
    결과물을 저장할 txt파일의 이름을 정해주세요( 미입력시 ./result.txt파일로 저장)
    !!!확장자는 따로 적어줄 필요 없음!
    ------------------------------------------------------------------------------
    결과파일 이름:
    """)
    result_name=input()
    RESULT_NAME="./%s.txt"%result_name

    return idx





if __name__=='__main__':  
    idx=init()
    app=QApplication(sys.argv)
    ex = MyApp(idx)
    sys.exit(app.exec_())