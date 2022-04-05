import os
import telegram_code
import time

while True:
    time.sleep(600)
    running_process = os.popen("ps -aef | grep -i 'python3' | grep -v 'grep'").read().strip().split('\n')
    if len(running_process) < 6:
        telegram_code.send_message("Hey dev some process have stopped, here is the list")
        telegram_code.send_message(running_process)
        break
