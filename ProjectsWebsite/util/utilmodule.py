from typing import Dict, List, Union

# ------------------ AlertUtil ------------------
__all__ = ["alert", "AlertUtil"]


class InvalidType(Exception):
    """
    Raised when theres an Invalid type
    """

    def __init__(self, msg):
        super().__init__(msg)


class AlertUtil(object):
    """
    Util for alert management
    """

    alert_dict = {"type": "", "message": ""}

    def __init__(self, app=None):
        if isinstance(app, type(None)):
            pass
        else:
            self.init_app(app)

    def init_app(self, app):
        """
        Initializes AlertUtil
        """
        if not hasattr(self, "config"):
            setattr(self, "config", app.config)
            if not (
                self.config.get("ALERT_CODES_NUMBER_LIST")
                or self.config.get("ALERT_CODES_DICT")
                or self.config.get("ALERT_TYPES")
            ):
                raise ValueError(
                    """Either ALERT_CODES_NUMBER_LIST or ALERT_CODES_DICT or
                                ALERT_TYPES was not found in the apps Config"""
                )
        else:
            if not (
                self.config.get("ALERT_CODES_NUMBER_LIST")
                or self.config.get("ALERT_CODES_DICT")
                or self.config.get("ALERT_TYPES")
            ):
                raise ValueError(
                    """Either ALERT_CODES_NUMBER_LIST or ALERT_CODES_DICT or
                                ALERT_TYPES was not found in the apps Config"""
                )

        app.extensions["AlertUtil"] = self

    def getConfigValue(self, configValue: str):
        try:
            response = self.config.get(configValue)
            return response
        except:
            raise ValueError(f"Value: {configValue} was not found in the apps Config")

    def setAlert(self, alertType: str, msg: Union[str, int]):
        """
        Set Alert for webpages that supports Alert messages
        """
        alert_types: List[str] = self.getConfigValue("ALERT_TYPES")
        if alertType not in alert_types:
            raise InvalidType(f"{alertType} is an Invalid Type")
        self.alert_dict["type"] = alertType
        self.alert_dict["message"] = msg
        return True

    def getAlert(self) -> Dict[str, str]:
        """
        Gets the Alert Type and message
        Returns:
            valueDict
        """
        alert_codes_list: List[str] = self.getConfigValue("ALERT_CODES_NUMBER_LIST")
        alert_codes_dict: Dict[str, str] = self.getConfigValue("ALERT_CODES_DICT")
        alertType = self.alert_dict["type"]
        alertMsg = self.alert_dict["message"]
        self.alert_dict.update(type="", message="")
        if alertType == "error":
            if isinstance(alertMsg, int):
                raise TypeError("type int is not allowed")
            for code in alert_codes_list:
                if code != alertMsg:
                    continue
                else:
                    alertMsg = alert_codes_dict[code]
            valueDict = {"Type": alertType, "Msg": alertMsg}
            return valueDict
        else:
            valueDict = {"Type": alertType, "Msg": alertMsg}
            return valueDict


alert = AlertUtil()
