import threading
import time

# Global variable to indicate if the first function is running
is_running = False

def function1():
    global is_running
    is_running = True
    print("Function 1 started")
    time.sleep(5)  # Simulate work by sleeping for 5 seconds
    is_running = False
    print("Function 1 stopped")

def function2():
    while True:
        if is_running:
            print("Function 2 is running because Function 1 is running")
        else:
            print("Function 2 stopped because Function 1 is not running")
            break
        time.sleep(1)  # Check the status every second

# Create threads for each function
thread1 = threading.Thread(target=function1)
thread2 = threading.Thread(target=function2)

# Start the threads
thread1.start()
thread2.start()

# Wait for threads to finish
thread1.join()
thread2.join()
