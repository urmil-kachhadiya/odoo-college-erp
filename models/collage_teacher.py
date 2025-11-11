from odoo import models, fields, api

class CollageTeacher(models.Model):
    _name = 'collage.teacher'
    _description = 'College Teacher Record'

    name = fields.Char(string='Teacher Name', required=True)
    teacher_id = fields.Char(string='Teacher ID', required=True)
    department_id = fields.Many2one('collage.department', string='Department', required=True)
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    joining_date = fields.Date(string='Joining Date')

    course_ids = fields.One2many('collage.course', 'teacher_id', string='Courses Taught')
