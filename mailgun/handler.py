from Log_Api import log_resquest_response
from aws_handler_decorators import json_schema_validator, loads_json_body
from main.email import Email

@loads_json_body
@json_schema_validator('schemas/send_email.json', in_file=True)
def send_email(event, context):
    try:
        request_body = event['body']

        to = request_body['to']
        subject = request_body['subject']
        body = request_body['body']
        files = request_body.get('files', [])
        is_html = request_body.get('is_html', True)

        email = Email(subject)
        email.set_to(to)
        email.set_body(body)
        email.set_files(files)
        email.set_is_html(is_html)

        email = email.send_mailgun_email()
        response = Email.success({'id': email})
    except TypeError as e:
        response = Email.internal_server_error()
    except KeyError as e:
        response = Email.internal_server_error()
    except ValueError as e:
        response = Email.error(message=f'{e}')
    except Exception as e:
        response = Email.internal_server_error()

    return response
