import asyncio


async def bar():
    await asyncio.sleep(0)
    return "ok"


await bar()


def await_from_sync():
    return await bar()


async def nested_functions():
    def bar1():
        return 1

    async def bar2():
        return 1

    async def bar3():
        return 1

    def bar4():
        return await bar2()

    async def bar5():
        return 1

    def bar6():
        return await bar5()

    res = await bar2()
    res += await bar3()
    res += bar4()
    res += bar4()

    res += await bar5()
    res += bar6()
    return res


def call_nested_functions():
    return await nested_functions()


def test_async_for():
    async def fn():
        return True

    async def async_iter():
        for i in range(2):
            yield i
            await asyncio.sleep(0)

    async def async_wrapper():
        res = []
        # async for cannot be used outside async context, but we can wrap it in async function and await it
        async for i in async_iter():
            res.append(i)
        return res

    return await async_wrapper()


def test_async_with():
    class AsyncContextManager:
        async def __aenter__(self):
            await asyncio.sleep(0)

        async def __aexit__(self, exc_type, exc, tb):
            await asyncio.sleep(0)

    async def w():
        async with AsyncContextManager():
            pass
        return True

    return await w()
