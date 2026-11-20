THEME_DETAIL=[
[
'Operational definitions should name the evaluation population, the kinds of tasks, and the range of environments. If the claim concerns human-level capability, specify the human comparator and the conditions under which performance counts as comparable. Such choices make the claim contestable and testable.',
'A taxonomy and an instrument serve different roles. A taxonomy names candidate capabilities; the instrument samples observable behavior. Researchers should publish example tasks and scoring rubrics for each faculty, then estimate inter-rater agreement and test whether one task actually isolates the intended construct.',
'Vary both the goal and the means of achieving it. Keep some procedures reusable while changing interface, task wording, or background assumptions. Record the amount of adaptation required. This can reveal whether an agent transfers a general strategy or simply recognizes a familiar workflow.',
'Threshold proposals should report measurement error and sensitivity to task weights. A threshold that changes when a few tasks are added is unstable. Until a robust decision standard exists, report capability ranges and explicit boundaries around each claim.'
],
[
'Report the full distribution rather than a single average. Include the weakest task family, performance by difficulty band, and variance across runs. This makes a capability gap visible to users who need to know whether an agent can be trusted for a particular task.',
'Human-referenced normalization can improve interpretation, yet the reference group influences the scale. Publish raw scores, the reference cohort, and the normalization method. A sensitivity analysis over alternative cohorts and weights can show whether a conclusion depends on one arbitrary baseline.',
'Use stable anchor tasks and a rotating frontier set. Anchors enable longitudinal comparison; frontier tasks maintain diagnostic value. Calibrate new items with expert and agent pilots, and audit the verifier against human judgments before using generated difficulty as a training signal.',
'Distinguish first-attempt reliability, best-of-N potential, and the cost of retries. Report independent trials with failures retained. When the evaluator permits retrying, state how retry selection works and whether the user would see the same benefit in deployment.'
],
[
'Visual benchmarks should test whether perception enables a prediction or action. Changing the available view while keeping the task constant can identify which observations matter. Pair recognition scores with task outcomes and inspect errors that originate in attention or scene interpretation.',
'Active sensing can be scored by the relevance of chosen observations, the time required to gather them, and whether important evidence was overlooked. Efficient observation is useful only when the agent preserves accuracy under misleading or incomplete visual input.',
'Connect generated answers to their source evidence. For visual sources, record page, region, chart axis, or table cell. When several documents conflict, test whether the system notices the conflict and qualifies its answer instead of citing one convenient passage.',
'Transfer requires an explicit shift. Move the same goal from static images to video, interfaces, or an interactive simulator. List what changed in the observation and action channels, and report performance before and after any demonstrations or task-specific setup.'
],
[
'An execution trace should separate observations, internal state summaries, chosen plans, calls, tool results, verification, and memory updates. This makes a failure diagnosable and allows another researcher to compare the actual system with its description.',
'Persistent state needs provenance. Store timestamps, source links, validation results, and dependencies between artifacts. Test how the agent behaves when state is stale or one intermediate summary is wrong. Recovery ability is a separate property from simple memory retention.',
'Run component ablations under equal budgets. Remove memory, delegation, reflection, or planning one at a time, then compare success, latency, and error severity. Architecture gains are meaningful when they survive matched model calls and tool access.',
'The reproducible object includes the controller, permissions, retry logic, prompts, memory policy, and exact tools. If a component is unavailable, say which causal claims can no longer be independently checked. A model name alone is an incomplete methods section.'
],
[
'Task synthesis should be evaluated as data production. Audit duplicate rates, task realism, solvability, verifier precision, and coverage of intended skills. Independently execute a sample with humans and alternate agents so that a generator does not grade itself.',
'The calibration learner and the verifier can share blind spots. Validate each separately on expert-written and held-out tasks. A difficulty label is credible when it predicts behavior across several systems, not only the learner used to construct the curriculum.',
'Agentic pretraining changes knowledge and procedures at once. Separate these effects with held-out domains, unfamiliar source formats, and tasks requiring corrections after contradiction. Score citation quality and calibration in addition to final answer quality.',
'A curator should produce an auditable experimental history: source pool, policy, selected examples, recipe, result, and reason for the next change. Check whether a discovered policy improves a fresh dataset or only tunes to the local benchmark reward.'
],
[
'Count unique task structures, tool schemas, state transitions, and fault classes. Report overlap between training and test environments. Many nominal environments may be near copies, while a smaller set can cover genuinely different interaction patterns.',
'Compare simulated and live systems on paired tasks. Track failures caused by authentication, rate limits, latency, changed state, or missing feedback. Protect live systems from accidental writes and provide a reset path for any state altered during research.',
'Hold out a domain, tool family, or task composition, then measure zero-shot performance, adaptation examples, recovery time, and human intervention. This shows whether the agent carries reusable strategies into the new setting.',
'Preserve benchmark versions. Report results on stable anchors and newly generated tasks, and independently review new tasks before release. Without version control, apparent progress may reflect a changed task sample or a more forgiving verifier.'
],
[
'State the population of tasks a benchmark samples and the intended scope of the inference. Publish task versions, inclusion rules, and uncertainty. A benchmark name cannot substitute for a specification of what a score means.',
'Component tests help locate a bottleneck; end-to-end tests show whether the full system integrates its components. Report both when possible. A system can compensate for a weak component or fail despite strong isolated scores, so trace inspection helps interpret the outcome.',
'Calibrate automated graders on a stratified human-labeled sample. Report disagreement, false passes on critical violations, and adjudication procedure. A grader that is accurate on ordinary cases can still fail on the edge cases that determine benchmark validity.',
'Separate benchmark development from final testing. Document public exposure and contamination checks, while acknowledging that checks cannot prove zero exposure. Fresh variants should retain stable anchor tasks so that updated benchmarks remain comparable.'
],
[
'Define which actions count as unsafe or unsupported before evaluation. A process rubric should distinguish harmless inefficiency from violation of a meaningful constraint. The rubric should map to the actual deployment risks being studied.',
'Faithfulness is a relation between a claim and evidence. Test whether cited material entails the answer, whether contradictory evidence is acknowledged, and whether uncertainty is stated. Retrieval alone does not guarantee that a source was used correctly.',
'Constrain tool permissions to the experiment. Log write actions and use a sandbox, rollback, or human confirmation for irreversible operations. A benchmark should include cases where the correct response is to ask, defer, or refuse an action.',
'Run repeated and targeted stress cases, reporting severity, detectability, and recovery. These results bound a safety claim to the tested settings; they do not guarantee behavior after a model, tool, or user population changes.'
],
[
'Capture assignments, messages, shared-state changes, and handoffs. Label duplicated work, dropped requirements, and incompatible plans. This reveals whether the team architecture adds coordination value or simply spends more inference on a task.',
'Compare role prompts with matched general-agent settings on held-out tasks. A role label is useful when behavior and performance change in a task-relevant way, not merely when the writing style changes.',
'Track every capability before and after a merge. Evaluate domains outside the merge objective, plus calibration and safety behavior. Per-domain profiles can expose interference that an aggregate score would hide.',
'Report total model calls, wall-clock time, tool calls, and human correction. Ablate the coordinator and shared memory to locate the gain. A larger team can increase coverage while making errors harder to trace.'
],
[
'Retain executable queries and intermediate results. Vary schema naming, table relationships, and ambiguous user questions. These tests show whether an agent can infer a data model instead of reproducing familiar query shapes.',
'Vary workflow dependencies, tool versions, partial completion, and access rights. Report recovery and compliance as well as completion. Name the model and scaffold versions so architecture comparisons can be reproduced.',
'Operational value depends on cost, latency, privacy, and review effort. Compare the complete assisted workflow with a human baseline that includes verification and correction time, not just the initial execution.',
'Hold out schemas and workflow families. Measure whether the agent asks a useful clarification question when the data are insufficient. A calibrated question can prevent a confident database error; include this behavior in the scoring rubric.'
]
]
PAPER_DETAIL=[
[
'The faculty map is most useful as a measurement agenda. A follow-up study can sample tasks for each dimension, publish rubrics, estimate evaluator agreement, and test whether faculty scores predict behavior outside the original test set.',
'Do not infer an AGI threshold from the illustration. The authors present a conceptual comparison framework; a threshold needs validated tasks, stable reference populations, and a defensible rule for combining scores.'
],
[
'The scenario map is useful for identifying assumptions about compute, algorithms, autonomy, and institutions. Readers can use it to compare pathways without treating a scenario as a prediction or timeline.',
'Separate theoretical possibility from current evidence. The report’s constraints matter: digital systems remain bounded by knowledge, compute, interfaces, and physical-world coupling.'
],
[
'Use this paper to frame experiments on visual abstraction and active observation. A strong follow-up would vary views, actions, and feedback while holding the task goal constant, then test transfer into an unseen environment.',
'The white paper’s proposed agenda should not be read as a validated model architecture. Claims about general visual understanding require empirical tests of prediction, counterfactuals, and action consequences.'
],
[
'The profile view can inform risk communication when users need to know where a system is weak. Follow-up work should test whether jaggedness predicts failures in realistic workflows better than task-specific measures.',
'The index depends on task choice and normalization. Present it beside the profile and conduct sensitivity analysis so that a dispersion score does not hide which dimensions drive the result.'
],
[
'The factorial comparison helps distinguish model effects from agent-implementation effects. Reproductions should expand the model and environment sample while preserving matched budgets and per-task failure reports.',
'Rankings remain conditional on the selected system components and benchmarks. A unified protocol improves comparability, but no finite benchmark suite can certify general-purpose capability.'
],
[
'Environment synthesis provides a testbed for studying coverage and scaling. Researchers should publish environment schemas, task-generation rules, reset behavior, and the overlap between training and test trajectories.',
'The observed scaling relationship is bounded by the generated environments and evaluation models. Simulated tool use cannot fully represent unstable real services, so claims about deployment need live or independently validated tests.'
],
[
'This paper supports treating training trajectories and research procedures as part of agent learning. Further work should measure evidence selection, correction, and transfer to unfamiliar fields independently of benchmark familiarity.',
'The paper appeared in ICLR 2026; an earlier preprint date may precede the conference record. Downstream comparisons should name the version and separate training effects from scaffold differences.'
],
[
'The pipeline makes difficulty a controlled variable. Its quality can be assessed through independent human calibration, multiple learner models, task diversity audits, and results on external benchmarks.',
'Generated tasks and verifier judgments may be coupled. A positive result on the paper’s own evolving benchmark is weaker evidence of transfer than success on a separately authored test set.'
],
[
'The staged task design makes long-horizon trajectories easier to inspect than a single success label. Human audits and adversarial verifier tests should accompany cost comparisons and coverage claims.',
'The authors report verifier errors on near-miss trajectories, demonstrating that automated pass/fail decisions need calibration. Treat cost and scale claims as specific to the proposed pipeline and current setup.'
],
[
'The schema-based design supports controlled variation in domains and action sequences. Releasing environment specifications would enable direct tests of the same policies under changed tools and more realistic service failures.',
'The simulated user and state model simplify deployment conditions. The evidence establishes behavior on the selected benchmarks, not broad transfer to unstable or safety-critical live APIs.'
],
[
'External state offers a concrete way to sustain document-heavy work beyond a single context window. Follow-up evaluations should test corrupted artifacts, abrupt tool failures, and whether the agent can resume without compounding mistakes.',
'Long-horizon coverage is a distinct capability from strong reasoning. The evaluation scope and model size constrain generalization; file persistence adds auditability but does not correct faulty intermediate conclusions.'
],
[
'The taxonomy is useful for designing a benchmark suite and for identifying gaps in present test practice. Pair the survey’s categories with a task inventory and specify which areas a given study omits.',
'Because benchmark landscapes change quickly, check primary papers and current versions before reusing comparisons. A survey can organize evidence but cannot replace evaluation under the intended deployment conditions.'
],
[
'The benchmark measures an important intermediate step in automated research: choosing data based on measured learning outcomes. Reproduce selected policies on fresh pools and retain manifests so changes can be audited.',
'Open-prompt agents can execute the loop while remaining weak at method selection. This gap shows why successful automation should include justified choices and repeatable artifacts, not only improved scores.'
],
[
'The benchmark makes source use observable through multimodal evidence tasks. A useful extension would score claim-level entailment, retrieval omissions, and uncertainty when source material conflicts.',
'Citation presence is an incomplete proxy for faithfulness. The rubric and retrieval set affect results; test whether the same answer remains grounded under changed source ordering and distractors.'
],
[
'The method offers a training-free route to combining task specialists. A robust evaluation should check whether merged systems preserve each specialist’s strengths and avoid regressions on unrelated tasks.',
'Neuron-level merging is sensitive to the selected models and target roles. Per-task profiles, calibration, and independent downstream tasks are needed to support a generalist claim.'
],
[
'The architecture diagrams make memory and orchestration choices explicit. Cross-platform tests and ablations can identify which components improve transfer versus merely improve a fixed interface benchmark.',
'Computer-use agents face UI changes, permission boundaries, and security risks. Performance on selected applications does not establish robust operation across operating systems or irreversible actions.'
],
[
'The dual-role setup makes environment feedback a training variable. An independent simulator or externally authored benchmark can test whether the agent learned reusable behavior rather than adapting to its co-evolving environment.',
'Agent and simulator may share a model’s blind spots. Separate environment validation from agent evaluation and report failure cases where the simulated state or feedback diverges from the task specification.'
],
[
'Architecture comparisons can help practitioners select a system for a known workflow family. Results become more general when researchers vary model, budget, tool access, and dependency structure independently.',
'Enterprise workflows vary by organization and permission policy. The benchmark’s task set provides a defined scope; broader claims require external schemas, realistic access constraints, and cost-aware replications.'
],
[
'Process records make shortcuts visible and help distinguish a correct answer from a safe method. A next study can test whether process labels predict incident risk in interactive tasks and whether reviewers agree on the rubric.',
'Process evaluation needs careful threat modeling and privacy controls. The paper motivates a broader evaluation target; it does not supply a universal process score that applies unchanged to every deployment.'
],
[
'Query traces make data-agent errors easier to diagnose. Follow-up studies should hold out database schemas, measure query execution separately from explanation, and check access control and refusal behavior.',
'Structured data benchmarks test a valuable but bounded family of tasks. Schema and database coverage shape results, and fluent explanations can obscure incorrect filters or joins.'
]
]
ANNEX_DETAIL=[
'For a reproducible implementation, define component contracts and version them. Keep a human-readable event log that links every state transition to the tool result that caused it. The architecture should make it possible to stop unsafe execution without losing the audit trail.',
'Select benchmark tasks to cover each matrix cell that matters. A full Cartesian product is often too expensive; explain sampling choices and identify untested cells. Report confidence intervals by environment class rather than only the global score.',
'Publish metric formulas and worked examples. Distinguish a failed task from an invalid run, and state how timeouts, tool errors, partial credit, retries, and human interventions affect the denominator.',
'Redact secrets while preserving task identifiers and event order. Record time stamps, tool versions, and evaluator outputs. A trace schema should allow independent scoring and should document which information is hidden from the agent at each step.',
'Use a primary failure label and allow contributing causes. Track whether a failure was detected by the system, evaluator, or user. The same visible error can arise from different components, so causal attribution should remain tentative until tested.',
'Every roadmap stage should produce a falsifiable hypothesis, baseline, and artifact package. Independent groups should be able to rerun the evaluation. Replication failures are evidence about construct stability and should be reported.',
'Threat models should match the tools and data in the experiment. Specify who can authorize changes, what actions need human review, how logs are protected, and what happens when a system cannot determine whether an action is safe.',
'These are working terms for cross-paper comparison. Preserve the terminology used by each source when citing it, and explain disagreements rather than forcing different definitions into one label.',
'Definitions should be refined as benchmarks and systems evolve. Keep the glossary concise and linked to the measurement choices in this review; terms such as “general,” “autonomous,” and “safe” need explicit operational meanings.'
]
THEME_DETAIL_TWO=[
[
'This definition also affects the training story. A model that performs well after extensive demonstrations is different from one that learns the task from a few examples. Record training exposure and adaptation effort so breadth is not confused with accumulated task-specific preparation.',
'When combining faculties, publish the weights and justify them against the study purpose. A safety review may assign more importance to rare severe failures than an overall capability benchmark. Different uses call for different profiles and should not be collapsed into one universal score.',
'Include tasks where visual or social information is irrelevant as controls. This tests whether success depends on the purported capability or on shortcuts. Keep task instances fresh enough to limit memorized answers while preserving a stable definition of the skill.',
'A credible research claim separates observation from interpretation. State what the system did, what the measured result supports, and which stronger conclusion remains untested. This discipline makes progress reports useful even when they do not support a headline AGI threshold.'
],
[
'For deployment decisions, a profile can be translated into conditional guidance: where the system is suitable, where review is needed, and which task families remain out of scope. The guidance should connect to observed evidence rather than a general assurance statement.',
'Normalization methods should be selected before inspecting the headline result. Researchers can compare median-based, percentile-based, and human-relative views, then report whether the conclusion changes. Transparent sensitivity checks reduce the risk that a favorable summary was selected after the fact.',
'Task writers should distinguish reasoning depth from irrelevant complexity. Harder items can become longer or noisier without testing a new capability. Human experts can review whether each added step is necessary and whether a valid alternative path exists.',
'A reliability statement should include a lower confidence bound for success, especially when a user may rely on the result. Rare failures need more runs to estimate than common outcomes. The number of trials should follow the risk and expected error rate.'
],
[
'Visual tests should include controlled occlusions and ambiguous scenes. Ask whether the agent seeks additional views or communicates uncertainty. The target is not perfect perception in every case, but behavior that detects when available evidence is insufficient.',
'Observe the interaction between perception and planning. An agent may accurately describe an image yet choose an action inconsistent with that description. Store the visual interpretation and action plan so researchers can test whether the error begins in perception or downstream use.',
'Source attribution can be evaluated with counterfactual edits: change a value in a chart or remove a paragraph and check whether the answer updates. This tests dependence on the cited source instead of superficial citation matching.',
'A multimodal transfer result should account for changes in tokenization, resolution, latency, and feedback frequency. These implementation details can explain performance shifts and should be documented with the benchmark design.'
],
[
'For each component, record both intended and observed behavior. An implementation diagram often leaves out retries or silent fallbacks. Listing them helps reviewers judge whether a system follows the described architecture and whether a result can be reproduced.',
'State corruption tests should include missing files, contradictory summaries, and stale task plans. Measure detection, recovery, and whether an agent propagates the bad information. This is a direct test of memory reliability over a long horizon.',
'Ablations should include operational measures. A reflection step may improve accuracy but double latency; delegation may raise coverage and increase coordination errors. Report the trade-off and show which deployment setting could benefit.',
'Where access to a proprietary model prevents exact replication, publish the interface contract and all controllable settings. A second lab can then reproduce the method with a different backbone and test whether the effect is architectural or model-specific.'
],
[
'Keep a reserved set of tasks outside the synthesis loop. Repeated iteration against one verifier encourages adaptation to its quirks. Periodically measure transfer to the reserved set and publish performance by task family.',
'If the verifier uses a model, disclose the model and prompts, validate it against human ratings, and test adversarial paraphrases. A verifier error can silently relabel training data and push learning in the wrong direction.',
'Continual learning can produce forgetting as well as improvement. Measure retained capabilities before and after each training stage, and check for shifts in calibration or refusal behavior. A single downstream score is an incomplete account of the training effect.',
'A data curator should justify why a policy may generalize. Compare its rationale with the actual selection behavior and test it under a new budget or sample distribution. Agreement between explanation and artifact is a separate quality dimension.'
],
[
'Benchmark builders can release clusters of related tasks so researchers can measure both coverage and redundancy. Describe how task clusters were formed and how many independent underlying skills the suite is intended to sample.',
'Live-system tests require safe accounts and bounded scopes. Record data retention, audit access, and cleanup procedures. Where live testing cannot be safely repeated, use a replayable trace plus a smaller supervised live validation set.',
'Adaptation cost should include human demonstrations, tool setup, and evaluation time. A system with strong eventual performance may require so much assistance that its practical transfer differs from zero-shot competence.',
'Generated environments should be inspected for the same policy exploiting repeated structures. Hold out schemas and task grammars, then test whether performance survives structural novelty rather than only new item wording.'
],
[
'Benchmarks can support cumulative science when changes are documented. Record additions, removals, rubric edits, and model access changes. If a result is no longer comparable, mark the break in the series instead of presenting a continuous trend.',
'End-to-end evaluators should inspect partial completion and safe stopping. Some tasks cannot be completed because required information is absent; a system that recognizes this can be more reliable than one that fabricates completion.',
'Measure evaluator performance on the errors most likely to change the claim. If a benchmark rewards exact outputs, test acceptable variants; if it rewards safety, test subtle policy violations. Global agreement hides the mistakes that matter.',
'Task leakage can arise through both public benchmark items and templated variants. Rotate only part of the suite, retain an anchor set, and monitor unusually sharp gains. Include a clear account of what the authors know about exposure.'
],
[
'Keep safety and task quality separate in reporting. A task can be completed accurately while the process violates a rule. A transparent dashboard shows each dimension and makes it possible to decide whether one should gate the other.',
'Trace review should verify the exact evidence available at decision time. An agent may cite a source acquired after forming a claim or rely on hidden benchmark metadata. Replaying the episode can establish the sequence of evidence and action.',
'Permission tests should include ambiguous user requests and urgent scenarios. Evaluate whether the system pauses for confirmation when consequences are irreversible. Document which operations were disabled by the harness, because sandboxing changes the problem.',
'Monitoring plans should specify thresholds for escalation, responsibility for review, and update cadence. A benchmark can inform those thresholds but cannot determine them without context about affected users and consequences.'
],
[
'Report a communication graph and shared-state policy for multi-agent experiments. If a team shares all intermediate content, one flawed answer may contaminate every member; if it shares too little, it may duplicate work.',
'Role quality can be tested using counterbalanced assignments. Swap the same task between agent roles, keep the model fixed, and compare changes in action selection. This distinguishes specialization from differences in task allocation.',
'Compare parameter merging with system-level routing or tool delegation under matched inference costs. Merging may reduce runtime overhead, while routing can preserve expert behavior; the best choice depends on latency, maintainability, and failure isolation.',
'In addition to outcome scores, measure communication tokens and recovery behavior when one agent is wrong. Strong coordination includes the ability to detect and correct an error rather than simply pass it downstream.'
],
[
'Data reasoning tests should include wrong but plausible schemas and missing values. Score whether the agent diagnoses the mismatch, asks a question, or explains what cannot be computed rather than returning an unsupported number.',
'Enterprise tasks may have irreversible effects. Include action authorization, rollback, and audit requirements as part of the evaluation. Successful completion should not erase evidence of an access-control or state-integrity violation.',
'Latency and cost comparisons should use the same hardware or clearly state differences. Include retries and verification calls; these often account for a substantial part of a production system’s operational cost.',
'A held-out test should change the organization-specific layer while keeping the task concept familiar. This separates transferable data skills from memorized schemas, and it gives a concrete measure of the work needed to adapt.'
]
]
