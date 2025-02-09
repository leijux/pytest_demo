import inspect
from functools import wraps
from threading import Lock
from typing import Any, Callable, TypeVar, Dict

import allure_commons
from allure_commons._core import plugin_manager
from allure_commons.utils import uuid4, func_parameters, represent

_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])


class StepContext:
    _lock = Lock()

    def __init__(self, title: str, params: Dict[str, Any]):
        self.title = title
        self.params = params
        self.uuid = uuid4()

    def __enter__(self):
        with self._lock:
            plugin_manager.hook.start_step(
                uuid=self.uuid, title=self.title, params=self.params)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._lock:
            plugin_manager.hook.stop_step(
                uuid=self.uuid, title=self.title, exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)

    async def __aenter__(self):
        self.__enter__()  # 直接调用同步 __enter__
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.__exit__(exc_type, exc_val, exc_tb)

    def _create_context(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> 'StepContext':
        """Helper method to create context and format title."""
        params = func_parameters(func, *args, **kwargs)
        formatted_args = list(map(represent, args))
        title = self.title.format(*formatted_args, **params)
        return StepContext(title, params)

    def __call__(self, func: _TFunc) -> _TFunc:
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_impl(*args: Any, **kwargs: Any) -> Any:
                __tracebackhide__ = True
                async with self._create_context(func, *args, **kwargs):
                    return await func(*args, **kwargs)
            return async_impl  # type: ignore
        else:
            @wraps(func)
            def impl(*args: Any, **kwargs: Any) -> Any:
                __tracebackhide__ = True
                with self._create_context(func, *args, **kwargs):
                    return func(*args, **kwargs)
            return impl  # type: ignore


allure_commons._allure.StepContext = StepContext
