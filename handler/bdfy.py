# -*- coding: utf-8 -*-
# shujuchuli
import re
import datetime
import time,hmac
from base import BaseHandler
from app.model import Passport,User,Device,CorpDevice,UserDevice,CorpUser,Warn,Supply,DeliverOrder,Consume
from base import RestHandler
from sqlalchemy import func
import tornado.gen
import tornado.httpclient
current_user = 'bdfy'
today = datetime.datetime.today()
year = str(today.year)[-2:]
month = str(today.month).zfill(2)
day = str(today.day).zfill(2)
projectname = '北大妇幼'
field_list = 'device_id,weight1,height1,pressure1,temp1,valve1,warn'

# 获取设备数据
class BDFY(RestHandler):
    def permission(self):
        'all allowd'

    def login(self):
        self.render("bdfy/login.html", projectname='北大妇幼')

    def dologin(self):
        username = self.get_argument('username', '')
        ret = self.session.query(Passport).filter_by(username=username,type='normal').all()
        if len(ret) > 0:
            self.set_secure_cookie("user", str(ret[0].user))
            self.redirect('overview')
        else:
            self.finish('login failed')

    def logout(self):
        self.set_secure_cookie("user", '')
        self.redirect('login')

    def overview(self):
        cuser = self.get_secure_cookie("user")
        warnnu = 0
        rows = []
        if cuser == '':
            self.redirect('login')
        ret = self.session.query(CorpUser).filter_by(user=cuser).first()
        if ret.role == 'admin': #admin获取公司所有设备
            devices = self.session.query(CorpDevice.device).filter_by(corp=ret.corp).all()
        else: #普通user获取自己名下的设备
            devices = self.session.query(UserDevice.device).filter_by(user=cuser).all()
        for d in devices: 
            sql = 'select '+field_list+' from z_device_data_{} where device_id = :id order by id desc limit 1'.format(year+month)
            ret = self.session.execute(sql, {'id': d[0]}).fetchall()
            if int(ret[0].warn) != 0:
                warnnu += 1
            rows.append(ret[0])
        #self.finish(str(rows))
        self.render("bdfy/overview.html", projectname='北大妇幼', rows=rows, warnnu=warnnu)

    def detail(self): #查询摸个时间段数据 一个月之内
        device_id = self.get_argument('device_id','')
        if not device_id:
            self.finish({'code': 1, 'msg': u'device_id 不能为空'})
            return
        data = []
        warnnu = 0
        sql = "select "+field_list+",time from z_device_data_{ym} where device_id={device_id} order by time desc limit 50".format(
              ym=year+month, device_id=device_id)
        rows = self.session.execute(sql).fetchall()

        for r in rows:
            rtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r[7]))
            if int(r[6]) != 0:
                warnnu += 1
            l = list(r[1:7])
            l.append(rtime)
            data.append(l) 
        self.render("bdfy/detail.html", projectname='北大妇幼', rows=data, warnnu=warnnu)

    @tornado.gen.coroutine
    def gen_sql(self,field,year,month,i,b_time,e_time,remain_days,device_cpuid,data):
        remain_amounts = "select {} from z_device_data_{first} where device_id={device_id}" \
                         " order by z_device_data_{first}.create desc  " \
                         "limit 1".format(field, first=year + month, device_id=i.id)  # 最新数据
        rows = self.session.execute(remain_amounts)
        a = rows.fetchone()  # 最新一条
        if not a:
            return
        remain_amounts = a[0]
        a = {}
        avg_consume = self.session.query(func.avg(Consume.consume)).filter(Consume.type == 'month',
                                                                           Consume.cpu_id == i.cpu_id,  # 设备唯一cpu id
                                                                           Consume.time >= b_time,
                                                                           Consume.time < e_time,
                                                                           Consume.consume != 0.00).first()  # 7天的评均消耗数据数据
        if not avg_consume[0]:
            return
        remains = round(float(remain_amounts) / float(avg_consume[0]))  # 四射侮辱 ，还能用多少天
        if remains <= remain_days and not device_cpuid:  # 所有天数
            a['device_id'] = i.id
            a['remain_days'] = remains
            a['aver-day-consumption'] = avg_consume[0]
            a['name'] = i.name
            data.append(a)
        else:  # 差一天天数
            a['device_id'] = i.id
            a['remain_days'] = remains
            a['aver-day-consumption'] = avg_consume[0]
            a['name'] = i.name
            data.append(a)


    @tornado.gen.coroutine
    def inner(self):
        field = self.get_argument('field', 'weight1')  # 重量
        remain_days = int(self.get_argument('remain_days', 30))  # 剩余天数
        device_cpuid = self.get_argument('cpu_id', '')  # 设单台的天数
        device = self.get_query()
        q = self.session.query(Device).filter(Device.id.in_(device))
        if device_cpuid:
            q = q.filter(Device.cpu_id == device_cpuid)
        data = []
        timeArray = time.strptime(str(today.year)+'-'+month+day, "%Y-%m-%d")
        timestamp = int(time.mktime(timeArray))
        e_time = timestamp
        b_time = timestamp - 7 * 24 * 3600
        for i in q:
            yield self.gen_sql(field,year,month,i,b_time,e_time,remain_days,device_cpuid,data)
            # dic_yie = yield self.inner()
        data = [i for i in data]
        count = len(data)
        dic = {'code': 0, 'count': count, 'data': data}
        raise tornado.gen.Return(dic)

    @tornado.gen.coroutine
    def delivery_remind_done(self):
        dic_yie = yield self.inner()
        raise tornado.gen.Return(dic_yie)

    @tornado.gen.coroutine
    def delivery_remind(self):
        result = yield self.delivery_remind_done()
        self.finish(result)

    def time_format_change(self,timestamp):
        timeArray = time.localtime(timestamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        timeArray = time.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
        year = str(timeArray.tm_year)[-2:]
        month = "%02d" %timeArray.tm_mon
        return year,month

    def week_data(self):
        field_list = self.get_argument('field_list', '')
        limit = self.get_argument('limit', '')
        device_id = self.get_argument('device_id', '')
        page, per_page = self.get_page_and_per_page()

        if not device_id:
            self.finish({'code': 1, 'msg': u'device_id 不能为空'})
            return

        if field_list:
            field_list = ['`%s`' % x.strip() for x in filter(None, field_list.split(','))]
            for f in field_list:
                if ' ' in f:
                    self.finish({'code':1,'msg':u'格式错误'})
        else:
            field_list = ['*']

        today = datetime.datetime.today()
        timestamp = int(time.mktime(today.timetuple())) #dangtain0dianshijainchuo

        week_day = datetime.date.isoweekday(datetime.date.today())
        b_time = timestamp - 3600 * 24 * (6 + week_day)
        e_time = b_time + 3600 * 24 * 7
        b_year,b_month = self.time_format_change(b_time)
        e_year,e_month = self.time_format_change(e_time)

        try:
            if b_year!=e_year or b_month != e_month:  #查询上周数据，解决数据跨越的问题
                refresh_data = "select {} from z_device_data_{first} where device_id={device_id} " \
                               "and z_device_data_{first}.create >= {bt} order by " \
                               "z_device_data_{first}.create desc".format(
                    u','.join(field_list), first=b_year + b_month, bt=b_time, device_id=device_id)
                rows = self.session.execute(refresh_data)
                keys = rows.keys()
                rows = rows.fetchall()
                b_data = [list(r) for r in rows]

                refresh_data = "select {} from z_device_data_{first} where device_id={device_id} " \
                               "and z_device_data_{first}.create <= {et} order by " \
                               "z_device_data_{first}.create desc".format(
                    u','.join(field_list), first=e_year + e_month, et=e_time, device_id=device_id)
                rows = self.session.execute(refresh_data)
                rows = rows.fetchall()
                e_data = [list(r) for r in rows]
                data = e_data + b_data

                if limit:
                    data = data[0:int(limit)]
                count = len(data)
                data = data[(page - 1) * per_page:page * per_page]
                self.finish({'code': 0, 'data': {'count':count,'page':page,'per_page':per_page,'body': data, 'header': keys}})


            else: #在一个月之内
                refresh_data = "select {} from z_device_data_{first} where device_id={device_id} " \
                               "and z_device_data_{first}.create <= {et} and z_device_data_{first}.create >= {bt} order by " \
                               "z_device_data_{first}.create desc".format(
                    u','.join(field_list), first=b_year + b_month, bt=b_time, et=e_time, device_id=device_id)

                if limit:
                    refresh_data += ' limit {}'.format(int(limit))

                rows = self.session.execute(refresh_data)
                keys = rows.keys()
                rows = rows.fetchall()
                rows = [list(r) for r in rows]
                count = len(rows)
                rows = rows[(page - 1) * per_page:page * per_page]
                self.finish({'code': 0, 'data': {'count':count,'page':page,'per_page':per_page,'body': rows, 'header': keys}})

        except:
            self.finish({'code': 1, 'Error': 'unable to fecth data'})

class BDFYReport(RestHandler): #数据统计分析
    def get_query(self): #quanxian chaxun

        corp = self.get_current_session().corp
        q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)

        if self.session.query(q.exists()).scalar():
            # admin
            sub = self.session.query(CorpDevice.device).filter_by(corp=self.get_current_session().corp)
        else:
            # normal
            sub = self.session.query(UserDevice.device).filter_by(user=self.current_user.id)


        device = self.session.query(Device.cpu_id).filter(Device.id.in_(sub),
                                              Device.status.in_([Device.STATUS_WARNING, Device.STATUS_NORMAL]))
        return device

    def get_time(self):
        cur_time = int(time.time())
        timestamp = cur_time - cur_time % 86400 + time.timezone #0 dain
        type = self.get_argument("type",'day')

        if type == "today":
            b_time = timestamp
            e_time = cur_time
        elif type == "day":
            b_time = timestamp - 24*3600
            e_time = timestamp
        elif type == "week":
            b_time = timestamp - 3600 * 24 * 7
            e_time = timestamp
        elif type == "month":
            b_time = timestamp - 3600 * 24 *30
            e_time = timestamp
        elif type == "year":

            b_year = year - 1
            b_month = "%02d" %month
            b_date = "%s-%s-%s" %(b_year,b_month,1)
            timeArray = time.strptime(b_date, "%Y-%m-%d")
            timestamp = int(time.mktime(timeArray))
            b_time = timestamp

            if b_month == "01":
                e_date = "%s-%s-%s" % (b_year, 12, 1)
                timeArray = time.strptime(e_date, "%Y-%m-%d")
                timestamp = int(time.mktime(timeArray))
                e_time = timestamp
            else:
                e_date = "%s-%s-%s" %(year,month-1,1)
                timeArray = time.strptime(e_date, "%Y-%m-%d")
                timestamp = int(time.mktime(timeArray))
                e_time = timestamp
            return b_time,e_time,b_year,month

        else:
            b_time = 0
            e_time = cur_time

        if 'b_time' in self.p:
            b_time = self.p['b_time']
        if 'e_time' in self.p:
            e_time = self.p['e_time']
        return b_time,e_time

    def warn_process(self,time1,time2,q): #baojingshuliang
        q = q.filter(Warn.time>=time1,Warn.time<time2)
        warn_count ={}
        count =0
        for i in q:
            if int(i.code):
                count += 1
                if i.cpu_id in warn_count.keys():
                    warn_count[i.cpu_id] += 1
                else:
                    warn_count[i.cpu_id] = 1
        return count,warn_count

    def warn(self): #baojingbaobiao
        device = self.get_query()
        type = self.get_argument('type','day') # riyue zhou
        if type != "year":
            b_time, e_time = self.get_time()
        else:
            b_time, e_time, b_year, b_month = self.get_time()

        q = self.session.query(Consume).filter(Consume.cpu_id.in_(device))
        if 'cpu_id' in self.p :cpu_id = self.p.cpu_id #yitan
        else:cpu_id = ''
        if cpu_id:
            cpu_id_list = [i.strip() for i in filter(None,cpu_id.split(','))]
            device = device.filter(Device.cpu_id.in_(cpu_id_list))
            q = q.filter(Consume.cpu_id.in_(cpu_id_list))

        data = []
        length = 0
        for i in device:
            name = self.session.query(Device.name).filter_by(cpu_id=i[0]).first()
            warn_data = {name[0]: {"warn_count": []}}
            if type == 'day':
                q = self.session.query(Consume.warn).filter(Consume.cpu_id == i[0], Consume.time >= b_time,
                                                               Consume.time < e_time, Consume.type == 'day').order_by(
                    Consume.time)
                warn = [y[0] for y in q]
                length = len(warn)
                q = self.session.query(Consume.warn).filter(Consume.cpu_id == i[0], Consume.time == b_time,
                                                               Consume.type == 'month').first() #yitain
                if q:
                    sum_warn = q[0]
                else:
                    sum_warn = 0
                warn_data[name[0]]["warn_count"] = warn
                warn_data[name[0]]["sum_warn"] = sum_warn
                data.append(warn_data)

            elif type == "year": #yuenian
                b_time, e_time, b_year, b_month = self.get_time()
                q = self.session.query(Consume.warn, Consume.time).filter(Consume.cpu_id == i[0],
                                                                             Consume.time >= b_time,
                                                                             Consume.type == 'year',
                                                                             Consume.time < e_time)
                warn = [y[0] for y in q]
                time = [y[1] for y in q]
                length = len(warn)
                warn_data[name[0]]["warn_count"] = warn
                warn_data[name[0]]["time"] = time
                q = self.session.query(func.sum(Consume.warn)).filter(Consume.cpu_id == i[0], Consume.time >= b_time,
                                                                         Consume.type == 'year',
                                                                         Consume.time < e_time).first()
                if q[0]:
                    sum_warn = q[0]
                else:
                    sum_warn = 0
                warn_data[name[0]]["sum_warn"] = sum_warn
                data.append(warn_data)

            else:
                q = self.session.query(Consume.warn, Consume.time).filter(Consume.cpu_id == i[0],
                                                                             Consume.time >= b_time,
                                                                             Consume.type == 'month',
                                                                             Consume.time < e_time).order_by(
                    Consume.time)
                warn = [y[0] for y in q]
                length = len(warn)
                time = [y[1] for y in q]
                warn_data[name[0]]["warn"] = warn
                warn_data[name[0]]["time"] = time
                q = self.session.query(func.sum(Consume.warn)).filter(Consume.cpu_id == i[0], Consume.time >= b_time,
                                                                         Consume.type == 'month',
                                                                         Consume.time < e_time).first()
                sum_warn = q[0]
                warn_data[name[0]]["sum_consume"] = sum_warn
                data.append(warn_data)

        w_count = []
        for z in range(length):
            count = 0
            for j in data:
                for k,v in j.items():
                    count += v['warn_count'][z]
            w_count.append(count)
        sum_warn = sum(w_count)

        self.finish({'code': 0, "itemlist": data,"warn_count":w_count,"sum_warn":sum_warn})

    def supply_process(self,time1,time2,cpu_id): #chongzhuangbaobiao zongzhuangliang shijianduan
        device_supply = self.session.query(Supply).filter(Supply.cpu_id == cpu_id,Supply.create>=time1,Supply.create<time2)
        q = self.session.query(func.sum(Supply.add)).filter(Supply.cpu_id == cpu_id,Supply.create>=time1,Supply.create<time2)
        count = device_supply.count()
        if self.session.query(q.exists()).scalar():
            supply = q[0][0]
        else:
            supply = 0
        return count,supply

    def supply(self): #充装报表 昨天 前七天 前三十天 前12个月设备充装记录
        device = self.get_query()
        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            device = device.filter(Device.cpu_id == cpu_id)
        type = self.get_argument('type','day')
        if type != "year":
            b_time, e_time = self.get_time()
        else:
            b_time, e_time, b_year, b_month = self.get_time()

        b_time = int(b_time)
        data = {}
        for i in device:
            name = self.session.query(Device.name).filter_by(cpu_id=i[0]).first()
            data[name[0]] = {'count':[],'supply':[],'sum_supply':0}
            if type == 'day':
                for j in range(24):
                    time1 = j * 3600 + b_time
                    time2 = time1 + 3600
                    count,supply = self.supply_process(time1,time2,i.cpu_id)
                    data[name[0]]['count'].append(count)
                    data[name[0]]['supply'].append(supply)

            elif type == "week":
                for j in range(7):
                    time1 = j * 3600 * 24 + b_time
                    time2 = time1 + 3600 * 24
                    count, supply = self.supply_process(time1, time2, i.cpu_id)
                    data[name[0]]['count'].append(count)
                    data[name[0]]['supply'].append(supply)


            elif type == "month":
                for j in range(30):
                    time1 = j * 3600 * 24 + b_time
                    time2 = time1 + 3600 * 24
                    count, supply = self.supply_process(time1, time2, i.cpu_id)
                    data[name[0]]['count'].append(count)
                    data[name[0]]['supply'].append(supply)

            else:
                b_time, e_time, b_year, b_month = self.get_time()
                for j in range(1, 13):
                    b_time = b_time
                    if b_month != 12:
                        b_month = int(b_month) + 1
                    else:
                        b_month = 1
                        b_year = b_year + 1

                    e_date = "%s-%s-%s" % (b_year, b_month, 1)
                    timeArray = time.strptime(e_date, "%Y-%m-%d")
                    timestamp = int(time.mktime(timeArray))
                    e_time = timestamp
                    count, supply = self.supply_process(b_time, e_time, i.cpu_id)
                    data[name[0]]['count'].append(count)
                    data[name[0]]['supply'].append(supply)
                    b_time = e_time

            data[name[0]]['sum_supply'] = sum(data[name[0]]['supply'])
        self.finish({'code':0,'data':data})

    def consume(self): #设备消耗用量报表  昨天 前七天 前三十天 前12个月设备充装记录
        device = self.get_query()
        cpu_id = self.get_argument('cpu_id','')
        type = self.get_argument("type",'')
        if cpu_id:
            device = device.filter(Device.cpu_id == cpu_id)
        if type != "year":
            b_time, e_time = self.get_time()
        else:
            b_time, e_time, b_year, b_month = self.get_time()

        data = []
        consume = 0
        for i in device:
            name = self.session.query(Device.name).filter_by(cpu_id = i[0]).first()
            consume_data = {name[0]:{"consume":[]}}
            if type == "day":
                q = self.session.query(Consume.consume,Consume.time).filter(Consume.cpu_id == i[0],Consume.time>=b_time,
                                                               Consume.time<e_time,Consume.type == 'day').order_by(Consume.time)
                consume = [y[0] for y in q]
                time = [y[1] for y in q]
                q = self.session.query(Consume.consume).filter(Consume.cpu_id == i[0],Consume.time == b_time,Consume.type == 'month').first()

                if q:
                    sum_consume = q[0]
                else:
                    sum_consume = 0
                consume_data[name[0]]["consume"] = consume
                consume_data[name[0]]["sum_consume"] = sum_consume
                data.append(consume_data)

            elif type == "year":
                b_time, e_time, b_year, b_month = self.get_time()
                q = self.session.query(Consume.consume,Consume.time).filter(Consume.cpu_id == i[0], Consume.time >= b_time,
                                                               Consume.type == 'year', Consume.time < e_time)
                consume = [y[0] for y in q]
                time = [y[1] for y in q]
                consume_data[name[0]]["consume"] = consume
                q = self.session.query(func.sum(Consume.consume)).filter(Consume.cpu_id == i[0], Consume.time >= b_time,
                                                                         Consume.type == 'year',
                                                                      Consume.time < e_time).first()
                if q[0]:
                    sum_consume = q[0]
                else:
                    sum_consume = 0
                consume_data[name[0]]["sum_consume"] = sum_consume
                data.append(consume_data)

            else:
                q = self.session.query(Consume.consume,Consume.time).filter(Consume.cpu_id == i[0], Consume.time >= b_time,
                                        Consume.type == 'month', Consume.time < e_time).order_by(Consume.time)
                consume = [y[0] for y in q]
                time = [y[1] for y in q]
                consume_data[name[0]]["consume"] = consume
                q = self.session.query(func.sum(Consume.consume)).filter(Consume.cpu_id == i[0], Consume.time >= b_time,
                                                                         Consume.type == 'month',
                                                                         Consume.time < e_time).first()
                sum_consume = q[0]
                consume_data[name[0]]["sum_consume"] = sum_consume
                data.append(consume_data)

        c_count = []
        for z in range(len(consume)):
            count = 0
            for j in data:
                for k, v in j.items():
                    count += v['consume'][z]
            c_count.append(count)
        sum_count = sum(c_count)
        self.finish({'code':0,"itemlist":data,'c_count':c_count,'sum_count':sum_count,"time":time})

    def new_consume(self):
        import time
        device = self.get_query()
        cpu_id = self.get_argument('cpu_id', '')
        type = self.get_argument("type", '')
        if cpu_id:
            device = device.filter(Device.cpu_id == cpu_id)
        try:
            now_day = int(time.time())
            b_time_1 = int(self.get_argument('b_time', ''))
            e_time = int(self.get_argument('e_time', ''))
            print b_time_1
            N1 = (now_day - b_time_1) // 86400
            yesterday_min_time = datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=N1),
                                                           datetime.time.min)
            timeArray = time.strptime(str(yesterday_min_time), "%Y-%m-%d %H:%M:%S")
            b_time = int(time.mktime(timeArray))
        except Exception :
            self.finish({'code': 1,'data':'时间为空' })
        data = []
        consume = 0
        for i in device:
            name = self.session.query(Device.name).filter_by(cpu_id=i[0]).first()
            consume_data = {name[0]: {"consume": []}}
            q = self.session.query(Consume.consume, Consume.time).filter(Consume.cpu_id == i[0],
                                                                         Consume.time >= b_time,
                                                                         Consume.type == 'month',
                                                                         Consume.time < e_time).order_by(
                Consume.time)
            consume = [y[0] for y in q]
            time = [y[1] for y in q]
            consume_data[name[0]]["consume"] = consume
            q = self.session.query(func.sum(Consume.consume)).filter(Consume.cpu_id == i[0], Consume.time >= b_time,
                                                                     Consume.type == 'month',
                                                                     Consume.time < e_time).first()
            sum_consume = q[0]
            consume_data[name[0]]["sum_consume"] = sum_consume
            data.append(consume_data)
        print data
        c_count = []
        for z in range(len(consume)):
            count = 0
            for j in data:
                for k, v in j.items():
                    count += v['consume'][z]
            c_count.append(count)
        sum_count = sum(c_count)
        self.finish({'code': 0, "itemlist": data, 'c_count': c_count, 'sum_count': sum_count, "time": time})

    def get_deliver_order(self): #调度系统的配送订单信息
        corp = self.get_current_session().corp
        q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)
        if self.session.query(q.exists()).scalar():
            q = self.session.query(DeliverOrder).filter_by(user=self.current_user.id)
        else:
            username = self.session.query(User.name).filter_by(id=self.current_user.id)
            q = self.session.query(DeliverOrder).filter_by(contacter=username[0])
        q = q.filter(DeliverOrder.status.in_(['unload', 'dispatch', 'backspace', 'abnormal']))
        return q

    def deliver_report(self):#配送订单报表

        q = self.get_deliver_order()
        type = self.get_argument('type','')
        if type != "year":
            b_time, e_time = self.get_time()
        else:
            b_time, e_time, b_year, b_month = self.get_time()

        data = []
        coustomer_count = []
        sum_count = []

        if type == 'day':
            for j in range(24):
                time1 = j * 3600 + b_time
                time2 = time1 + 3600
                deliver,deliver_count,count = self.deliver_process(time1,time2,q)
                data.append(deliver)
                coustomer_count.append(deliver_count)
                sum_count.append(count)

        elif type == "week":
            for j in range(7):
                time1 = j * 3600 * 24 + b_time
                time2 = time1 + 3600 * 24
                deliver, deliver_count,count = self.deliver_process(time1, time2, q)
                data.append(deliver)
                coustomer_count.append(deliver_count)
                sum_count.append(count)

        elif type == "month":
            for j in range(30):
                time1 = j * 3600 * 24 + b_time
                time2 = time1 + 3600 * 24
                deliver, deliver_count,count = self.deliver_process(time1, time2, q)
                data.append(deliver)
                coustomer_count.append(deliver_count)
                sum_count.append(count)
        else:
            b_time, e_time, b_year, b_month = self.get_time() #特殊情况
            for j in range(1, 13):
                b_time = b_time
                if b_month != 12:
                    b_month = int(b_month) + 1
                else:
                    b_month = 1
                    b_year = b_year + 1

                e_date = "%s-%s-%s" % (b_year, b_month, 1)
                timeArray = time.strptime(e_date, "%Y-%m-%d")
                timestamp = int(time.mktime(timeArray))
                e_time = timestamp
                deliver, deliver_count,count = self.deliver_process(b_time, e_time, q)
                data.append(deliver)
                coustomer_count.append(deliver_count)
                sum_count.append(count)
                b_time = e_time
        self.finish({'code':0,'data':data,'count':coustomer_count,'sum_count':sum_count})

    def deliver_process(self,time1,time2,q):
        q = q.filter(DeliverOrder.create >= time1, DeliverOrder.create < time2)
        deliver = {}
        deliver_count = {}
        count = 0
        for i in q:
            if i.customer not in deliver.keys():
                deliver[i.customer] = float(i.add)
            else:
                deliver[i.customer] += float(i.add)

            if i.customer in deliver_count.keys():
                deliver_count[i.customer] += 1
            else:
                deliver_count[i.customer] = 1
        for j in deliver.values():
            count += j
        return deliver,deliver_count,count

    def device_loss(self):
        device = self.get_query()
        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            device = device.filter(Device.cpu_id == cpu_id)
        # q = self.get_deliver_order()
        type = self.get_argument('type', 'day')
        if type != "year":
            b_time, e_time = self.get_time()
        else:
            b_time, e_time, b_year, b_month = self.get_time()

        b_time = int(b_time)
        for i in device:
            name = self.session.query(Device.name).filter_by(cpu_id = i[0]).first()
            device_loss = {name[0]:{"loss":[],"sum_loss":0}}
            if type == 'day':
                for j in range(24):
                    time1 = j * 3600 + b_time
                    time2 = time1 + 3600
                    deliver_loss = self.deliver_loss_process(time1, time2, i.cpu_id)
                    device_loss[name[0]]['loss'].append(deliver_loss)

            elif type == "week":
                print b_time
                for j in range(7):
                    time1 = j * 3600 * 24 + b_time
                    time2 = time1 + 3600 * 24
                    deliver_loss = self.deliver_loss_process(time1, time2, i.cpu_id)
                    device_loss[name[0]]['loss'].append(deliver_loss)

            elif type == "month":
                print b_time
                for j in range(30):
                    time1 = j * 3600 * 24 + b_time
                    time2 = time1 + 3600 * 24
                    deliver_loss = self.deliver_loss_process(time1, time2, i.cpu_id)
                    device_loss[name[0]]['loss'].append(deliver_loss)

            else:
                b_time, e_time, b_year, b_month = self.get_time()
                for j in range(1, 13):
                    b_time = b_time
                    if b_month != 12:
                        b_month = int(b_month) + 1
                    else:
                        b_month = 1
                        b_year = b_year + 1

                    e_date = "%s-%s-%s" % (b_year, b_month, 1)
                    timeArray = time.strptime(e_date, "%Y-%m-%d")
                    timestamp = int(time.mktime(timeArray))
                    e_time = timestamp
                    deliver_loss = self.deliver_loss_process(b_time, e_time, i.cpu_id)
                    device_loss[name[0]]['loss'].append(deliver_loss)
                    b_time = e_time
            device_loss[name[0]]['sum_loss'] = sum(device_loss[name[0]]['loss'])
        self.finish({'code': 0, 'data': device_loss})

    def deliver_loss_process(self,time1,time2,cpu_id):
        q = self.session.query(DeliverOrder).filter(DeliverOrder.create >= time1, DeliverOrder.create < time2,DeliverOrder.station == cpu_id)
        if not self.session.query(q.exists()).scalar():
            deliver_loss = 0
        else:
            for i in q:
                supply = self.session.query(Supply).filter(Supply.cpu_id == cpu_id, Supply.create >= i.create).first()
                if not supply:
                    continue
                deliver_loss = float(i.add)-float(supply.add)
        return deliver_loss
