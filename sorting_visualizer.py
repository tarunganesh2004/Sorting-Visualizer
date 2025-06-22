import pygame
import pygame_gui
import random
import asyncio
import platform

# Initialize Pygame and Pygame GUI
pygame.init()
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Sorting Algorithms Visualizer")
manager = pygame_gui.UIManager(WINDOW_SIZE)
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Sorting state
array = []
array_size = 50
delay = 0.1
sorting = False
current_algorithm = None  # Will be set to bubble_sort by default in setup

# GUI Elements
algo_dropdown = pygame_gui.elements.UIDropDownMenu(
    options_list=[
        "Bubble Sort",
        "Selection Sort",
        "Insertion Sort",
        "Quick Sort",
        "Merge Sort",
    ],
    starting_option="Bubble Sort",
    relative_rect=pygame.Rect(10, 10, 150, 30),
    manager=manager,
)
size_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect(170, 10, 150, 30),
    start_value=50,
    value_range=(10, 100),
    manager=manager,
)
speed_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect(330, 10, 150, 30),
    start_value=0.1,
    value_range=(0.01, 1.0),
    manager=manager,
)
start_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(490, 10, 100, 30), text="Start", manager=manager
)
reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(600, 10, 100, 30), text="Reset", manager=manager
)


def generate_array(size):
    return [random.randint(10, 500) for _ in range(size)]


def draw_array(array, highlight_indices=None):
    screen.fill(BLACK)
    bar_width = WINDOW_SIZE[0] // len(array)
    for i, value in enumerate(array):
        color = RED if highlight_indices and i in highlight_indices else WHITE
        pygame.draw.rect(
            screen, color, (i * bar_width, WINDOW_SIZE[1] - value, bar_width - 2, value)
        )
    manager.draw_ui(screen)
    pygame.display.flip()


async def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(0, len(arr) - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                draw_array(arr, [j, j + 1])
                await asyncio.sleep(delay)
    return arr


async def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
            draw_array(arr, [i, j])
            await asyncio.sleep(delay)
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        draw_array(arr, [i, min_idx])
        await asyncio.sleep(delay)
    return arr


async def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            draw_array(arr, [j, j + 1])
            await asyncio.sleep(delay)
            j -= 1
        arr[j + 1] = key
        draw_array(arr, [j + 1])
        await asyncio.sleep(delay)
    return arr


async def quick_sort(arr, low, high):
    if low < high:
        pi = await partition(arr, low, high)
        await quick_sort(arr, low, pi - 1)
        await quick_sort(arr, pi + 1, high)
    return arr


async def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            draw_array(arr, [i, j])
            await asyncio.sleep(delay)
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    draw_array(arr, [i + 1, high])
    await asyncio.sleep(delay)
    return i + 1


async def merge_sort(arr, l, r):
    if l < r:
        m = (l + r) // 2
        await merge_sort(arr, l, m)
        await merge_sort(arr, m + 1, r)
        await merge(arr, l, m, r)
    return arr


async def merge(arr, l, m, r):
    left = arr[l : m + 1]
    right = arr[m + 1 : r + 1]
    i = j = 0
    k = l
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        draw_array(arr, [k])
        await asyncio.sleep(delay)
        k += 1
    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1
        draw_array(arr, [k])
        await asyncio.sleep(delay)
    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1
        draw_array(arr, [k])
        await asyncio.sleep(delay)


def setup():
    global array, current_algorithm
    array = generate_array(array_size)
    current_algorithm = bubble_sort  # Set default algorithm
    draw_array(array)


async def main():
    global array, array_size, delay, sorting, current_algorithm
    setup()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button and not sorting:
                    if current_algorithm is None:
                        print("No algorithm selected. Defaulting to Bubble Sort.")
                        current_algorithm = bubble_sort
                    sorting = True
                    algo = algo_dropdown.selected_option
                    algo_map = {
                        "Bubble Sort": bubble_sort,
                        "Selection Sort": selection_sort,
                        "Insertion Sort": insertion_sort,
                        "Quick Sort": lambda arr: quick_sort(arr, 0, len(arr) - 1),
                        "Merge Sort": lambda arr: merge_sort(arr, 0, len(arr) - 1),
                    }
                    current_algorithm = algo_map.get(
                        algo, bubble_sort
                    )  # Default to bubble_sort if algo not found
                    array = await current_algorithm(array.copy())
                    sorting = False
                    draw_array(array)
                elif event.ui_element == reset_button:
                    array = generate_array(array_size)
                    draw_array(array)
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == size_slider:
                    array_size = int(event.value)
                    array = generate_array(array_size)
                    draw_array(array)
                elif event.ui_element == speed_slider:
                    delay = event.value
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                algo = algo_dropdown.selected_option
                algo_map = {
                    "Bubble Sort": bubble_sort,
                    "Selection Sort": selection_sort,
                    "Insertion Sort": insertion_sort,
                    "Quick Sort": lambda arr: quick_sort(arr, 0, len(arr) - 1),
                    "Merge Sort": lambda arr: merge_sort(arr, 0, len(arr) - 1),
                }
                current_algorithm = algo_map.get(
                    algo, bubble_sort
                )  # Update on dropdown change
            manager.process_events(event)
        manager.update(clock.tick(FPS) / 1000.0)
        draw_array(array)
        await asyncio.sleep(1.0 / FPS)


if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
