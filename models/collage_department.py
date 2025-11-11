from odoo import models, fields ,api

class CollageDepartment(models.Model):
    _name = 'collage.department'
    _description = 'College Department'

    name = fields.Char(string="Department Name", required=True)
    code = fields.Char(string="Department Code")

    student_id = fields.One2many('collage.student','department_ids', string="Student")
    teacher_ids = fields.One2many('collage.teacher', 'department_id', string="Teachers")
    course_ids = fields.One2many('collage.course', 'department_id', string="Courses")


    # Computed field for student count
    student_count = fields.Integer(string="Student Count", compute='_compute_student_count')

    @api.depends('student_id')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_id)