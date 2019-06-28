from flask import Blueprint

sms_page = Blueprint('sms_page', __name__, template_folder='templates')
@sms_page.route('/sms')
def sms_func():
    return 'Listo'