import asyncio

import gmail


def periodic(period):
    def scheduler(fcn):
        async def wrapper(*args, **kwargs):
            while True:
                asyncio.create_task(fcn(*args, **kwargs))
                await asyncio.sleep(period)

        return wrapper

    return scheduler


@periodic(60)
async def gTask():
    gmail.main()


asyncio.run(gTask())
