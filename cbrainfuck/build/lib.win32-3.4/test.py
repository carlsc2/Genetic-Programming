import cbrainfuck
import brainfuck
from timeit import timeit

##def foo1():
##    brainfuck.evaluate(',.,.,.,.','abcd')
##
##def foo2():
##    cbrainfuck.evaluate(',.,.,.,.!abcd')
##
##
##print(timeit('foo2()','from __main__ import foo2',number=1000000))
##print(timeit('foo1()','from __main__ import foo1',number=1000000))


##bcode = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
##iloop = '-[-..]'
##l2up = '++++++++[->++++<],>[-<->]<.[-]++++++++++.'
##dcode = '+'
##
##
###cbrainfuck.evaluate(',.,.,.,.,.,.,.,.,.,.,.!abcd',.02)
##
##print("PBF: ")
##y = brainfuck.evaluate(l2up,'hello',.1)
##print(len(y),y)
##
##print("CBF: ")
##x = cbrainfuck.evaluate(l2up+"!hello",.1)
##print(len(x),x)


killer = "<<-><]+,,.,].+]].+<.#]],#][+-<-<-,,>>,><"

x = cbrainfuck.evaluate(killer,.1)
print(len(x),x)
