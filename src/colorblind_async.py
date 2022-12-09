import asyncio
import builtins
import sys
import importlib
import os
from threading import Thread, Lock
from typing import Optional
import libcst as cst


loop = None


def init_event_loop():
    lock = Lock()

    def run_loop():
        global loop
        loop = asyncio.new_event_loop()
        lock.release()
        loop.run_forever()

    lock.acquire()
    thread = Thread(target=run_loop, daemon=True)
    thread.start()
    lock.acquire()  # loop ready


def __colorblind_async(coro):
    global loop
    if not loop:
        init_event_loop()
    asyncio.run_coroutine_threadsafe(coro, loop).result()


builtins.__colorblind_async = __colorblind_async


_builtin_import = builtins.__import__


class TypingTransformer(cst.CSTTransformer):
    def __init__(self):
        self.upper_is_async = None

    def visit_FunctionDef(self, node: "FunctionDef") -> Optional[bool]:
        self.upper_is_async = bool(node.asynchronous)
        return super().visit_FunctionDef(node)

    def leave_FunctionDef(self, original_node, updated_node) -> None:
        self.upper_is_async = None
        return updated_node

    def leave_Await(self, original_node, updated_node) -> cst.CSTNode:
        if not self.upper_is_async:
            return cst.Call(func=cst.Name(value="__colorblind_async"), args=[cst.Arg(original_node.expression)])
        return updated_node


def modification_func(source, file):
    tree = cst.parse_module(source)
    transformer = TypingTransformer()
    modified_tree = tree.visit(transformer)

    if "DEBUG_COLORBLIND_ASYNC" in os.environ:
        print(f"~~~~modified source: {file}~~~~")
        print(modified_tree.code)
        print(f"~~~~modified source END~~~~")
    return modified_tree.code


def _my_import(name, *args, **kwargs):

    try:
        return _builtin_import(name, *args, **kwargs)
    except SyntaxError as e:
        if e.msg.startswith("'await' outside"):  # await outside function / await outside async function
            spec = importlib.util.find_spec(name)
            source = spec.loader.get_source(name)
            new_source = modification_func(source, name)
            module = importlib.util.module_from_spec(spec)

            codeobj = compile(new_source, module.__spec__.origin, "exec")
            exec(codeobj, module.__dict__)
            sys.modules[name] = module
            return module
        else:
            raise e


# @TODO refactor to import handlers (sys.meta_path)
builtins.__import__ = _my_import


from foo import foo

foo()

import foo

foo.foo()
