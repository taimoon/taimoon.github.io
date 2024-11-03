---
title: Type System 1
author: Leong Teng Man
date: 2024-10-30
tags:
    - type theory
    - python
category: type theory
license: CC BY-SA 4.0
lang: en
---
# Type System 1

# How to type json?
These are valid json

```json
3
```
number (either integer or float)

```json
true
```
boolean


```json
'patchouli'
```
string

```json
null
```
null

```json
[11,13,17]
```
array

```
{
    'jan' : 1,
    'feb' : 2,
    'mac' : 3
}
```
javascript object (or named-value pair)

But there are at least 6 types that describe json type.
We may use `Union` to describe the either-ness type.
When written in python, it will be like

```py
json_ty = int|float|bool|None|str|list|dict
```

# Options
Some functions might return either valid result or null as non-result/missing.
Its type can be described as `T|None`.

For example,
```py
def copy_file(input_path: str, output_path: str|None = None) -> None:
    '''
    Example Usage
    ---
    ```
    copy_file('foo.txt', 'bar.txt')
    copy_file('foo.txt') ==> copy_file('foo.txt','foo_copy.txt')
    ```
    '''
    import os
    if output_path is None:
        wkdir, file_name = os.path.split(input_path)
        file_stem, file_ext = os.path.splitext(file_name)
        output_path = os.path.join(wkdir, file_stem + '_copy' + file_ext)
    
    with open(input_path, 'rb') as inp:
        with open(output_path, 'wb+') as out:
            out.write(inp.read())
```

The usage of `T|None` is so frequent, that python provides `Optional` shorthand
```py
from typing import Optional
def copy_file(input_path: str, output_path: Optional[str] = None) -> None:
    '''
    Example Usage
    ---
    ```
    copy_file('foo.txt', 'bar.txt')
    copy_file('foo.txt') ==> copy_file('foo.txt','foo_copy.txt')
    ```
    '''
    import os
    if output_path is None:
        wkdir, file_name = os.path.split(input_path)
        file_stem, file_ext = os.path.splitext(file_name)
        output_path = os.path.join(wkdir, file_stem + '_copy' + file_ext)
    
    with open(input_path, 'rb') as inp:
        with open(output_path, 'wb+') as out:
            out.write(inp.read())
```

# Civilised use of union is tagged union
Reference: [https://en.wikipedia.org/wiki/Tagged_union](https://en.wikipedia.org/wiki/Tagged_union)

Make sure that write the program to handle every type/case as described in union.

Some programming language systems may check whether your program handled each case as described in union.
The exhaustive check is a feature in static programming language.
We can write similar pattern in python, for example

```py
def calc(e: bool|int|list) -> int|bool:
    match e:
        case int():
            return e
        case bool():
            return e
        case ['-', e1, e2]:
            return calc(e1) + calc(e2)
        case ['if', e1, e2 ,e3]:
            if calc(e1) is False:
                return calc(e3)
            else:
                return calc(e2)
        case [*_]:
            raise NotImplementedError('calc','unknown form' e)
        case _:
            raise NotImplementedError('calc','unknown input', e)
```

# Polymorphism
The program below return larger from two numbers.
```py
def max(x: int|float, y: int|float) -> int|float:
    if x < y:
        return y
    else:
        return x
```
The notion of `max` works for a lot of thing such as integer, rational number, real number and lexicographics. 
When something works for multiple types, it is polymorphic.

There are several implementations of polymorphism such as

- subtype polymorphism (e.g.: inheritance)
- parametric polymorphism (e.g.: C++ templates, rust generics)
- method dispatch (e.g.: Julia dynamic dispatch)
- duck typing (e.g.: Python)
- tagged union

# Advance : Generics

```py
from typing import Callable
def compose(f: Callable[[int], int], g: Callable[[int], int]) -> Callable[[int], int]:
    def wrapped(x: int) -> int:
        return f(g(x))
    return wrapped

def sqr(x: int) -> int:
    return x * x

f = compose(sqr,sqr)
print(f(2)) # 16
```
As above, we have implemented a function wrapper that make two functions into one function.
But the `compose` function is generally applicable for other type of functions such as

```py
str.strip   : ((str) -> str)
str.__len__ : ((str) -> int)
---
compose(str.strip, str.__len__) : ((str) -> int)

sqr : ((int) -> int)
---
compose(compose(str.strip, str.len),str.__len__) : ((str) -> int)
```

To better describe this, we can add generics to type system, it works like substitute type variable with type. 
After python version 3.12, it can be written as below
```py
from typing import Callable
def identity[X](x: X) -> X:
    return x

def compose[X, Y, Z](f: Callable[[X], Y], g: Callable[[Y], Z]) -> Callable[[X], Z]:
    def wrapped(x: X) -> Z:
        return f(g(x))
    return wrapped


def sqr(x: int) -> int:
    return x * x

x: int = identity(10)
y: str = identity('s')
f: Callable[[int], int] = compose(sqr,sqr)
g: Callable[[str], int] = compose(str.strip, str.__len__)
h: Callable[[str], int] = compose(compose(str.strip, str.__len__),sqr)
H: Callable[[str], int] = compose(compose(str.strip, str.__len__),compose(sqr,identity))
```

# Advance : Recursive Type
However, previous description does not describe the json fully. 
The javascript object is a collection of name-value pairs 
whose name must be string but values can be any one of json type. 
In addition, array here allow any one of json type. For example

```
{
    'jan' : 1,
    'feb' : '2',
    'mac' : 3,
    'foo' : false,
    'bar' : null,
    'omg' : {
            'jan' : 1,
            'feb' : 2,
            'mac' : 3
        },
    'basic' : [1,true,false,null]
}
```

In python, it can be rewritten as
```py
type json_ty = int|float|bool|None|str|list[json_ty]|dict[str,json_ty]
```

[https://ocaml.org/docs/basic-data-types#recursive-variants](https://ocaml.org/docs/basic-data-types#recursive-variants)

In ocaml, it can be written as
```
type json =
  | Null
  | Bool of bool
  | Int of int
  | Float of float
  | String of string
  | Array of json list
  | Object of (string * json) list;;
```
