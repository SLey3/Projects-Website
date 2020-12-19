# ------------------ Imports ------------------
from flask import abort
from functools import wraps
from src.util.helpers import alertMessageType, InvalidType
from typing import Dict, List
from src.database.models import Article
from warnings import warn
import re

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
        try:
            self.config = app.config
        except:
            raise ValueError("The app value is None. This cannot be None")
    
    def getConfigValue(self, configValue: str):
        try: 
            response = self.config.get(configValue)
            return response
        except:
            raise ValueError(f'Value: {configValue} was not found in app Config')
    
    def setAlert(self, alertType: str , msg: alertMessageType):
        """
        Set Alert for webpages that supports Alert messages
        """
        alert_types: List[str] = self.getConfigValue("ALERT_TYPES")
        if alertType not in alert_types:
            raise InvalidType(f"{alertType} is an Invalid Type")
        self.alert_dict['type'] = alertType
        self.alert_dict['message'] = msg
    
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