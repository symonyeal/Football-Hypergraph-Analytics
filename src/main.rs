//! tr: the minimal transversals of a family F, optionally only those with |T| <= k.
//!
//! Input (file or stdin): first line n (players 0..n-1), then one edge per line as
//! space-separated player indices. Output: JSON {"n", "m", "sets"}, sets sorted by (|T|, T).
//! Each set passes mcs::chk::check (covers every edge; private witness per member).
//!
//! Legend: F edge family, n players, m edges after normalization, k cardinality bound.

use mcs::{chk, hg, srch};
use std::io::Read;

fn parse(s: &str) -> Result<(usize, Vec<Vec<usize>>), String> {
    let mut ls = s.lines().filter(|l| !l.trim().is_empty());
    let n: usize = ls.next().ok_or("empty input")?.trim().parse().map_err(|e| format!("n: {e}"))?;
    let mut F = Vec::new();
    for l in ls {
        let mut e: Vec<usize> = l.split_whitespace().map(|t| t.parse().map_err(|x| format!("{t}: {x}"))).collect::<Result<_, _>>()?;
        if let Some(&v) = e.iter().find(|&&v| v >= n) {
            return Err(format!("player {v} >= n = {n}"));
        }
        e.sort_unstable();
        e.dedup();
        F.push(e);
    }
    Ok((n, F))
}

/// Tr(F) restricted to |T| <= k, each set checked against the raw rows.
pub fn tr(n: usize, F: &[Vec<usize>], k: Option<usize>) -> Vec<Vec<usize>> {
    let (H, _) = hg::norm(n, F);
    let cfg = srch::Cfg { ord: srch::Ord::Unhit, k, census: false, dl: None };
    let mut T: Vec<Vec<usize>> = Vec::new();
    srch::run(H.n, &H.ev, &cfg, &mut |s: &[usize]| T.push(s.to_vec()));
    for t in &T {
        chk::check(F, t).unwrap_or_else(|b| panic!("mcs output {t:?} fails check: {b:?}"));
    }
    T.sort_by(|a, b| (a.len(), a).cmp(&(b.len(), b)));
    T
}

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let mut k = None;
    let mut path = None;
    let mut i = 0;
    while i < a.len() {
        match a[i].as_str() {
            "--k" => {
                k = Some(a.get(i + 1).and_then(|x| x.parse().ok()).expect("--k needs an integer"));
                i += 1;
            }
            p => path = Some(p.to_string()),
        }
        i += 1;
    }
    let mut s = String::new();
    match &path {
        Some(p) => s = std::fs::read_to_string(p).unwrap_or_else(|e| panic!("{p}: {e}")),
        None => {
            std::io::stdin().read_to_string(&mut s).expect("stdin");
        }
    }
    let (n, F) = parse(&s).unwrap_or_else(|e| {
        eprintln!("tr: {e}");
        std::process::exit(2)
    });
    let T = tr(n, &F, k);
    let sets: Vec<String> = T.iter().map(|t| format!("[{}]", t.iter().map(|v| v.to_string()).collect::<Vec<_>>().join(","))).collect();
    println!("{{\"n\":{n},\"m\":{},\"sets\":[{}]}}", F.len(), sets.join(","));
}

#[cfg(test)]
mod tests {
    use super::tr;

    fn e(v: &[&[usize]]) -> Vec<Vec<usize>> {
        v.iter().map(|x| x.to_vec()).collect()
    }

    #[test]
    fn cycle4() {
        assert_eq!(tr(4, &e(&[&[0, 1], &[1, 2], &[2, 3], &[0, 3]]), None), e(&[&[0, 2], &[1, 3]]));
    }

    #[test]
    fn triangle() {
        assert_eq!(tr(3, &e(&[&[0, 1], &[1, 2], &[0, 2]]), None), e(&[&[0, 1], &[0, 2], &[1, 2]]));
    }

    #[test]
    fn solo_core() {
        // {0} is an edge, so 0 is in every minimal transversal.
        assert_eq!(tr(4, &e(&[&[0], &[0, 1], &[2, 3]]), None), e(&[&[0, 2], &[0, 3]]));
    }

    #[test]
    fn fano_minimum() {
        let L = e(&[&[0, 1, 2], &[0, 3, 4], &[0, 5, 6], &[1, 3, 5], &[1, 4, 6], &[2, 3, 6], &[2, 4, 5]]);
        let T = tr(7, &L, Some(3));
        // tau(Fano) = 3 and the minimum transversals are exactly the 7 lines.
        assert_eq!(T.len(), 7);
        assert!(T.iter().all(|t| t.len() == 3));
        assert!(tr(7, &L, Some(2)).is_empty());
    }

    #[test]
    fn no_edges() {
        assert_eq!(tr(3, &[], None), vec![Vec::<usize>::new()]);
    }
}
