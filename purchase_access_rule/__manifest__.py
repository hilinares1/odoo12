{
	'name': "Purchase Access Rule",
	'summary': "Access rule for purchase order and RFQ",
	'auther': "Muram Makkawi",
	'category':'Purchase',
	'depends': ['purchase'],
	'data': [
		'security/purchase_security.xml',
		'security/ir.model.access.csv',
		],		
	'installable': True,
	'license': 'OEEL-1',

}