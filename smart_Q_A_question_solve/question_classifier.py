# 训练问题分类器
import os
import re

import jieba
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


def getfilelist(path):  # 获取./data/question目录下的所有文件
    file_path_list = []
    walk = os.walk(path)
    for root, dirs, files in walk:
        for name in files:
            filepath = os.path.join(root, name)
            file_path_list.append(filepath)
    return file_path_list


def get_train_data():  # 获取问题分类器的训练数据
    trainx = []
    trainy = []
    pathinfo = os.path.split(os.path.realpath(__file__))[0]  # 重新组装文件地址
    # print(pathinfo)
    file_list = getfilelist(pathinfo + "/data/question")
    for f in file_list:
        num = re.sub(r'\D', "", f)  # 获取文件名中的数字
        if len(num) > 0:  # 读取
            label_num = num
            with open(f, "r", encoding="utf-8") as fr:
                question_list = fr.readlines()
                for q in question_list:
                    word_list = list(jieba.cut(str(q).strip()))
                    trainx.append(" ".join(word_list))  # 加入训练集
                    trainy.append(label_num)
    # print(trainx, trainy)
    return trainx, trainy


def train_model_NB(trainx, trainy):  # 训练分类器
    print("开始训练问题分类器……")
    tv = TfidfVectorizer()
    train_data = tv.fit_transform(trainx).toarray()
    clf = MultinomialNB(alpha=0.01)
    clf.fit(train_data, trainy)
    pathinfo = os.path.split(os.path.realpath(__file__))[0]  # 重新组装文件地址
    joblib.dump(clf, pathinfo + '/model/question_classifier.model')
    print("分类器训练并存储结束。")
    return tv


def get_tv():  # 获得 TfidfVectorizer (fitted)
    tx, ty = get_train_data()
    tv = TfidfVectorizer()
    tv.fit_transform(tx).toarray()
    return tv


if __name__ == "__main__":
    trainx, trainy = get_train_data()
    print(trainx, trainy)
    train_model_NB(trainx, trainy)