---
title: Truthy Falsy Does Not Taste Well
author: Leong Teng Man
date: 2024-11-09
tags:
    - python
    - scheme
    - food guide
    - style guide
    - programming languages
category: PL
license: CC BY-SA 4.0
lang: en
---
# Truthy Falsy Does Not Taste Well

Though I never taste trutti frutti flavour but never know that quite some songs [^songs] name have trutti frutti, they are good uwu

# A simple model for `or` and `and` expressions

Suppose that our langauge is python, but our `python` follows these 3 rules below:

```py
<conseq> if <pred> else <altern> => <conseq> if <boolean> else <altern>
<conseq> if True else <altern> => <conseq>
<conseq> if False else <atlern> => <altern>
```

When applied

```py
print(None if True else "no")   # None
print("yes" if False else "no") # "no"
print("safe" if (True if True else False) else "doom") # "safe"
```

Considering the expression that involve `or` operator as below,

```py
x = <sub-expression-1> or <sub-expression-2>
print(x)
```

Mathematically,
the `or` is defined as

```py
True or True == True
True or False == False
False or True == True
False or False == True
```

Which then, it is equivalent to program as below

```py
# x = <sub-expression-1> or <sub-expression-2>
x = True if <sub-expression-1> else <sub-expression-2>
print(x)
```
Reader may check this translation satisfies the definition just now.

Analogously, `and` expression can be translated as follows
```py
# x = <sub-expression-1> and <sub-expression-2>
x = <sub-expression-2> if <sub-expression-1> else False
print(x)
```

# Why python has Truthy (or Falsy) values?

Sadly, this is no how python really work.
A more precise translation should be as follows

```py
# x = <sub-expression-1> or <sub-expression-2>
tmp = <sub-expression-1>
x = tmp if bool(tmp) else <sub-expression-2>
print(x)
```

```py
# x = <sub-expression-1> and <sub-expression-2>
tmp = <sub-expression-1>
x = <sub-expression-2> if bool(tmp) else tmp
print(x)
```


It returns same result as previous construct for some cases.
But, then what these extra constructs actually imply and why?

Firstly, the predicate, consequent and alternative part of `if` in python not necessary have to be boolean,
it can be any values. Same idea for sub-expressions in `or` and `and` expressions.

Secondly, it is convenient.

# Accidental conveniency
```py
def query_doc(title: str, authors: list[str] = None):
    if authors is None:
        authors = []
    ...
```

Let consider the program is to query document data from database where document can have no authors at all.
Then, it makes sense to make the parameter `authors` to have default value.
However, there is a caveat in using mutable data type as default argument (see: [https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments](https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments)). A common workaround is to put `None` as default argument value to `authors` parameter, then the function will initialize the `authors` if `authors` is `None`.

Long time ago (say back before 2005), some pythonistas accidentally realize that they can do this to achieve similar effect.

```py
authors = authors or []
```

This works. Following the proposed model from previous section,

```py
# x = <sub-expression-1> or <sub-expression-2>
# authors = authors or []
tmp = authors
authors = tmp if bool(tmp) else []
```

To achieve the effect of initalize the value `authors` if `authors` is `None`, `bool(None)` value must be false.
Partially, this initialization sugar syntax motivates the concept of truthy and falsy values in python.

# Truthy and Falsy Value in python
In `python`, we may ask whether object is truthy and falsy by passing it into the function `bool`.
For example

```py
vals = [
    True,
    False,
    None,
    -1,
    0,
    1,
    '',
    'delay no more',
    [],
    ['',False],
    {},
    {'':''},
    set(),
    object(),
    bool,
]

for v in vals:
    print(f'bool({repr(v)}) = {bool(v)}')
```

When run in python, it prints

```py
bool(True) = True
bool(False) = False
bool(None) = False
bool(-1) = True
bool(0) = False
bool(1) = True
bool('') = False
bool('delay no more') = True
bool([]) = False
bool(['', False]) = True
bool({}) = False
bool({'': ''}) = True
bool(set()) = False
bool(<object object at 0x7f2e31d786f0>) = True
bool(<class 'bool'>) = True
```

For output above, we can see that

- `None` is a falsy value, since `bool(None)` returns `False`.
- `0` is falsy
- empty string `''` is falsy.


# When there is no conditional expression
Before 2005, the python does not have conditional expression like `<conseq> if <pred> else <altern>`.
The workaround is to translate the form by hand into

```py
# x = <conseq> if <pred> else <altern>
x = (<pred> and <conseq>) or <altern>
```

Following our model, translate the `or` expression,

```py
tmp1 = (<pred> and <conseq>)
x = tmp1 if bool(tmp1) else <altern>
```

Then, translate the `and` expression
```py
tmp2 = <pred>
tmp1 = <conseq> if bool(tmp2) else False
x = tmp1 if bool(tmp1) else <altern>
```

When manually translate `-n if n < 0 else n` form

```py
n = -1
res = ((n < 0) and -n) or n

n = 3
res = ((n < 0) and -n) or n
```

The translated form

```py
n = -1
tmp2 = n < 0
tmp1 = -n if bool(tmp2) else False
res = tmp1 if bool(tmp1) else n
print(res)
n = 3
tmp2 = n < 0
tmp1 = -n if bool(tmp2) else False
res = tmp1 if bool(tmp1) else n
print(res)
```

And it works as expected.

```py
1
3
```

# Falsy values defeat the workaround

Adapted example from
[https://mail.python.org/pipermail/python-dev/2005-September/056510.html](https://mail.python.org/pipermail/python-dev/2005-September/056510.html)

```py
from dataclasses import dataclass

@dataclass
class ComplexType:
    real: int|float = 0
    imag: int|float = 0

def real(zs: list):
    'Return a list with the real part of each input element'
    # do not convert integer inputs to floats
    return [(type(z)==ComplexType and z.real) or z
            for z in zs]
```

> The code fails silently when z is (0+4i) (i.e.: `ComplexType(0, 4)`)

To see why it failed, let eval the expression `(type(z)==ComplexType and z.real) or z`.

```py
z = Complex(0,4)
(type(z)==ComplexType and z.real) or z
| (type(z)==ComplexType and z.real)
| | type(z)==ComplexType
| | True
| True and z.real
| | z.real
| | 0
| | bool(0)
| | False
| True and False
| False
False or z
| z
```
Where `z` is still complex number.

This motivates the PEP 308 proposal to add conditional expression, which result the expression form `<conseq> if <pred> else <altern>`.

# A Bug in Initialization
One time when my spark job didn't run and the job initializes configuration from the local `.env` file.
This was for development preview.
It was caused by pydantic model validation error complaining the `port` is not a valid integer.

```py
# https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/connection/index.html
# AirflowConnection is a custom pydantic model
# which assert port must be integer
from warehouse import AirflowConnection
def connection_factory(config_prefix: str, spark = None):
    if spark is None:
        spark: SparkSession = SparkSession.getActiveSession()
    
    conf = spark.sparkContext.getConf()
    # https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.SparkConf.get.html#pyspark.SparkConf.get
    # suppose that conf.get always return either None or str
    # conf.get(key: str, defaultValue: Optional[str] = None) -> Optional[str]

    air_conf = {}
    options = ['type', 'host', 'port', 'schema', 'login', 'password', 'extra']
    for k in options:
        val = conf.get(f'{config_prefix}.{k}')
        if val == 'None':
            val = None
        air_conf[k] = val
    ...
    if air_conf['port']:
        air_conf['port'] = int(air_conf['port'])
    return AirflowConnection(**cfg)
```

And there is an entry for `port` in the `.env`

```
MYDB.PORT=""
```

Knowing that empty string `""` is falsy, when `port` is an empty string, python skips this conditional statement

```py
if air_conf['port']:
    air_conf['port'] = int(air_conf['port'])
```

Python proceeds to the line `AirflowConnection` pydantic base model lead to validation error.

# Scheme - false is the only falsy value

In `shceme`, its expressions for `and` and `or` are expanded as follows

```scheme
(and e1 e2)
=> (let ((%tmp e1)) (if %tmp e2 %tmp))
(or e1 e2)
=> (let ((%tmp e1)) (if %tmp e2 #f))
```

Same as python, scheme is also dynamically type. Then, subexpressions of `and` and `or` need not be necessarily boolean.
But how come schemers do not have the same confusion as above?

Because scheme does not fool around with the truthiness, and RnRs standard decide that `#f` is the false value and the only falsy value, otherwise all object is truthy.
The rules for `if` form are

```scheme
(if #f <conseq> <altern>)
=> <altern>
(if <any> <conseq> <altern>)
=> <conseq>
```

# A motivating use case of `=>` in `cond`

Reference: Exercise 4.5 of SICP chapter 4

```scheme
(cond <clause> ...)
<clause> := (<test> => <proc>) 
        | (<test> <e> ...)
```

> Scheme allows an additional syntax for cond clauses, (`test` => `recipient`).
> If `test` evaluates to a true value, then `recipient` is evaluated.
> Its value must be a procedure of one argument; 
> this procedure is then invoked on the value of the `test`,
> and the result is returned as the value of the cond expression.

Instead of
```scheme
(define (apply-env x env)
  (let ((res (assoc x env)))
    (if res
        (cadr res)
        (error "apply-env" "unbound" x))))
```

We may use `=>` in `cond`, to make use of return result from `assoc`

```scheme
(define (apply-env x env)
  (cond ((assoc x env) => cadr)
        (else (error "apply-env" "unbound" x))))
```

It works because `assoc` return `#f` if no matches found,
otherwise if matched, it returns a list of two objects whose second object is the corresponding value for the key `x`.

Suppose a tutorial scheme compiler implementation, the `uniquify` pass transforms `sexp` input program to an intermediate representation.

For example,

```scheme
(<form> <subform> ...)

(if <pred> <conseq> <altern>)   ; `if` is a keyword
=> (if <pred> <conseq> <altern>)
(+ <left> <right>)              ; `+` is primitive operator
=> (prim-call + <left> <right>)
(sqr 2)                         ; depends on current environment
=> (call sqr 2)
```

There are some forms either keywords, primitives or others.

The excerpt below is program for the `uniquify` pass

```scheme
(define (apply-env x env)
  (cond ((assoc x env) => cadr)
        (else (error "apply-env" "unbound" x))))

(define (keyword? kw env)
  (and (symbol? kw)
       (let ((maybe (assoc kw env)))
        (if maybe
            (eq? (cadr maybe) 'keyword)
            maybe))))

(define (prim? x)
  (and (pair? x) (eq? (car x) 'prim)))

(define (prim->prim-call prim es)
  (list* 'prim-call (car es) es))

(define (init-env)
  '((if keyword)
    (+ (prim +))))

(define (uniquify e env)
  (cond
    ((symbol? e) (apply-env e env))
    ((not (pair? e)) e)
    ((not (keyword? (car e)))
     (let ((e* (uniquify e env)))
      (if (prim? e*)
          (prim->prim-call op (uniquify-each (cdr e) env))
          (make-apply (uniquify (car e)) (uniquify-each (cdr e) env)))))
    ((if? e) ...))
    ...)
```

When it is `(uniquify '(+ 1 2) (init-env))`,
the program already know that `+` is primitive when evaluated in the procedure `keyword?`.
Modifying the `keyword?` to return the matches if matched otherwise return false,
and make use of `=>`, to avoid multiple list traversal. Though I rarely use `=>` in my program.

```scheme
(define (keyword? kw env)
  (and (symbol? kw)
       (let ((maybe (assoc kw env)))
        (if maybe
            (if (eq? (cadr maybe) 'keyword)
                #t
                (cadr maybe))
            maybe))))

(define (uniquify e env)
  (cond
    ((symbol? e) (apply-env e env))
    ((not (pair? e)) e)
    ((not (keyword? (car e)))
     => (lambda (op)
          (if (prim? op)
              (prim->prim-call op (uniquify-each (cdr e) env))
              (make-apply (uniquify (car e)) (uniquify-each (cdr e) env)))))
    ((if? e) ...)
    ...))
```

Idiomatic scheme use false value `#f` represent missing value.
This is how schemers model option type/maybe type.
For example, `assoc` return `#f` if no matches found in the association list `alist`, otherwise return the matching list of key and value.

```scheme
(define (assoc x alist)
  (cond
    ((null? alist) #f)
    ((not (pair? alist))
     (error "assoc" "improperly formed alist"))
    (((not (pair? (car alist))))
     (error "assoc" "improperly formed alist"))
    ((equal? (caar alist) x)
     (car alist))
    (else (assoc x (cdr alist)))))
```

Besides, similar caveat from python still applicable in scheme.

Consider an example below,

```scheme
(define x (cadr (or (assoc k record-1) (assoc k record-2) '(whatever default-value))))
(define y (cadr (or (assoc k record-1) (assoc k record-2))))
```

For first line, it works but confusing but second line will fail if `k` is not bound in `record-1` and `record-2`. So don't do these.

# Lesson learned - only boolean in boolean expression

To summarize, relying on truthy and falsy values is an error-prone practice. This technique neither generally applicable nor compatible to other programming languages such as C, Ocaml, Haskell, Javascript, Lua, etc.

For example, 

- Javascript's empty object `{}` is not falsy whereas python's empty dictionary `{}` is falsy.
- Scheme `#f` is the only falsy value. 
- Lua `nil` and `false` are the only falsy values.
-  Common Lisp uses empty list `nil` (or `'()`) as the only falsy value. 
- C use `0` represent the false value and anything non-zero is true. 
- Statically typed languages like Ocaml and Haskell permit only boolean value in test/predicate subexpression in conditional expression.

Despite the difference, the most portable practice is to restrict yourself only boolean in boolean expressions.
If it is too strong, a weaker condition is to use only one thing to be falsy and any others are truthy for the programming language system.

When the expression is either `or`, `and` and predicate of `if`, try to have the subexpressions evaluate to boolean value only.

Indeed, the concept of truthiness is a deprecated practice in the libraries `pandas` and `numpy`. They decide that it is **ambiguous** to ask if empty dataframe or empty array is truhty or falsy.

Rather than

```py
if not authors:
    authors = []
```

Instead

```py
if authors is None:
    authors = []
```

Rather than

```py
if not author:
    author = 'reimu'
```

Instead

```py
if author == '':
    author = 'reimu'
```

Rather than

```py
if not rate:
    rate = 0.06
```

Instead

```py
if rate is None:
    rate = 0.06
```

Notice that `if not rate` is also an example that falsiness defeat conveniency.
There are sensible use cases for 0 rate,
but the program mistakenly think that it is empty value and re-initalize it to some value.

PEP 8 programming recommendations section suggest something similar.

# Interlude : Unexpected Coercion and notion of Identity and Equality

```py
# python
print(0 == False)
```

Quick quiz: what those prints? yep, it prints true.

Whichever why it is, it is not important because

> If it shouldn't behave that way, then it must be the programming languages' fault! - by Lelouch probably.

Python pep 285 (see [https://peps.python.org/pep-0285/](https://peps.python.org/pep-0285/)) guarentee that `True`, `False` and `None` are singletons.
Therefore the constructs below always mean that they are `True`, `False` and `None` when it is true.

```py
x is True
x is False
x is None
```

However, in python, the expression `x is 0` is not guarenteed to be true if `x` is 0 because integers can be allocated objects.

```py
from math import factorial
print(factorial(10) == factorial(10)) # True
print(factorial(10) is factorial(10)) # False
```

This is because identity is different from equality.
Simple analogy is that eventhough the Reimu's bank account has 0 money while Marisa's bank account also has 0 money,
doesn't mean that these 2 accounts are the same, rather they are equal in some sense (equality).
Unless, they shared the same account, then it is same (identity).

In python, `is` operator is to test identity (i.e.: only one thing if it is true), whereas `==` is to test equality (i.e.: it can be two or more things).
Idiomatic python use `is` if the objects are singletons.
That's why the program here use `is` to test if `None`.

# Reference
- PEP 308 – Conditional Expressions, [https://peps.python.org/pep-0308/](https://peps.python.org/pep-0308/)
- PEP 285 - Adding a bool type, [https://peps.python.org/pep-0285/](https://peps.python.org/pep-0285/)
- [Python-Dev] "and" and "or" operators in Py3.0, [https://mail.python.org/pipermail/python-dev/2005-September/056846.html](https://mail.python.org/pipermail/python-dev/2005-September/056846.html)
- [Python-Dev] Conditional Expression Resolution, [https://mail.python.org/pipermail/python-dev/2005-September/056510.html](https://mail.python.org/pipermail/python-dev/2005-September/056510.html)
- SICP, [https://web.mit.edu/6.001/6.037/sicp.pdf](https://web.mit.edu/6.001/6.037/sicp.pdf)
- R5RS scheme standard, [https://conservatory.scheme.org/schemers/Documents/Standards/R5RS/r5rs.pdf](https://conservatory.scheme.org/schemers/Documents/Standards/R5RS/r5rs.pdf)
- Caveat of mutable default argument, [https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments](https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments)
- Maybe type in racket, [https://docs.racket-lang.org/functional/maybe.html](https://docs.racket-lang.org/functional/maybe.html)

---

[^songs]: Song names that contains Trutti Frutti:
Little Richard ([https://www.youtube.com/watch?v=NnIIvWnpaBU](https://www.youtube.com/watch?v=NnIIvWnpaBU)),
Elvis Presley ([https://youtu.be/gKCz_4YV0YY?si=6K04hKlMKQ7Z0rTz](https://youtu.be/gKCz_4YV0YY?si=6K04hKlMKQ7Z0rTz)),
Queen ([https://youtu.be/y78OOarDPic?si=0bw_Mp0dD5WXrg3Z](https://youtu.be/y78OOarDPic?si=0bw_Mp0dD5WXrg3Z)),
Caramella Girls ([https://youtu.be/zCulj2AbOGc?si=moQskeKm-HUXYv9V](https://youtu.be/zCulj2AbOGc?si=moQskeKm-HUXYv9V))