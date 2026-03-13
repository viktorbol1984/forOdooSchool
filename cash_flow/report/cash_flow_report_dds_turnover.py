from odoo import api, models


class CashFlowReportDDSTurnover(models.AbstractModel):
    """Report for DDS article turnover."""

    _name = "report.cash_flow.report_dds_turnover"
    _description = "DDS Article Turnover Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        """Build report lines with income/expense per DDS article."""
        Article = self.env["cash.flow.dds.article"].sudo()
        Transaction = self.env["cash.flow.transaction"].sudo()

        totals = {}
        transactions = Transaction.search(
            [("is_planned", "=", False), ]
        )
        for tx in transactions:
            article_id = tx.article_id.id
            entry = totals.setdefault(article_id, {"income": 0.0, "expense": 0.0})
            if tx.transaction_type == "income":
                entry["income"] += tx.amount
            elif tx.transaction_type == "expense":
                entry["expense"] += tx.amount

        lines = []
        articles = Article.browse(list(totals.keys())).sorted(lambda a: a.name or "")
        for article in articles:
            amounts = totals.get(article.id, {"income": 0.0, "expense": 0.0})
            income = amounts.get("income", 0.0)
            expense = amounts.get("expense", 0.0)
            net = income - expense
            lines.append(
                {
                    "article": article,
                    "category": article.category_id,
                    "income": income,
                    "expense": expense,
                    "net": net,
                }
            )

        return {
            "doc_ids": docids,
            "doc_model": "cash.flow.dds.article",
            "docs": articles,
            "lines": lines,
        }
