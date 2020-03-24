#!/usr/bin/env python3

import rx
from rx import operators as ops
from rx.subject import Subject, ReplaySubject, BehaviorSubject
from rx.scheduler import ThreadPoolScheduler, ImmediateScheduler, CurrentThreadScheduler, EventLoopScheduler, TrampolineScheduler
import jsonpickle as jp
import threading
import time

# All subscriptions must be serialized on some thread
# if thread pool is used (with subscribe_on function) then subscriptions go wild
# but if thread pool(1) is used with observe_on then all subscriptions execute on the same thread (but not in an ordered way) 

xS = ReplaySubject()
yS = ReplaySubject()


theVar = 5

def doTheVar(x):
    global theVar
    theVar = x
    print('new vlaue for the var: ', theVar)

def _raise():
    raise Exception('Exception')

p = ThreadPoolScheduler(1)

xS.pipe(
    ops.observe_on(p),
    ops.do_action(lambda x: print('Commencing X pipe')),
    ops.do_action(lambda x: time.sleep(1)),
    ops.do_action(lambda v: _raise()),
    ops.retry(1),
    ops.do_action(lambda x: print('one second passed')),
    ops.do_action(lambda x: time.sleep(1)),
    ops.do_action(lambda v: doTheVar(v)),
    ops.do_action(lambda v: print('Executing thread: ', threading.currentThread().name))
).subscribe()

yS.pipe(
    ops.observe_on(p),
    ops.do_action(lambda x: print('Commencing Y pipe')),
    ops.do_action(lambda v: doTheVar(v))
).subscribe(lambda x: print('Executing thread: ', threading.currentThread().name))



def do_next():
    print('Executing next thread: ', threading.currentThread().name)
    xS.on_next(10)
    xS.on_next(15)
    yS.on_next(20)


threading.Thread(target=do_next).start()

print('I am over here')

time.sleep(5)

print(theVar)

exit(0)