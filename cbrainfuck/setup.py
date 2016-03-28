from distutils.core import setup, Extension

setup(
    ext_modules = [
        Extension("cbrainfuck", sources=["brainfuck2.c"]),
   ],
)
