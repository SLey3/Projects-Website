# ------------------ Imports ------------------
import os.path as _path
import sys
import traceback
from pathlib import Path
from random import choice

import pytest
from flask import jsonify, url_for
from flask.testing import FlaskClient
from polib import detect_encoding, pofile

try:
    from ProjectsWebsite import app
    from ProjectsWebsite.util._util import *
    from ProjectsWebsite.util._util import temp_save as _temp_save
    from ProjectsWebsite.util.tests.utils import (
        _pofile_expected_translations,
        _temp_save_expected_responces,
    )
    from ProjectsWebsite.util.utilmodule import AlertUtil
except ModuleNotFoundError:
    from ... import app
    from .._util import *
    from .._util import temp_save as _temp_save
    from ..utilmodule import AlertUtil
    from .utils import _pofile_expected_translations, _temp_save_expected_responces

test_directory = Path(_path.dirname(_path.abspath(__file__)))

app.config["TESTING"] = True
app.config["REMOTE_ADDR"] = "127.0.0.1:5000"
app.config["SERVER_NAME"] = app.config["REMOTE_ADDR"]

# ------------------ tests ------------------
def test_InternalError_or_success():
    # test the InternalError_or_success class
    client = FlaskClient(application=app)

    @app.route("/test_route/<string:indexerror>", methods=["GET"])
    def test_route(indexerror="False"):
        with InternalError_or_success(ValueError, RuntimeError):
            if indexerror == "True":
                raise IndexError()
            decision = choice([ValueError, RuntimeError, "No exceptions"])
            if not isinstance(decision, str):
                if issubclass(decision, Exception):
                    raise decision
            return jsonify(dict(type="test"))

    for _ in range(2):
        res = client.get("/test_route", follow_redirects=True)
        json = res.get_json(True, True)
        if json and json["type"] == "test":
            if res.status_code == 200 or res.status_code == 500:
                continue
            else:
                pytest.fail(
                    f"The url did not return a 200 or 500 status code, Instead: {res.status_code}"
                )

    with pytest.raises(IndexError):
        with app.app_context():
            url = url_for("test_route", indexerror="True")
        client.get(url, follow_redirects=True)


def test_temp_save():
    # tests the __getitem__ and __setitem__ for the temp_save dict
    temp_save = _temp_save()
    try:
        if temp_save["python"]:
            pytest.fail("temp_save object has a value that has not been set")
    except Exception as e:
        pytest.fail(e)
    try:
        temp_save["type"] = "test"
        temp_save["number"] = 5
    except Exception as e:
        pytest.fail(traceback.format_exception(sys.last_type, e, sys.last_traceback))

    # assertions
    assert (
        temp_save["type"] == _temp_save_expected_responces["type"]
    ), 'temp_save["type"] does not equal  _temp_save_expected_responces["type"]'
    assert (
        temp_save["number"] == _temp_save_expected_responces["number"]
    ), 'temp_save["number"] does not equal  _temp_save_expected_responces["number"]'


def test_temp_save_setMultipleValues():
    # tests the setMultipleValues from the temp_save dict
    temp_save = _temp_save()
    temp_save.setMultipleValues(
        ("Numbers", "str", "line", "test"),
        (1, 2, 3, 4),
        "This is a test string",
        "foo bar",
        "temp_save",
    )
    assert (
        temp_save["Numbers"],
        temp_save["str"],
        temp_save["line"],
        temp_save["test"],
    ) == (
        _temp_save_expected_responces["multivalues"]["Numbers"],
        _temp_save_expected_responces["multivalues"]["str"],
        _temp_save_expected_responces["multivalues"]["line"],
        _temp_save_expected_responces["multivalues"]["test"],
    ), 'temp_save values set by setMultipleValues did not match the values stored inside of _temp_save_expected_responces["multivalues"]'


@pytest.mark.usefixtures("poFileInitializer", "poFileTranslate")
def test_PoFileAutoTranslator():
    path_to_po = test_directory / "po" / "testpo.po"
    enc = detect_encoding(path_to_po)
    po = pofile(path_to_po, encoding=enc)
    for entry in po:
        assert (
            entry.msgstr == _pofile_expected_translations[entry.msgid]
        ), f"""{entry.msgstr} does not equal 
        the translation of msgid: {_pofile_expected_translations[entry.msgid]}"""


def test_unverfiedLogUtil():
    # test all functions in the unverfiedLogUtil object
    _log_dir = test_directory / "log_file" / "testlog.txt"
    test_log = unverfiedLogUtil()
    test_log.filepath = _log_dir
    test_string = (
        "Exerpt",
        "This is a test excerpt",
    )
    test_log.addContent(test_string)
    with open(_log_dir, "r", encoding="utf-8") as log:
        lines = log.readlines()
        log.close()
    assert (
        lines != [] and lines[0] == f"({test_string[0]}) {test_string[1]}"
    ), "The log was blank or the log line did not match the test_string"

    test_log.removeContent(test_string[0])
    with open(_log_dir, "r", encoding="utf-8") as log:
        lines = log.readlines()
        log.close()
    assert lines == [], "The excerpt line was still present"


def test_AlertUtil():
    # tests all functionality of the AlertUtil object
    test_alert = AlertUtil(app)
    with pytest.raises(ValueError):
        test_alert.getConfigValue("foo")
    assert test_alert.getConfigValue("ALERT_CODES_NUMBER_LIST") == [
        "0",
        "1",
        "2",
        "3",
        "4",
    ], "function AlertUtils.getConfigValue did not get the correct value for ALERT_CODES_NUMBER_LIST"

    test_alert.setAlert("info", "This is a test alert.")
    assert test_alert.alert_dict == {
        "type": "info",
        "message": "This is a test alert.",
    }, "The test_alert dictionary does equal to what it is supposed to."

    test_alert_dict = test_alert.getAlert()
    assert (
        test_alert_dict["Type"] == "info"
        and test_alert_dict["Msg"] == "This is a test alert."
    ), "One of the values in the dict is not correct."


@pytest.mark.parametrize("app", [app])
def test_is_valid_article_page(app):
    # tests whether the function is able to detect if a url is a valid article link or not
    client = FlaskClient(application=app)
    res = client.get("/articles/1", follow_redirects=True)
    assert (
        res.status_code == 200
    ), f"""Test Client did not return a 200 http status. returned: {res.status_code}. Traceback if there is one:
                                    Type: {sys.exc_info()[0] if sys.exc_info() else "None"}
                                    Traceback: {traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]) if sys.exc_info() else "None"}
                                    """
    res = client.get("/articles/1000000000000", follow_redirects=True)

    assert (
        res.status_code == 404
    ), f"""Test client did not return a 404 http status but returned {res.status_code}. Traceback if there is one:
                                    Type: {sys.exc_info()[0] if sys.exc_info() else "None"}
                                    Traceback: {traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]) if sys.exc_info() else "None"}"""
