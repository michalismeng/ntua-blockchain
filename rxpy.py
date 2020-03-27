#!/usr/bin/env python3

import rx
from rx import operators as ops
from rx.subject import Subject, ReplaySubject, BehaviorSubject
from rx.scheduler import ThreadPoolScheduler, ImmediateScheduler, CurrentThreadScheduler, EventLoopScheduler, TrampolineScheduler, VirtualTimeScheduler
import jsonpickle as jp
import threading
import time

# All subscriptions must be serialized on some thread
# if thread pool is used (with subscribe_on function) then subscriptions go wild
# but if thread pool(1) is used with observe_on then all subscriptions execute on the same thread (but not in an ordered way) 

xS = ReplaySubject()
yS = ReplaySubject()
zS = Subject()

theVar = 0

# def doTheVar(x):
#     global theVar
#     theVar = x
#     print('new vlaue for the var: ', theVar)

def _raise():
    raise Exception('Exception')

p = ThreadPoolScheduler(1)

# xS.pipe(
#     ops.observe_on(p),
#     ops.do_action(lambda x: print('Commencing X pipe')),
#     ops.do_action(lambda x: time.sleep(1)),
#     ops.do_action(lambda v: _raise()),
#     ops.retry(1),
#     ops.do_action(lambda x: print('one second passed')),
#     ops.do_action(lambda x: time.sleep(1)),
#     ops.do_action(lambda v: doTheVar(v)),
#     ops.do_action(lambda v: print('Executing thread: ', threading.currentThread().name))
# ).subscribe()

# yS.pipe(
#     ops.observe_on(p),
#     ops.do_action(lambda x: print('Commencing Y pipe')),
#     ops.do_action(lambda v: doTheVar(v))
# ).subscribe(lambda x: print('Executing thread: ', threading.currentThread().name))



# def do_next():
#     print('Executing next thread: ', threading.currentThread().name)
#     xS.on_next(10)
#     xS.on_next(15)
#     yS.on_next(20)


# threading.Thread(target=do_next).start()

def cond(x):
    inc_var()
    print(theVar)
    return theVar <= 5

def inc_var():
    global theVar
    theVar += 1


def op():
    return rx.pipe(
    # ops.observe_on(p),
    ops.do_action(lambda x: time.sleep(5)),
    ops.do_action(lambda v: print('Executing thread: dummyS', threading.currentThread().name))
)


def do_next():
    print('Executing')
    time.sleep(5)
    print('Ending')

import multiprocessing 

t = multiprocessing.Process(target=do_next) 
zS.pipe(
    ops.observe_on(p),
    ops.do_action(lambda v: print('Executing thread: zS', threading.currentThread().name)),
    ops.do_action(lambda v: t.terminate()),
    ops.do_action(lambda v: print('Executing thread: zS', threading.currentThread().name)),
).subscribe()

z_temp = Subject()


# .subscribe()

print('I am over here')
t.start()

zS.on_next(0)
z_temp.on_next(0)
# sorceS.on_next(0)
t.join()
exit(0)