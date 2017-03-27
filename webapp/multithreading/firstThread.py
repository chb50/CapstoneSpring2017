import thread
import time

#function that the threads will run in parallel
def printTime(threadName, delay):
	count = 0
	while count < 5:
		time.sleep(delay)
		count += 1
		print("%s: %s" % (threadName, time.ctime(time.time())) )

#here we try to create two new threads
try:
	thread.start_new_thread(printTime, ("Thread-1", 2))
	thread.start_new_thread(printTime, ("Thread-2", 4))
except:
	print("Unable to start thread")

while 1:
	pass