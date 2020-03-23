import rx
from rx import operators as ops
from rx.subject import Subject, ReplaySubject
from rx.scheduler import ThreadPoolScheduler, ImmediateScheduler, CurrentThreadScheduler, EventLoopScheduler, TrampolineScheduler
import jsonpickle as jp
import threading
import time

# All subscriptions must be serialized on main thread
# if thread pool is used (with subscribe_on function) then subscriptions go wild

xS = ReplaySubject()
yS = ReplaySubject()

theVar = 5
pool_scheduler = ThreadPoolScheduler(1)
immediate_scheudler = ImmediateScheduler()
trampoline = TrampolineScheduler()
event = EventLoopScheduler()

def doTheVar(x):
    global theVar
    theVar = x
    print('new vlaue for the var: ', theVar, threading.currentThread().name)

# commented solution is good
# def do_subs(xS, yS):
#     xS.pipe(
#         ops.observe_on(CurrentThreadScheduler()),
#         ops.do_action(lambda x: time.sleep(1)),
#         ops.do_action(lambda x: print('one second passed')),
#         ops.do_action(lambda x: time.sleep(1)),
#         ops.do_action(lambda v: doTheVar(v))
#     ).subscribe()

#     yS.pipe(
#         ops.observe_on(CurrentThreadScheduler()),
#         ops.do_action(lambda v: doTheVar(v))
#     ).subscribe()

# x = threading.Thread(target=do_subs, args=(xS, yS))
# x.start()

yS.pipe(
        ops.observe_on(event),
        ops.do_action(lambda v: doTheVar(v))
    ).subscribe()

xS.pipe(
    ops.observe_on(event),
    ops.do_action(lambda x: time.sleep(1)),
    ops.do_action(lambda x: print('one second passed')),
    ops.do_action(lambda x: time.sleep(1)),
    ops.do_action(lambda v: doTheVar(v))
).subscribe()


xS.on_next(10)
xS.on_next(15)
yS.on_next(20)

print(threading.currentThread().name)

print('sleeping')
time.sleep(5)

print(theVar)

exit(0)