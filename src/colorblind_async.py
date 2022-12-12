import asyncio
import builtins
import sys
import importlib
import os

from threading import Thread, Lock
from typing import Optional

import nest_asyncio
from collections import deque
import libcst as cst


class _TypingTransformer(cst.CSTTransformer):
    """Class for transforming Complete Syntax Tree used by ColorblindAsync._modification_func"""

    def __init__(self):
        self.upper_is_async = deque([None])

    def visit_FunctionDef(self, node) -> Optional[bool]:
        self.upper_is_async.append(bool(node.asynchronous))
        # print("visit fn def", node.name.value, self.upper_is_async)
        return super().visit_FunctionDef(node)

    def leave_FunctionDef(self, original_node, updated_node) -> None:
        self.upper_is_async.pop()
        # print("leave fn def", updated_node.name.value, self.upper_is_async)
        return updated_node

    def leave_Await(self, original_node, updated_node) -> cst.CSTNode:
        # print("leave await", self.upper_is_async[-1])
        if not self.upper_is_async[-1]:
            return cst.Call(func=cst.Name(value="__colorblind_async__"), args=[cst.Arg(original_node.expression)])
        return updated_node


class _ColorblindAsync:
    def __init__(self) -> None:
        self.loop = None
        self._builtin_import = builtins.__import__

        builtins.colorblind_async = self.colorblind_async

    def init(self, loop=None):
        if loop:
            nest_asyncio.apply(loop)
            self.loop = loop
        else:
            self.init_event_loop()

        set_builtins(self._colorblind_enhanced_import, self.colorblind_async)

    def init_event_loop(self):
        lock = Lock()
        lock.acquire()

        def run_loop():
            self.loop = asyncio.new_event_loop()
            nest_asyncio.apply(self.loop)
            print("release")
            lock.release()
            print("rum forever")
            self.loop.run_forever()

        thread = Thread(target=run_loop, daemon=True)
        thread.start()
        lock.acquire()

    def colorblind_async(self, coro):
        try:
            # check if code is in async context
            asyncio.get_running_loop()
        except RuntimeError:
            # not in async context `asyncio.get_running_loop()` raised exception
            # the first call into the async world should be threadsafe, because we created loop in separate thread
            return asyncio.run_coroutine_threadsafe(coro, self.loop).result()
        # the loop is running
        return self.loop.run_until_complete(coro)

    def _modification_func(self, source, file):
        tree = cst.parse_module(source)
        transformer = _TypingTransformer()
        modified_tree = tree.visit(transformer)

        if "DEBUG_COLORBLIND_ASYNC" in os.environ:
            print(f"~~~~modified source: {file}~~~~")
            print(modified_tree.code)
            print(f"~~~~modified source END~~~~")
        return modified_tree.code

    def _colorblind_enhanced_import(self, name, *args, **kwargs):

        try:
            return self._builtin_import(name, *args, **kwargs)
        except SyntaxError as e:
            if e.msg.startswith("'await' outside"):  # await outside function / await outside async function
                spec = importlib.util.find_spec(name)
                source = spec.loader.get_source(name)
                new_source = self._modification_func(source, name)
                module = importlib.util.module_from_spec(spec)

                codeobj = compile(new_source, module.__spec__.origin, "exec")
                exec(codeobj, module.__dict__)
                sys.modules[name] = module
                return module
            else:
                raise e


def set_builtins(colorblind_enhanced_import, colorblind_async):

    builtins.__import__ = colorblind_enhanced_import
    builtins.__colorblind_async__ = colorblind_async


ColorblindAsync = _ColorblindAsync()
