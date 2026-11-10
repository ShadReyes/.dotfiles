# Skill Management

Language for managing a skill library across machines. Source provenance, acquisition, installation, selection, and exposure are distinct concepts.

## Language

**Skill ID**:
A stable identity assigned to a skill in the managed library, independent of its upstream name, source location, or installation location.

**Authored skill**:
A skill whose source the user maintains directly.

**Third-party skill**:
A skill originating with another maintainer. Local modifications do not erase its upstream provenance.

**Vendored source**:
A retained copy of third-party source, potentially including local modifications.

**Fetched source**:
Source obtained from an upstream repository at a recorded revision.

**Installed skill**:
A skill for which the manager has prepared a local installation. Installation alone does not imply selection or exposure to a harness.

**Selected skill**:
A skill included in a machine's desired set for use, independently of whether installation is currently available.

**Exposed skill**:
A skill made discoverable to a particular harness.

**Shared skill**:
A skill registered for distribution through the shared library, with source content and identifying metadata suitable for sharing.

**Private skill**:
A skill whose source and identifying metadata belong only to one machine and are excluded from shared library outputs. Private status is not a guarantee against disclosure through external tools or deliberate use.

**Shared profile**:
A reusable selection containing only shared skills and distributed with the shared library.

**Private profile**:
A machine-local selection containing only private skills. A machine may select private and shared profiles together without combining their definitions.

**Profile ID**:
A stable identity for a profile, distinct from its optional display name.

**Machine override**:
A machine-local membership choice for one skill: explicitly enabled, explicitly disabled, or inherited from selected profiles. It does not fix a source revision.

**Effective selection**:
The deduplicated skill membership obtained by combining selected profiles with machine overrides.

**Stale selection**:
A previously resolved effective selection retained after current references fail validation. It is not a successfully resolved selection of the current configuration.

**Desired selection**:
The effective selection resolved from the machine's current valid configuration, regardless of whether all selected skills are installed.

**Active installed set**:
The set of prepared skill installations designated by the most recent successful sync. It can differ from desired selection and does not imply harness exposure.

**Installation mismatch**:
A difference between a valid desired selection or its required source content and the active installed set. Unlike a stale selection, it does not imply invalid selection references.
