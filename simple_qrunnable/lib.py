import inspect
from typing import Any, Callable, Tuple
from PySide6.QtCore import QObject, Signal, QObject, Signal, QRunnable, QThreadPool

class Emitter(QObject):
    done = Signal(object)
    error = Signal(Exception)    
    final = Signal()
    
class SimpleQRunnable(QRunnable):
    def __init__(self, f: Callable[..., Any], *args: Tuple, **kwargs: dict):
        super().__init__()
        self.emitter = Emitter()
        
        self.func = f
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        try:
            result = self.func(*self.args, **self.kwargs)
            self.emitter.done.emit(result)
        except Exception as err:
            self.emitter.error.emit(err)
        finally:
            self.emitter.final.emit()
            
    def bind(self, done = None, error = None, final = None):    
        if done is not None:
            self.emitter.done.connect(done)
        if error is not None:
            self.emitter.error.connect(error)
        if final is not None:
            self.emitter.final.connect(final)
        
        return self
    
    def start(self, pool = None):
        if pool is None:
            pool = QThreadPool.globalInstance()
        pool.start(self)

def make_func_simple_qrunnable(func: Callable[..., Any]):
    def new_func(*args: Any, **kwargs: Any):
        return SimpleQRunnable(func, *args, **kwargs)
    return new_func

def make_method_simple_qrunnable(method: Callable[..., Any]):
    def new_method(self, *args: Any, **kwargs: Any):
        return SimpleQRunnable(method, self, *args, **kwargs)
    return new_method

def make_simple_qrunnable(
    func_or_class,
    whitelist: list[str] = None, 
    blacklist: list[str] = None, 
    blacklist_private: bool = True
):
    if inspect.isfunction(func_or_class):
        return make_func_simple_qrunnable(func_or_class)
    
    def should_wrap(method_name: str) -> bool:
        if blacklist and method_name in blacklist:
            return False
        if whitelist and method_name not in whitelist:
            return False
        if blacklist_private and method_name.startswith('_'):
            return False
        return True
    
    class_name = func_or_class.__name__ + "Runnablified"
    bases = (func_or_class,)
    dct = {}
    
    for method_name, method in vars(func_or_class).items():
        if callable(method) and method_name != '__init__' and should_wrap(method_name):
            dct[method_name] = make_method_simple_qrunnable(method)

    return type(class_name, bases, dct)