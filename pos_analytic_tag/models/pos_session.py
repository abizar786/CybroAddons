# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Haseen (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import fields, models


class PosSession(models.Model):
    """To add analytic tags in pos session"""
    _inherit = 'pos.session'

    pos_analytic_account_id = fields.Many2one('account.analytic.account',
                                              string='Pos Analytic Tag',
                                              help="Pos Analytic account in"
                                                   " pos session",
                                              readonly=True)

    def _create_account_move(self, balancing_account=False,
                             amount_to_balance=0,
                             bank_payment_method_diffs=None):
        """Call the parent class method using super() and creates
         analytic distribution model"""
        res = super()._create_account_move(balancing_account,
                                           amount_to_balance,
                                           bank_payment_method_diffs)
        self.pos_analytic_account_id = self.config_id.analytic_account_id
        for rec in self.move_id.line_ids:
            rec.write({
                'analytic_distribution': {
                    self.config_id.analytic_account_id.id: 100}
            })
        if self.pos_analytic_account_id:
            self.env['account.analytic.distribution.model'].create([{
                'analytic_distribution': {
                    self.config_id.analytic_account_id.id: 100}
            }])
        else:
            return False
        return res

    def _validate_session(self, balancing_account=False, amount_to_balance=0,
                          bank_payment_method_diffs=None):
        res = super()._validate_session(balancing_account, amount_to_balance,
                                        bank_payment_method_diffs)
        ids = self.move_id.line_ids.open_reconcile_view()
        for rec in self.env['account.move.line'].search(ids['domain']):
            rec.write({
                'analytic_distribution': {
                    self.config_id.analytic_account_id.id: 100}
            })
        return res
