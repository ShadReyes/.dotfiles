# Figma skill acquisition, use, modification, and redistribution terms

Research snapshot: 2026-11-10. Subject: the official `figma/mcp-server-guide` **`skills/` files at commit `2b85b7d27bd6ee124667fcfe88856f6b1f81671a`**, plugin `2.2.155`, published 2026-10-14. This is published-evidence research, **not legal clearance, an ownership decision, or a migration policy**. [S1, S2]

## Finding in brief

**There is an express first-party terms pointer at the recorded revision.** Its README says:

> “By using the Figma MCP server and the related resources (including these skills), you agree to the Figma Developer Terms. These skills are currently available as a Beta feature.” [S1]

The linked Developer Terms contain an express, **limited access-and-use license**, not a general open-source license. Figma currently identifies the applicable published version as effective **May 5, 2026**, before the recorded revision. Its grant is for using Developer Resources to develop, test, and support a connection with Figma Services; its Beta provision says testing purposes only. This materially adds to the earlier source report: no standalone license file was established there, but **“no published permission at all” would be incorrect**. [S3, S4, S15]

Figma's current documentation expressly offers downloading and manually installing the skills, and encourages learning from and adapting two example skills. Those statements have different scopes and different historical certainty from the pinned README. **An express right to republish this entire pinned skills tree, with or without modifications, in a public dotfiles library was not established.** Nor does this report conclude that such publication is necessarily prohibited: contractual application, any additional permissions, and legal exceptions require the appropriate human determination. [S5–S8; §5 below]

## 1. Evidence boundaries and revision timeline

| Evidence | Observed publication/revision | What it establishes; what it does not |
| --- | --- | --- |
| Recorded source commit | `2b85b7d27bd6ee124667fcfe88856f6b1f81671a`, 2026-10-14; plugin `2.2.155` | The exact subject revision and its README terms/Beta notice. The completed source comparison identifies 14 skills and 93 files under `skills/`; that comparison is inherited context, not re-performed here. [S1, S2, S15] |
| README terms addition | PR **#32**, merged 2026-03-24, merge commit `2817a837b8b7b9685c24e91a225e370b25ad842e` | The PR's stated purpose is “Added the developer terms acknowledgement and beta disclaimer for MCP skills”; its patch inserts the quoted sentence. This is not a notice first added after the recorded October revision. [S9] |
| Developer Terms | Current page: effective **2026-05-05**; official version feed lists that date as its most recent entry | Figma's published version chronology places this version before the recorded commit. The previous version is separately archived as **2025-10-27**, with an archive notice dated 2026-05-05. No post-October terms version or later broad skill license was identified in the examined sources. These mutable legal pages are not an independently preserved October 14 web capture. [S3, S4, S10] |
| Current distribution/help documentation | Read 2026-11-10; no historical snapshot established | Direct first-party evidence for today's download, installation, use, and example-adaptation instructions. Their precise wording at the October revision remains unverified; they must not be silently backdated. [S5–S8] |
| Current repository reference | `main` resolved to `9d296d0768c3e29c813922b3b11e390f1e47d8aa` | A later source revision exists. The README history endpoint returned 27 entries, latest README change `f0493295acf5f7cbdebcbcc483c06de814420cb1` on 2026-10-05. This is bounded README-history evidence, not proof about every later file, unindexed statement, or permission. [S11] |

Only the named research ticket, the already-published shared-source report, and public primary sources were inspected. No private Skillset catalog, private originals, plans, receipts, recovery material, or local runtime/configuration was inspected. No installer, acquired skill/plugin code, or MCP operation was executed; no maintainers were contacted. No source, tracker, registration, profile, discovery, or runtime changes were made. This report is the only intended research-branch change.

## 2. Terms explicitly linked to these skills

### The actual grant and its scope

The Developer Terms' opening definition includes **“Application Programming Interfaces, Software Development Kits, Model Context Protocol servers, and related resources and documentation”** as **Developer Resources**. Coupled with the pinned README's express “including these skills,” this is a source-specific applicability chain, rather than an assumption that unrelated product terms license repository content. [S1, S3]

Section **2, License**, says:

> “Subject to these Terms, we grant you a non-exclusive, royalty free, worldwide (except to the extent prohibited by applicable law), non-transferable (subject to the section titled ‘Assignment’, below), limited license to access and use the Developer Resources only as necessary to develop, test, and support an integration or other connection (collectively, a ‘Figma Integration’) with the Services as permitted in Figma's associated developer documentation.” [S3]

This is affirmative access/use language, including a purpose limitation and reference to developer documentation. It does **not** enumerate a general right to sublicense, distribute copies, publish adaptations, or relicense the skill files. That observation concerns what the clause actually says; it is not a conclusion that no other permission or lawful basis can exist. [S3]

Section **8(a), Ownership**, distinguishes your integration from the Developer Resources:

> “you own all right, title, and interest in your Figma Integrations (excluding any Developer Resources)”
>
> “All rights not expressly granted are reserved, and no license or other right should be implied under these Terms.” [S3]

Consequently, ownership of a surrounding skill manager, library, or integration is not itself evidence that Figma's embedded materials can be relicensed. **[INFERENCE]** A separate integration and a copy of the upstream skill payload are different rights questions under this language. [S3]

### Conditions that remain attached to access/use

These are relevant limits, not a complete legal-compliance checklist:

- **Other agreements:** §1 says these terms do not grant access to Figma's online collaboration tools, which are governed by a separate **Agreement**. Developer Resource use is subject to both; these terms control conflicts, and the Acceptable Use Policy also applies. No person's or employer's actual Agreement, authority to accept it, or additional negotiated terms was inspected. [S3]
- **Beta:** the pinned README labels **these skills** Beta. Section **8(d)** says Developer Resources clearly identified as Alpha/Beta are **“provided to you for testing purposes only”**; Figma can remove them immediately without notice and provides them as-is. The report does not override this with the help article's “ready to use” description or declare unrestricted production use. [S1, S3, S5]
- **Updates/termination:** §4(b) includes agreeing to update to the latest Developer Resources promptly after updates; §4(d) requires deleting Developer Resources on termination. A Git commit pin supplies reproducibility, not an independently established perpetual frozen-version license or exemption. No update automation or retention policy follows from this report. [S3]
- **Public integrations:** §7 imposes additional requirements when **your integration** is made available outside your organization, including data/privacy/security obligations. It is not worded as a blanket redistribution license for the Developer Resources used by that integration. Whether a particular skills-only library is a “Figma Integration” is not settled here. [S3]
- **Acceptable Use Policy:** the linked current policy says **Last Updated: October 7, 2026** and applies to “anything that Figma makes available.” Section **2(n)** disallows “modify, or use anything that modifies, Figma's code or code execution”; §2(j) contains a programmatic-access restriction with an express-permission/applicable-law exception. These are conduct restrictions, not a reuse grant. Whether “Figma's code” covers particular Markdown, bundled JavaScript, or wrapper edits is a precise interpretation question; this report does not generalize it into a categorical ban on editing skills, especially alongside the example-adaptation documentation below. [S12]

The archived **2025-10-27** Developer Terms already include the same limited access/use grant, ownership reservation, MCP/related-resources definition, and Beta testing language (then §8(c)). They are useful historical corroboration, but the **May 5, 2026** version—not that older version merely because the repository notice was introduced in March—is the version Figma's current chronology places before the October baseline. [S3, S4, S10]

## 3. What official distribution and adaptation guidance actually says

### Local acquisition and client use

The **pinned README** recommends the Figma plugin for Claude Code, explicitly saying it includes MCP server settings and Agent Skills, and gives the official-marketplace install command. It also links the Figma help article about the plugin's skills. That is explicit intended acquisition/use documentation at the subject revision; the command was **not run**. [S1]

The current **Figma skills for MCP** help article states:

> “If your AI tool doesn't have a Figma MCP plugin, you can download and manually install the skills.”

Its download link targets `figma/mcp-server-guide/archive/refs/heads/main.zip`. It instructs placing the contents in the appropriate folder for the user's tool. The current FAQ likewise tells users without plugins to download the skills and put them in the client folder. [S5, S6]

**Observed:** this is more specific than merely making source public or listing an official plugin: Figma positively documents local downloading, installation, and use of its skill files. **[INFERENCE]** It supports the intended local-acquisition/use pathway within the linked terms and documentation, not an unlimited right to mirror or redistribute a standalone bundle. The archive follows `main`, not the recorded commit; these pages do not establish that the exact manual-download wording existed on October 14. [S1, S3, S5, S6]

The current usage article defines skills as Markdown **and supporting files** such as scripts/assets and distinguishes skills (instructions) from tools (capabilities). Installing copies does not itself grant tool access or add MCP capabilities; the authoring article expressly says writing a skill does not grant access to its tools. This research makes no claim that any Claude Code, Codex, OMP, or Pi installation is present, supported, or legally cleared for a particular runtime configuration. [S7, S8]

### Modification: a narrow positive statement, not an all-files license

The current official skills article specifically describes **`figma-generate-library` and `figma-generate-design`** as examples and says:

> “Both skills are fully functional and ready to use. They're also provided as references: if you want to build your own skill for a workflow specific to your team, these are good starting points to learn from and adapt.” [S5]

**Observed:** Figma positively encourages learning from and adapting these **two named examples** for team-specific workflows. It would be inaccurate to say the official documentation contains no adaptation encouragement. However, this is not a repository-wide copyright license enumerating permissions for all 14 skills and their companion files, and it does not specify publishing copies or derivatives, sublicensing, attribution obligations, or applicability to this older revision. The statement's historical availability at the baseline is unverified. [S5]

The FAQ's **“Anyone can write and share skills, and there's no approval process”** appears in a discussion of creating skills and links to the Community and `community-resources` collection. The authoring article teaches creation of **your own** skill. Neither sentence specifically says that Figma grants permission to copy, modify, and publicly redistribute the complete official `mcp-server-guide/skills/` tree. Do not equate sharing original skills with permission to republish someone else's skill content. [S6, S8]

## 4. Repository statements, public-hosting rights, and misleading shortcuts

### The directly relevant upstream licensing exchange

PR **#29** (2026-03-17) proposed source/author metadata and explicitly asked which license to add. The proposal's author was an outside contributor (`author_association: NONE`), not a Figma licensing statement. The PR was closed without merging. On 2026-04-08, repository collaborator `ebentley-figma` replied:

> “Thanks for the feedback, we'll take it on board!” [S13]

That acknowledgement is **not** an answer choosing a license, granting modification/redistribution rights, or promising a retroactive grant. Conversely, it is not an express prohibition. The pinned README's incorporated Developer Terms remain stronger affirmative terms evidence than this unresolved exchange. [S1, S3, S13]

GitHub's repository-scoped public searches for `license`, `terms`, and `copyright OR redistribute OR permission OR licensing` in titles/bodies/comments returned complete indexed result sets. They identified #29, #32, and a potential misleading license mention in **#71**. The #71 PR summary mentions a “skill-local README and MIT license” for **`workflow-skills/video-interaction-mapper`**, a separate standalone workflow—not the bundled `skills/` tree. Its final changed-files response does not itself include a license file. Neither that proposal summary nor a license from another repository/marketplace can be generalized to these 14 official skills. The searches did not identify a broader upstream grant; indexed searches are not proof that no statement exists anywhere. [S14, S1]

### GitHub supplies a narrower, separate public-repository grant

GitHub's published Terms of Service, effective **April 27, 2026**, §D.5, say a public repository grants other users a nonexclusive worldwide license to **“use, display, perform and reproduce (by forking) Your Content through the Service as permitted by GitHub's functionality.”** The preceding sentence defines forks as users' copies **within the Service**. Section D.3 makes the uploader responsible for rights to material it did not create. [S16]

This hosting-platform grant is relevant evidence, so public availability is not treated as having no permissions whatsoever. But it is **not a Figma-authored MIT/Apache-style grant**, does not expressly cover arbitrary off-platform distribution or relicensing, and does not resolve whether copying a selected subtree into a different public dotfiles repository is within that scope. This report neither rejects nor extends §D.5 by legal inference, and does not reconcile it with a user's separate Figma Agreement. Those are human legal questions if that grant is relied on. [S3, S16]

No applicable license is inferred from GitHub's `license: null`, an “official” plugin listing, author metadata, public forks, another vendor's marketplace license, or the absence of a file named `LICENSE`. The repository metadata itself is only a bounded present-state observation, not the copyright grant. [S17]

## 5. Permission matrix and exact unresolved inputs

| Proposed activity | Affirmative published evidence | Boundary / unresolved input |
| --- | --- | --- |
| Acquire locally and load the official skills for a Figma workflow | Pinned README's specific terms notice and plugin instructions; Developer Terms §2 access/use grant; current official manual-download instructions. [S1, S3, S5, S6] | Subject to purpose, Beta, Agreement/AUP, account/tool-access, and other terms; no unrestricted production-use conclusion. Exact manual-download wording at the baseline is unverified. |
| Read/reference skills while developing, testing, or supporting a Figma connection | Explicit limited access/use grant, subject to documentation. [S3] | Does not establish use unrelated to Figma Services or exemptions from the other conditions. |
| Make local adaptations | Current documentation explicitly encourages learning from/adapting the two named example skills. [S5] | Need scope for the exact revision, the other skills/support files, code/wrapper changes, and interaction with AUP §2(n). No blanket all-files modification grant was established. |
| Share newly authored skills | Official authoring and FAQ documentation invites writing/sharing skills. [S6, S8] | Original instructions and copies/derivatives of official materials are distinct; this is not a substitute license for the latter. |
| Make a GitHub fork | GitHub §D.5 expressly describes copies within its Service. [S16] | No decision that this covers a repackaged subtree, external mirrors, a client cache, or relicensing; Figma-specific terms still require consideration. |
| Publicly vendor, mirror, redistribute, or relicense unchanged/modified official files | No express general grant for that activity was established from the examined Figma sources. [S1, S3, S5, S13, S14] | **Unestablished, not adjudicated prohibited.** Need applicable written permission/license or a human legal determination of an existing lawful basis, with scope and conditions. |
| Keep using a frozen old revision indefinitely | Reproducible commit identity only; §4(b) contains update language. [S2, S3] | Need a human interpretation or upstream exception for retention/use of an old pin; do not silently treat reproducibility as a perpetual-use term. |

### Narrow clarification needed before treating public redistribution/modification as cleared

An authorized human can ask Figma's appropriate rights/legal contact for a published license or written clarification covering:

1. **Exact payload and revision:** `figma/mcp-server-guide/skills/` at `2b85b7d27bd6ee124667fcfe88856f6b1f81671a`, including all Markdown references, JavaScript helpers, and type declarations—not only `SKILL.md`, and not a different Community collection.
2. **Specific acts:** downloading/caching for the existing clients; modifying instructions/helpers or compatibility metadata; distributing unchanged or modified copies in a public dotfiles/skill library or mirror; whether recipient downloads must instead come directly from Figma. Clarify any sublicense/relicense and commercial-use permissions rather than assuming them.
3. **Conditions and time:** required attribution/notices; whether a grant covers this recorded revision retroactively or only later versions; whether Beta/testing, update, and termination provisions continue to govern distributed copies or adaptations; and which interpretation applies to AUP §2(n).
4. **Surrounding contract:** which Agreement applies to the actual individual/entity and proposed use, who can bind it, and whether a separate written authorization already exists. This prerequisite must be supplied by an authorized human; this research intentionally did not inspect private contracts or account state.

No outreach was made. These are missing rights/scope facts, not a recommendation to choose remote acquisition, vendoring, forking, a particular owner, or a migration. No automatic upstream update, manager takeover of plugin/MCP capabilities, or expansion beyond the existing workflows is authorized by this report.

## Sources

All web sources were read on 2026-11-10. GitHub commit/blob links are immutable; legal/help pages, API search results, and branch references are mutable and are identified as such above.

- **S1 — Pinned Figma README**, terms/Beta notice; Claude Code distribution; tools/skills scope: [README at `2b85b7d…`](https://github.com/figma/mcp-server-guide/blob/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/README.md).
- **S2 — Pinned Figma commit and manifest**: [commit `2b85b7d…`](https://github.com/figma/mcp-server-guide/commit/2b85b7d27bd6ee124667fcfe88856f6b1f81671a), [GitHub commit API](https://api.github.com/repos/figma/mcp-server-guide/commits/2b85b7d27bd6ee124667fcfe88856f6b1f81671a) (date and manifest patch to `2.2.155`).
- **S3 — Figma Developer Terms**, published effective May 5, 2026; opening definition and §§1, 2, 4, 7, 8: <https://www.figma.com/legal/developer-terms/>.
- **S4 — Official Developer Terms version feed**, dates and prior-version URLs: <https://www.figma.com/legal/developer-terms/feed/feed.json>.
- **S5 — Figma skills for MCP**, “Get the Figma skills,” “Download the skills,” and “Example skills: Write to canvas”: <https://help.figma.com/hc/en-us/articles/39166810751895-Figma-skills-for-MCP>.
- **S6 — Figma MCP server FAQs**, “What are skills, and where can I find them?” and “Why can't I see the Figma skills?”: <https://help.figma.com/hc/en-us/articles/39252411778583-Figma-MCP-server-FAQs>.
- **S7 — Use skills with the Figma MCP server**, definitions and tool/skill distinction: <https://help.figma.com/hc/en-us/articles/39287396773399-Use-skills-with-the-Figma-MCP-server>.
- **S8 — Create Skills for the Figma MCP server**, own-skill authoring, supporting files, tool permissions: <https://help.figma.com/hc/en-us/articles/42495326765591-Create-Skills-for-the-Figma-MCP-server>.
- **S9 — Figma PR #32**, first-party accepted terms notice: [PR](https://github.com/figma/mcp-server-guide/pull/32), [PR metadata](https://api.github.com/repos/figma/mcp-server-guide/pulls/32), [exact patch](https://api.github.com/repos/figma/mcp-server-guide/pulls/32/files), [merged README](https://github.com/figma/mcp-server-guide/blob/2817a837b8b7b9685c24e91a225e370b25ad842e/README.md).
- **S10 — Archived October 27, 2025 Developer Terms**, archive notice and older clauses: <https://www.figma.com/legal/developer-terms/archive/v2025-10-27/>.
- **S11 — Current Figma reference and README history**: [main reference](https://api.github.com/repos/figma/mcp-server-guide/git/ref/heads/main), [README history](https://api.github.com/repos/figma/mcp-server-guide/commits?path=README.md&per_page=100), [last observed README-changing commit](https://github.com/figma/mcp-server-guide/commit/f0493295acf5f7cbdebcbcc483c06de814420cb1).
- **S12 — Figma Acceptable Use Policy**, last updated October 7, 2026, opening scope and §2: <https://www.figma.com/legal/aup/> (the incorporated `https://www.figma.com/aup/` redirects here).
- **S13 — PR #29 and collaborator response**, not a license grant: [proposal](https://github.com/figma/mcp-server-guide/pull/29), [response permalink](https://github.com/figma/mcp-server-guide/pull/29#issuecomment-4205458608), [comments API identifying collaborator/date](https://api.github.com/repos/figma/mcp-server-guide/issues/29/comments). Closed/unmerged state and proposal text also appear in S14's license search.
- **S14 — Bounded upstream public-statement searches**: [license](https://api.github.com/search/issues?q=repo%3Afigma%2Fmcp-server-guide+license+in%3Atitle%2Cbody%2Ccomments&per_page=100), [terms](https://api.github.com/search/issues?q=repo%3Afigma%2Fmcp-server-guide+terms+in%3Atitle%2Cbody%2Ccomments&per_page=100), [copyright/redistribution/permission/licensing](https://api.github.com/search/issues?q=repo%3Afigma%2Fmcp-server-guide+%28copyright+OR+redistribute+OR+permission+OR+licensing%29+in%3Atitle%2Cbody%2Ccomments&per_page=100); [PR #71 final changed files](https://api.github.com/repos/figma/mcp-server-guide/pulls/71/files?per_page=100), [PR #71](https://github.com/figma/mcp-server-guide/pull/71).
- **S15 — Prior shared-source comparison**, inherited inventory only, not a licensing authority: [source-ownership report at `9cfffaf…`](https://github.com/ShadReyes/.dotfiles/blob/9cfffafc6296fd40dd131ad30ea75b14eb3cea54/research/skill-distribution/source-ownership.md).
- **S16 — GitHub Terms of Service**, effective April 27, 2026, §§D.3 and D.5; hosting-platform terms, not Figma's own file license: <https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#d-user-generated-content>.
- **S17 — Current Figma repository metadata**, observed `license: null`, public visibility, disabled issues/discussions: <https://api.github.com/repos/figma/mcp-server-guide>.
