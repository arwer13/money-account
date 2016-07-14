import dropbox
from dropbox.files import WriteMode


def get_money_txt(dropbox_token, money_txt_file_name='money.txt'):
    dbx = dropbox.Dropbox(dropbox_token)
    for entry in dbx.files_list_folder("").entries:
        print(entry.name)
        if entry.name == money_txt_file_name:
            meta, res = dbx.files_download("/" + entry.name)
            return res.content.decode()
    return None


def set_money_txt(dropbox_token, data, money_txt_file_name='money.txt'):
    dbx = dropbox.Dropbox(dropbox_token)
    dbx.files_upload(data.encode(), "/" + money_txt_file_name, WriteMode('overwrite', None))
