# HW0: Where to run this notebook

**Ranked options — use the first one that works for you.**

HW0's ranking is the reverse of the later assignments', for two reasons. Part 1 of HW0 *is* a
lesson in building a Python environment; and HW0 is released before the semester starts, when
**the course computing environment is not yet available to you.**

## 1. Your own laptop (the path for HW0)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then, in the folder
holding this notebook:

```bash
uv run jupyter lab
```

That is the whole setup. `uv` reads `pyproject.toml`, builds the environment the first time
(a few minutes), and opens JupyterLab. There is nothing to activate and nothing to install by
hand. **Part 1 walks through what that command actually does** — if you have never built a
virtual environment before, read it rather than pasting.

Windows users: PowerShell will work, but [WSL](https://learn.microsoft.com/en-us/windows/wsl/about)
or [Git Bash](https://gitforwindows.org/) will match the commands you see all term.

### If you want more than HW0 needs

The command above installs what this assignment uses. Two larger sets are defined in
`pyproject.toml`, and you can move up to either later without starting over:

```bash
uv sync --extra ai-tools    # adds the in-notebook coding assistant
uv sync --extra full        # adds the whole course stack, matching FASOnDemand
```

Neither is needed for HW0. `--extra full` is worth having once the term starts and you are
working across several assignments; it is a large download.

### Using a coding assistant locally

`--extra ai-tools` installs the JupyterLab side of the assistant, but not the assistant itself:
that is a command-line program rather than a Python package, so two things have to come from
outside pip.

1. [Node.js](https://nodejs.org/) (version 22 or newer).
2. The Claude Code CLI: `curl -fsSL https://claude.ai/install.sh | bash`

Then run `claude` once in a terminal to sign in. You can also just use `claude` in the terminal
on its own — the JupyterLab extension is a convenience, not a requirement.

**On FASOnDemand both are already installed**, which is a good reason to work there once it
opens. If setting this up locally turns into a project, that is a fine reason to switch rather
than something to push through.

Whatever you use it for, the point of this course is that *you* can read, run and defend the
code you submit. An assistant that writes something you cannot explain has cost you the
assignment's value, and the midterms are closed-book.

## 2. Course computing (FASOnDemand, via Canvas)

The environment is pre-installed and your files persist between sessions — but it is reached
through Canvas, and **it will not be open to you until the semester begins**, which is after HW0
goes out. Plan on option 1 for this assignment. From HW1 onward this becomes the recommended
option, and if FASOnDemand does come online before your HW0 deadline you are welcome to finish
there: open the notebook and `Restart Kernel and Run All Cells`.

## 3. Google Colab (backup only)

Colab works, with two caveats:

- **The otter cells will error on Colab.** That is the `# Initialize Otter` cell at the very top
  and the `grader.check(...)` cells throughout; they need the notebook file itself, which Colab
  does not expose. They are worth nothing either way, but on Colab **`Run all` stops at the first
  one**, which leaves the rest of your notebook unexecuted and empty. **Delete those cells before
  you run.** You lose nothing: the same checks run again on Gradescope the moment you upload.
- **Colab's disk is wiped every session.** Upload `data/pg12242.txt` and `hw0_utils.py` alongside
  the notebook, or mount Google Drive and keep them there:

```python
from google.colab import drive
drive.mount('/content/drive')
%cd /content/drive/MyDrive/hw0     # keep the notebook, data/ and hw0_utils.py here
```

Note that Colab tells you nothing about whether you can build an environment yourself, which is
one of the things HW0 is trying to find out. Use it if you are stuck, and say so in the
Reflection.

## Whatever you use

Keep `data/pg12242.txt` and `hw0_utils.py` next to the notebook while you work — several
questions read them.

## Submitting

### First: run the whole notebook

`Kernel → Restart Kernel and Run All Cells`, then save. Do this before you export the PDF and
before you upload anything.

This is not a formality. Three things score **zero on the notebook assignment**, whatever is
written in the cells:

- **it was never run** — no output at all;
- **its cells were run out of order** — Jupyter records the order in the `[7]` beside each cell,
  the autograder reads it, and output that no longer matches the code it came from is worse than
  no output;
- **it stopped partway.** `Run All` halts at the first cell that raises, so everything below that
  cell stays blank — in the notebook and in the PDF.

**Your notebook has to run. It does not have to be right.** Those are different requirements, and
only the first one is enforced here: a wrong answer earns full credit, and the whole assignment is
graded on completion. But a cell that raises takes the rest of the notebook with it, and a
submission that stops on page 6 is one nobody can read — including you, since the diagnostic is
built from what your code actually did.

So if a cell raises and you cannot fix it, **stop it raising**: put a plausible value in it and
leave a comment saying what you were attempting. The cells below it then have something to work
with. Part 2 is a chain, so an error is usually caused by an earlier answer rather than by the
cell that reported it — the autograder's feedback names the cell that stopped, and that is where
to start looking backwards from.

Resubmission is unlimited before the deadline. There is no reason to submit a notebook you have
not just run.

### The two uploads

Both on Gradescope, both due at the same time. They are the same document in two formats:

1. **Homework 0 — Notebook 📔** — the notebook itself, `cs1090a_hw0.ipynb`. An autograder replies
   within a couple of minutes.
2. **Homework 0 — PDF 📄** — a PDF of the same notebook.

The 📔 and 📄 in the Gradescope titles tell you which file goes where. Upload the `.ipynb` to the
📔 one and the PDF to the 📄 one — swapping them is the most common way to lose points on an
assignment you have already finished.

### Making the PDF

**File → Save and Export Notebook As → HTML**, open that HTML file in your browser, and print it
to PDF. Exporting straight to PDF from Jupyter also works, but needs a LaTeX installation you
probably do not have. On Colab, use **File → Print**.

Skim the result before you upload. Anything printing pages of raw text is worth narrowing — a TF
reads this file, and `text` alone is nearly 200,000 characters.

### Marking the pages

After you upload the PDF, Gradescope shows you the assignment's outline and asks **which pages
each item is on**. There are six:

| Item | Mark these pages |
| :--- | :--------------- |
| Part 1 — Setting the Stage | the start of the PDF through the end of Part 1 |
| Part 2 — Python Poetry Challenge | all of Part 2 |
| Part 3 — Math and Statistics | all of Part 3 |
| Q3.3 — Partial derivatives | just your derivation |
| Q3.4c — Conditional probability | just your derivation |
| Q4 — Reflection | just your reflection |

The three parts are marked as whole chunks because **a TF reads your entire submission** — that
is where the *solid* / *shaky* verdicts on this side come from, and it is why there is no point
mapping thirteen separate questions. The last three are marked narrowly because they carry all
30 points on this assignment, and the page you mark is the page that gets graded.

Q3.3 and Q3.4c sit inside Part 3, so those pages get marked twice. That is expected — Gradescope
is happy for a page to belong to more than one item.

Every page should end up claimed by something. Gradescope's
[guide to submitting a PDF assignment](https://guides.gradescope.com/hc/en-us/articles/21853632412621-Submitting-a-PDF-Assignment)
walks through that screen. This is the same workflow you will use on HW1–HW5.

## Accessibility

If anything about the format of this assignment is a barrier, email the teaching staff. No
explanation needed, no penalty.

## If you get stuck on setup

Setup problems are the single most common way to lose an afternoon on HW0, and they are not what
the assignment is testing. Post on Ed with:

- your operating system and version,
- the exact command you ran,
- the full error message.

Then answer whatever you can on Colab in the meantime, and tell us about it in the Reflection —
question 4 exists for exactly this.
