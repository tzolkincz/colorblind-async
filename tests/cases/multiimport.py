import asyncio

async def foo_async():
    await asyncio.sleep(0)
    return True

def foo():
    return await foo_async()

def bar():
    return await foo_async()
