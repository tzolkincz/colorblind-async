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
