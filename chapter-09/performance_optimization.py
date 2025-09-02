import time

def long_running_task(total_steps: int = 5) -> str:
    """Simulate a task that periodically emits progress notifications."""
    for step in range(1, total_steps + 1):
        # simulate work taking some time
        time.sleep(0.2)
        progress = int((step / total_steps) * 100)
        message = f"{progress}% complete"
        # progress notification using the MCP structure
        notification = {
            "method": "notifications/progress",
            "params": {
                "progressToken": "demo-token",
                "progress": progress,
                "total": 100,
                "message": message,
            },
        }
        print(notification)
    return "Task finished"

print("--- Part 1: Progress Notifications ---")
result = long_running_task()
print(result)

import time

print("\n--- Part 2: Predictive Caching Demonstration ---")

# Simulate expensive context loading
context_cache = {}

def load_context(item_id):
    """Simulate an expensive context load."""
    time.sleep(0.5)  # Simulate network/disk delay
    return f"data_for_{item_id}"

# Predictive caching: preload predicted items
predicted_items = ['doc1', 'doc2', 'doc3']
for item in predicted_items:
    context_cache[item] = load_context(item)

def get_context(item_id):
    """Retrieve context, using cache if available."""
    if item_id in context_cache:
        print(f"Retrieved {item_id} from cache")
        return context_cache[item_id]
    else:
        print(f"Loading {item_id} on demand")
        return load_context(item_id)

# Test retrieving context with and without caching
start = time.time()
print(get_context('doc1'))  # Should be fast (cached)
print(get_context('doc4'))  # Not cached, will load
end = time.time()
print(f"Total retrieval time: {end - start:.2f}s")

import asyncio
import random
import time

print("\n--- Part 3: Sequential vs Parallel Execution ---")

async def simulated_operation(name):
    delay = random.uniform(0.2, 0.5)
    await asyncio.sleep(delay)
    return f"{name} finished in {delay:.2f}s"

async def run_sequential():
    start = time.time()
    results = []
    for i in range(3):
        results.append(await simulated_operation(f"Task{i+1}"))
    duration = time.time() - start
    print("Sequential results:", results, f"Took {duration:.2f}s")

async def run_parallel():
    start = time.time()
    tasks = [simulated_operation(f"Task{i+1}") for i in range(3)]
    results = await asyncio.gather(*tasks)
    duration = time.time() - start
    print("Parallel results:", results, f"Took {duration:.2f}s")

# Run sequentially then in parallel
asyncio.run(run_sequential())
asyncio.run(run_parallel())
