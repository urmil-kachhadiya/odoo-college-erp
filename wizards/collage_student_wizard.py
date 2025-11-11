from odoo import models, fields, api

class StudentWizard(models.TransientModel):
    _name = 'student.wizard'
    _description = 'Wizard to Create Students'

    name = fields.Char(string="Student Name", required=True)
    course_id = fields.Many2one('collage.course', string="Course", required=True)
    percentage = fields.Float(string="Percentage")  # No validation here

    def action_create_student(self):
        # Directly create student, let the model handle auto-approve/reject
        student = self.env['collage.student'].create({
            'name': self.name,
            'course_id': self.course_id.id,
            'percentage': self.percentage,
        })
        return {'type': 'ir.actions.act_window_close'}
