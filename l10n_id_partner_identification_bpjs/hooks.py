# Copyright 2018-2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def _load_partner_identification_data(cr):
    try:
        from openupgradelib import load_data
        load_data(
            cr, "l10n_id_partner_identification_bpjs",
            "/data/res_partner_id_category_data.xml")
    except:
        return
