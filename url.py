# -*- coding: utf-8 -*-

Handlers = []

from handler.test import TestHandler

Handlers += [
    ('/test', TestHandler)
]

from handler.login import LoginHandler, LogoutHandler
from handler.captcha import CaptchaHandler
from handler.mobile_code import SendMobileCode
Handlers += [
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/captcha', CaptchaHandler),
    ('/mobile_code',SendMobileCode)
]


from handler.admin_template import AdminTemplateHandler,AdminTestTemplateHandler,StaticTemplateHandler,HPLTemplateHandler,WebTemplateHandler

Handlers += [
    ('/admin', AdminTemplateHandler),
    ('/admin-test', AdminTestTemplateHandler),
    ('/private', StaticTemplateHandler),
    ('/hpl', HPLTemplateHandler),
    ('/web', WebTemplateHandler),

]

from handler.me import MeHandler
from handler.session import SessionHandler
from handler.user import UserHandler
from handler.corp import CorpHandler
from handler.corp_user import CorpUserHandler
from handler.device import DeviceHandler
from handler.corp_device import CorpDeviceHandler
from handler.system import SystemHandler
from handler.action_log import ActionLogHandler
from handler.rule import RuleHandler
from handler.warn import WarnHandler
from handler.user_device import UserDeviceHandler
from handler.device_package_record import DevicePackageRecordHandler,AppUpgradeHandler
from handler.wechat import WeiXinLoginHandler
from handler.wechat import WeChatHandler
from handler.warn import WarnContrastHandler
from handler.mobile_code import MobileVerify
from handler.user_message import UserMessageHandler
from handler.telecontrol import TelecontrolHandler
from handler.newwarn import NewWarnHandler,NewWarnMessageHandler,WarnCloseHandler

Handlers += [
    ('/api/me(/[^/]*?)?', MeHandler),
    ('/api/session(/[^/]*?)?', SessionHandler),
    ('/api/user(/[^/]*?)?', UserHandler),
    ('/api/corp(/[^/]*?)?', CorpHandler),
    ('/api/corp-user(/[^/]*?)?', CorpUserHandler),
    ('/api/device(/[^/]*?)?', DeviceHandler),
    ('/api/corp-device(/[^/]*?)?', CorpDeviceHandler),
    ('/api/system(/[^/]*?)?', SystemHandler),
    ('/api/action-log(/[^/]*?)?', ActionLogHandler),
    ('/api/rule(/[^/]*?)?', RuleHandler),
    ('/api/warn(/[^/]*?)?', WarnHandler),
    ('/api/warn-contrast(/[^/]*?)?', WarnContrastHandler),
    ('/api/user-device(/[^/]*?)?', UserDeviceHandler),
    ('/api/device-package-record(/[^/]*?)?', DevicePackageRecordHandler),
    ('/api/app-upgrade(/[^/]*?)?', AppUpgradeHandler),
    ('/api/wechat-login(/[^/]*?)?',WeiXinLoginHandler),
    ('/api/wechat(/[^/]*?)?', WeChatHandler),
    ('/api/mobile(/[^/]*?)?', MobileVerify),
    ('/api/user-message(/[^/]*?)?', UserMessageHandler),
    ('/api/telecont(/[^/]*?)?', TelecontrolHandler),
    ('/api/newwarn(/[^/]*?)?', NewWarnHandler),
    ('/api/closewarn(/[^/]*?)?', WarnCloseHandler),
    ('/api/warnmessage(/[^/]*?)?', NewWarnMessageHandler),
]

from handler.aliyuniot import ALiProductHandler,ALiDeviceHandler,ALiTopicHandler,ALiRouteHandler,ALiMessageHandler,ALiShadowHandler

Handlers += [
    ('/api/aliyuniot/product(/[^/]*?)?', ALiProductHandler),
    ('/api/aliyuniot/device(/[^/]*?)?', ALiDeviceHandler),
    ('/api/aliyuniot/topic(/[^/]*?)?', ALiTopicHandler),
    ('/api/aliyuniot/route(/[^/]*?)?', ALiRouteHandler),
    ('/api/aliyuniot/message(/[^/]*?)?', ALiMessageHandler),
    ('/api/aliyuniot/shadow(/[^/]*?)?', ALiShadowHandler),
]

from handler.corp import MyCorpHandler
from handler.corp_user import MyCorpUserHandler
from handler.device import MyDeviceHandler,MyDeviceApendixHandler
from handler.action_log import MyActionLogHandler
from handler.corp_user_device import MyCorpUserDeviceHandler
from handler.user_message import MyUserMessageHandler
from handler.user_order import MyTakeOrderHandler,MyDeliverOrderHandler
from handler.warn import MyWarnHandler
from handler.corp_device import MyCorpDevice
from handler.invoice import MyInvoiceHandler
from handler.telecontrol import MyTelecontrolHandler

Handlers += [
    ('/api/my-corp(/[^/]*?)?', MyCorpHandler),
    ('/api/my-corp-user(/[^/]*?)?', MyCorpUserHandler),
    ('/api/my-device(/[^/]*?)?', MyDeviceHandler),
    ('/api/my-action-log(/[^/]*?)?', MyActionLogHandler),
    ('/api/my-corp-user-device(/[^/]*?)?', MyCorpUserDeviceHandler),
    ('/api/my-user-message(/[^/]*?)?', MyUserMessageHandler),
    ('/api/my-take-order(/[^/]*?)?', MyTakeOrderHandler),
    ('/api/my-deliver-order(/[^/]*?)?', MyDeliverOrderHandler),
    ('/api/my-warn(/[^/]*?)?', MyWarnHandler),
    ('/api/my-corp-device(/[^/]*?)?', MyCorpDevice),
    ('/api/my-invoice(/[^/]*?)?', MyInvoiceHandler),
    ('/api/my-telecont(/[^/]*?)?', MyTelecontrolHandler),
    ('/api/my-device-appendix(/[^/]*?)?', MyDeviceApendixHandler)
]

from handler.tool import ToolHandler
from handler.realdata import RealdataHandler
from handler.data import DataHandler,FetchDataHandler,RunReportHandler

Handlers += [
    ('/api/tool(/[^/]*?)?', ToolHandler),
    ('/api/realdata', RealdataHandler),
    ('/api/data', DataHandler),
    ('/api/fetchdata(/[^/]*?)?', FetchDataHandler),
    ('/api/runreport(/[^/]*?)?', RunReportHandler)
]


from handler.analytics import FactHandler, MetricHandler, CalculateMetricHandler, DimensionHandler, FactResourceHandler, AnalyticsQueryHandler

Handlers += [
    ('/analytics/fact(/[^/]*?)?', FactHandler),
    ('/analytics/metric(/[^/]*?)?', MetricHandler),
    ('/analytics/calculate-metric(/[^/]*?)?', CalculateMetricHandler),
    ('/analytics/dimension(/[^/]*?)?', DimensionHandler),
    ('/analytics/fact-resource(/[^/]*?)?', FactResourceHandler),
    ('/analytics/query', AnalyticsQueryHandler),
]

from handler.information import InformationHandler
from handler.demandpub import DemandPubHandler
from handler.invoice import InvoiceHandler
from handler.mail import MailHandler

Handlers += [
    ('/api/information(/[^/]*?)?', InformationHandler),
    ('/api/demandpub(/[^/]*?)?',DemandPubHandler ),
    ('/api/invoice(/[^/]*?)?', InvoiceHandler),
    ('/api/mail(/[^/]*?)?', MailHandler),
]

from handler.bdfy import BDFY
Handlers += [
    ('/bdfy(/[^/]*?)?', BDFY),
]
