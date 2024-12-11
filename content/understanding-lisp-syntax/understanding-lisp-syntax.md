---
title: Understanding the Lisp Syntax
author: Leong Teng Man
date: 2024-11-11
tags:
    - lisp
    - scheme
    - programming languages
    - design
category: PL
license: CC BY-SA 4.0
lang: en
---

# Understanding the Lisp Syntax

TL;DR Lisp syntax is the simplified format of XML, JSON, representing tree-like data in textual form.

# List of Things

In set notation,

```
{1, 2, 3}
```

In English,

> one two three


In JSON,

```json
[1, 2, 3]
```

Approximately in XML

```xml
<set>
    <item> 1 </item>
    <item> 2 </item>
    <item> 3 </item>
</set>
```

# Powerset: Lists of list

In set notation,

```
{{}, {1}, {2}, {3}, {1, 2}, {1, 3}, {2, 3}, {1, 2, 3}}
```


In JSON,

```json
[[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
```

Approximately in XML

```xml
<set>
    <set></set>
    <set>
        <item> 1 </item>
    </set>
    <set>
        <item> 2 </item>
    </set>
    <set>
        <item> 3 </item>
    </set>
    <set>
        <item> 1 </item>
        <item> 2 </item>
    </set>
    <set>
        <item> 1 </item>
        <item> 3 </item>
    </set>
    <set>
        <item> 2 </item>
        <item> 3 </item>
    </set>
    <set>
        <item> 1 </item>
        <item> 2 </item>
        <item> 3 </item>
    </set>
</set>
```

# A Simplification

Say we decide that use of comma is too verbose and use space to seperate things,
then we get

```scheme
[[] [1] [2] [3] [1 2] [1 3] [2 3] [1 2 3]]
```

Since English words are also separated by space

```scheme
[Since English words are also seperated by space]
```

I shall refer the list space separated as symbolic expression or s-expression.


# Parse Tree

Adapted from [https://en.wikipedia.org/wiki/Parse_tree](https://en.wikipedia.org/wiki/Parse_tree)

Given the English sentence "Reimu hit the ball" and suppose that it can have the parse tree as follows

```xml
<Sentence> Reimu hit the ball </Sentence>
<Sentence>
    <Noun> Reimu </Noun>
    <Verb_Phase>
    <Verb> hit </Verb>
    <Noun_Phase>
        <Determiner> the </Determiner>
        <Noun> ball </Noun>
    </Noun_Phase>
    </Verb_Phase>
</Sentence>
```

In JSON

```json
{
    "original sentence": "Reimu hit the ball",
    "sentence": {
        "Noun": "Reimu",
        "Verb Phase": {
            "Verb": "hit",
            "Noun Phase": {
                "Determiner": "the",
                "Noun": "ball"
            }
        }
    }
}
```

In YAML

```yaml
original sentence:  Reimu hit the ball
sentence:
    Noun: Reimu
    Verb Phase:
        Verb: hit
        Noun Phase:
            Determiner: the
            Noun: ball
```

Equivalent s-expression

```scheme
(Reimu hit the ball)
(Sentence
    (Noun Reimu)
    (Verb-Phase
        (Verb hit)
        (Noun-Phase
            (Determiner the)
            (Noun ball))))
```

# Program in YAML

Below is a python program calculating fibonacci number

```python
def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)
```

Equivalent scheme

```scheme
(define (fib n)
  (if (<= n 1)
      n
      (+ (fib (- n 1)) (fib (- n 2)))))
```

Say we reprogram them in YAML and JSON for fun

In YAML

```yaml
define:
    name: fib
    params:
        - n
body:
    if:
        le:
            left: n
            right: 1
    consequent: n
    alternative:
        add:
            left:
                call:
                    operator: fib
                    operand:
                        sub:
                            left: n
                            right: 1
            right:
                call:
                    operator: fib
                    operand:
                        sub:
                            left: n
                            right: 2
```

Equivalently in JSON

```json
{
    "define": {
        "name": "fib",
        "params": [
            "n"
        ]
    },
    "body": {
        "if": {
            "le": {
                "left": "n",
                "right": 1
            }
        },
        "consequent": "n",
        "alternative": {
            "add": {
                "left": {
                    "call": {
                        "operator": "fib",
                        "operand": {
                            "sub": {
                                "left": "n",
                                "right": 1
                            }
                        }
                    }
                },
                "right": {
                    "call": {
                        "operator": "fib",
                        "operand": {
                            "sub": {
                                "left": "n",
                                "right": 2
                            }
                        }
                    }
                }
            }
        }
    }
}
```

Or YAML without using associative array


```yaml
- define
- - fib
  - n
- - if
  - - "<="
    - n
    - 1
  - n
  - - "+"
    - - fib
      - "-"
      - n
      - 1
    - - fib
      - "-"
      - n
      - 2
```

Observation about YAML is that it uses identation to represent nesting structure.
JSON and s-experssion use brackets to represent nesting whereas their identation is merely for visual clue.
The consequence of using identation is that we cannot freely reorder the program.

For example,

```scheme
(define (fib n)
  (if (<= n 1)
      n
      (+ (fib (- n 1))
         (fib (- n 2)))))
```

```json
{ "define": { "name": "fib", "params": ["n"]},
  "body": {
      "if": { "le": { "left": "n", "right": 1}},
      "consequent": "n",
      "alternative": {
          "add": { "left": { "call": { "operator": "fib",
                                       "operand": { "sub": { "left": "n", "right": 1 }}}},
                   "right": { "call": { "operator": "fib",
                                        "operand": { "sub": { "left": "n", "right": 2}}}}}}}}
``` 

These are same as previous when parsed but YAML cannot do that.
Though we may write JSON in YAML to reorder the things.

Unfortunately, expressions or programs themselves are inherently nested, tree-like and recursive.
Using identation to represent nesting would require a lot of columns.

# One Problem

Lisp has its root from artifical intelligence to analyze natural languages.
The problem is that the sentence length is arbitrary.

There are at least 2 solution: linked list and dynamic array.
However, the solution at the time is to use pair represent sentence.
Though I could not figure why pair is chosen rather than dynamic array.
Even in the paper "The History of Lisp",
John Mc Carthy say list structure is apporiate representing sentence but without explaining further why

Here are few reasons I thought of

- coincidental and make use of existing idioms since predecessors used list to represent sentence
- inspired by Church encoding of pair in lambda calculus
- dynamic array still have to record length, not as arbitrary as pair
- dynamic array have to recopy whole thing everytime expand whereas expand list is as simple as pairing two lists

Pair is a data structure stored only two things.
We can represent pair in textual form using dot notation as follows

```scheme
(first . second)
```

To represent list, we use pair and nil

```scheme
(since . (english . (words . (are . (also . (seperate . (by . (space . NIL))))))))
```

And we decide below is a sugar syntax of above

```scheme
(since english words are also seperate by space)
```

Extend from that, this is how we represent empty list

```scheme
()
```

But we do not have this in dot notation. Or is it?
We may reuse the empty list to represent nil rather than using additional symbol `nil`.

```scheme
(since . (english . (words . (are . (also . (seperate . (by . (space . ()))))))))
```

In reality, John McCarthy can't reallly remember why adopt parenthesized list notation as external form of LISP data.

Another question arises is why designing external or textual form for list structure at the first place?

Imagine that we are using a stack machine to construct the list structure `(0 1 2 3)` without having textual form

```
push 0
push 1
push 2
push 3
push NIL
pair
pair
pair
pair
```

It is hard to visualize the list structure by looking at the program alone.
Secondly, it is not convenient when have to write the construction sequence for every list structure.
Implement a parser that take external form and construct list interanlly is better, hence the design of textual form.


# Accidental Conveniency

So LISP system include a reader that parse list external form construct list internally.
To complement it, LISP system include a printer that print internal list to external form on screen.

Rather than designing new syntax for primitive operations, just reuse existing reader

For example

```scheme
(cons 3 3)       ; construct pair
(car (cons 3 3)) ; 3
(cdr (cons 3 3)) ; 3
(+ 9 16)         ; 25
(quote (+ (* 3 3) (* 4 4)))  ; not to calculate (+ (* 3 3) (* 4 4)), rather just construct it
```

This suggests another perspective of reading Lisp program

> The Lisp programs are list structure data

For example,

```scheme
(+ 9 16)
```

It is same as

```scheme
(cons + (cons 9 (cons 16 '())))
```

Or it is a list of 3 things which are `+` symbol, 9 and 6 numbers.


To make it more concrete,

```scheme
(car (quote (+ 9 16)))       ; +
(cdr (quote (+ 9 16)))       ; (9 16)
(car (cdr (quote (+ 9 16)))) ; 9
```

```python
xs = ['+', 9, 16]
print(xs[0]) # +
print(xs[1]) # 9
```

In other word, rather than reading Lisp programs as they are streams of words like other languages,
we can read Lisp program like reading YAML and JSON.

Take a further step, we can even imagine Lisp system indeed operates on list structure that is same as the input program.

For example,

```scheme
(define (eval x)
  (cond
   ((number? x) x)
   ((eq? (car x) (quote +))
    (+ (eval (car (cdr x))) (eval (car (cdr (cdr x))))))
   ((eq? (car x) (quote *))
    (* (eval (car (cdr x))) (eval (car (cdr (cdr x))))))))

(eval (quote (+ (* 3 3) (* 4 4))))
```

# Reference
- "The History of Lisp" - [http://jmc.stanford.edu/articles/lisp.html](http://jmc.stanford.edu/articles/lisp.html).
- "The root of Lisp" - [https://paulgraham.com/rootsoflisp.html](https://paulgraham.com/rootsoflisp.html)