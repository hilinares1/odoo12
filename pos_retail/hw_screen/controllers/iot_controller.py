# -*- coding: utf-8 -*
import time
from threading import Thread, Lock
from odoo import http, _
import os
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

try:
    from queue import Queue
except ImportError:
    from Queue import Queue  # pylint: disable=deprecated-module

# TODO: chef screens
from odoo.addons.web.controllers import main as web


import json
import logging

_logger = logging.getLogger(__name__)


class SyncDrive(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.lock = Lock()
        self.chef_login = {}
        self.sync_datas = {}
        self.transactions = {}
        self.transactions_removed = {}
        self.status = {'status': 'connecting', 'messages': []}
        self.chef_screen_status = 'offline'

    def get_sync(self, bus_id, device_id):
        result_list = []
        if not self.sync_datas.get(bus_id, None):
            self.register_point(bus_id, device_id)
            return []
        if self.sync_datas.get(bus_id, None) and not self.sync_datas.get(bus_id, None).get(device_id):
            self.register_point(bus_id, device_id)
            return []
        else:
            while not self.sync_datas[bus_id][device_id].empty():
                result_list.append(self.sync_datas[bus_id][device_id].get())
            return result_list

    def save_sync(self, bus_id, device_id, datas={}):
        if not self.sync_datas.get(bus_id, None):
            self.register_point(bus_id, device_id)
        for device_saved_id, queue in self.sync_datas[bus_id].items():
            if device_id != device_saved_id:
                self.sync_datas[bus_id][device_saved_id].put((time.time(), device_id, datas))
        if not self.transactions.get(bus_id, {}):
            self.transactions[bus_id] = {}
        if not self.transactions_removed.get(bus_id, {}):
            self.transactions_removed[bus_id] = []
        for data in datas:
            value = data.get('value', None)
            action = value.get('action', None)
            uid = value.get('order_uid', None)
            order_json = value.get('order_json', None)
            if not value or not uid or not action or not order_json:
                _logger.error('value %s - uid %s - action %s - order json %s' % (value, uid, action, order_json))
                continue
            else:
                self.transactions[bus_id][uid] = order_json
                if action in ['unlink_order', 'paid_order']:
                    self.transactions_removed[bus_id].append(uid)
                    _logger.info("removed order %s" % uid)
                _logger.info('Order %s (%s)- Total Lines: %s' % (uid, action, len(order_json['lines'])))

    def register_point(self, bus_id, device_id):
        if not self.sync_datas.get(bus_id, None):
            self.sync_datas[bus_id] = {}
            self.sync_datas[bus_id][device_id] = Queue()
        else:
            if not self.sync_datas[bus_id].get(device_id, None):
                self.sync_datas[bus_id][device_id] = Queue()


driver = SyncDrive()

class SyncController(web.Home):

    @http.route('/pos/register/sync', type="json", auth='none', cors='*')
    def register_sync(self, bus_id, device_id):
        # TODO: each bus_id we stores all event of pos sessions
        driver.register_point(bus_id, device_id)
        return json.dumps({'state': 'succeed', 'values': {}})

    @http.route('/pos/save/sync', type="json", auth='none', cors='*')
    def save_sync(self, bus_id, device_id, messages):
        # TODO: save all transactions event from pos sessions
        driver.save_sync(bus_id, device_id, messages)
        return json.dumps({'state': 'succeed', 'values': {}})

    @http.route('/pos/re-save/sync', type="json", auth='none', cors='*')
    def re_save_sync(self, bus_id, device_id, messages):
        # TODO: when IoT or odoo server offline, transactions push to /save/sync will fail, and when IoT box (odoo) online back, re-save again
        _logger.info('--------- re_save_sync -------------')
        driver.save_sync(bus_id, device_id, messages)
        return json.dumps({'state': 'succeed', 'values': {}})

    @http.route('/pos/get/sync', type="json", auth='none', cors='*')
    def get_sync(self, bus_id, device_id):
        # TODO: get any events change from another pos sessions
        values = driver.get_sync(bus_id, device_id)
        return json.dumps({'state': 'succeed', 'values': values})

    @http.route('/pos/get/lost_transactions', type="json", auth='none', cors='*')
    def get_lost_transactions(self, bus_id):
        # TODO:
        #       - step 1: cashier A open session
        #       - step 2: cashier B open session
        #       - Question: how sync all event from cashier A (doing before cashier B open session) ?
        #       - We store all orders from cashier A, when cashier B or another cashier open session late times, will auto sync
        transactions = driver.transactions.get(bus_id, {})
        transactions_live = []
        transactions_removed = driver.transactions_removed.get(bus_id, {})
        for uid, order in transactions.items():
            if uid not in transactions_removed:
                transactions_live.append(order)
        return json.dumps({'state': 'succeed', 'values': {
            'transactions_live': transactions_live,
            'transactions_removed': transactions_removed
        }})

    @http.route('/pos/ping', type='http', auth='none', cors='*')
    def pos_hello(self):
        os.system(" mount -o rw,remount /")
        return "ping"

    @http.route('/pos/passing/login', type='http', auth='none', cors='*')
    def pos_login(self):
        os.system(" mount -o rw,remount /")
        return "ping"

    @http.route('/pos/display-chef-screen', type="json", auth='none', cors='*')
    def display_chef_screen(self, link, database, login, password):
        _logger.info('open_chef_screen')
        try:
            driver.xmlrpc_url = url_8 = '%s/xmlrpc/2/' % link
            driver.xmlrpc_common = xmlrpclib.ServerProxy(url_8 + 'common')
            driver.xmlrpc_object = xmlrpclib.ServerProxy(url_8 + 'object')
            driver.uid = driver.xmlrpc_common.login(database, login, password)
            if driver.uid:
                driver.chef_login['link'] = link
                driver.chef_login['database'] = database
                driver.chef_login['login'] = login
                driver.chef_login['password'] = password
                return json.dumps({'state': 'succeed', 'values': driver.uid})
            else:
                return json.dumps({'state': 'fail', 'values': 'login fail'})
        except:
            return json.dumps({'state': 'fail', 'values': 'login fail'})

    @http.route('/pos/get-login-chef', type='json', auth='none')
    def get_login_chef_screen(self):
        _logger.info('get_login_chef_screen')
        _logger.info(driver.chef_login)
        return driver.chef_login

    @http.route('/pos/reboot', type='json', auth='none', cors='*')
    def reboot(self):
        os.system('sudo reboot now')
        return json.dumps({'state': 'succeed', 'values': 'OK'})
