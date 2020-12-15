# ------------------ Imports ------------------
from flask import abort
from functools import wraps
from .helpers import alertMessageType
from typing import (
    Dict, Optional, Any, List
)
from src.database.models import Article
from warnings import warn
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
    
    def getConfigValue(self, configValue: str) -> Any:
        try: 
            response = self.config.get(configValue)
            return response
        except:
            raise ValueError(f'Value: {configValue} was not found in app Config')
    
    def setAlert(self, alertType: str , msg: Optional[alertMessageType] = None):
        if isinstance(msg, type(None)):
            warn("Alert message has been detected as None. Defaulting to Error msg", category=ResourceWarning)
            self.alert_dict['type'] = 'error'
            self.alert_dict['message'] = 'Error: AlertUtil: setAlert: Failed to load alert message. Please contact the administrator if this continues.'
        else:
            self.alert_dict['type'] = alertType
            self.alert_dict['message'] = msg
    
    def getAlert(self) -> Dict[str, Any]:
        alert_codes_list: List[int] = self.getConfigValue("ALERT_CODES_NUMBER_LIST")
        alert_codes_dict: Dict[int, str] = self.getConfigValue("ALERT_CODES_DICT")
            
        alertType = self.alert_dict['type']
        alertMsg: alertMessageType = self.alert_dict['message']                
        self.alert_dict.update(type='', message='')
        if alertType == 'error':
            for code in alert_codes_list:
                if alertMsg == code:
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