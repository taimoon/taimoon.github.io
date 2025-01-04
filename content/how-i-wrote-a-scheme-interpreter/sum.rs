fn sum_recur(n: isize) -> isize {
    if n == 0 {
        0
    }
    else {
        n + sum_recur(n - 1)
    }
}

fn sum_iter(mut n: isize, mut init: isize) -> isize {
    loop {
        if n == 0 {
            init
        }
        else {
            init = init + n;
            n = n - 1;
            0
        }
    }
}

fn main(){
    println!("{}", sum_iter(123456789, 0));
}