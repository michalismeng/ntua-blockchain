import rx
from rx import operators as ops
from rx.subject import Subject, ReplaySubject
from rx.scheduler import ThreadPoolScheduler, ImmediateScheduler
import jsonpickle as jp
import threading
import time

# All subscriptions must be serialized on main thread
# if thread pool is used (with subscribe_on function) then subscriptions go wild

xS = ReplaySubject()
y = ReplaySubject()

theVar = 5
pool_scheduler = ThreadPoolScheduler(1)
immediate_scheudler = ImmediateScheduler()

def doTheVar(x):
    global theVar
    theVar = x
    print('new vlaue for the var: ', theVar, threading.currentThread().name)

y.pipe(
    # ops.subscribe_on(pool_scheduler),
).subscribe(lambda v: doTheVar(v))

xS.pipe(
    ops.do_action(lambda x: time.sleep(2)),
    # ops.subscribe_on(pool_scheduler),
    ops.delay(2)
).subscribe(lambda v: doTheVar(v))

xS.on_next(10)
y.on_next(20)

time.sleep(5)

print(theVar)

exit(0)