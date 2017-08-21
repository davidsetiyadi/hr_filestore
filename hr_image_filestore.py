from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, tools

import logging
import sys

_logger = logging.getLogger(__name__)


class hr_employee(osv.osv):
	_inherit = "hr.employee"

	def _get_image(self, cr, uid, ids, name, args, context=None):
		attachment_field = 'image_attachment_id' if name=='image' else 'image_medium_attachment_id'
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			# print obj.image_attachment_id.datas,'daviddddddddddd'
			result[obj.id] = {
				'image': obj.image_attachment_id and obj.image_attachment_id.datas or None,
				'image_small': obj.image_small_attachment_id and obj.image_small_attachment_id.datas or None,
				'image_medium': obj.image_medium_attachment_id and obj.image_medium_attachment_id.datas or None,
			}
		return result

	def _set_image(self, cr, uid, id, name, value, args, context=None):
		obj = self.browse(cr, uid, id, context=context)
		image_id = obj.image_attachment_id.id
		image_small_id = obj.image_small_attachment_id.id
		image_medium_id = obj.image_medium_attachment_id.id
		if not value:
			ids = [attach_id for attach_id in [image_id, image_small_id, image_medium_id] if attach_id]
			if ids:
				self.pool['ir.attachment'].unlink(cr, uid, ids, context=context)
			return True
		if not (image_id and image_small_id and image_medium_id):
			image_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Employee Image'}, context=context)
			image_small_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Employee Small Image'}, context=context)
			image_medium_id = self.pool['ir.attachment'].create(cr, uid, {'name': 'Employee Medium Image'}, context=context)
			self.write(cr, uid, id, {'image_attachment_id': image_id,
									 'image_small_attachment_id': image_small_id,
									 'image_medium_attachment_id':image_medium_id},
					   context=context)

		images = tools.image_get_resized_images(value, return_big=True, avoid_resize_medium=True)
		self.pool['ir.attachment'].write(cr, uid, image_id, {'datas': images['image']}, context=context)
		self.pool['ir.attachment'].write(cr, uid, image_small_id, {'datas': images['image_small']}, context=context)
		self.pool['ir.attachment'].write(cr, uid, image_medium_id, {'datas': images['image_medium']}, context=context)

		return True

	_columns = {
		'image_attachment_id': fields.many2one('ir.attachment', 'Image attachment', help='Technical field to store image in filestore'),
		'image_small_attachment_id': fields.many2one('ir.attachment', 'Small-sized Image  attachment', help='Technical field to store image in filestore'),
		'image_medium_attachment_id': fields.many2one('ir.attachment', 'Medium-sized Image  attachment', help='Technical field to store image in filestore'),

		'image': fields.function(_get_image, fnct_inv=_set_image, string="Image", multi='_get_image', type='binary',
            help="This field holds the image used as image for the product, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            help="Medium-sized image of the product. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            help="Small-sized image of the product. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
	   }