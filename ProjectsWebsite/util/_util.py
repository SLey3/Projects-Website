# ------------------ Imports ------------------
from flask import abort, jsonify, g, session, current_app, request
from functools import wraps
from ProjectsWebsite.util.helpers import alertMessageType, InvalidType
from typing import (
    Dict, List, Tuple, Any, Optional
)
from ProjectsWebsite.database.models import Article
from ProjectsWebsite.modules import guard, login_manager
try:
    from werkzeug import LocalProxy
except ImportError:
    from werkzeug.local import LocalProxy
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString
from six import reraise
from sys import exc_info
from base64 import b64encode, b64decode
from requests.auth import HTTPDigestAuth
from requests.exceptions import ConnectionError
from re import Pattern
import re
import requests

# ------------------ Utils ------------------
class AlertUtil(object):
    """
    Util for alert manegement
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
        alert_codes_list: List[int] = self.getConfigValue("ALERT_CODES_NUMBER_LIST")
        alert_codes_dict: Dict[int, str] = self.getConfigValue("ALERT_CODES_DICT")
        alertType = self.alert_dict['type']
        alertMsg = self.alert_dict['message']            
        self.alert_dict.update(type='', message='')
        if alertType == 'error':
            for code in alert_codes_list:
                if code == alertMsg:
                    alertMsg = alert_codes_dict[alertMsg]
                else:
                    continue 
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
    @wraps(func)
    def validator(*args, **kwargs):
        articles = Article.query.all()
        for article in articles:
            article_id_number = str(article.id)
            if id == article_id_number:
                return func(*args, **kwargs)
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



@dataclass(eq=False)
class DateUtil:
    """
    DateUtil for Correcting and Validating Date
    """
    date: Any
        
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
         
    def subDate(self, re_sub_pattern: Pattern, reversed_sub: bool = False):
        """
        Corrects Date to correct format
        """
        if isinstance(self.date, datetime):
            self.date = "{month}/{day}/{year}".format(month=self.date.month, day=self.date.day, year=self.date.year)
            return self.date
        else:
            if self.validateDate(re_sub_pattern):
                return self.date
            else:
                if reversed_sub:
                    new_date = re.sub(r"(\d{1,2})/(\d({1,2})/(\d{2,4})", r"\3-\1-\2", self.date)
                    self.date = new_date
                    return new_date
                new_date = re.sub(r"(\d{2,4})-(\d{1,2})-(\d{1,2})", r"\2/\3/\1", self.date)
                self.date = new_date
                return new_date   
                       
def scrapeError(url: str, o: Tuple[str, str], field_err: List[str], auth: Optional[bool] = False) -> str:
    """
    Scrapes input error from argument: url
    """
    with requests.Session() as sess:
        if auth:
            token = b64decode(session["token"])
            token = str(token, encoding="utf-8")
            web_page = sess.get(url, params={"token":token})
        else:
            web_page = sess.get(url)
        soup = BeautifulSoup(web_page.content, 'html5lib')
        p_tag = soup.find_all('p', {f"{o[0]}": f"{o[1]}"})
        print("P tag:", p_tag)
        for p in p_tag:
            print(p)
            for err in field_err:
                print(err)
                p.insert(0, NavigableString(f"- {err}\n"))
                error = p
                print(error)
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
                return abort(403)
            return f(*args, **kwargs)
        elif "token" in request.args:
            token = request.args.get("token")
            try:
                data = guard.extract_jwt_token(token)
            except:
                return abort(403)
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated

def login_user(token, user):
    """
    Logs in user
    """
    session["_id"] = login_manager._session_identifier_generator()
    session["_user_id"] = user.identity
    session["_fresh"] = True
    session["token"] = b64encode(bytes(token, encoding="utf-8"))
    return True

def logout_user():
    """
    Logs out user if user is logged in
    """
    if "_user_id" in session:
        for key in list(session.keys()):
            session.pop(key, None)
    return True