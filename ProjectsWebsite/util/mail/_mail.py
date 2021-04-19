# ------------------ Imports ------------------
from flask import url_for, current_app
from typing import List, Optional
from ProjectsWebsite.util.mail.filter import letterFilter
import os.path as path

# ------------------ Mail Utility ------------------
BASE_PATH = path.join(path.abspath('.'), "email_template")

def _insert_content(letter: List[str], recipient:str, content: str, sender: Optional[str] = None) -> List[str]:
    for char in letter[:]:
        i = letter.index(char)
        if char == r"Dear{name},":
            char.replace(r"{name}", recipient)
            letter[i] = char
        elif char == r"{body}":
            char = char.replace(r"{name}", recipient)
            letter[i] = char
        elif char == r"{contacturl}":
            with current_app.app_context():
                char = char.replace(r"{contacturl}", url_for("main_app.contact_us"))
            letter[i] = char
        if isinstance(sender, str):
            if char == r"{sender}":
                char = char.replace(r"{sender}", sender)
                letter[i] = char
    return letter


def _format_contact(letter: List[str], name: str, inquiry_selection: str, email: str, tel: str, msg: str) -> List[str]:
    for char in letter[:]:
        i = letter.index(char)
        if char == "{name}":
            letter[i] = char.replace("{name}", name)
        elif char == "{inquiry_selection}":
            letter[i] = char.replace("{inquiry_selection}", inquiry_selection)
        elif char == "{email}":
            letter[i] = char.replace("{email}", email)
        elif char == "{tel}":
            letter[i] = char.replace("{tel}", tel)
        else:
            letter[i] = char.replace("{msg}", msg)
    return letter

def automatedMail(recipient_name: str, body: str):
    """
    formats the automated Mail Letter
    """
    with open("ProjectsWebsite/util/mail/email_template/automated_template.txt", 'r', encoding="utf-8") as a:
        letter = a.readlines()
    filtered_letter = letterFilter(letter)
    letter = _insert_content(filtered_letter, recipient_name, body)
    mail = "".join(char for char in letter)
    return mail

def defaultMail(recipient_name: str, body: str, sender: str):
    """
    formats the default Mail Letter
    """
    with open("ProjectsWebsite/util/mail/email_template/default_template.txt") as d:
        letter = d.readlines()
    print(letter)
    filtered_letter = letterFilter(letter)
    letter = _insert_content(filtered_letter, recipient_name, body, sender)
    mail = "".join(char for char in letter)
    return mail

def formatContact(**kwargs):
    """
    formats Contact Us email
    """
    with open("ProjectsWebsite/util/mail/email_template/contact_us_template.txt", 'r', encoding="utf-8") as c:
        contact = c.readlines()
    filtered_contact = letterFilter(contact)
    contact = _format_contact(filtered_contact, **kwargs)
    mail = "".join(char for char in contact)
    return mail