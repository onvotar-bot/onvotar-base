# coding: utf-8
import os
import logging
import hashlib

from flask import Flask, request, send_from_directory, render_template

from fbmq import Page
from config import CONFIG
from onvotar import answer

app = Flask(__name__)

from log_helper import config_logging
config_logging('on_votar_fb.log')

logger = logging.getLogger('fb_on_votar')

page = Page(CONFIG['FACEBOOK_TOKEN'])


@page.after_send
def after_send(payload, response):
    print('AFTER_SEND : ' + payload.to_json())
    print('RESPONSE : ' + response.text)



@app.route('/webhook', methods=['GET'])
def validate():
    if request.args.get('hub.mode', '') == 'subscribe' and \
                    request.args.get('hub.verify_token', '') == CONFIG['VERIFY_TOKEN']:

        print("Validating webhook")

        return request.args.get('hub.challenge', '')
    else:
        return 'Failed validation. Make sure the validation tokens match.'


@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    page.handle_webhook(payload)

    return "ok"


@app.route('/authorize', methods=['GET'])
def authorize():
    account_linking_token = request.args.get('account_linking_token', '')
    redirect_uri = request.args.get('redirect_uri', '')

    auth_code = '1234567890'

    redirect_uri_success = redirect_uri + "&authorization_code=" + auth_code

    return render_template('authorize.html', data={
        'account_linking_token': account_linking_token,
        'redirect_uri': redirect_uri,
        'redirect_uri_success': redirect_uri_success
    })


@page.handle_message
def message_handler(event):
    """:type event: fbmq.Event"""
    sender_id = event.sender_id
    message = event.message_text

    logger.info(
        'Incoming message from %s',
        hashlib.sha256(bytes(sender_id, 'utf8')).hexdigest()
    )
    res = answer(message)
    logger.info('---')

    page.send(sender_id, res)


@page.after_send
def after_send(payload, response):
    """:type payload: fbmq.Payload"""
    print("complete")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
