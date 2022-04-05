import os
import telegram
import time

while True:
    time.sleep(600)
    running_process = os.popen("ps -aef | grep -i 'python3' | grep -v 'grep'").read().strip().split('\n')
    if len(running_process) < 5:
        telegram.send_message("Hey dev some process have stopped, here is the list")
        telegram.send_message(running_process)
        break
