# The World Today — Friday 20 November 2026

A one-page newspaper front page summing up the world's news of
Friday 20 November 2026, drawn by a pure-stdlib Python 3.13 program
(`main.py`) into a 1024x1024 PNG. No network, no clock, no randomness:
two runs write byte-identical output.

## The day's stories

- **Cyclone Akvan bears down on India** — the severe storm is due to
  cross the Odisha and Andhra coasts by noon; more than 300,000 people
  moved to safety, 423 rescue teams on standby, 69 trains cancelled.
  (IMD; Daily Jagran live tracker)
- **Trump: no rush on Iran** — the president says the US will "see
  what happens" after 1 January, pushing any war decision into 2027.
  (Reuters; The Times of India)
- **Europe ready for Ukraine peace talks** — leaders in Berlin say
  they will negotiate with Russia, but any deal must be acceptable to
  Kyiv and to Europe. (BBC)
- **Voyager 1, a light-day away** — NASA confirms the 1977 probe is
  the first craft a light-day from Earth, 26 billion km out; its
  signal takes a day to arrive. (Reuters; NASA)
- **GTA VI tops $1.84bn** — Sensor Tower estimates the game beat
  The Odyssey's $1.805bn box office, the biggest launch ever.
  (Reuters; Forbes)
- **Ticker:** Houthi missile threat at Riyadh, Saudi coalition says;
  Nicholls 113 not out as NZ reach 243/5 vs India; World Children's
  Day marked today; Sensex at 83,022 after Thursday's rally.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, under 1 MiB)
```

Built on https://make.fun/r/7bgjyjbe — referral code `7bgjyjbe`.
