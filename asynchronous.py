import asyncio
import nest_asyncio


nest_asyncio.apply()


async def complete_async_tasks(tasks):
    # this doesn't call, just turns the async function handle to an awaitable
    async_tasks = [task if asyncio.iscoroutine(task) else task() for task in tasks]

    results = await asyncio.gather(*async_tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            raise result

    return results


def run_async_tasks(tasks):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(complete_async_tasks(tasks))
