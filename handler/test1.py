from base import RestHandler
from app.model.test import Test

class MyTestHandler(RestHandler):
    def permission(self):
        pass

    def create(self):
        p = {
            'type':self.get_argument('type','normal'),
            'status':self.get_argument('status','normal')
        }
        if p['type'] != 'delete':
            try:
                test = Test(**p)
                self.session.add(test)
                self.session.commit()
                self.finish({'code':0,'data':'insert sucess'})
            except:
                self.finish({'code':1,'data':'insert fail'})

    def update(self):
        id = self.get_argument('id','')
        if not id:
            self.finish({'code':1,'data':'the id is missing'})
            return

        p = {
            'type': self.get_argument('type', ''),
            'status': self.get_argument('status', '')
        }
        update_data = {}
        for i in p:
            if p[i]:
                update_data[i] = p[i]
        if update_data:
            self.session.query(Test).update(update_data)
            self.session.commit()
            self.finish({'code':0,'data':'update sucess'})


    def get_query(self):
        q = self.session.query(Test)
        return q

    def list_filter(self, q):
        id = self.get_argument('id','')
        if id:
            q = q.filter(Test.id == id)

        status = self.get_argument('status', '')
        if status:
            q = q.filter(Test.status == status)
        return q

    def delete(self):
        id = self.get_argument('id','')
        if not id:
            self.finish({'code':2,'data':'the id is missing '})
            return
        
        try:
            self.session.query(Test).filter_by(id = id).delete()
            self.session.commit()
            self.finish({'code':0,'data':'delete sucess'})
        except:
            self.finish({'code':1,'data':'delete fail'})
