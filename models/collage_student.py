from dateutil.utils import today
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
from datetime import date

_logger = logging.getLogger(__name__)   # ✅ Correct place for logger setup


class CollageStudent(models.Model):
    _name = 'collage.student'
    _description = 'Collage Student Record'
    _rec_name = 'roll_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # ✅ ADD THIS LINE

    # ---------- Fields ----------
    name = fields.Char(string="Student Name", required=True, tracking=True)
    roll_no = fields.Char(string="roll no")
    course_id = fields.Many2one('collage.course', string="Course", required=True)
    percentage = fields.Float(string="Percentage", required=True)
    address = fields.Char(string="Address")
    admission_date = fields.Date(string="Admission Date")
    image = fields.Binary(string="STUDENT PIC", attachment=True)
    dob = fields.Date(string="DOB")
    age = fields.Integer(string="current_age", compute="_compute_age", inverse="_inverse_age", store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string="Status", default='draft', tracking=True)

    department_ids = fields.Many2one('collage.department', string="Departments")

    # ---------- Compute Methods ----------
    @api.depends('dob')
    def _compute_age(self):
        for record in self:
            if record.dob:
                today_date = date.today()
                record.age = today_date.year - record.dob.year - (
                    (today_date.month, today_date.day) < (record.dob.month, record.dob.day)
                )
            else:
                record.age = 0

    def _inverse_age(self):
        """Agar user age change kare to DOB automatic nikal do"""
        for rec in self:
            if rec.age:
                today = date.today()
                rec.dob = date(today.year - rec.age, today.month, today.day)

    @api.onchange('age')
    def _onchange_age(self):
        if self.age:
            today = date.today()
            self.dob = date(today.year - self.age, today.month, today.day)
            if self.age < 5:
                return {
                    'warning': {
                        'title': "Too Young!",
                        'message': "Student age must be at least 5 years old."
                    }
                }

    # ---------- Wizard ----------
    def open_student_wizard(self):
        return {
            'name': 'Add Student Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'student.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    # ---------- Constraints ----------
    _sql_constraints = [
        ('check_name_length', 'CHECK (char_length(name) >= 3)', 'Name must be at least 3 characters long.'),
    ]

    @api.constrains('name')
    def _check_name_length(self):
        for rec in self:
            if rec.name and len(rec.name) < 3:
                raise ValidationError("Student name must be at least 3 characters long.")

    # ---------- State Actions with Logging ----------
    def action_approve(self):
        for rec in self:
            if rec.state != 'draft':
                _logger.warning("⚠️ Tried to approve non-draft student: %s", rec.name)
                raise UserError("Only draft records can be approved")
            rec.state = 'approved'
            _logger.info("✅ Student approved successfully: %s", rec.name)

    def action_reject(self):
        for rec in self:
            if rec.state != 'draft':
                _logger.warning("⚠️ Tried to reject non-draft student: %s", rec.name)
                raise UserError("Only draft records can be rejected")
            rec.state = 'rejected'
            _logger.info("🚫 Student rejected: %s", rec.name)

    def action_set_to_draft(self):
        for record in self:
            record.state = 'draft'
            _logger.info("↩️ Student moved back to draft: %s", record.name)

    # ---------- Create + Auto State + Logging ----------
    def create(self, vals):
        _logger.info("🎓 Creating student record with values: %s", vals)

        # ✅ Auto-generate roll number
        if not vals.get('roll_no'):
            vals['roll_no'] = self.env['ir.sequence'].next_by_code('collage.student.sequence')
            _logger.debug("Generated roll number: %s", vals['roll_no'])

        # ✅ Auto-approve / reject based on percentage
        if vals.get('percentage') is not None:
            if vals['percentage'] < 65:
                vals['state'] = 'rejected'
                _logger.info("🚫 Student auto-rejected due to percentage < 65")
            else:
                vals['state'] = 'approved'
                _logger.info("✅ Student auto-approved due to percentage >= 65")

        record = super(CollageStudent, self).create(vals)
        _logger.info("✅ Student created successfully: %s (ID %s)", record.name, record.id)
        return record

    # ---------- Auto-update on Edit ----------
    def write(self, vals):
        res = super(CollageStudent, self).write(vals)

        for rec in self:
            if 'percentage' in vals:
                if rec.percentage < 65:
                    rec.state = 'rejected'
                    _logger.info("🚫 Student auto-rejected because new percentage < 65: %s", rec.name)
                else:
                    rec.state = 'approved'
                    _logger.info("✅ Student auto-approved because new percentage >= 65: %s", rec.name)

        return res

    # ---------- Delete + Logging ----------
    def unlink(self):
        for rec in self:
            _logger.error("🗑️ Deleting student record: %s (ID %s)", rec.name, rec.id)
        return super(CollageStudent, self).unlink()
