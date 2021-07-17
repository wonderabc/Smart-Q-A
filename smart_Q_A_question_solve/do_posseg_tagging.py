# 词性标注 + 将问题转换为问题模板 测试 （包含分类模型训练过程）
# 无法识别英文领域词汇，词性会被定义为eng
import re
import jieba
import numpy as np
from jieba import posseg
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from question_classifier import get_tv


def dopredict(question):  # 调用分类模型判断问题类别
    model = joblib.load("./model/question_classifier.model")
    question = [" ".join(list(jieba.cut(question)))]
    test_data = tv.transform(question).toarray()
    y_predict = model.predict(test_data)[0]
    # print("question type:",y_predict)
    return y_predict


def question_posseg(question):
    jieba.load_userdict("./data/dictbasicinfo.txt")  # 添加自定义词典
    clean_question = re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+", "", question)
    question_seged = posseg.cut(str(clean_question))
    result = []
    question_word, question_flag = [], []
    for w in question_seged:  # 词性标注的结果
        tmp_word = f"{w.word}/{w.flag}"
        result.append(tmp_word)
        word, flag = w.word, w.flag
        question_word.append(str(word).strip())
        question_flag.append(str(flag).strip())

    print(result)
    print(question_word)
    print(question_flag)
    return result, question_word, question_flag


def get_question_template(result, question_word, question_flag):  # 将问题抽象成模板
    for item in ['nr', 'nm', 'ng', 'nc', 'nl']:
        while item in set(question_flag):
            index = question_flag.index(item)
            question_word[index] = item  # 用nm / nr / ng / nc / nl等替换原词语
            question_flag[index] = item+"ed"  # 表示已处理完成
            print(question_word, question_flag)

    str_question = "".join(question_word)  # 替换后的问题字符串
    print("抽象问题为：", str_question)

    # 对抽象问题进行分类
    question_template_num = dopredict(str_question)
    print("使用模板编号：", question_template_num)


if __name__ == "__main__":
    result, question_word, question_flag = question_posseg("霸王别姬由哪些演员主演？")
    tv = get_tv()
    get_question_template(result, question_word, question_flag)