from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    fal_header_sticker = fields.Char(
        string='Header Sticker',
        help='This field will fill the\
        Header Sticker on Delivery Sticker Report')

    fal_description_sticker_1 = fields.Char(
        string='Description Sticker',
        help='This field will fill the\
        Description Sticker on Delivery Sticker Report')

    fal_description_sticker_2 = fields.Char(
        string='Description Sticker',
        help='This field will fill the\
        Description Sticker on Delivery Sticker Report')

    fal_logo_sticker = fields.Binary("Logo Sticker", attachment=True,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px",)

    fal_website_sticker = fields.Char(string='Website Sticker')

    fal_producer_name_sticker = fields.Char(string='Producer Name Sticker')
