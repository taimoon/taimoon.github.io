(define (sum? e)
  (and (= (length e) 3) (eq? (car e) '+)))

(define (product? e)
  (and (= (length e) 3) (eq? (car e) '*)))

(define (make-sum left right)
  (list '+ left right))

(define (make-product left right)
  (list '* left right))

(define (left-operand e)
  (cadr e))

(define (right-operand e)
  (caddr e))

(define (variable? x) (symbol? x))

(define (variable=? x y) (and (variable? x) (variable? y) (eq? x y)))

(define (deriv exp var)
  (cond
    ((number? exp) 0)
    ((variable? exp)
     (if (variable=? exp var) 1 0))
    ((sum? exp)
     (make-sum (deriv (left-operand exp) var)
               (deriv (right-operand exp) var)))
    ((product? exp)
     (make-sum (make-product (left-operand exp)
                             (deriv (right-operand exp) var))
               (make-product (deriv (left-operand exp) var)
                             (right-operand exp))))
    (else (error 'deriv 'unknown exp))))

(define (simplify exp)
  (cond
    ((number? exp) exp)
    ((variable? exp) exp)
    ((sum? exp)
     (let ((left (simplify (left-operand exp)))
           (right (simplify (right-operand exp))))
      (cond 
        ((eq? 0 left) right)
        ((eq? 0 right) left)
        ((and (number? left) (number? right))
         (+ left right))
        ((equal? left right)
         (make-product 2 left))
        (else (make-sum left right)))))
    ((product? exp)
     (let ((left (simplify (left-operand exp)))
           (right (simplify (right-operand exp))))
      (cond 
        ((or (eq? 0 left) (eq? 0 right)) 0)
        ((and (number? left) (number? right))
         (* left right))
        ((eq? 1 left) right)
        ((eq? 1 right) left)
        (else (make-product left right)))))
    (else (error 'simplify 'unknown exp))))

(define (writeln x) (write x) (newline))

(writeln (simplify (deriv '(* (+ x 3) (+ x 5)) 'x)))
(writeln (simplify (deriv '(+ (* x x) (+ (* 8 x) 15)) 'x)))
(write (simplify (deriv '(+ x 1) 'x))) (newline)
(write (simplify (deriv '(+ x 1) 'y))) (newline)
(write (simplify (deriv '(+ (* x x) (* x 3) ) 'x))) (newline)
(write (simplify (deriv '(* x x) 'y))) (newline)