def sum_way(s: int) -> list[list[int]]:
  return sum_way_recur(s, list(range(1, s+1)), [])

def sum_way_recur(s: int, ns: list[int], used: list[int]) -> list[list[int]]:
  if s == 0:
    return [used]
  elif s < 0 or ns == []:
    return []
  else:
    return sum_way_recur(s - ns[0], ns, used + [ns[0]]) + sum_way_recur(s, ns[1:], used)

def sum_way(s: int, n: int) -> int:
  if s == 0:
    return 1
  elif s < 0 or n <= 0:
    return 0
  else:
    return sum_way(s - n, n) + sum_way(s, n - 1)


def sum_way_k(s: int, n: int) -> int:
  kont = ['sum_way_k', s, n, []]
  val = None
  while True:
    match kont:
      case []:
        return val
      case 'sum_way_k', 0, _, _kont:
        kont = _kont
        val = 1
      case 'sum_way_k', _, 0, _kont:
        kont = _kont
        val = 0
      case 'sum_way_k', s, _, _kont if s < 0:
        kont = _kont
        val = 0
      case 'sum_way_k', s, n, _kont:
        kont = ['sum_way_k', s - n, n, ['sum_way_k_cont', s, n, _kont]]
      case 'sum_way_k_cont', s, n, _kont:
        kont = ['sum_way_k', s, n - 1, ['add', val, _kont]]
      case 'add', prev, _kont:
        kont = _kont
        val = prev + val
      case _:
        raise NotImplementedError(kont)

# print(sum_way(10, 10))
# print(sum_way_k(10, 10))

from dataclasses import dataclass
@dataclass
class Expr:...
@dataclass
class Add: ...
@dataclass
class Mul: ...
@dataclass
class Hole(Expr):...
@dataclass
class Prim(Expr):
  left: Expr
  op: Add|Mul
  right: Expr

def calc(e: Expr) -> int:
  match e:
    case int():
      return e
    case Prim(e1, Add(), e2):
      return calc(e1) + calc(e2)
    case Prim(e1, Mul(), e2):
      return calc(e1) * calc(e2)
    case _:
      raise NotImplementedError(e)

def unparse(e: Expr) -> str:
  match e:
    case int():
      return str(e)
    case Hole():
      return '_'
    case Prim(e1, Add(), e2):
      return f'({unparse(e1)} + {unparse(e2)})'
    case Prim(e1, Mul(), e2):
      return f'({unparse(e1)} * {unparse(e2)})'
    case [*es]:
      return '(' + ', '.join(unparse(e) for e in es) + ')'

def calc(e: Expr, ctx: list[Expr]|Hole = Hole()) -> int:
  print(unparse(e), unparse(ctx), sep=' , ')
  match e, ctx:
    case int(v), Hole():
      return v
    case int(v),[Prim(Hole(), op, e2), _ctx]:
      return calc(Prim(v, op, e2), _ctx)
    case int(v),[Prim(e1, op, Hole()), _ctx]:
      return calc(Prim(e1, op, v), _ctx)
    case Prim(int(v), Add(), int(w)), _ctx:
      return calc(v + w, _ctx)
    case Prim(int(v), Mul(), int(w)), _ctx:
      return calc(v * w, _ctx)
    case Prim(int(v), op, e2), _ctx:
      return calc(e2, [Prim(v, op, Hole()), _ctx])
    case Prim(e1, op, e2), _ctx:
      return calc(e1, [Prim(Hole(), op, e2), _ctx])
    case _:
      raise NotImplementedError(e)

print(calc(Prim(2, Add(), Prim(3, Mul(), 5))))

def calc(e: Expr) -> int:
  ctx = Hole()
  while True:
    print(unparse(e), unparse(ctx), sep=' , ')
    match e, ctx:
      case int(v), Hole():
        return v
      case int(v),[Prim(Hole(), op, e2), _ctx]:
        e = Prim(v, op, e2)
        ctx = _ctx
      case int(v),[Prim(e1, op, Hole()), _ctx]:
        e = Prim(e1, op, v)
        ctx = _ctx
      case Prim(int(v), Add(), int(w)), _ctx:
        e = v + w
        ctx = _ctx
      case Prim(int(v), Mul(), int(w)), _ctx:
        e = v * w
        ctx = _ctx
      case Prim(int(v), op, e2), _ctx:
        e = e2
        ctx = [Prim(v, op, Hole()), _ctx]
      case Prim(e1, op, e2), _ctx:
        e = e1
        ctx = [Prim(Hole(), op, e2), _ctx]
      case _:
        raise NotImplementedError(e)

print(calc(Prim(2, Add(), Prim(3, Mul(), 5))))


def calc(e: Expr, ctx = lambda x: x) -> int:
  match e:
    case int(v):
      return ctx(v)
    case Prim(e1, Mul(), e2):
      return calc(e1, lambda v: calc(e2, lambda w: ctx(v * w)))
    case Prim(e1, Add(), e2):
      return calc(e1, lambda v: calc(e2, lambda w: ctx(v + w)))
    case _:
      raise NotImplementedError(e)


# print(calc(Prim(2, Add(), Prim(3, Mul(), 5))))


def trampolined_calc(e: Expr) -> int:
  bounce = calc(e)
  while not isinstance(bounce, int):
    bounce = bounce()
  return bounce

def calc(e: Expr, ctx = lambda x: x) -> int:
  match e:
    case int(v):
      return lambda: ctx(v)
    case Prim(e1, Mul(), e2):
      return lambda: calc(e1, lambda v: calc(e2, lambda w: ctx(v * w)))
    case Prim(e1, Add(), e2):
      return lambda: calc(e1, lambda v: calc(e2, lambda w: ctx(v + w)))
    case _:
      raise NotImplementedError(e)

from functools import reduce
e = reduce(lambda e, i: Prim(e, Add(), i), range(1000))

print(trampolined_calc(e))