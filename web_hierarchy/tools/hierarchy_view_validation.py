# -*- coding: utf-8 -*-
import logging
import os

from lxml import etree

from odoo.loglevels import ustr
from odoo.tools import misc, view_validation

_logger = logging.getLogger(__name__)

_hierarchy_validator = None
@view_validation.validate('hierarchy')
def schema_hierarchy(arch):
    """ Check the hierarchy view against its schema

    :type arch: etree._Element
    """
    global _hierarchy_validator

    if _hierarchy_validator is None:
        with misc.file_open(os.path.join('web_hierarchy', 'views', 'hierarchy.rng')) as f:
            _hierarchy_validator = etree.RelaxNG(etree.parse(f))

    if _hierarchy_validator.validate(arch):
        return True

    for error in _hierarchy_validator.error_log:
        _logger.error(ustr(error))
    return False

@view_validation.validate('hierarchy')
def valid_field_in_hierarchy(arch):
    """ Children of ``hierarchy`` view must be ``field`` or ``button``."""
    return all(
        child.tag in ('field', 'button')
        for child in arch.xpath('/hierarchy/*')
    )


@view_validation.validate('hierarchy')
def valid_att_in_field(arch):
    """ ``field`` nodes must all have a ``@name`` """
    return not arch.xpath('//field[not(@name)]')