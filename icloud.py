import os
import sys
import logging

from shutil import copyfileobj

from dotenv import load_dotenv
from pyicloud import PyiCloudService


def check_2fa(api):
    if api.requires_2fa:
        print("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)

        if not result:
            print("Failed to verify security code")
            sys.exit(1)

        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print("Session trust result %s" % result)

            if not result:
                print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
    elif api.requires_2sa:
        import click

        print("Two-step authentication required. Your trusted devices are:")

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print(
                "  %s: %s" % (i, device.get('deviceName',
                                            "SMS to %s" % device.get('phoneNumber')))
            )

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print("Failed to send verification code")
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print("Failed to verify verification code")
            sys.exit(1)


def save_file(drive_file):
    with drive_file.open(stream=True) as response:
        with open(drive_file.name, 'wb') as file_out:
            copyfileobj(response.raw, file_out)


def upload_file(api, path, file):
    try:
        with open('Vacation.jpeg', 'rb') as file_in:
            api.drive['Holiday Photos'].upload(file_in)
    except KeyError as e:
        api.drive.params.update(api.session_data['client_id'])
        logging.error(e)


def main():
    logging.basicConfig(filename='pyicloud.log', filemode='a', level=logging.DEBUG)
    load_dotenv()
    password = os.getenv('PASSWORD')
    apple_id = os.getenv('APPLE_ID')
    api = PyiCloudService(apple_id=apple_id, password=password)
    check_2fa(api)


if __name__ == '__main__':
    main()


