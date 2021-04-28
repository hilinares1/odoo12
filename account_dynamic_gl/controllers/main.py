import base64
import functools
import logging
import simplejson
import time
import urllib2
import zlib
from openerp.addons.web.controllers.main import Reports
from openerp.addons.web.controllers.main import serialize_exception
from openerp.addons.web.controllers.main import content_disposition
try:
    import xlwt
except ImportError:
    xlwt = None

import werkzeug.utils
import werkzeug.wrappers
from openerp.tools import ustr
from openerp import http
from openerp.service.report import exp_report, exp_report_get

from openerp.http import request, serialize_exception as _serialize_exception
_logger = logging.getLogger(__name__)


class Reports(Reports):

    @http.route('/web/report', type='http', auth="user")
    @serialize_exception
    def index(self, action, token):
        action = simplejson.loads(action)

        report_srv = request.session.proxy("report")
        context = dict(request.context)
        context.update(action["context"])

        report_data = {}
        report_ids = context.get("active_ids", None)
        if 'report_type' in action:
            report_data['report_type'] = action['report_type']
        if 'datas' in action:
            if 'ids' in action['datas']:
                report_ids = action['datas'].pop('ids')
            report_data.update(action['datas'])

        report_id = exp_report(
            request.session.db, request.session.uid,
            action["report_name"], report_ids or [],
            report_data, context)

        report_struct = None
        while True:
            report_struct = exp_report_get(
                request.session.db, request.session.uid, report_id)
            if report_struct["state"]:
                break

            time.sleep(self.POLLING_DELAY)

        report = base64.b64decode(report_struct['result'])
        if report_struct.get('code') == 'zlib':
            report = zlib.decompress(report)
        report_mimetype = self.TYPES_MAPPING.get(
            report_struct['format'], 'octet-stream')
        file_name = action.get('name', 'report')
        if 'name' not in action:
            reports = request.session.model('ir.actions.report.xml')
            res_id = reports.search(
                [('report_name', '=', action['report_name']), ],
                context=context)
            if len(res_id) > 0:
                file_name = reports.read(res_id[0], ['name'], context)['name']
            else:
                file_name = action['report_name']
        file_name = '%s.%s' % (file_name, report_struct['format'])

        return request.make_response(report,
                                     headers=[
                                         ('Content-Disposition',
                                          content_disposition(file_name)),
                                         ('Content-Type', report_mimetype),
                                         ('Content-Length', len(report))],
                                     cookies={'fileToken': token})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
