a = 1


async def bar():
    print("bar")
    global a
    if a == 1:
        a = 0
        await bar()


# await bar()


def foo():

    print("foo")
    await bar()
