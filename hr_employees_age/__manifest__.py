
# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2015  TM_FULLNAME
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
###############################################################################
{
    'name': 'HR Employees Age',
    'version': '12.0.0.0',
    'sequence': 1,
    'category': 'Human Resources',
    'description':"""Display Employees Age on Employee Form""",
    'summary': 'odoo Apps will help to add Employees Age on Employee module', 
    'author': 'Ananthu Krishna',
    'website': 'http://www.codersfort.com',
    'maintainer': 'Ananthu Krishna',
    'depends': ['hr'],
    'data': [
        'views/hr_views.xml'
    ],
    'images': ['images/hr_employee.png'],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

