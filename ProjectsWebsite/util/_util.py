# ------------------ Imports ------------------
from collections import UserDict, namedtuple
from collections.abc import Iterable, Iterator
from functools import partial, partialmethod, wraps
from typing import Any, Callable, List, Optional, Tuple, Type, TypeVar, Union

from flask import abort, current_app, g, request, session, url_for
from flask_mail import Message
from flask_principal import Permission, RoleNeed
from flask_security import RoleMixin as _role_mixin
from flask_sqlalchemy import Pagination
from flask_wtf import FlaskForm

from ProjectsWebsite.modules import guard, login_manager, mail
from ProjectsWebsite.util.helpers import OperationError, date_re, reversed_date_re
from ProjectsWebsite.util.mail import automatedMail

try:
    from werkzeug import LocalProxy
except ImportError:
    from werkzeug.local import LocalProxy

import hashlib
import hmac
import inspect
import os.path as _path
import re
import signal
import tempfile
import threading
import uuid
import warnings
from base64 import b64decode, b64encode
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from sys import exc_info, exit
from time import sleep

import pendulum
import schedule
from flask_praetorian.user_mixins import SQLAlchemyUserMixin
from fuzzywuzzy import fuzz, process
from googletrans import Translator
from itsdangerous import SignatureExpired
from password_strength import PasswordPolicy
from pendulum.datetime import DateTime
from polib import detect_encoding, pofile
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
    "is_valid_article_page",
    "formatPhoneNumber",
    "DateUtil",
    "makeResultsObject",
    "QueryLikeSearch",
    "countSQLItems",
    "current_user",
    "roles_required",
    "roles_accepted",
    "token_auth_required",
    "login_user",
    "logout_user",
    "AnonymousUserMixin",
    "RoleMixin",
    "validate_multiple_forms",
    "MultipleFormsConfig",
    "create_password",
    "verify_password",
    "UserMixin",
    "NonDuplicateList",
    "PasswordTestManager",
    "generate_temp_pdf_file",
]

_pagination_args = namedtuple(
    "_pagination_args", "page total_pages error_out max_per_page"
)


def checkExpireRegistrationCodes():
    print("[Scheduler Thread]Commencing token check")
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
            print("[Schedule]Starting operation...")
            while not cease_operation.is_set():
                schedule.run_pending()
                sleep(1)

    thread = tokenCheckThread()
    thread.daemon = True
    print("[Schedule]Starting Schedule Thread...")
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
        print("ScheduleStopping schedule operation")
        signal.signal(signal.SIGINT, _signal_handler)
        print("ScheduleSchedule Operation stopped successfully...")


class InternalError_or_success(AbstractContextManager):
    """
    Object checks if an Exception occurred, if it did then a 500 Internal Server error would occur
    """

    def __init__(self, exceptions: Tuple[str, str], log=False):
        self._exceptions = exceptions
        self.log = log

    def __exit__(self, exctype, excinst, exctb):
        if inspect.istraceback(exctb) and exctype is not None:
            if issubclass(exctype, self._exceptions):
                if self.log:
                    warnings.warn(f"{exctype}: {exc_info()[1]}", UserWarning)
                return abort(500)
        return


K = TypeVar("K")
V = TypeVar("V")


class temp_save(UserDict):
    """
    temporary data save dictionary that allows returning false
    if KeyError is raised when __getitem__ can't get an item due to the item being mistyped or not existing
    """

    def __init__(self, default_return: Any = False, *args, **kwargs):
        self.default_return = default_return
        super(temp_save, self).__init__(*args, **kwargs)

    def __setitem__(self, key: K, val: V) -> None:
        self.data[key] = val

    def __getitem__(self, k: K, with_pop=True) -> Union[Union[bool, Any], None]:
        try:
            if with_pop:
                return self.pop(k)
            return super().__getitem__(k)
        except KeyError:
            return self.default_return

    def get_without_pop(self, k: K) -> Union[Any, None]:
        """
        gets item without the default behavior of popping the item
        """
        val = self.__getitem__(k, False)
        if not val:
            return self.default_return
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


del K, V


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
            if self.translator.detect(entry).lang == self.locale:
                continue
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
            for line in lines:
                potential_email = line[line.find("(") + 1 : line.rfind(")")]
                if potential_email == content_identifier:
                    lines.remove(line)

                    if lines == []:
                        f.truncate(0)
                        f.close()
                    else:
                        f.writelines(lines)
                        f.close()


def is_valid_article_page(func):
    """
    Returns whether the article page is valid or not.
    if not valid:
    Returns:
        404 http code
    """
    try:
        Article = import_string("ProjectsWebsite.database.models:Article")
    except ModuleNotFoundError:
        Article = import_string("..database.models:Article")

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

    _reversed_date = False  # When basic web settings for client dashboard is avail and a method to only save the
    # changes made to be shown to the user only is found

    def __init__(
        self,
        date: Optional[Union[Type[DateTime], str]] = None,
        format_token: str = "",
        reversed_date: bool = False,
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

        self._reversed_date = reversed_date

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

    subDate = partialmethod(_subDate, reversed_sub=_reversed_date)

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
        super().__init__(
            results.query, results.page, results.per_page, results.total, results.items
        )

    def __iter__(self) -> Iterator[Any]:
        if isinstance(self.items, Iterable):
            yield from self.items
        else:
            raise TypeError(f"Object {type(self.results)} is not iterable")


def makeResultsObject(object: Callable[..., Pagination]) -> Results:
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
    try:
        Model = import_string(f"ProjectsWebsite.database.models:{model_name}")
    except ModuleNotFoundError:
        Model = import_string(f"..database.models:{model_name}")
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
    try:
        Model = import_string(f"ProjectsWebsite.database.models:{model_name}")
    except ModuleNotFoundError:
        Model = import_string(f"..database.models:{model_name}")
    items = Model.query.all()
    item_count = len(items)
    return item_count


current_user = LocalProxy(lambda: _get_user())


def _get_user():
    try:
        AnonymousUser = import_string("ProjectsWebsite.database.models:AnonymousUser")
        User = import_string("ProjectsWebsite.database.models:User")
    except ModuleNotFoundError:
        AnonymousUser = import_string("..database.models:AnonymousUser")
        User = import_string("..database.models:User")
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
    try:
        User = import_string("ProjectsWebsite.database.models:User")
    except ModuleNotFoundError:
        User = import_string("..database.models:User")
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
    try:
        User = import_string("ProjectsWebsite.database.models:User")
    except ModuleNotFoundError:
        User = import_string("..database.models:User")
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
        if not r:
            return False
        return True

    @classmethod
    def find_role(cls, role):
        r = cls.query.filter_by(name=role).first()
        if not r:
            return None
        return r

    def __repr__(self):
        raise NotImplementedError()


form_class = TypeVar("form_class", bound=FlaskForm)

form_field = TypeVar("form_field", str, List[str])

form_ignore = TypeVar("form_ignore", bound=List[str])


class MultipleFormsConfig:
    """
    `validate_multiple_forms` config object
    """

    objs_name = set()

    def __init__(
        self,
        objs: List[form_class],
        fields: List[Union[List[form_field], form_field]],
        ignores: List[form_ignore] = [],
        all: Union[bool, List[bool]] = False,
    ):
        self._make_attrs(objs=objs, fields=fields, ignores=ignores, all=all)

    def _make_str_attr(self, string: str, key: str, value: Any):
        class tmp(type(string)):
            def attr(self, k, v):
                setattr(self, k, v)
                return self

        return tmp(string).attr(key, value)

    def _make_attrs(
        self,
        objs: List[form_class],
        fields: List[Union[List[form_field], form_field]],
        ignores: List[form_ignore] = [],
        all: Union[bool, List[bool]] = False,
    ):
        for obj, fields in zip(objs, fields):
            _obj = self._make_str_attr(obj.__name__, "obj", obj)
            _obj = _obj.attr("fields", fields)
            if ignores == []:
                _obj = _obj.attr("ignore", ignores)
            else:
                _ignores = ignores.pop(0)
                _obj = _obj.attr("ignore", _ignores)
            if not all:
                _obj = _obj.attr("all", all)
            else:
                _obj = _obj.attr("all", all.pop(0))
            self.objs_name.add(_obj)
            setattr(self, _obj, _obj)

    def getobj(self, name: str):
        """
        gets config object by name
        """
        return getattr(self, name)

    def iter_obj_name(self):
        """
        iter the name of form objects
        """
        yield from self.objs_name


def validate_multiple_forms(config: MultipleFormsConfig) -> bool:
    """
    validates multiple wtforms at once:

    returns if all forms validation returns True
    if one form validation returns False, this validator will also return False

    :param ignore: will not ignore the field if data is present
    """
    result_list = []
    for form_name in config.iter_obj_name():
        _obj = config.getobj(form_name)
        form_obj = _obj.obj
        validate_all = _obj.all
        if validate_all:
            res = form_obj.validate(form_obj)
            result_list.append(res)
            continue
        field = _obj.fields
        ignore_list = _obj.ignore
        if isinstance(field, list):
            for f in field:
                field = getattr(form_obj, f, None)
                if not field:
                    continue
                if f in ignore_list:
                    if not field.data:
                        continue
                res = field.validate(form_obj)
                result_list.append(res)
            continue
        f = getattr(form_obj, field, None)
        if not f:
            continue
        if field in ignore_list:
            if not f.data:
                continue
        res = f.validate(form_obj)
        result_list.append(res)
    if False in result_list:
        return False
    return True


del form_class
del form_field
del form_ignore


def _pwd_pepper():
    """
    returns pepper for password
    """
    return "0782$KncD".encode()


def _hashpwd(salt, pwd):
    sha256_encrypt = hashlib.pbkdf2_hmac("sha256", pwd, salt, 200000)
    md5_encrypt = hashlib.md5(pwd).hexdigest().encode()
    sha512_encrypt = hashlib.sha512(pwd).hexdigest().encode()
    pepper = _pwd_pepper()
    return sha256_encrypt + md5_encrypt + sha512_encrypt + pepper


def create_password(original: str):
    """
    Creates an encrypted password with salt and pepper. Returns two values in the following order:
    salt - the randomly created salt implemented into the password
    password - the encrypted password with salt
    """
    _salt = uuid.uuid4().hex
    salt = _salt.encode()
    original = original.encode()
    encrypt = _hashpwd(salt, original)
    return _salt, encrypt


def verify_password(salt, pw_hash, input_pw) -> bool:
    """
    verifies inputed password from the existing password hash
    """
    input_pw = input_pw if isinstance(input_pw, bytes) else input_pw.encode()
    salt = salt if isinstance(salt, bytes) else salt.encode()

    return hmac.compare_digest(pw_hash, _hashpwd(salt, input_pw))


class UserMixin(SQLAlchemyUserMixin):
    """
    UserMixin for User SQL table
    """

    db = import_string("ProjectsWebsite.modules:db")

    @classmethod
    def lookup_by_name(cls, name):
        """
        looks up user by name
        """
        return cls.query.filter_by(name=name).one_or_none()

    @classmethod
    def activate(cls, email):
        """
        Activates user
        """
        user = cls.lookup(email)
        if user.active:
            return False
        else:
            user.active = True
            cls.put(user)
            cls.commit()
            return True

    @classmethod
    def deactivate(cls, email):
        """
        deactivates user
        """
        user = cls.lookup(email)
        if user.active:
            user.active = False
            cls.put(user)
            cls.commit()
            return True
        return False

    @classmethod
    def put(cls, obj):
        """
        adds object to Sql session
        """
        cls.db.session.add(obj)

    @classmethod
    def commit(cls):
        """
        Commits SQL Session
        """
        cls.db.session.commit()

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        """
        returns if user is authenticated
        """
        return True

    @property
    def is_blacklisted(self):
        """
        returns if user is blacklisted
        """
        if self.blacklisted:
            return True
        return False

    def has_role(self, role):
        """
        Checks if role is in the users role
        """
        return role in self.roles

    def get_id(self):
        """
        for Flask-Login
        """
        return self.identity

    def verify_password(self, pwd):
        """
        Returns True if pwd equals the users hashed password
        """
        return verify_password(self.user_salt, self.hashed_password, pwd)

    def iter_roles(self):
        """
        Iter's through the users roles
        """
        yield from self.roles

    def __repr__(self):
        return self.name


class NonDuplicateList:
    """
    List that removes duplicate items
    """

    base_list = []

    def __init__(self, items=[], *, delete_duplicates: bool = True):
        self.delete_duplicates = delete_duplicates
        if items:
            self._make_list(*items)

    @staticmethod
    def _loop_ratiolist(ratio_list, args):
        for ratio in ratio_list:
            if ratio[1] >= 90:
                args.remove(ratio[0])

    @classmethod
    def _loop_ratio_args(cls, args, _arg):
        extract = partial(process.extract, choices=args, scorer=fuzz.ratio, limit=10)
        if _arg:
            ratio_list = extract(_arg)
            cls._loop_ratiolist(ratio_list, args)
        else:
            for arg in args[:]:
                ratio_list = extract(arg)
                cls._loop_ratiolist(ratio_list, args)
        return args

    def _make_list(self, args):
        if self.delete_duplicates:
            args = self.clean_duplicates(args)
        args = self.clean_similar(args)
        self.extend(*args)

    @classmethod
    def clean_similar(
        cls, args: List[Any], arg: Optional[Any] = None, return_cls: bool = False
    ) -> Union[Callable[..., Any], List[Any]]:
        """
        removes similar items in lit
        """
        args = cls._loop_ratio_args(args, arg)
        if return_cls:
            return cls(*args)
        return args

    @classmethod
    def clean_duplicates(
        cls, args: List[Any], delete_similar: bool = False, return_cls: bool = False
    ) -> Union[Callable[..., Any], List[Any]]:
        """
        removes duplicates from list
        """
        for arg in args[:]:
            count = args.count(arg)
            if count > 1:
                while count != 1:
                    args.remove(arg)
                    count = args.count(arg)
        if delete_similar:
            args = cls.clean_similar(args)
        if return_cls:
            return cls(*args, delete_duplicates=False)
        return args

    def append(self, item, delete_similar: bool = False):
        """
        appends item into the list, and checks for duplicates.
        Does not append duplicate items
        """
        if item not in self.base_list:
            if delete_similar:
                self.clean_similar(self.baselist, item)
            self.base_list.append(item)

    def __getitem__(self, index) -> Any:
        return self.base_list[index]

    def __iter__(self):
        yield from self.base_list

    pop = base_list.pop
    index = base_list.index
    count = base_list.count
    remove = base_list.remove
    extend = base_list.extend


class __PasswordTestManagerIsInstanceCases:
    def __init__(self, test_result_obj):
        self.test_result = test_result_obj

    def _check_condition(self, condition):
        if condition in str(self.test_result).lower():
            return True
        return False

    @property
    def is_uppercase(self):
        """
        checks if the test result obj is uppercase
        """
        return self._check_condition("upper")

    @property
    def is_numbers(self):
        """
        check if the test result obj is numbers
        """
        return self._check_condition("numbers")

    @property
    def is_special(self):
        """
        check if the test result obj is special
        """
        return self._check_condition("special")


class PasswordTestManager(PasswordPolicy):
    """
    Extension for password_strength.PasswordPolicy that adds find methods
    for finding the total number of characters of a specific test to meet
    test requirements
    """

    def test(self, pwd):
        self.pwd = self.password(pwd)  # password Statistics function
        test_list = super(PasswordTestManager, self).test(pwd)
        for test_obj in test_list:
            isistancecases = __PasswordTestManagerIsInstanceCases(pwd)
            test_obj.is_uppercase = isistancecases.is_uppercase
            test_obj.is_numbers = isistancecases.is_numbers
            test_obj.is_special = isistancecases.is_special
        return test_list

    def find_missing_upper_characters(self, test) -> int:
        """
        Finds the total number of uppercase characters needed to fulfill the test requirement
        """
        required_char_count = test.count
        char_count = self.pwd.letters_uppercase
        return required_char_count - char_count

    def find_missing_number_characters(self, test) -> int:
        """
        Finds the total number of number characters needed to fulfill the test requirement
        """
        required_char_count = test.count
        char_count = self.pwd.numbers
        return required_char_count - char_count

    def find_missing_special_characters(self, test) -> int:
        """
        Finds the total number of special characters needed to fulfill the test requirement
        """
        required_char_count = test.count
        char_count = self.pwd.special_characters
        return required_char_count - char_count


def generate_temp_pdf_file(file_name: str, file_ext: str, _data: Union[bytes, Any]):
    tmp_file_path = current_app.config["PDF_TEMP_DIR"]
    tmp = tempfile.NamedTemporaryFile(
        prefix=file_name, suffix=file_ext, dir=tmp_file_path
    )
    data = _data if isinstance(_data, bytes) else _data.encode()
    tmp.write(data)
    setattr(tmp, "file_dir", _path.join(tmp_file_path, f"{file_name}.{file_ext}"))
    return tmp
