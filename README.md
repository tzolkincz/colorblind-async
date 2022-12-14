# colorblind-async


> **Warning**
> This is only a proof-of-concept.


## Usage

1. import `ColorblindAsync` from `colorblind_async`
2. init by: `ColorblindAsync.init()`
3. include files/modules with awaits outside async context
4. run

### Example

main.py
```python
from colorblind_async import ColorblindAsync

ColorblindAsync.init()

import file # now when you include other modules, the colorblind_async will do it's job

# await my_coro() # you cannot do that here, colorblind_async binds to import statement and it won't work here
```

file.py
```python
async def my_coro():
    return "foo"

def my_sync_fn():
    await my_coro() #  call `await` in sync function

await my_coro() # I can even call `await` outside any function
```


## Install

```sh
pip3 install colorblind-async
```

## Optional setup

### Pass already defined event loop

```python
from colorblind_async import ColorblindAsync

ColorblindAsync.init(loop=my_loop)

```

## Debug

Prints altered code with `await`s outside async context replaced with `__colorblind_async__(coro)` call.

`DEBUG_COLORBLIND_ASYNC=True python script.py`

## Run Tests

`make test`

## How does it work

After you import `colorblind_async` module, it'll enhance the `include` function to catch `SyntaxError` `await outside function...`. When it catches it, it parse AST of the included file and replace `await` keyword with call `__colorblind_async__(coroutine)`. `__colorblind_async__` is simple wrapper which executes passed coroutine in the (provided) event loop.
Because you can call sync functions from async context and then call async context in a nested fashion, library `nest-asyncio` is used for reentrant async semantics.

## Limitations

As per library `nest-asyncio`: _only event loops from asyncio can be patched; Loops from other projects, such as uvloop or quamash, generally can't be patched._

Be aware of unexpected preemptions as they may occur outside of visible `async` keyword context and you may need to apply additional synchronization.

## FAQ

### Why?

Python async is more complicated than it needs to be. And I like the idea of [Zig's colorblind Async/Await](https://kristoff.it/blog/zig-colorblind-async-await/). Obviously there are cases when you do not care about event loop stuff and just what the code running without spending too much time on dealing with sync/async parts calling each other.

### Is this dark magic?

Well, um, technically yes. Because it allows you to import _syntactically incorrect_ program, so use it with caution. But don't worry, no kittens were harmed during the experiments.
