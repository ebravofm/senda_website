from flask import Blueprint

sms_page = Blueprint('sms_page', __name__, template_folder='templates')

@sms_page.route('/sms', methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    msg = request.form.get('Body')

    # Create reply
    resp = MessagingResponse()
    resp.message("You said: {}".format(msg))

	return str(resp)