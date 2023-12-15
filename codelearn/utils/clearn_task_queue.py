import asyncio
import os
from codelearn.config import project_config

class AsyncQueue:
    def __init__(self):
        self.tasks = asyncio.Queue()

    async def add_task(self, coro):
        await self.tasks.put(coro)

    async def run(self):
        while True:
            task = await self.tasks.get()
            await task
            self.tasks.task_done()

def get_directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_least_recently_used_files(path):
    files = [os.path.join(path, f) for f in os.listdir(path)]
    files.sort(key=lambda x: os.path.getatime(x))
    return files

async def async_cleanup(storage_path):
    max_size = project_config.max_clean_threadshold_size
    cleaned_size = project_config.after_cleaned_threadshold_size
    current_size = get_directory_size(storage_path)

    if current_size > max_size:
        # 删除最近最少访问的文件
        lru_files = get_least_recently_used_files(storage_path)
        for file in lru_files:
            if current_size <= cleaned_size:
                break
            size = os.path.getsize(file)
            os.remove(file)
            current_size -= size