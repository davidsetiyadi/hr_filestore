from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, tools

import logging
import sys

_logger = logging.getLogger(__name__)


class product_template(osv.Model):