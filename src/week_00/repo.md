---
title: Repo Clone
---

# Repo Clone

The project template lives at **[rocketjetpack/summer-intern-2026](https://github.com/rocketjetpack/summer-intern-2026)**. You won't push directly to it — instead you'll fork it, work in your own copy, and pull in any updates the mentors publish as the summer goes on.

## 1. Fork it

On the [project repo's GitHub page](https://github.com/rocketjetpack/summer-intern-2026), click **Fork** (top right) and create the fork under your own account. You'll end up with your own copy at `github.com/<your-username>/summer-intern-2026`. <br />*You are welcome to make this private if you wish.*

## 2. Clone your fork

Clone *your fork* (not the original) onto whichever machine you'll be working. You can clone this on multiple systems, but be sure to use sane Git workflows or you may wind up needing a hand with Git.

```sh
git clone https://github.com/<your-username>/summer-intern-2026.git
cd summer-intern-2026
```

## 3. Add the original as "upstream"

Right now `origin` points at your fork. To track the oringal repo where I will add changes as we go, you need to add a second remote. This is conventionally named `upstream`, and points at the original template repo. This will allow you to sync your copy with changes I make without losing your own work:

```sh
git remote add upstream https://github.com/rocketjetpack/summer-intern-2026.git
git remote -v   # confirm: origin -> your fork, upstream -> rocketjetpack/summer-intern-2026
```

## 4. Pulling in upstream updates

Whenever you want to check for and bring in updates from the original repo:

```sh
git fetch upstream
git merge upstream/main
```

Do this periodically — especially before starting a new week's content, in case that week's page was updated or corrected after you forked.

## 5. Documenting your weekly notes

Each week's page (e.g. [Week 2](../week_02/objectives)) has its own **Personal Notes** section/page — that's where your running lab notebook lives: what you learned, what confused you, and the artifacts you'd want to discuss. Please fill these in *as you go* (a note jotted down about a question you have mid-week beats trying to reconstruct it on Friday afternoon).

Commit and push your notes (and any code, captures, or scripts you produce) to **your fork**:

```sh
git add <files>
git commit -m "Week 2: notes and ARP capture from the Wireshark lab"
git push origin main
```

Small, frequent commits with descriptive messages make it much easier to follow your progress over the summer.

## 6. Do NOT commit sensitive information

This likely goes without saying, but **never** commit sensitive information to GitHub. That includes obvious things like passwords, but also less obvious things like machine names, usernames, internal network addresses, etc.
