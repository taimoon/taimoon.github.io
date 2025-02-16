---
title: How I Wrote a Self-Hosting Compiler
author: Leong Teng Man
date: 2024-12-11
tags:
    - scheme
    - C
    - programming languages
    - implementation
category: PL
license: CC BY-SA 4.0
lang: en
---

# How I Wrote a Self-Hosting Compiler

[https://github.com/taimoon/scheme-compiler](https://github.com/taimoon/scheme-compiler)

# Prequel

Before I write the self-hosting compiler, I have written at least 2 compilers and many interpreters.

First time, I learn from nand2tetris project to write assembler, VM assembler and Jack compiler emit VM bytecode. However, I could not really grasp the methodology.

Second time, I learn to build optimizing compiler from IU Compiler Course. The course include register allocation, tail call optimization, closure conversion.
This course has huge impact to me.

Recently, I came to the compiler tutorial blog post series [https://generalproblem.net/lets_build_a_compiler/01-starting-out/](https://generalproblem.net/lets_build_a_compiler/01-starting-out/).
This blog enabled me to start out my compiler development without much support code as in IU compiler course.

Unfortunately, the blog did not update subsequent contents.
Anyway, the blog's primary reference is "An Incremental Approach to Compiler Construction" paper by Abdulaziz Ghuloum,
so I use the same paper as main reference to continue my development.

Just in case, readers are interested about tutorial implementation for other language while prefer incremental style,
then may refer to self-hosted C compiler implementation at [https://github.com/rui314/chibicc](https://github.com/rui314/chibicc).
It also has associated blog post by the author [https://www.sigbus.info/how-i-wrote-a-self-hosting-c-compiler-in-40-days](https://www.sigbus.info/how-i-wrote-a-self-hosting-c-compiler-in-40-days).

# Methodology

IU compiler course design inherit from Abdulaziz's paper "An Incremental Approach to Compiler Construction".
"Incremental" is the essence to learn compiler implementation.
The journery starts from a compiler that can only print integers.
Afterward, extend the compiler, adding feature
and every added feature must pass all tests including old and new tests before commiting.

You always have a working compiler for every commit.
In other word, you have multiple working compilers, isn't that amazing?

In addition to that, innovation of the course is the use of nanopass framework.
Nanopass framework is a beginner-friendly framework.
Under the nanopass framework, the compiler compile the source program in multiple passes.
Each pass only does simple task.
It can be as simple as one pass does free variable analysis,
next pass does closure conversion, pass after it does limit function.
This is a great method: if it is too difficult, then break it into two smaller steps, hoping that it is simpler.

Some might argue that
"isn't that too slow and inefficient to repeating tree traversal causing longer compilation time?"

But since being a beginner, make it work first is more important.
Fancy thing like register allocation, SSA conversion, optimization can be tackled later.

Since being a beginner, it will be painful to write parser for hard-to-parse language.
Scheme, dialect of lisp is easy to parse.
Therefore, I choose scheme as my source program.
Since this is self-hosting compiler, scheme is also the implementation language.

# How programming languages work?

Programming language itself does not execute itself. It must be run on something.
Analogously, CPU is the ultimate interpreter and the input is machine code (sequence of 0 and 1)
then CPU fetches the machine code, decode and execute.
At this level, machine code is a programming language but itself does not run.
Jacquard machine's punch cards alone cannot make textiles with complex patterns.

The attempt to make programming language works, I call it implementing a programming language.

There are at least 2 ways to implement a programming language.
First way is to write a translator that translate input into machine code,
then executed by the CPU.
Second way is to write the interpreter in the machine code,
when the interpreter is executed by the CPU,
it read source program and return result without doing translation.

The thing supports programming language execution is runtime system.
So, programming language + supported platform + system = programming language system. This is also why chez scheme introduce itself like this

> Chez Scheme is both a programming language and an implementation of that language, with supporting tools and documentation.

Then, is Python an interpreted language?

Partly. Like Java and Lua, python official implementation first compile the source program into bytecode then executed by its virtual machine.
Unlike Java, Python immediately executes program after compilation and print result to user.
We can see that a programming language can have several implementations.
For example, LLVM's clang and gcc both are implementations of C.

Thus, to understand the behaviour of a program, we need to learn how program is linked and loaded.
Similarily, to implement a language, we need to design and implement its runtime system together.

# Starting

The source program is scheme and the implementation also use scheme, target platform is 32bits i386 CPU.
My compiler compile program emit assembly which then assembled by gcc assembler `as`.
Development effort is at least one man month.

To start thing up, I need to write a simple runtime that can print result to screen.
This runtime can be served as loader where inside call the function `scheme_entry`.
Due to that, the resultant assembly use `scheme_entry` as entry point.

Example runtime written in C.

```c
#include<stdio.h>

extern int scheme_entry();
int main(){
    int val = scheme_entry();
    printf("%d\n", val);
    return 0;
}
```

And the first compiler,

```scheme
(define (emit op . args)
  (apply format (cons op args))
  (newline op))

(define (emit-exp op e)
  (cond
    ((integer? e)
     (emit op "mov $~a, %eax" e))
    (else
     (error "emit-exp" "unmatch" e))))

(define (emit-file input-path output-path)
  (system (format "rm -f /tmp/a.s"))
  (let ((exp (read (open-input-file input-path)))
        (op (open-output-file "/tmp/a.s")))
    (emit op ".section .text")
    (emit op ".globl scheme_entry")
    (emit op "scheme_entry:")
    (emit op "push %ebp")
    (emit op "mov %esp, %ebp")
    (emit-exp op exp)
    (emit op "pop %ebp")
    (emit op "ret")
    (close-output-port op)
    (system
      (format "gcc -fomit-frame-pointer -m32 /tmp/a.s runtime.c -o ~a" output-path))))

(emit-file (cadr (command-line)) (caddr (command-line)))
```

The testing framework is simple: use `diff` or `git diff` to compare print result with answer text file like below

```bash
scheme --script compiler.scm lit.scm lit.out
./lit.out > res.txt
git diff res.txt ans.txt
```

Where is the parser? I snarfed the `read` from chez scheme, I implement it later.
Now, I can shamelessly announce that I have a working compiler,
though it only prints integer.


# What you need in bootstrapping

Original paper goal is to have a compiler powerful enough to compile an interactive evaluator.
I took a more ambitious goal: self-hosting the compiler.

A self-hosted compiler at least required

1. separate compilation
2. foreign function interface
3. file input and output
4. garbage collection
5. tail call optimization


# May separate compilation save my time

Separate compilation is very important.
When the input programs get larger,
I strongly recommend designing the compiler able to compile program separately and linked later.
Otherwise, every re-compilation compiles library code only then input program,
the compilation takes a long time, not mentioning mulitplied by the number of tests during testing.
My first version testing time took few minutes.
I hope the paper emphasise the separate compilation.
In addition to that, I could not find separate compilation tutorial implementation.
I am forced to come out a naive implementation.

Naively, we can suppose our system execute the files strictly in sequence.
But, the next file needs to know the names of functions from previous files,
this needs linking process. Linking process need to do symbol resolution.
To make linking possible, the compiler need to record the linking information:
list of function names and entry.

My first version compiler generates additional linker file.
My second version compiler makes use of `objcopy` tool
to inject custom linking information into compiled object files.
The feature is that it can combine multiple object files into one.

The idea

```scheme
;;; compile to object file
file-1.scm -> emit-obj -> file-1.o -> read-meta -> ((main-entry mian-1) ...)
file-2.scm -> emit-obj -> file-2.o -> read-meta -> ((main-entry mian-1) ...)

;;; when compile to executable
file-1.o -> read-meta -> ((main-entry mian-1) ...)
file-2.o -> read-meta -> ((main-entry mian-1) ...)
-> linking ->
main:
  <init>
  call mian-1
  call mian-2
  <epilogue>
  ret
```

# Procedure Call

ABI specifies the calling convention on how arguments are passed to callee on the given platform.
Rui have collected ABI for various platform at his repo [https://github.com/rui314/psabi](https://github.com/rui314/psabi).
32bit i386 Sys V dictates that all arguments are pushed on stack.

Except it has a problem in tail call implementation.

Sys V calling convention push arguments first,
and push the return address after these, then jump to callee.

Tail call optimization required to copy same argument to same position.

- if same arity, then it is fine
- if less arity, then it is probably workable (not tested)
- if greater arity, then rewrite the return address to other places and existing is overwritten to argument.

However, modern OS and compilers implement return address proctection,
where the return addresses on stack are read only.
This prevents hackers from overwriting return address to trick the CPU jump to their malware. Shadow stack is one of the defensive techniques (see: [https://devblogs.microsoft.com/oldnewthing/20241018-00/?p=110385](https://devblogs.microsoft.com/oldnewthing/20241018-00/?p=110385))

In fact, the paper have proposed the workaround, where arguments are pushed after the return address.
It effectively prevents overwriting return address when doing tail call.

In IU compiler course, the target platform is 64bits CPU, usually pass arguments using registers. The workaround is to limit arguments that pass to registers, remaining are packaged into tuple and passed to last register. Though six registers for six arguments are a lot.

# How to cheat using FFI

When you understand how procedure call is implemented,
it is really easy to implement foreign function interface,
then start cheating.

For instance, if you cannot understand how x86's `div` and `mod` work?
No problem, write those procedures in runtime using C, then call these functions.


# Garbage Collection

Idea of tracing garbage collection is simple, 
but interface is diffcult one.
Personally recommend first step figuring out how to do stack walking and print the things out.
After that, change stack walking function to garbage collector function.

You would need frame pointer to do stack walking.
It required compiler support to do stack walking without frame pointer, and it seems hard.
Because of that, I choose to store frame pointer.
This is where the paper does not mention frame pointer.
Sys V ABI state that frame pointer is optional.

My second version tried not to store frame pointer
and stumbled upon stack walking, and I am forced to store frame pointer.

# My optimization is not having too much optimization

Sometimes, my compiler run all tests as fast as chez scheme does,
because my compiler does not have much optimization, hence faster compilation.

# Recommendation

I strongly recommend EOPL for those who are interested in programming language design.
EOPL feature is its use of interpreter to study the meaning of programming language.
Secondly, EOPL covers many essential techniques including
tree walk interpreter, free variable analysis, lexical addressing,
defunctionalize, type system, type inference, CPS, trampolining, etc.

CPS is what really empower a developer to implement functional programming language
in non-functional programming language.

EOPL is a great prerequisite to TAPL since TAPL contains chapters implementing type system
which you have learn from EOPL.

# Why self-hosting compiler?

Bootstrapping is like a litmus paper that test whether compiler can compile complex program without bug.
It is a form of integration testing to the compiler.
Since compiler is a complex piece of software.

# Sequel

I only have the time writing this article after I have done my scheme interpreter using C.
The repo is at [https://github.com/taimoon/scheme-interpreter](https://github.com/taimoon/scheme-interpreter).
The scheme interpreter is capable of bootstrapping the scheme compiler.
The implementation relies on CPS technique heavily.


# Reference
- [https://www.schemeworkshop.org/2006/11-ghuloum.pdf](https://www.schemeworkshop.org/2006/11-ghuloum.pdf)
- [https://eopl3.com/](https://eopl3.com/)
- [https://www.cis.upenn.edu/~bcpierce/tapl/](https://www.cis.upenn.edu/~bcpierce/tapl/)
- Workshop: Mixing Mutability into the Nanopass Framework - [https://www.youtube.com/watch?v=wTGlKCfP90A](https://www.youtube.com/watch?v=wTGlKCfP90A)
- [https://www.sigbus.info/how-i-wrote-a-self-hosting-c-compiler-in-40-days](https://www.sigbus.info/how-i-wrote-a-self-hosting-c-compiler-in-40-days)
- [https://www.yinwang.org/blog-cn/2013/03/28/chez-scheme](https://www.yinwang.org/blog-cn/2013/03/28/chez-scheme)
- [https://www.yinwang.org/blog-cn/2013/03/29/scripting-language](https://www.yinwang.org/blog-cn/2013/03/29/scripting-language)
- [https://iucompilercourse.github.io/IU-Fall-2021/](https://iucompilercourse.github.io/IU-Fall-2021/)
- [https://devblogs.microsoft.com/oldnewthing/20230725-00/?p=108482](https://devblogs.microsoft.com/oldnewthing/20230725-00/?p=108482)
- [https://okmij.org/ftp/Scheme/macros.html#match-case-simple](https://okmij.org/ftp/Scheme/macros.html#match-case-simple)

