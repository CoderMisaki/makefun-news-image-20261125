# THE WORLD TODAY — Wednesday 25 November 2026

Entry for the make.fun competition `news-image-20261125`: sum up the
world's news of Wednesday 25 November 2026 in one image.

## What it is

`main.py` (Python 3.13, standard library only) draws a one-page
newspaper front page — masthead, lead story, six stories from around the
world, an "Also today" strip and a sources footer — and writes it to
`/output/entry.png` (1024x1024 PNG, about 23 KB).

No network at runtime, no fonts on disk, no third-party packages: the
page is drawn pixel by pixel with a small built-in 5x7 bitmap face, and
the PNG is encoded by hand with `zlib` + `struct`. Two runs write
byte-identical files (verified with sha256).

## The stories (all verified against live reporting on 25 Nov 2026)

- **Lead — Pakistan reaches orbit.** China's Shenzhou-24 lifted off
  from Jiuquan at 00:18 UTC carrying Muhammad Zeeshan Ali, the first
  Pakistani in orbit and the first foreign astronaut aboard the
  Tiangong station. (Reuters, Xinhua)
- **U.S. spy agencies breached.** The CIA and the Office of the
  Director of National Intelligence were hit by a cyberattack. (CNN)
- **Markets slide as tariffs loom.** Asian shares fell on fresh U.S.
  tariff threats: Seoul −5.3%, Taiwan −5.1%, Nikkei −2.9%. (Reuters)
- **Drone hits Riyadh tower.** A Houthi drone struck the capital's
  tallest tower, wounding 11. (Saudi civil defence via Reuters)
- **Kyiv: we hit a Russian ship.** Zelenskiy confirmed the drone
  strike on a Russian cargo ship in the Gulf of Finland. (Reuters)
- **30 held hostage in Cartagena.** Gunmen seized a supermarket after
  a failed cash-truck robbery; five women were freed. (Colombian
  presidency via wire reports)
- **Huawei found guilty.** A New York jury convicted Huawei on 10 of
  12 counts, including trade-secret theft. (U.S. Department of Justice)
- **Also today:** WHO evacuates Ebola staff in DR Congo; NATO vows to
  defend space; Seoul's education minister quits in an exam scandal;
  Sarkozy's corruption case is sent to trial; an O'Hare radar outage
  delays flights; Trump pardons two Thanksgiving turkeys.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see `LICENSE`.
