# ------------------ Imports ------------------
from flask import abort, g, session, current_app, request, url_for
from flask_security import RoleMixin as _role_mixin
from flask_principal import Permission, RoleNeed
from flask_mail import Message
from functools import wraps, partialmethod
from ProjectsWebsite.util.helpers import alertMessageType, InvalidType, OperationError
from typing import (
    Dict, List, Tuple, Any, Optional
)
from ProjectsWebsite.modules import guard, login_manager, db, mail
try:
    from werkzeug import LocalProxy
except ImportError:
    from werkzeug.local import LocalProxy
from bs4 import BeautifulSoup, NavigableString
from base64 import b64encode, b64decode
from itsdangerous import SignatureExpired
from rich import print as rprint
from time import sleep
from re import Pattern
import re
import requests
import schedule
import threading

# ------------------ Utils ------------------
def checkExpireRegistrationCodes(): 
    rprint("[black][Scheduler Thread][/black][bold green]Commencing token check[/bold green]")
    from ProjectsWebsite.views import urlSerializer
    from ProjectsWebsite.database.models import user_datastore, User
    with open(f"{current_app.static_folder}\\unverified\\unverified-log.txt", 'r+', encoding="utf-8") as f:
        lines = f.readlines()
        f.close()
        if lines == []:
            return None
        for line in lines:
            user = line[line.find("(")+1:line.rfind(")")]
            parenthesis_length = len(user) + 3
            token = line[parenthesis_length:]
        try:
            urlSerializer.loads(token, salt="email-confirm", max_age=3600/2)
        except SignatureExpired:
            lines.remove(line)
            expired_user = User.lookup(user)
            expired_msg = Message("Account Deleted", recipients=[user])
            expired_msg.html = f'''
            Dear {expired_user.name},
            Your current account in MyProjects has not been verified and your verification link has expired. 
            You must <a href="{url_for("main_app.registerPage")}">register</a> again if you want to have an account in MyProject.
            
            From,
            
            MyProjects Support Automated Service
            
            <hr>
            <i>If you have any questions, feel free to contact us at: <a href="{url_for("main_app.contact_us")}">Contact Us</a></i>
            '''
            mail.send(expired_msg)
            user_datastore.delete_user(user)
            user_datastore.commit()
            f.writelines(lines)
            f.close()
        except Exception as e:
            raise OperationError("urlSerializer args or kwargs caused the current operation to fail.", "itsdangerous.URLSafeTimedSerializer") from e
        else:
            for line in lines:
                f.writelines(line)
            f.close()
                

def runSchedulerInspect():
    """
    Starts Scheduler task to check unverified tokens
    """
    cease_operation = threading.Event()
    
    class tokenCheckThread(threading.Thread):
        """
        Thread to run the checks
        """
        @classmethod
        def run(cls):
            """
            runs thread if cease_operation.is_set() returns false
            """
            rprint("[black][Schedule][/black][bold green]Starting operation[/bold green]")
            while not cease_operation.is_set():
                schedule.run_pending()
                sleep(1)
    thread = tokenCheckThread()
    thread.daemon = True
    rprint("[black][Schedule][/black][red]Starting Schedule Thread...[/red]")
    thread.start()
    return cease_operation

class unverfiedLogUtil:
    """
    Utilities for managing the unverified token log file.
    
    The encoding kwarg for `open()` has been provided by default for each function.
    """
    def __init__(self):
        self.encoding = "utf-8"
    
    def addContent(self, *line_content, **openKwargs):
        """
        adds an unverfied member email and token in the unverfied log
        
        Format:
            (email) token
        """
        openKwargs.setdefault("encoding", self.encoding)
        with open(f"{current_app.static_folder}/unverified/unverfied-log.txt", **openKwargs) as f:
            line = f"({line_content[0]}) {line_content[1]}"
            lines = f.readlines()
            if lines == []:
                f.write(line)
                f.close()
            else:
                lines.append(line)
                f.writelines(lines)
                f.close()
        
    def removeContent(self, content_identifier: str, **openKwargs):
        """
        removes line matching :param content_identifier: from the log
        
        :param content_identifier: : email string
        """
        openKwargs.setdefault("encoding", self.encoding)
        with open(f"{current_app.static_folder}/unverified/unverfied-log.txt", **openKwargs) as f:
            lines = f.readlines()
            self.content = lines
            for line in lines:
                potential_email = line[line.find("(")+1:line.rfind(")")]
                if potential_email == content_identifier:
                    lines.remove(line)
                    f.writelines(lines)
                    f.close()
       
    def __eq__(self, other):
        if hasattr(self, "content"):
            if isinstance(self.content, list):
                for c in self.content:
                    if c == content:
                        return True
                return False
            return False
        raise NotImplementedError("__eq__ not implemented at the moment")

class AlertUtil(object):
    """
    Util for alert management
    """
    alert_dict = {
    'type': '',
    'message':''
    }
    
    def __init__(self, app=None):
        if isinstance(app, type(None)):
            pass
        else:
            self.init_app(app)
            
        
    def init_app(self, app):
        """
        Initializes AlertUtil
        """
        if not hasattr(self, 'config'):
            setattr(self, 'config', app.config)
            if not (
                self.config.get("ALERT_CODES_NUMBER_LIST")
                or 
                self.config.get("ALERT_CODES_DICT")
                or 
                self.config.get("ALERT_TYPES")
            ):
                raise ValueError('''Either ALERT_CODES_NUMBER_LIST or ALERT_CODES_DICT or
                                ALERT_TYPES was not found in the apps Config''')
        else:
            if not (
                self.config.get("ALERT_CODES_NUMBER_LIST")
                or 
                self.config.get("ALERT_CODES_DICT")
                or 
                self.config.get("ALERT_TYPES")
            ):
                raise ValueError('''Either ALERT_CODES_NUMBER_LIST or ALERT_CODES_DICT or
                                ALERT_TYPES was not found in the apps Config''')
                
        app.extensions['AlertUtil'] = self
    
    def getConfigValue(self, configValue: str):
        try: 
            response = self.config.get(configValue)
            return response
        except:
            raise ValueError(f'Value: {configValue} was not found in the apps Config')
    
    def setAlert(self, alertType: str , msg: alertMessageType):
        """
        Set Alert for webpages that supports Alert messages
        """
        alert_types: List[str] = self.getConfigValue("ALERT_TYPES")
        if alertType not in alert_types:
            raise InvalidType(f"{alertType} is an Invalid Type")
        self.alert_dict['type'] = alertType
        self.alert_dict['message'] = msg
        return True
    
    def getAlert(self) -> Dict[str, str]:
        """
        Gets the Alert Type and message
        Returns:
            valueDict
        """
        alert_codes_list: List[str] = self.getConfigValue("ALERT_CODES_NUMBER_LIST")
        alert_codes_dict: Dict[str, str] = self.getConfigValue("ALERT_CODES_DICT")
        alertType = self.alert_dict['type']
        alertMsg = self.alert_dict['message']            
        self.alert_dict.update(type='', message='')
        if alertType == 'error':
            if isinstance(alertMsg, int):
                raise ValueError("Type: int is not allowed")
            for code in alert_codes_list:
                if code != alertMsg:
                    continue
                else:
                    alertMsg = alert_codes_dict[code]
            valueDict = {
                    'Type': alertType,
                    'Msg': alertMsg
                }
            return valueDict   
        else:
            valueDict = {
                'Type': alertType,
                'Msg': alertMsg
            }
            return valueDict    
    
def is_valid_article_page(func):
    """
    Returns whether the article page is valid or not.
    if not valid:
    Returns:
        404 http code
    """
    from ProjectsWebsite.database.models import Article
    @wraps(func)
    def validator(id):
        articles = Article.query.all()
        for article in articles:
            article_id_number = str(article.id)
            if id == article_id_number:
                return func(id)
        return abort(404)
    return validator

def formatPhoneNumber(phone_number: str) -> str:
    """
    Formats a phonenumber.
    Returns:
        formatted_phone_number
        
    Example:
        phone_number = '9255605549'
        formatted_number = formatPhoneNumber(phone_number)
    """
    clean_phone_number = re.sub('[^0-9]+', '', phone_number)
    formatted_phone_number = re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1-", f"{int(clean_phone_number[:-1])}") + clean_phone_number[-1]
    return formatted_phone_number

class DateUtil:
    """
    DateUtil for Correcting and Validating Date
    """
    def __init__(self, date):
        self.date = date
    
    def _subDate(self, re_sub_pattern: Pattern, reversed_sub: bool, datetime_date: bool):
        """
        Corrects Date to correct format
        """
        if datetime_date:
            if reversed_sub:
                new_day = "{year}-{month}-{day}".format(year=self.date.year, month=self.date.month, day=self.date.day)
                self.date = new_day
                return new_day
            new_day = "{month}/{day}/{year}".format(month=self.date.month, day=self.date.day, year=self.date.year)
            self.date = new_day
            return new_day
        else:
            if self.validateDate(re_sub_pattern):
                return self.date
            else:
                if reversed_sub:
                    new_date = re.sub(r"(\d{1,2})/(\d{1,2}/(\d{2,4})", r"\3-\1-\2", self.date)
                    self.date = new_date
                    return new_date
                new_date = re.sub(r"(\d{2,4})-(\d{1,2})-(\d{1,2})", r"\2/\3/\1", self.date)
                self.date = new_date
                return new_date 
            
    subDate = partialmethod(_subDate, reversed_sub=False, datetime_date=False) 
    
    reversedSubDate = partialmethod(_subDate, reversed_sub=True, datetime_date=False)
    
    datetimeSubDate = partialmethod(_subDate, reversed_sub=False, datetime_date=True)
    
    reversedDatetimeSubDate = partialmethod(_subDate, reversed_sub=True, datetime_date=True)
        
    def validateDate(self, re_pattern: Pattern):
        """
        returns True if date is valid. Returns false if not
        """
        if len(self.date) == (7, 8, 9):
            return False
        elif not re_pattern.match(self.date):
            return False
        else:
            return True
                              
def scrapeError(url: str, elem: str, attr: Tuple[str, str], field_err: List[str], auth: Optional[bool] = False) -> str:
    """
    Scrapes input error from argument: url
    """
    if auth:
        token = b64decode(session["token"])
        token = str(token, encoding="utf-8")
        web_page = requests.request('GET', url, headers={'User-Agent': f"{request.user_agent}"}, params={"token":token}, allow_redirects=False)
    else:
        web_page = requests.request('GET', url, headers={'User-Agent': f"{request.user_agent}"}, allow_redirects=False)
    soup = BeautifulSoup(web_page.content, 'html5lib')
    elem_tag = soup.find_all(f'{elem}', {f"{attr[0]}": f"{attr[1]}"})
    for i in elem_tag:
        for err in field_err:
            i.insert(0, NavigableString(f"- {err}\n"))
            error = i
            return error


current_user = LocalProxy(lambda: _get_user())

def _get_user():
    from ProjectsWebsite.database.models import User, AnonymousUser
    
    if "_user_id" not in session:
        if hasattr(g, "_cached_user"):
            del(g._cached_user)
        return AnonymousUser
    if not hasattr(g, "_cached_user"):
        try:
            setattr(g, "_cached_user", User.identify(session["_user_id"]))
        except:
            session.clear()
            return AnonymousUser
    return g._cached_user

def roles_required(*roles):
    """
    Interpretation of flask-security roles_required decorator
    """
    def _wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            perms = [Permission(RoleNeed(role)) for role in roles]
            for perm in perms:
                if not perm.can():
                    if not current_user.is_authenticated:
                        return abort(401)
                    return abort(403)
            return f(*args, **kwargs)
        return decorator
    return _wrapper

def roles_accepted(*roles):
    """
    Interpretation of flask-security roles_accepted decorator
    """
    def _wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            perm = Permission(*[RoleNeed(role) for role in roles])
            if not current_user.is_authenticated:
                return abort(401)
            if perm.can():
                return f(*args, **kwargs)
            return abort(403)
        return decorator
    return _wrapper

def token_auth_required(f):
    """
    checks if token is in the session
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "token" in session:
            token = b64decode(session["token"])
            token = str(token, encoding="utf-8")
            try:
                data = guard.extract_jwt_token(token)
            except:
                return abort(401)
            return f(*args, **kwargs)
        elif "token" in request.args:
            token = request.args.get("token")
            try:
                data = guard.extract_jwt_token(token)
            except:
                return abort(401)
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated

def login_user(token, user):
    """
    Logs in user
    """
    from ProjectsWebsite.database.models import User
    session["_id"] = login_manager._session_identifier_generator()
    session["_user_id"] = user.identity
    session["_e-recipient"] = b64encode(bytes(user.username, encoding="utf-8"))
    session["_fresh"] = True
    session["token"] = b64encode(bytes(token, encoding="utf-8"))
    User.activate(user.username)
    return True

def logout_user():
    """
    Logs out user if user is logged in
    """
    from ProjectsWebsite.database.models import User
    if "_user_id" in session:
        if "_e-recipient" in session:
            user_email = b64decode(session["_e-recipient"])
            user_email = str(user_email, encoding="utf-8")
            User.deactivate(user_email)
        for key in list(session.keys()):
            session.pop(key, None)
    if "_permanent" in session:
        session.pop("_permanent", None)
    if "_fresh" in session:
        session.pop("_fresh", None) 
    return True

class staticproperty(property):
    """
    Makes Classmethod with property possible
    """
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
    
class AnonymousUserMixin(object):
    """
    AnonymouseUserMixin
    """
    @staticproperty
    def is_authenticated(cls):
        return False
    
    @staticproperty
    def is_active(cls):
        return False

    @staticproperty
    def is_anonymous(cls):
        return True

    def get_id(self):
        return
    

def generate_err_request_url(page: str = "", *, in_admin_acc_edit_page: bool = False, account_name: Optional[str] = None) -> str:
    """
    Utility for admin to generate the url for any admin accounts management errors
    Returns:
        generated url
    """
    if in_admin_acc_edit_page:
        if isinstance(account_name, type(None)):
            raise ValueError("account_name arg cannot be None")
        base_url = "{}admin/management/accounts/edit_user/{}/"
        account_name = account_name.replace(" ", "%20")
        url = base_url.format(request.host_url, account_name)
    else:
        url = f"{request.host_url}{page}"
    return url


class RoleMixin(_role_mixin):
    """
    RoleMixin with Flask-Security RoleMixin
    """
    @classmethod
    def is_role(cls, role):
        """
        Checks if role is in the Role database
        Returns:
            True - if role exists
            False = if role does not exist
        """
        r = cls.query.filter_by(name=role).first()
        if isinstance(r, type(None)):
            return False
        return True
    
    def __repr__(self):
        raise NotImplementedError()