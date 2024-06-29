from PySide6.QtCore import QCoreApplication, QTimer
import pytest

from simple_qrunnable import make_simple_qrunnable

@pytest.fixture()
def app():
    return  QCoreApplication([])


def test_base(app: QCoreApplication):
    def sum(a, b):
        return a + b

    def on_done(sum):
        assert sum == 11
        app.quit()
    
    runnable_sum = make_simple_qrunnable(sum)
    runnable_sum(5, 6).bind(done=on_done).start()

    app.exec()
    
def test_class(app: QCoreApplication):
    class Foo:
        def sum(a, b):
            return a + b
    
    obj = make_simple_qrunnable(Foo)()
    r = obj.sum(5, 6).bind(final=app.quit).start()
    
    app.exec()
