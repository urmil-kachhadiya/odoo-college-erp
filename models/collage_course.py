from odoo import models, fields, api

class CollageCourse(models.Model):
    _name = 'collage.course'
    _description = 'College Course Record'

    name = fields.Char(string='Course Name', required=True)
    code = fields.Char(string='Course Code', required=True)
    department_id = fields.Many2one('collage.department', string='Department', required=True)
    teacher_id = fields.Many2one('collage.teacher', string='Course Teacher')
    duration = fields.Integer(string='Duration (months)')
    credit_points = fields.Integer(string='Credit Points')

    student_ids = fields.Many2many('collage.student', 'collage_course_student_rel',
                                   'course_id', 'student_id', string='Enrolled Students')
