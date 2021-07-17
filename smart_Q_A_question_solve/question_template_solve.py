# 根据问题模板查询neo4j数据库，获得问题答案
# 演员、导演、制片人实体是否可以合并为person类？
# 0627 新增问题类的处理 【20-25】
"""
【提问模板】
0:nm 评分
1:nm 上映时间
2:nm 类型
3:nm 简介
4:nm 演员列表
5:nm 导演/制片
6:nr ng 电影作品
7:nr 电影作品
8:nr 参与 评分大于 x
9:nr 参与 评分小于 x
10:nr 电影类型
11:nr nr 合作 电影列表
12:nr 电影数量
13:nr 作品平均分
14:nm 排名
15:nm 语言
16:nm 推荐
17:nm 长度
18:nm 主要奖项
19:nm 国家
20:ng 电影数量
21:大于x 数量
22:小于x 数量
23:nc 电影数量
24:nl 电影数量
"""
import re

from py2neo import Graph


class Query:  # 连接图数据库
    def __init__(self):
        host = "http://120.53.2.37:7474"
        username = "neo4j"
        password = "981015"
        self.graph = Graph(host, user=username, password=password)

    def search(self, cql):  # 运行查询语句
        result = []
        find_rela = self.graph.run(cql)
        # list(find_rela) 形如 [Record({'m.score': '9.7'})]
        for i in find_rela:
            result.append(i.items()[0][1])
        return result


class QuestionTemplate:
    def __init__(self):
        self.q_template_dict = {  # 模板编号：查询方法
            0: self.get_movie_rating,
            1: self.get_movie_release_date,
            2: self.get_movie_type,
            3: self.get_movie_introduction,
            4: self.get_movie_actorlist,
            5: self.get_director_or_producer,
            6: self.get_people_type_movie,
            7: self.get_people_movielist,
            8: self.get_people_movie_rating_larger,
            9: self.get_people_movie_rating_smaller,
            10: self.get_people_movietype,
            11: self.get_pwithp_movielist,
            12: self.get_people_movienum,
            13: self.get_people_average_movierating,
            14: self.get_movie_rank,
            15: self.get_movie_language,
            16: self.get_movie_recommend,
            17: self.get_movie_length,
            18: self.get_movie_brief_prize,
            19: self.get_movie_country,
            20: self.get_genre_num,
            21: self.get_rating_larger,
            22: self.get_rating_smaller,
            23: self.get_country_num,
            24: self.get_language_num,
        }

        self.graph = Query()

    def get_question_answer(self, question, template):
        """
        :param question: 词性标注后的问题 形如 ['陈凯歌/nr', '导/v', '了/ul', '哪些/r', '爱情/ng', '电影/n']
        :param template: 模板序号+模板内容 形如 "0\tnm 评分"
        :return:
        """
        templatelist = str(template).strip().split("\t")
        if len(templatelist) != 2:
            print("出错！问题模板格式不正确！")
            error_msg = "出错！问题模板格式不正确！"
            return error_msg
        template_id, template_str = int(templatelist[0]), str(templatelist[1])
        self.template_id = template_id
        self.template_str2list = template_str.split()  # 转化为列表，例如 nr 作品平均分 → ["nr", "作品平均分"]

        # 预处理问题
        question_word, question_flag = [], []
        for wpair in question:
            word, flag = wpair.split("/")
            question_word.append(str(word).strip())
            question_flag.append(str(flag).strip())
        self.question_word = question_word
        self.quesiton_flag = question_flag
        self.raw_question = question

        # 根据问题模板进行对应的查询，获得答案
        if template_id != 7:
            ans = self.q_template_dict[template_id]()
        else:
            ans = self.q_template_dict[template_id]("")
        return ans

    def get_movie_name(self):  # 获取电影名称
        tag_index = self.quesiton_flag.index("nm")
        movie_name = self.question_word[tag_index]
        return movie_name

    def get_name(self, type_str):  # 获得原实体内容
        """
        :param type_str: 实体类型，nm,nr,ng
        :return: result: 原实体内容，例如['章子怡']
        """
        result = []
        for i, flag in enumerate(self.quesiton_flag):
            if flag == str(type_str):
                result.append(self.question_word[i])
        return result

    def get_num_x(self):  # 获得查询中的数字
        x = re.sub(r'\D', "", "".join(self.question_word))
        return x

    def get_noinfo_word(self, basicinfo):  # 数据库没有相关信息的提示语
        returninfo = "小球的数据库里没有" + str(basicinfo) + "的相关信息，请重新输入要查询的内容！"
        return returninfo

    def get_movie_rating(self):  # 0:nm 评分
        print("问题模板是【0:nm 评分】")

        # 先获取电影名称
        movie_name = self.get_movie_name()
        cql = f"match (m:movie) where m.name contains '{movie_name}' return m.score"
        print("cql查询语句是：{0}".format(cql))

        ans = self.graph.search(cql)
        if len(ans) > 0:
            ans = float(ans[0])
            ans = round(ans, 2)
        else:
            final_ans = self.get_noinfo_word(movie_name)
            return final_ans

        print("得分查询结果是：{0}".format(ans))

        cql = f"match (m:movie) where m.name contains '{movie_name}' return m.evaluators"
        print("cql查询语句是：{0}".format(cql))
        ans_evaluators = int(self.graph.search(cql)[0])
        print("评分人数查询结果是：{0}".format(ans_evaluators))

        final_ans = movie_name + "电影评分为" + str(ans) + "分，评分人数为" + str(ans_evaluators) + "人。"
        return final_ans

    def get_movie_release_date(self):  # 1:nm 上映时间
        print("问题模板是【1:nm 上映时间】")
        movie_name = self.get_movie_name()
        cql = f"match (m:movie) where m.name contains '{movie_name}' return m.release_date"
        print("cql查询语句是：{0}".format(cql))

        ans = self.graph.search(cql)
        if len(ans) > 0:
            ans = ans[0]
        else:
            final_ans = self.get_noinfo_word(movie_name)
            return final_ans

        print("上映时间查询结果是：{0}".format(ans))
        final_ans = movie_name + "的上映时间是" + str(ans) + "。"
        return final_ans

    def get_movie_type(self):  # 2:nm 类型
        print("问题模板是【2:nm 类型】")
        movie_name = self.get_movie_name()
        cql = f"match (m:movie)-[r:belong_to]->(b) where m.name contains '{movie_name}' return b.name"
        print("cql查询语句是：{0}".format(cql))

        ans = list(self.graph.search(cql))
        if len(ans) > 0:
            ans = "、".join(ans)
        else:
            final_ans = self.get_noinfo_word(movie_name)
            return final_ans

        print("电影类型的查询结果是：{0}".format(ans))

        final_ans = movie_name + "属于" + str(ans) + "类型的电影。"
        return final_ans

    def get_movie_introduction(self):  # 3:nm 简介
        print("问题模板是【3:nm 简介】")
        movie_name = self.get_movie_name()
        cql = f"match (m:movie) where m.name contains '{movie_name}' return m.brief_introduction"
        print("cql查询语句是：{0}".format(cql))

        ans = self.graph.search(cql)
        if len(ans) > 0:
            ans = str(ans[0])
        else:
            final_ans = self.get_noinfo_word(movie_name)
            return final_ans

        ans = ans.replace(" ", "")  # 删去多余的空格
        print("电影简介的查询结果是：{0}".format(ans))

        final_ans = movie_name + "主要讲述了" + str(ans)
        return final_ans

    def get_movie_actorlist(self):  # 4:nm 演员列表
        print("问题模板是【4:nm 演员列表】")
        movie_name = self.get_movie_name()
        cql = f"match(a:actor)-[r:acted_in]->(m:movie) where m.name contains '{movie_name}' return a.name"
        print("cql查询语句是：{0}".format(cql))

        ans = list(self.graph.search(cql))
        if len(ans) > 0:
            n = len(ans)
            for index in range(n):
                blank_index = ans[index].find(" ")  # 空格的位置
                if blank_index != -1:
                    ans[index] = ans[index][:blank_index]  # 只返回中文信息
            ans = "、".join(ans)
        else:
            final_ans = self.get_noinfo_word(movie_name)
            return final_ans

        print("电影演员列表的查询结果是：{0}".format(ans))

        final_ans = movie_name + "由" + str(ans) + "等演员主演。"
        return final_ans

    def get_director_or_producer(self):  # 5:nm 导演/制片
        print("问题模板是【5:nm 导演/制片】")
        movie_name = self.get_movie_name()
        cql1 = f"match (d:director)-[r:directed]->(m:movie) where m.name contains '{movie_name}' return d.name"
        cql2 = f"match (p:producer)-[r:produced]->(m:movie) where m.name contains '{movie_name}' return p.name"
        print("cql查询语句是：\n{0}\n{1}".format(cql1, cql2))

        ans1 = self.graph.search(cql1)
        ans2 = self.graph.search(cql2)
        if len(ans1) > 0 and len(ans2) > 0:
            if len(ans1) > 0:
                ans1 = str(ans1[0])
                blank_index = ans1.find(" ")
                if blank_index != -1:
                    ans1 = ans1[:blank_index]
            else:
                ans1 = ""
            if len(ans2) > 0:
                ans2 = str(ans2[0])
                blank_index = ans2.find(" ")
                if blank_index != -1:
                    ans2 = ans2[:blank_index]
            else:
                ans2 = ""
        else:
            final_ans = self.get_noinfo_word(movie_name)
            return final_ans

        print("电影导演查询结果是：{0}".format(ans1))
        print("电影制片人查询结果是：{0}".format(ans2))

        final_ans = movie_name + "的导演是" + str(ans1) + "，制片人是" + str(ans2) + "。"
        return final_ans

    def get_people_type_movie(self):  # 6:nr ng 电影作品
        print("问题模板是【6:nr ng 电影作品】")
        people_name = str(self.get_name("nr")[0])  # 单个查询只能有一个nr
        movietype = self.get_name("ng")  # 可以有多个类型限制

        # 查询该人物的电影作品名称（不做类型限制），电影人可以同时是演员、导演、制片人
        cql = f"match (a:actor)-[]->(m:movie) where a.name contains '{people_name}' return m.name"
        resultlist = list(self.graph.search(cql))

        cql = f"match (d:director)-[]->(m:movie) where d.name contains '{people_name}' return m.name"
        resultlist += list(self.graph.search(cql))

        cql = f"match (p:producer)-[]->(m:movie) where p.name contains '{people_name}' return m.name"
        resultlist += list(self.graph.search(cql))

        if len(resultlist) == 0:
            final_ans = self.get_noinfo_word(people_name)
            return final_ans

        # 查询类型电影
        result = []
        for movie_name in resultlist:
            movie_name = str(movie_name).strip()
            cql = f"match (m:movie)-[r:belong_to]->(g) where m.name contains '{movie_name}'return g.name"
            tmp_type = self.graph.search(cql)
            if tmp_type == 0:  # 无类型信息
                continue
            for t in tmp_type:
                if t in movietype:  # 符合类型查询要求
                    result.append(movie_name)

        if len(result) == 0:
            final_ans = self.get_noinfo_word(people_name)
            return final_ans

        n = len(result)
        for i in range(n):
            blank_index = result[i].find(" ")
            if blank_index != -1:
                result[i] = result[i][:blank_index]
        ans = "、".join(result)
        print("电影人特定类型的电影作品查询结果是：".format(ans))
        typestr = str("、".join(movietype))
        final_ans = people_name + "参与的" + typestr + "电影有：\n" + ans + "。"
        return final_ans

    def get_people_movielist(self, peoplename):  # 7:nr 电影作品
        print("问题模板是【7:nr 电影作品】")
        if len(peoplename) == 0:  # 不是中间结果需求
            people_name = str(self.get_name("nr")[0])  # 单个查询只能有一个nr
        else:
            people_name = peoplename
        # 查询该人物的电影作品名称（不做类型限制），电影人可以同时是演员、导演、制片人
        cql = f"match (a:actor)-[]->(m:movie) where a.name contains '{people_name}' return m.name"
        resultlist = list(self.graph.search(cql))

        cql = f"match (d:director)-[]->(m:movie) where d.name contains '{people_name}' return m.name"
        resultlist += list(self.graph.search(cql))

        cql = f"match (p:producer)-[]->(m:movie) where p.name contains '{people_name}' return m.name"
        resultlist += list(self.graph.search(cql))
        if len(resultlist) == 0:
            final_ans = self.get_noinfo_word(people_name)
            return final_ans, resultlist

        n = len(resultlist)
        for i in range(n):
            blank_index = resultlist[i].find(" ")
            if blank_index != -1:
                resultlist[i] = resultlist[i][:blank_index]

        ans = "、".join(resultlist)
        print("电影人的电影作品查询结果是：{0}".format(ans))
        final_ans = str(people_name) + "参与过" + str(ans) + "等电影。"
        return final_ans, resultlist  # resultlist 作为中间结果提供给其他查询

    def get_people_movie_rating_larger(self):  # 8:nr 参与 评分大于 x
        print("问题模板是【8:nr 参与 评分大于 x】")
        people_name = str(self.get_name("nr")[0])  # 单个查询只能有一个nr
        x = self.get_num_x()  # 获得查询中的数字

        # 查询该人物的电影作品名称（不做类型限制），电影人可以同时是演员、导演、制片人
        cql = f"match (a:actor)-[]->(m:movie) where a.name contains '{people_name}' and m.score>={x} return m.name"
        resultlist = list(self.graph.search(cql))

        cql = f"match (d:director)-[]->(m:movie) where d.name contains '{people_name}' and m.score>={x} return m.name"
        resultlist += list(self.graph.search(cql))

        cql = f"match (p:producer)-[]->(m:movie) where p.name contains '{people_name}' and m.score>={x} return m.name"
        resultlist += list(self.graph.search(cql))

        if len(resultlist) == 0:
            final_ans = self.get_noinfo_word(people_name)
            return final_ans

        n = len(resultlist)
        for i in range(n):
            blank_index = resultlist[i].find(" ")
            if blank_index != -1:
                resultlist[i] = resultlist[i][:blank_index]

        ans = "、".join(resultlist)
        print("符合评分限制的电影作品查询结果是：{0}".format(ans))

        final_ans = people_name + "参与的电影评分大于" + x + "分的有" + ans + "等。"

        return final_ans

    def get_people_movie_rating_smaller(self):  # 9:nr 参与 评分小于 x
        print("问题模板是【9:nr 参与 评分小于 x】")
        people_name = str(self.get_name("nr")[0])  # 单个查询只能有一个nr
        x = self.get_num_x()  # 获得查询中的数字

        # 查询该人物的电影作品名称（不做类型限制），电影人可以同时是演员、导演、制片人
        cql = f"match (a:actor)-[]->(m:movie) where a.name contains '{people_name}' and m.score<={x} return m.name"
        resultlist = list(self.graph.search(cql))

        cql = f"match (d:director)-[]->(m:movie) where d.name contains '{people_name}' and m.score<={x} return m.name"
        resultlist += list(self.graph.search(cql))

        cql = f"match (p:producer)-[]->(m:movie) where p.name contains '{people_name}' and m.score<={x} return m.name"
        resultlist += list(self.graph.search(cql))

        if len(resultlist) == 0:
            final_ans = self.get_noinfo_word(people_name)
            return final_ans

        n = len(resultlist)
        for i in range(n):
            blank_index = resultlist[i].find(" ")
            if blank_index != -1:
                resultlist[i] = resultlist[i][:blank_index]

        ans = "、".join(resultlist)
        print("符合评分限制的电影作品查询结果是：{0}".format(ans))

        final_ans = people_name + "参与的电影评分小于" + x + "分的有" + ans + "等。"

        return final_ans

    def get_people_movietype(self):  # 10:nr 电影类型
        print("问题模板是【10:nr 电影类型】")
        people_name = str(self.get_name("nr")[0])  # 单个查询只能有一个nr

        # 查询该人物的电影作品名称（不做类型限制），电影人可以同时是演员、导演、制片人
        cql = f"match (a:actor)-[]->(m:movie) where a.name contains '{people_name}' return m.name"
        resultlist = list(self.graph.search(cql))

        cql = f"match (d:director)-[]->(m:movie) where d.name contains '{people_name}' return m.name"
        resultlist += list(self.graph.search(cql))

        cql = f"match (p:producer)-[]->(m:movie) where p.name contains '{people_name}' return m.name"
        resultlist += list(self.graph.search(cql))

        if len(resultlist) == 0:
            final_ans = self.get_noinfo_word(people_name)
            return final_ans

        result = []
        for movie_name in resultlist:
            movie_name = str(movie_name).strip()
            cql = f"match (m:movie)-[r:belong_to]->(g) where m.name contains '{movie_name}' return g.name"
            tmp_type = self.graph.search(cql)
            if len(tmp_type) == 0:  # 缺少类型信息
                continue
            for t in tmp_type:
                if t not in set(result):
                    result.append(t)
        if len(result) == 0:
            final_ans = self.get_noinfo_word(people_name)
            return final_ans

        ans = "、".join(result)
        print("电影人参与的电影作品类型查询结果为：{0}".format(ans))
        final_ans = people_name + "参与的电影有" + ans + "等类型。"
        return final_ans

    def get_pwithp_movielist(self):  # 11:nr nr 合作 电影列表
        # nr 可以大于等于2个
        print("问题模板是【11:nr nr 合作 电影列表】")
        people_namelist = self.get_name('nr')
        resultlist = []  # 合作的电影列表
        for i, people_name in enumerate(people_namelist):
            tmpstr, tmplist = self.get_people_movielist(people_name)  # people_name 参演的电影列表
            if i == 0:
                resultlist = tmplist
            resultlist = list(set(resultlist).intersection(tmplist))
        if len(resultlist) == 0:
            final_ans = "小球的数据库里没有符合条件的电影信息，请重新输入查询内容！"
            return final_ans

        n = len(resultlist)
        for i in range(n):
            blank_index = resultlist[i].find(" ")
            if blank_index != -1:
                resultlist[i] = resultlist[i][:blank_index]

        ans = "、".join(resultlist)
        print("合作电影查询结果是：{0}".format(ans))

        final_ans = people_namelist[0]
        for i in range(1, len(people_namelist)):
            final_ans += "和" + str(people_name)

        final_ans += "合作的电影有" + str(ans) + "。"
        return final_ans

    def get_people_movienum(self):  # 12:nr 电影数量
        print("问题模板是【12:nr 电影数量】")
        people_name = str(self.get_name("nr")[0])  # 只能有一个nr

        tmpstr, movielist = self.get_people_movielist(people_name)
        movienum = len(movielist)
        print("参与电影数量查询结果是：{0}".format(str(movienum)))

        final_ans = people_name + "参与过" + str(movienum) + "部电影。"
        return final_ans

    def get_people_average_movierating(self):  # 13:nr 作品平均分
        print("问题模板是【13:nr 作品平均分】")
        people_name = str(self.get_name("nr")[0])

        tmpstr, movielist = self.get_people_movielist(people_name)
        tot_score = 0
        cnt = 0
        for movie_name in movielist:
            cql = f"match (m:movie) where m.name contains '{movie_name}' return m.score"
            tmpscore = self.graph.search(cql)
            if len(tmpscore) > 0:  # 有评分记录
                tot_score += float(tmpscore[0])
                cnt += 1
        if cnt > 0:
            ans = tot_score / cnt
            ans = round(ans, 2)
            print("电影人电影作品平均分查询结果是：{0}".format(ans))
            final_ans = people_name + "参与的作品平均分为" + str(ans) + "分。"
        else:
            final_ans = "小球的数据库里没有符合条件的" + str(people_name) + "的作品，请重新输入查询内容！"

        return final_ans

    def get_movie_rank(self):  # 14:nm 排名
        print("问题模板是【14:nm 排名】")

        movie_name = self.get_movie_name()
        cql = f"match (m:movie) where m.name contains '{movie_name}' return m.rank"
        resultlist = self.graph.search(cql)
        if len(resultlist) > 0:  # 在数据库中
            ans = resultlist[0]
            print("电影排名的查询结果是：{0}".format(ans))
            final_ans = "电影" + str(movie_name) + "在豆瓣网Top250中排名是" + str(ans) + "。"
        else:
            final_ans = self.get_noinfo_word(movie_name)

        return final_ans

    def get_movie_language(self):  # 15:nm 语言
        print("问题模板是【15:nm 语言】")
        movie_name = self.get_movie_name()
        cql = f"match (m:movie)-[r:spoke_in]->(la) where m.name contains '{movie_name}' return la.name"
        resultlist = self.graph.search(cql)
        if len(resultlist) > 0:  # 在数据库中
            ans = "、".join(resultlist)
            print("电影语言的查询结果是：{0}".format(ans))
            final_ans = "电影" + str(movie_name) + "的拍摄语言是" + str(ans) + "。"
        else:
            final_ans = self.get_noinfo_word(movie_name)
        return final_ans

    def get_movie_recommend(self):  # 16:nm 推荐
        print("问题模板是【16:nm 推荐】")
        movie_name = self.get_movie_name()
        cql = f"match (m:movie) where m.name contains '{movie_name}' return m.recommend"
        ans = self.graph.search(cql)
        if len(ans) > 0:  # 在数据库中
            ans = str(ans[0])
            final_ans = ans
        else:
            final_ans = self.get_noinfo_word(movie_name)
        return final_ans

    def get_movie_length(self):  # 17:nm 长度
        print("问题模板是【17:nm 长度】")
        movie_name = self.get_movie_name()
        cql = f"match (m:movie) where m.name contains '{movie_name}' return m.length"
        ans = self.graph.search(cql)
        if len(ans) > 0:
            ans = str(ans[0])
            final_ans = "电影" + str(movie_name) + "的长度是" + ans + "。"
        else:
            final_ans = self.get_noinfo_word(movie_name)
        return final_ans

    def get_movie_brief_prize(self):  # 18:nm 主要奖项
        print("问题模板是【18:nm 主要奖项】")
        movie_name = self.get_movie_name()
        cql = f"match (m:movie) where m.name contains '{movie_name}' return m.brief_prize"
        ans = self.graph.search(cql)
        if len(ans) > 0:
            ans = str(ans[0])
            final_ans = "电影" + str(movie_name) + "获得的主要奖项有：\n" + ans
        else:
            final_ans = self.get_noinfo_word(movie_name)

        return final_ans

    def get_movie_country(self):  # 19:nm 国家
        print("问题模板是【19:nm 国家】")
        movie_name = self.get_movie_name()
        cql = f"match (m:movie)-[r:made_in]->(co) where m.name contains '{movie_name}' return co.name"
        ans = self.graph.search(cql)
        if len(ans) > 0:
            ans = "、".join(ans)
            final_ans = "电影" + str(movie_name) + "的制作地区是" + str(ans) + "。"
        else:
            final_ans = self.get_noinfo_word(movie_name)

        return final_ans

    def get_genre_num(self):  # 20:ng 电影数量
        print("问题模板是【20:ng 电影数量】")
        genrename = str(self.get_name("ng")[0])
        cql = f"match (m:movie)-[r:belong_to]->(g:genre) where g.name='{genrename}' return m.name"
        ans = self.graph.search(cql)
        ans = len(ans)
        final_ans = genrename + "类型的电影有" + str(ans) + "部。"
        return final_ans

    def get_rating_larger(self):  # 21:大于x 数量
        print("问题模板是【21:大于x 数量】")
        x = self.get_num_x()
        cql = f"match (m:movie) where m.score>={x} return m.name"
        ans = self.graph.search(cql)
        ans = len(ans)
        final_ans = "评分大于" + str(x) + "分的电影共有" + str(ans) + "部。"
        return final_ans

    def get_rating_smaller(self):  # 22:小于x 数量
        print("问题模板是【22:小于x 数量】")
        x = self.get_num_x()
        cql = f"match (m:movie) where m.score<={x} return m.name"
        ans = self.graph.search(cql)
        ans = len(ans)
        final_ans = "评分小于" + str(x) + "分的电影共有" + str(ans) + "部。"
        return final_ans

    def get_country_num(self):  # 23:nc 电影数量
        print("问题模板是【23:nc 电影数量】")
        countryname = str(self.get_name("nc")[0])
        cql = f"match (m:movie)-[r:made_in]->(c:country) where c.name='{countryname}' return m.name"
        ans = self.graph.search(cql)
        ans = len(ans)
        final_ans = countryname + "制作的电影有" + str(ans) + "部。"
        return final_ans

    def get_language_num(self):  # 24:nl 电影数量
        print("问题模板是【24:nl 电影数量】")
        languagename = str(self.get_name("nl")[0])
        cql = f"match (m:movie)-[r:spoke_in]->(la:language) where la.name='{languagename}' return m.name"
        ans = self.graph.search(cql)
        ans = len(ans)
        final_ans = languagename + "电影有" + str(ans) + "部。"
        return final_ans


if __name__ == "__main__":

    # 进行cql查询测试
    # tmp = Query()
    # ans = tmp.search("match (m:movie) where m.name contains '肖申克的救赎' return m.score")
    # print(ans)

    # 进行模板查询测试
    tmp = QuestionTemplate()
    ans = tmp.get_question_answer(['霸王别姬/nm', '由/p', '哪些/r', '演员/n', '主演/n'], "4\tnm 演员列表")
    print(ans)