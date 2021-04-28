# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2017 Alphasoft
#    (<http://www.alphasoft.co.id>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Localization for Indonesia',
    'version': '12.0.0.1.0',
    'sequence': 1,
    'summary': 'Localization for Indonesia',
    'author': "Alphasoft",
    'website': 'http://www.alphasoft.co.id',
    'images':  ['images/main_screenshot.png'],
    'license': 'OPL-1',
    'category': 'Base',
    'description': '''Module based on Alphasoft
        - Province
        - Kabupaten
        - Kecamatan
        - Kelurahan
        - Agama
        - Ras
    NB: This module will take time to create keluarahan with 65k data''',
    'depends': ['base', 'contacts'],
    'data': [
             "security/ir.model.access.csv",
             "views/localization_view.xml",
             "views/company_view.xml",
             "views/partner_view.xml",
     ],
    'demo': [],
    'test': [],
    'qweb': [],
    'css': [],
    'js': [],
    'installable': True,
    'auto_install': False,
    'post_init_hook': '_post_base_init',#ACTIVE WHEN NEEDED
}
