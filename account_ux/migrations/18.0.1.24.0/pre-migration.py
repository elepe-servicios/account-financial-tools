from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """
    Delete view_account_payment_tree_personalization view before module update.
    This view is being removed from the module.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    view = env.ref(
        "account_ux.view_account_payment_tree_personalization",
        raise_if_not_found=False,
    )
    if view:
        view.unlink()
