# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    bpjs_kesehatan_number = fields.Char(
        string="# BPJS Kesehatan",
        compute=lambda s: s._compute_identification(
            "bpjs_kesehatan_number", "bpjs_kes"),
        search=lambda s, *a: s._search_identification(
            "bpjs_kes", *a),
    )
    bpjs_ketenagakerjaan_number = fields.Char(
        string="# BPJS Ketenagakerjaan",
        compute=lambda s: s._compute_identification(
            "bpjs_ketenagakerjaan_number", "bpjs_tnk"),
        search=lambda s, *a: s._search_identification(
            "bpjs_tnk", *a),
    )
