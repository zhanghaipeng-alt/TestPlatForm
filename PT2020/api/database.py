import pymysql
import pandas as pd

class ClientDataBase(object):

    def __init__(self, host, port, username, password, DATABASE, charset='utf-8'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.DATABASE = DATABASE
        self.charset = charset

    def connect_mysql(self):
        '''
        建立MySQL连接
        :return:
        '''
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            db=self.DATABASE
        )

        cursor = conn.cursor()

        return conn, cursor

    # def connect_oracle(self):
    #     conn = cx_Oracle.connect(self.username, self.password, f'{self.host}:{self.port}/{self.DATABASE}')
    #     cursor = conn.cursor()
    #     return conn, cursor
    #
    # def select_sql_oracle(self, sql):
    #     conn, cursor = self.connect_oracle()
    #     cursor.execute(sql)
    #     data = cursor.fetchall()
    #     return data


    def select_sql(self, sql):
        '''
        根据传入的sql语句返回一个结果列表
        :param sql:
        :return:
        '''
        try:
            conn, cursor = self.connect_mysql()
            cursor.execute(sql)
            datas = cursor.fetchall()
            cols = cursor.description
        except Exception as e:
            conn.rollback(e)
        conn.close()

        result = []
        for data in datas:
            dic = {}
            for i in range(len(cols)):
                dic[cols[i][0]] = data[i]
            result.append(dic)

        return result

    def select_user_by_phone(self, mobile):
        '''
        根据上传的身份证查询用户信息
        :param phone:
        :return:
        '''
        str = '''
            select userID, userTypeID, mobile, is_bindmobile, status, idno, joyoCode, parentJoyoCode, branchID, branchCode, name, new_nick_name, staff_id, staff_name
            from user 
            where mobile in ({mobile});
        '''.format(mobile=mobile)
        # print(str)
        # try:
        #     conn, cursor = self.connect_mysql()
        #     cursor.execute(str)
        #     datas = cursor.fetchall()
        #     cols = cursor.description
        # except Exception as e:
        #     conn.rollback(e)
        # conn.close()
        #
        # result = []
        # for data in datas:
        #     dic = {}
        #     for i in range(len(cols)):
        #         dic[cols[i][0]] = data[i]
        #     result.append(dic)
        #
        result = self.select_sql(str)
        return result

    def select_user_by_idno(self, idno):
        '''
        根据传入的身份证号码，获取用户信息
        :param idno:
        :return:
        '''
        str = '''
            select userID, userTypeID, mobile, is_bindmobile, status, idno, joyoCode, parentJoyoCode, branchID, branchCode, name, new_nick_name, staff_id, staff_name
            from user 
            where idno in ({idno});
        '''.format(idno=idno)

        # try:
        #     conn, cursor = self.connect_mysql()
        #     cursor.execute(str)
        #     datas = cursor.fetchall()
        #     cols = cursor.description
        # except Exception as e:
        #     conn.rollback(e)
        # conn.close()
        #
        # result = []
        # for data in datas:
        #     dic = {}
        #     for i in range(len(cols)):
        #         dic[cols[i][0]] = data[i]
        #     result.append(dic)
        result = self.select_sql(str)
        return result

    def select_user_by_idandmobile(self, mobile, idno):
        '''
        根据提交的id和身份证号码查询用户信息
        :return:
        '''
        str = '''
                    select userID, userTypeID, mobile, is_bindmobile, status, idno, joyoCode, parentJoyoCode, branchID, branchCode, name, new_nick_name, staff_id, staff_name
                    from user 
                    where idno in ({idno}) and mobile in ({mobile});
                '''.format(idno=idno, mobile=mobile)

        # try:
        #     conn, cursor = self.connect_mysql()
        #     cursor.execute(str)
        #     datas = cursor.fetchall()
        #     cols = cursor.description
        # except Exception as e:
        #     conn.rollback(e)
        # conn.close()
        #
        # result = []
        # for data in datas:
        #     dic = {}
        #     for i in range(len(cols)):
        #         dic[cols[i][0]] = data[i]
        #     result.append(dic)
        result = self.select_sql(str)
        return result

    def B2B_search(self, idno):
        '''
        根据身份证号码查询B2B信息
        :return:
        '''
        str = '''
            SELECT DISTRIBUTOR_ID, DISTRIBUTOR_NAME, xj_fz || xj_rx as 当前级别, xj_fzj || xj_rxj as 获奖级别, grxf as 个人销售, pw as 小市场销售, zwall as 当月销售累计 
            FROM TS_JS_LVL_202101A WHERE DISTRIBUTOR_ID = {idno};
        '''.format(idno=idno)
        result = self.select_sql_oracle(str)
        return result

if __name__ == '__main__':
    pass

