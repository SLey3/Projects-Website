# ------------------ Imports ------------------
from collections import UserDict, namedtuple
from collections.abc import Iterable, Iterator
from functools import partial, partialmethod, wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

from flask import abort, current_app, g, request, session, url_for
from flask_mail import Message
from flask_principal import Permission, RoleNeed
from flask_security import RoleMixin as _role_mixin
from flask_sqlalchemy import Pagination

from ProjectsWebsite.modules import guard, login_manager, mail
from ProjectsWebsite.util.helpers import (
    InvalidType,
    OperationError,
    alertMessageType,
    date_re,
    reversed_date_re,
)
from ProjectsWebsite.util.mail import automatedMail

try:
    from werkzeug import LocalProxy
except ImportError:
    from werkzeug.local import LocalProxy

import os.path as _path
import re
import signal
import threading
from base64 import b64decode, b64encode
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from sys import exit
from time import sleep

import pendulum
import requests
import schedule
from bs4 import BeautifulSoup as _beautifulsoup
from bs4 import NavigableString
from googletrans import Translator
from itsdangerous import SignatureExpired
from pendulum.datetime import DateTime
from polib import detect_encoding, pofile
from rich import print as rprint
from sqlalchemy.exc import InvalidRequestError
from werkzeug.utils import import_string

# ------------------ Utils ------------------
__all__ = [
    "appExitHandler",
    "checkExpireRegistrationCodes",
    "runSchedulerInspect",
    "InternalError_or_success",
    "temp_save",
    "PoFileAutoTranslator",
    "unverfiedLogUtil",
    "AlertUtil",
    "is_valid_article_page",
    "formatPhoneNumber",
    "DateUtil",
    "makeResultsObject",
    "QueryLikeSearch",
    "countSQLItems",
    "scrapeError",
    "current_user",
    "roles_required",
    "roles_accepted",
    "token_auth_required",
    "login_user",
    "logout_user",
    "generate_err_request_url",
    "AnonymousUserMixin",
    "RoleMixin",
]


BeautifulSoup = partial(_beautifulsoup, features="html5lib")
del _beautifulsoup
del partial

_pagination_args = namedtuple(
    "_pagination_args", "page total_pages error_out max_per_page"
)


def checkExpireRegistrationCodes():
    rprint(
        "[black][Scheduler Thread][/black][bold green]Commencing token check[/bold green]"
    )
    urlSerializer, user_datastore, User = (
        import_string("ProjectsWebsite.views:urlSerializer"),
        import_string("ProjectsWebsite.database.models:user_datastore"),
        import_string("ProjectsWebsite.database.models:User"),
    )
    with open(
        f"{current_app.static_folder}\\unverified\\unverified-log.txt",
        "r+",
        encoding="utf-8",
    ) as f:
        lines = f.readlines()
        f.close()
        if lines == []:
            return None
        for line in lines:
            user = line[line.find("(") + 1 : line.rfind(")")]
            parenthesis_length = len(user) + 3
            token = line[parenthesis_length:]
        try:
            urlSerializer.loads(token, salt="email-confirm", max_age=3600 / 2)
        except SignatureExpired:
            lines.remove(line)
            with current_app.app_context():
                expired_user = User.lookup(user)
            expired_msg = Message("Account Deleted", recipients=[user])
            expired_msg.html = automatedMail(
                expired_user.name,
                f"""
                                             Your current account in MyProjects has not been verified and your verification link has expired. 
                                            You must <a href="{url_for("main_app.registerPage")}">register</a> again if you want to have an account in MyProject.""",
            )
            mail.send(expired_msg)
            with current_app.app_context():
                user_datastore.delete_user(user)
                user_datastore.commit()
            f.writelines(lines)
            f.close()
        except Exception as e:
            raise OperationError(
                "urlSerializer args or kwargs caused the current operation to fail.",
                "itsdangerous.URLSafeTimedSerializer",
            ) from e
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
            rprint(
                "[black][Schedule][/black][bold green]Starting operation[/bold green]"
            )
            while not cease_operation.is_set():
                schedule.run_pending()
                sleep(1)

    thread = tokenCheckThread()
    thread.daemon = True
    rprint("[black][Schedule][/black][red]Starting Schedule Thread...[/red]")
    thread.start()
    return cease_operation


def _signal_handler(signal, frame):
    thread_event = runSchedulerInspect()
    thread_event.set()
    return exit(0)


@contextmanager
def appExitHandler():
    schedule.every(30).minutes.do(checkExpireRegistrationCodes)
    try:
        yield
    finally:
        rprint("[black]Schedule[/black][red]Stopping schedule operation[/red]")
        signal.signal(signal.SIGINT, _signal_handler)
        rprint(
            "[black]Schedule[/black][bold green]Schedule Operation stopped successfully...[/bold green]"
        )


class InternalError_or_success(AbstractContextManager):
    """
    Object checks if an Exception occurred, if it did then a 500 Internal Server error would occur
    """

    def __init__(self, *exceptions):
        self._exceptions = exceptions

    def __enter__(self):
        ...

    def __exit__(self, exctype, excinst, exctb):
        if exctype is not None:
            if issubclass(exctype, self._exceptions):
                return abort(500)
        return


K = TypeVar("K")
V = TypeVar("V")


class temp_save(UserDict):
    """
    temporary data save dictionary that allows returning false
    if KeyError is raised when __getitem__ can't get an item due to the item being mistyped or not existing
    """

    def __setitem__(self, key: K, val: V) -> None:
        self.data[key] = val

    def __getitem__(self, k: K, with_pop=True) -> Union[bool, None]:
        try:
            if with_pop:
                return self.pop(k)
            return super().__getitem__(k)
        except KeyError:
            return False

    def get_without_pop(self, k: K) -> Union[Any, None]:
        """
        gets item without the default behavior of popping the item
        """
        val = self.__getitem__(k, False)
        if not val:
            return None
        return val

    def setMultipleValues(
        self,
        kwds: Union[Tuple[str, str], List[str]],
        values: Union[Tuple[str, str], List[str]],
    ) -> None:
        """
        set's multiple items into the dictionary
        """
        for kwd, val in zip(kwds, values):
            self[kwd] = val

    def pop(self, k: K):
        val = self.data[k]
        super().__delitem__(k)
        return val

    def items(self):
        return self.data.items()


class PoFileAutoTranslator:
    """
    Object to auto translate a Pofiles msgtxt to the locale set by Babel
    NOTE: Babel has not been set up right now.
    Do not use this class and finish setting up self.locale when Babel is present
    """

    def __init__(self, file: Union[str, Type[Path]]):
        encoding = detect_encoding(file)
        self.pfile = pofile(file, encoding=encoding, check_for_duplicates=True)
        self.locale = self.pfile.metadata["Language"]
        self.translator = Translator()

    def translate(self):
        """
        Translates all msgtxt in the pofile to the locale set by the self.locale attribute
        """
        percent_translated = self.pfile.percent_translated()
        if percent_translated == 100:
            return
        for entry in self.pfile:
            translated = self.translator.translate(entry.msgid, dest=self.locale)
            entry.msgstr = translated.text
        self.pfile.save()


class unverfiedLogUtil:
    """
    Utilities for managing the unverified token log file.

    The encoding kwarg for `open()` has been provided by default for each function.
    """

    def __init__(self):
        dir = Path(_path.dirname(_path.abspath(__file__)))
        self.openKwargs = {}
        self.openKwargs["mode"] = "r+"
        self.openKwargs["encoding"] = "utf-8"
        # to make testing much easier as it would allow for the file path to be changed easily
        self.filepath = dir / "unverified" / "unverfied-log.txt"

    def addContent(self, line_content: Tuple[str, str]):
        """
        adds an unverfied member email and token in the unverfied log

        Format:
            (email) token
        """
        with open(self.filepath, **self.openKwargs) as f:
            line = f"({line_content[0]}) {line_content[1]}"
            lines = f.readlines()
            if lines == []:
                f.write(line)
                f.close()
            else:
                lines.append(line)
                f.writelines(lines)
                f.close()

    def removeContent(self, content_identifier: str):
        """
        removes line matching :param content_identifier: from the log

        :param content_identifier: : email string
        """
        with open(self.filepath, **self.openKwargs) as f:
            lines = f.readlines()
            print(lines)
            for line in lines:
                potential_email = line[line.find("(") + 1 : line.rfind(")")]
                if potential_email == content_identifier:
                    lines.remove(line)
                    print(lines)
                    if lines == []:
                        f.truncate(0)
                        f.close()
                    else:
                        f.writelines(lines)
                        f.close()


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

    def setAlert(self, alertType: str, msg: alertMessageType):
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


def is_valid_article_page(func):
    """
    Returns whether the article page is valid or not.
    if not valid:
    Returns:
        404 http code
    """
    Article = import_string("ProjectsWebsite.database.models:Article")

    @wraps(func)
    def validator(id):
        articles = Article.query.all()
        for article in articles:
            if id == str(article.id):
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
    clean_phone_number = re.sub("[^0-9]+", "", phone_number)
    formatted_phone_number = (
        re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1-", f"{int(clean_phone_number[:-1])}")
        + clean_phone_number[-1]
    )
    return formatted_phone_number


class DateUtil:
    """
    DateUtil for Correcting and Validating Date
    """

    def __init__(
        self, date: Optional[Union[Type[DateTime], str]] = None, format_token: str = ""
    ):
        if not date:
            date = pendulum.now()
        self.date = date
        if isinstance(self.date, DateTime):
            if not format_token:
                raise ValueError(
                    "format_token cannot be blank when date is the instance of pendulum DateTime"
                )
            self.token = format_token
        else:
            self.token = None

    def _subDate(self, reversed_sub: bool):
        """
        Corrects Date to correct format
        """
        if isinstance(self.date, DateTime):
            if self.validateDate():
                return self.date
            new_day = self.date.format(self.token)
            self.date = new_day
            return new_day
        else:
            if reversed_sub:
                if self.validateDate(True):
                    return self.date
                new_date = re.sub(
                    r"(\d{1,2})/(\d{1,2}/(\d{2,4})", r"\3-\1-\2", self.date
                )
                self.date = new_date
                return new_date
            if self.validateDate():
                return self.date
            new_date = re.sub(r"(\d{2,4})-(\d{1,2})-(\d{1,2})", r"\2/\3/\1", self.date)
            self.date = new_date
            return new_date

    subDate = partialmethod(_subDate, reversed_sub=False)

    reversedSubDate = partialmethod(_subDate, reversed_sub=True)

    def validateDate(self, reversed: bool = False):
        """
        returns True if date is valid. Returns false if not
        """
        if isinstance(self.date, DateTime):
            try:
                pendulum.from_format(self.date, self.token)
            except:
                return False
            else:
                return True
        if len(self.date) == (7, 8, 9):
            return False
        if reversed:
            if not reversed_date_re.match(self.date):
                return False
            return True
        if not date_re.match(self.date):
            return False
        return True

    def __eq__(self, other):
        return self.date == other.date


class Results(Pagination):
    """
    allows Pagination object to be iterable
    """

    def __init__(self, results: Pagination):
        self.per_page = results.per_page
        self.total = results.total
        self.items = results.items
        self.page = results.page

    def __iter__(self) -> Iterator[Any]:
        if isinstance(self.items, Iterable):
            yield from self.items
        else:
            raise TypeError(f"Object {type(self.results)} is not iterable")


def makeResultsObject(object: Callable[[Pagination], Results]) -> Results:
    """
    makes a results object from the provided object
    """
    results_object = Results(object)
    return results_object


def QueryLikeSearch(
    model_name: str,
    kw: str,
    page: int,
    total_pages: int,
    name: str = "",
    attr_name: str = "name",
) -> Results:
    """
    finds a result from the keyword provided in the Model imported by :param: model_name that may be in the name of a user

    Returns:
        Results
    """
    model_name = model_name.capitalize()
    Model = import_string(f"ProjectsWebsite.database.models:{model_name}")
    args = _pagination_args(page, total_pages, False, 3)
    if not kw:
        if name:
            try:
                results = Model.query.filter_by(name=name).paginate(*args)
            except InvalidRequestError:
                results = Model.query.filter_by(author=name).paginate(*args)
            finally:
                results = makeResultsObject(results)
                return results
        results = Model.query.all().paginate(*args)
        results = makeResultsObject(results)
        return results
    row_attr = getattr(Model, attr_name, None)
    if row_attr:
        if name:
            try:
                results = (
                    Model.query.filter(row_attr.like(f"%{kw}%"))
                    .filter_by(name=name)
                    .paginate(*args)
                )
            except InvalidRequestError:
                results = (
                    Model.query.filter(row_attr.like(f"%{kw}%"))
                    .filter_by(author=name)
                    .paginate(*args)
                )
            finally:
                results = makeResultsObject(results)
                return results
        results = Model.query.filter(row_attr.like(f"%{kw}%")).paginate(*args)
        results = makeResultsObject(results)
        return results


def countSQLItems(model_name) -> int:
    """
    count the number of items in an SQL Database
    """
    Model = import_string(f"ProjectsWebsite.database.models:{model_name}")
    items = Model.query.all()
    item_count = len(items)
    return item_count


def scrapeError(
    url: str, elem: str, attr: Tuple[str, str], field_err: List[str], auth: bool = False
) -> str:
    """
    Scrapes input error from argument: url
    """
    if auth:
        token = b64decode(session["token"])
        token = str(token, encoding="utf-8")
        web_page = requests.request(
            "GET",
            url,
            headers={"User-Agent": f"{request.user_agent}"},
            params={"token": token},
            allow_redirects=False,
        )
    else:
        web_page = requests.request(
            "GET",
            url,
            headers={"User-Agent": f"{request.user_agent}"},
            allow_redirects=False,
        )
    soup = BeautifulSoup(web_page.content)
    elem_tag = soup.find_all(f"{elem}", {f"{attr[0]}": f"{attr[1]}"})
    for i in elem_tag:
        for err in field_err:
            i.insert(0, NavigableString(f"- {err}\n"))
            error = i
            return error


current_user = LocalProxy(lambda: _get_user())


def _get_user():
    from ProjectsWebsite.database.models import AnonymousUser, User

    if "_user_id" not in session:
        if hasattr(g, "_cached_user"):
            del g._cached_user
        return AnonymousUser
    if not hasattr(g, "_cached_user"):
        try:
            g._cached_user = User.identify(session["_user_id"])
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
    checks if token is in the session and is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if "token" in session:
            token = b64decode(session["token"])
            token = str(token, encoding="utf-8")
            try:
                guard.extract_jwt_token(token)
            except:
                return abort(401)
            return f(*args, **kwargs)
        elif "token" in request.args:
            token = request.args.get("token")
            try:
                guard.extract_jwt_token(token)
            except:
                return abort(401)
            return f(*args, **kwargs)
        return abort(403)

    return decorated


def login_user(token, user):
    """
    Logs in user
    """
    User = import_string("ProjectsWebsite.database.models:User")
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
    User = import_string("ProjectsWebsite.database.models:User")
    if current_user.is_anonymous:
        return True
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


class AnonymousUserMixin:
    """
    AnonymouseUserMixin functions
    """

    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return False

    @property
    def is_anonymous(self):
        return True

    @property
    def is_blacklisted(self):
        return False

    @property
    def get_id(self):
        return


def generate_err_request_url(
    page: str = "",
    *,
    in_admin_acc_edit_page: bool = False,
    account_name: Optional[str] = None,
) -> str:
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
