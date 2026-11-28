# Offside Stories: daily automation runbook

A scheduled session follows this every day at 15:12 IST. It makes whatever is due and posts it. Nothing else.

## 0. Setup (every run starts on a fresh machine)
1. Repo: `weezykhan-bit/portfolio`, branch `claude/ecstatic-albattani-4t1ykb`. Fetch it and work from `offside-stories/`. Media (mp4, wav) is not in git; rebuild what you need.
2. Voice: `python3 -m venv .venv && .venv/bin/pip install kokoro-onnx soundfile numpy scipy`, then `export HYPERFRAMES_PYTHON=$PWD/.venv/bin/python`. Kokoro downloads its model from GitHub on the first `tts` call. Voice `bm_george`. Respell names in `say` (see existing `vo/script.json` and `lf01/lines.py` for examples).
3. HyperFrames launcher: `node .claude/skills/hyperframes/scripts/plugin-cli.mjs` (from the repo root). Read the `/hyperframes` skill before building.
4. Composio session for app tools. Accounts: Instagram `instagram_relot-ashlar` (IG user 29163511996645815); Facebook `facebook_filago-ens` (Page 1467859606408300); YouTube `offside-stories-channel` (`youtube_gradin-dreamt`). **Never** use the YouTube account aliased `offside-stories` (`youtube_alette-honker`): that is the owner's personal channel. Before any YouTube upload, call YOUTUBE_LIST_CHANNELS mine=true on `offside-stories-channel` and confirm the ID is exactly `UCbvyLTr4LrLwn1Pwufrq0DA`; if not, upload nothing.

## 1. Decide what is due
Read `plan/content-queue.csv` (today = IST date).
- **Publish** rows where `publish_date` is today, or up to 2 days overdue **and not already live**.
- **Produce** long-forms where `produce_date` is today (render the day before; see §3).
- "Already live" is decided from the platforms, not from git: list the latest IG media (INSTAGRAM_GET_IG_USER_MEDIA), latest YouTube uploads, and latest Facebook Page posts, and match on topic/title. If it is already live, skip it. This prevents duplicates.
- Nothing due → stop and report "nothing due".

## 2. Facts (the hard rule)
- Every claim needs a source you actually read in this run (Wikipedia match/season pages, club sites, UEFA/FIFA/Premier League, major outlets). Write them into `<project>/FACTS.md`.
- Transfer fees say "reported". Quotes only if you find the exact wording in a reliable source; otherwise paraphrase without quote marks.
- If a fact cannot be confirmed, cut it. A shorter video is fine; an invented fact is not.
- Sensitive topics (Escobar, Karius, Eriksen, Vichai): no jokes, no polls, no sound-effect hits on death or injury, muted music.

## 3. Formats
**Long-form (YouTube, 8–10 min, 1920×1080)**: copy the `lf01/` pipeline: `lines.py` → `gen_vo.py` → `build.py` (scene per beat; chapter cards; cold open; brand sign-off) → `check` → snapshot review of ~12 moments → render → `mix.py` (underscore + SFX) → mux → `ffmpeg` small copy (crf 23) for hosting. Also make SRT, chapters, a 1280×720 thumbnail and a 1080×1920 cover.
- Produce on `produce_date`: upload to YouTube as **private** with title/description/tags/category 17, upload the SRT if a captions tool exists, and schedule the Facebook native upload with FACEBOOK_CREATE_VIDEO_POST (`published=false`, `scheduled_publish_time` = publish_date 18:00 IST).
- On `publish_date`: switch the YouTube video to **public**. Confirm the Facebook post went live.
**Reel / Short (9:16, 40–60 s)**: cut from that long-form's script and graphics: re-lay the scenes to 1080×1920 (see ep003 for the vertical system), with its own 6–8 shots, its own hook line in the first 2 s, and burned-in captions. Post as an Instagram Reel (share_to_feed=true, cover_url) and as a YouTube Short (same file, title ends "#Shorts"). Facebook gets it through Instagram's auto-share, so do not post it to Facebook separately.
**Instagram carousel (1080×1350, 6–8 slides)**: render slides as HyperFrames snapshots; host on GitHub raw; INSTAGRAM_CREATE_CAROUSEL_CONTAINER with `child_image_urls`; publish. Last slide: "Full stories on YouTube, link in bio". Facebook through auto-share.

Brand: black #0A0A0A, off-white #F5F5F0, yellow #FFE600, red #E10600; League Gothic + Inter; sign-off "OFFSIDE STORIES · Beyond the 90 minutes." No match footage, no broadcast audio, no AI-generated faces of real people. Photos: only CC BY / CC0 / public domain from Wikimedia Commons (never CC BY-SA), credited; if Commons rate-limits this machine, use graphic panels instead.

## 4. Hosting media for Instagram/Facebook
Copy files to `social/` in the repo, commit, push to the branch you are allowed to push to, then use `https://raw.githubusercontent.com/weezykhan-bit/portfolio/<that-branch>/social/<file>`. Verify md5 of the hosted file before creating a container. Keep files under 95 MB (use the crf 23 copy).

## 5. Posting rules
- Captions: hook line, 2–4 short lines of story, "Offside Stories. Beyond the 90 minutes.", one question, 4–5 specific hashtags. Instagram: "link in bio" (links are not clickable). YouTube: chapters in the description for long-forms; credits for any photo used.
- After publishing on Instagram, post the question as the first comment.
- Instagram publish calls can time out while still succeeding: **check the profile before any retry.** Never publish the same container twice.
- YouTube quota errors: leave the item for the next run (it is picked up as overdue) and say so in the report.

## 6. Report
End the run with a short report: what was posted (links), what was skipped and why, and any fact that was cut. Commit the new project folder (code, lines, FACTS.md, captions; no mp4/wav) to your branch.
