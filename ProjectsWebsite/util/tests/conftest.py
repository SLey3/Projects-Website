from pytest import fixture
from polib import POFile, POEntry
from pathlib import Path
try:
    from .. import PoFileAutoTranslator
except ImportError:
    from ProjectsWebsite.util import PoFileAutoTranslator
import os.path as _path
import pendulum

test_directory = Path(_path.dirname(_path.abspath(__file__)))

dt = pendulum.now()

@fixture
def poFileInitializer():
    file = POFile()
    file.metadata = {
        'Project-Id-Version': "1.0",
        'Report-Msgid-Bugs-To': "ghub4127@gmail.com",
        'PO-Revision-Date': f"{dt.to_datetime_string()}",
        'Language': "es",
        'MIME-Version': "1.0",
        'Content-Type': "text/plain; charset=utf-8"
    }
    entry1 = POEntry(
        msgid=u'This is a test PO File.',
        occurrences=[('fixtures.py', '22')]
    )
    entry2 = POEntry(
        msgid=u'TERMS AND CONDITIONS: 1) No Plagerizing in ANY way!',
        occurrences=[('fixtures.py', '27')]
    )
    file.append(entry1)
    file.append(entry2)
    file.save(test_directory.joinpath("po", "testpo.po"))
    
@fixture
def poFileTranslate():
    translator = PoFileAutoTranslator(test_directory.joinpath("po", "testpo.po"))
    translator.translate()