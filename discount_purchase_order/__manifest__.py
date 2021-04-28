# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Discount On Purchase Order",
  "summary"              :  "Discount on order line and purchase order",
  "category"             :  "Purchases",
  "version"              :  "1.2.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Discount-On-Purchase-Order.html",
  "description"          :  """Discount with fixed type on order line and global on order""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=discount_purchase_order",
  "depends"              :  ['purchase'],
  "data"                 :  [
                             'views/purchase_views.xml',
                             'views/account_invoice_view.xml',
                             'views/res_config_views.xml',
                             'report/purchase_order_templates.xml',
                             'security/discount_security.xml',
                            ],
  "demo"                 :  [
                             'data/discount_data.xml',
                             'data/discount_demo.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  25,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
