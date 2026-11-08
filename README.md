# GitHub Actions + Semgrep: Detect, then Enforce (beginner lab)

**Goal:** experience a real pull request that introduces an insecure coding pattern, see the SAST result, then make the security check mandatory.

**Safe demo:** no credentials, external systems, AWS resources, or live servers are used. Do not execute the intentionally vulnerable example. It exists only to be scanned as text.

## What each file does

| Path | Purpose |
| --- | --- |
| `src/check_host.py` | Secure starting code. This is what the SAST workflow scans. |
| `rules/sast.yml` | Semgrep rule identifying Python `subprocess.run(..., shell=True, ...)`. |
| `.github/workflows/sast.yml` | Active GitHub Actions workflow. Initially **report-only**. |
| `examples/vulnerable_check_host.py.txt` | Deliberately insecure replacement code for your test PR. |
| `examples/enforced-workflow.yml.txt` | Full alternative workflow that **fails the check** on a finding. |

## Phase 0 — Create the repository (browser only)

1. Sign in to [GitHub](https://github.com/) and click **New repository**.
2. Name it `github-sast-training`. Choose **Public** if you're using GitHub Free and want to enforce required checks later; GitHub Free currently provides branch protection/rulesets for public repositories, not private ones. The content of this lab is intentionally safe to share publicly. Do not upload any actual corporate code or secrets.
3. Initialize with a README if GitHub requires one for the browser upload process; it's fine to overwrite/replace it with this README.
4. Extract the ZIP file on your PC.
5. In the GitHub repository choose **Add file > Upload files**. Drag and drop the extracted files/folders, preserving their nested paths. Make sure that `.github/workflows/sast.yml` appears **at the repository root** under `.github` (not inside a second `github-sast-training` folder).
6. Commit directly to `main` for this initial lab setup. If GitHub prompts for a PR, complete the initial setup PR.
7. Open **Actions** > **SAST Demo** > select the latest run > click `security-scan` > expand **Scan application code (detect only)**. The safe starting code should yield **0 findings**, if the environment can download the scanner image.

If the upload UI struggles with hidden folders or folder hierarchy, use **Add file > Create new file** and enter the full path `.github/workflows/sast.yml` (GitHub automatically creates the directories). Paste the content from the extracted file. Do the same for `rules/sast.yml`, `src/check_host.py`, and the two `examples/*` files if needed.

## Phase 1 — Introduce a vulnerability and DETECT it

1. Open `src/check_host.py` on GitHub and click the pencil icon **Edit this file**.
2. Replace its content with the contents of `examples/vulnerable_check_host.py.txt`.
3. Under **Commit changes**, choose **Create a new branch** (example: `test/insecure-ping`) and **Propose changes**.
4. Create a pull request into `main`.
5. Open the PR's **Checks** tab, or go to **Actions > SAST Demo** and click the run related to this PR.
6. Expand the step **Scan application code (detect only)**. You should see a `python-subprocess-shell-true` finding pointing at `shell=True` in `src/check_host.py`.
7. **Crucial:** the job should still have a green/successful result because Semgrep's normal `scan` command reports findings but does not exit nonzero solely because findings exist. It detects the issue without blocking the PR.
8. **Do not merge yet.** We'll turn this into an enforced security gate in the next phase.

If you don't see a run, check **Actions** is enabled under the repository **Settings > Actions > General**. GitHub may require initial approval for workflows originating from outside collaborators; your own PR from a branch in your own repo should ordinarily run.

## Phase 2 — Make the scanner FAIL on findings

1. While still on the `test/insecure-ping` branch, edit `.github/workflows/sast.yml`.
2. Find this line:

   ```yaml
   run: semgrep scan --metrics=off --config=rules/sast.yml src
   ```

   Replace it with:

   ```yaml
   run: semgrep scan --metrics=off --error --config=rules/sast.yml src
   ```

   Or copy the entire example from `examples/enforced-workflow.yml.txt`.
3. Commit that workflow change to the *same feature branch* associated with the PR.
4. GitHub reruns the PR workflow. The `security-scan` job should be **red/failed** because Semgrep detected a finding and `--error` made it return a nonzero exit code.
5. **Important:** A failed job is not the same thing as an enforced merge prohibition. Continue to Phase 3.

## Phase 3 — Require the security check before merging

For a public repo on GitHub Free:

1. Visit repository **Settings > Rules > Rulesets** (or **Settings > Branches** for classic branch protection).
2. Create a **branch ruleset**, name it `require-security-checks`, set status to **Active**, and target the **default branch (`main`)**.
3. Enable **Require a pull request before merging** and **Require status checks to pass before merging**.
4. Add the required status check **`security-scan`**. GitHub may offer suggestions after a scan has run. Choose the job/check with this exact name. Keep the check name stable in your workflow.
5. Save the active ruleset. If available, restrict bypass permissions; for a realistic security control, ensure developers can't simply push directly to `main` or bypass review.
6. Return to the PR. The red `security-scan` result should now **block merging**.

If you don't see Rulesets or branch protection, check repository visibility/plan. GitHub Free generally supports these for **public** repositories. For a private personal repo, the status check may still fail visually but enforcement options can be unavailable.

## Phase 4 — Remediate and confirm that the PR can merge

1. On the feature branch, edit `src/check_host.py` again, replacing its content with the original secure implementation (from `main` or the original ZIP).
2. Commit the fix to the same branch.
3. Watch the new workflow run: **no finding**, **green status**, and the required status check can now pass.
4. Merge the PR. You've completed an automated detect → fail → prevent merge → remediate → pass cycle.

## Interview-ready explanation

> "I configured a GitHub Actions workflow triggered by pull requests. The job checked out the code into a runner and used Semgrep with a custom Python rule to find unsafe shell execution. I started with report-only scans, then changed the command to fail the job on findings. Finally, I set a required status check on `main` so a failing PR couldn't merge until the code was fixed."

This is **a training lab**, not a full production design. In an organization, also secure changes to workflow/rule files using code-owner reviews, protect branches, review third-party Actions, avoid privileged `pull_request_target` triggers for untrusted code, pin dependencies/images, and run periodic comprehensive scans. A developer able to remove the scanner from a PR without review can undermine an in-repo check.

## Official docs

- [GitHub Actions quickstart](https://docs.github.com/en/actions/get-started/quickstart)
- [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub repository rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)
- [Semgrep CI example](https://semgrep.dev/docs/semgrep-ci/sample-ci-configs)
- [GitHub Actions security guidance](https://docs.github.com/en/actions/reference/security/secure-use)
