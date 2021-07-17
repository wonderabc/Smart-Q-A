# 原始问题的预处理
# 自然语言表达的问题 --> 分类器能理解并正确分类的形式
# 0627 新增问题类 【20-24】

import os
import re
import jieba
from jieba import posseg
from sklearn.externals import joblib
from smart_Q_A_question_solve.question_classifier import get_tv
from smart_Q_A_question_solve.question_template_solve import QuestionTemplate


class question:
    def __init__(self):
        # 初始化相关设置：得到分类器，读取问题模板，连接数据库
        self.path_info = os.path.split(os.path.realpath(__file__))[0]  # python包位置
        mydict = self.path_info + "/data/dictbasicinfo.txt"
        jieba.load_userdict(mydict)  # dictbasicinfo是自定义词典，包含电影领域的专有词汇，避免被jieba错误切词
        self.init_config()

    def init_config(self):
        self.tv = get_tv()
        # 读取问题模板
        with open(self.path_info + "./data/question/question_classification.txt", "r", encoding="utf-8") as f:
            question_mode_list = f.readlines()
        self.question_mode_dict = {}
        for one_mode in question_mode_list:
            mode_id, mode_str = str(one_mode).strip().split(":")
            self.question_mode_dict[int(mode_id)] = str(mode_str)
        # print(self.question_mode_dict)

        # 创建问题模板对象
        self.questiontemplate = QuestionTemplate()

    def dopredict(self, question):  # 调用分类模型判断问题类别
        model = joblib.load(self.path_info + "./model/question_classifier.model")
        question = [" ".join(list(jieba.cut(question)))]
        print("分词结果是：{0}".format(question))
        test_data = self.tv.transform(question).toarray()
        # print("分类器的输入是：{0}".format(test_data))
        y_predict = model.predict(test_data)[0]
        # print("question type:",y_predict)
        return y_predict

    def question_posseg(self):
        clean_question = re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+", "", self.raw_question)
        self.clean_question = clean_question
        question_seged = posseg.cut(str(clean_question))

        result = []
        question_word, question_flag = [], []
        for w in question_seged:  # 词性标注的结果
            tmp_word = f"{w.word}/{w.flag}"
            result.append(tmp_word)
            word, flag = w.word, w.flag
            question_word.append(str(word).strip())
            question_flag.append(str(flag).strip())

        self.question_word = question_word
        self.question_flag = question_flag

        return result

    def get_question_template(self):
        # 将问题抽象成模板
        for item in ['nr', 'nm', 'ng']:
            while item in self.question_flag:
                ix = self.question_flag.index(item)
                self.question_word[ix] = item
                self.question_flag[ix] = item+"ed"
        # 将问题转化字符串
        str_question = "".join(self.question_word)
        print("抽象问题为：", str_question)
        # 通过分类器获取问题模板编号
        question_template_num = int(self.dopredict(str_question))
        print("使用模板编号：", question_template_num)
        question_template = self.question_mode_dict[question_template_num]
        print("问题模板：", question_template)
        question_template_id_str = str(question_template_num)+"\t"+question_template
        return question_template_id_str

    def query_template(self):
        # 调用问题模板类中查询答案的方法
        try:
            template_num = int(self.question_template_id_str.split("\t")[0])
            print(template_num)
            if template_num != 7:
                answer = self.questiontemplate.get_question_answer(self.pos_question, self.question_template_id_str)
            else:
                answer = self.questiontemplate.get_question_answer(self.pos_question, self.question_template_id_str)[0]
        except:
            answer = "小球暂未学习到问题的答案……期待我的成长吧！"
        return answer

    def question_process(self, question):
        self.raw_question = str(question).strip()  # 原始问题
        self.pos_question = self.question_posseg()  # 词性标注后的问题
        print("词性标注结果是：{0}".format(self.pos_question))
        self.question_template_id_str = self.get_question_template()  # 得到问题模板

        self.answer = self.query_template()  # 查询图数据库，得到答案


if __name__ == "__main__":
    # 查询答案测试【0-19】
    questionlist = ["电影肖申克的救赎的评分是？",
                    "盗梦空间的上映时间是",
                    "星际穿越是什么类型的电影？",
                    "霸王别姬主要讲什么故事",
                    "阿甘正传有哪些演员出演？",
                    "霸王别姬的导演是谁",
                    "张国荣拍过哪些剧情电影？",
                    "周星驰有哪些电影？",
                    "张国荣拍的评分大于9的电影有哪些？",
                    "张国荣拍的评分小于9的电影有哪些？",
                    "赵文瑄演过哪些类型的电影？",
                    "张国荣和张丰毅合作的电影有哪些？",
                    "周星驰拍过多少电影？",
                    "张国荣电影的平均分是多少",
                    "肖申克的救赎排第几",
                    "肖申克的救赎用什么语言拍的？",
                    "盗梦空间看不看",
                    "霸王别姬有多长？",
                    "熔炉的主要奖项",
                    "霸王别姬在哪国拍的"]

    # 问题查询测试【20-24】
    questionlist += ["爱情电影有多少",
                     "大于9的有多少",
                     "低于8的有多少",
                     "有多少部是中国大陆制作的",
                     "英语电影有多少"]

    # questionlist = ["张国荣演了什么电影？"]
    answerlist = []
    for q in questionlist:
        tmp = question()
        tmp.question_process(q)
        answerlist.append(tmp.answer)

    for i in range(len(questionlist)):
        print(questionlist[i], answerlist[i])
