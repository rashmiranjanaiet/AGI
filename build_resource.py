from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from pptx import Presentation
from pptx.util import Inches as PInches, Pt as PPt
from pptx.dml.color import RGBColor as PRGB
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_THEME_COLOR
from content_expansions import THEME_DETAIL, THEME_DETAIL_TWO, PAPER_DETAIL, ANNEX_DETAIL
import re, json, textwrap

ROOT=Path(__file__).parent
OUT=ROOT/'output'
OUT.mkdir(exist_ok=True)
NAVY=colors.HexColor('#12253F'); TEAL=colors.HexColor('#087E8B'); GOLD=colors.HexColor('#C99A3B')
PALE=colors.HexColor('#EAF1F3'); INK=colors.HexColor('#233044'); MUTED=colors.HexColor('#5B6878')

def P(title, body, sub='', visual=None, refs='', kind=''):
    return dict(title=title, body=body if isinstance(body,list) else [body], sub=sub, visual=visual, refs=refs, kind=kind)

pages=[]
# 1-6: front matter
pages += [
P('GENERAL INTELLIGENCE AS A RESEARCH PROGRAM',
  ['A critical synthesis of twenty recent papers on cognitive breadth, visual grounding, agent architectures, learning environments, evaluation, and reliability.',
   'Prepared by Rashmi Ranjan Behera\nPrepared for Dr. Vidya Mohanty\nLiterature review · Version 1 · 20 November 2026',
   'This document is an independent literature synthesis. “Prepared for” identifies the intended academic reader; it does not imply co-authorship, endorsement, supervision, or verification by Dr. Vidya Mohanty. The review makes no claim that the author worked on this project for a year.'],
  'Research resource paper · 100 pages · 20-paper corpus', 'cover', '[R01–R20]'),
P('ABSTRACT',
  ['This review asks what evidence would justify a claim that an artificial system has broad, transferable intelligence. It synthesizes twenty 2026 research papers and technical reports on cognitive frameworks, visual intelligence, agent training, environment construction, persistent state, task benchmarks, process evaluation, and specialist integration.',
   'Across the corpus, progress appears as a systems property. A capable model must combine useful representations with planning, tools, memory, learning from feedback, and controlled action in environments it has not seen during training. Aggregate benchmark scores alone conceal uneven capabilities and risky paths to success. The stronger evidence comes from held-out tasks, repeated runs, trace-level diagnostics, calibrated difficulty, and explicit accounting for cost and failures.',
   'The review proposes a layered evaluation protocol and a reference architecture for studying generality. It separates (i) capability breadth, (ii) transfer, (iii) sustained autonomy, and (iv) reliability under constraints. These are research dimensions, not a definitive AGI threshold. The evidence base is recent and heterogeneous; several prominent works are preprints or lab reports. Results in a benchmark support claims about that benchmark and setup, not a conclusion that AGI exists.'],
  'Keywords: artificial general intelligence; agents; evaluation; transfer; reliability; multimodal learning', 'layers', '[R01–R20]'),
P('EXECUTIVE SYNTHESIS',
  ['The papers collectively move discussion of AGI from a single score toward a profile of interacting capacities. Cognitive frameworks make breadth legible; visual intelligence work argues that perception should support prediction and action; agent studies add tools, state, and long-horizon execution. Training papers test whether curricula and environment diversity extend the frontier. Evaluation papers ask whether systems finish tasks, respect constraints, and use trustworthy processes.',
   'Three conclusions guide this review. First, a system can be broadly useful yet sharply uneven; capability profiles should accompany averages. Second, learning and transfer depend on the task distribution and environment, so benchmark construction is part of the scientific claim. Third, successful outcomes do not establish safe or general behavior when process, reproducibility, and failure recovery remain unmeasured.',
   'A practical research program should state its operational definition, disclose the model and scaffold, test novel combinations of familiar skills, measure repeated-run variance, inspect action traces, report resource use, and preserve independent reproduction. No paper in this collection demonstrates AGI. Together, the papers provide tools for asking more disciplined questions about progress toward it.'],
  'The central question is empirical: what changes when tasks, settings, and constraints change?', 'radar', '[R01,R04,R05,R12,R19]'),
P('SCOPE, METHOD, AND LIMITS',
  ['The corpus contains twenty locally supplied PDFs dated within the twelve months ending 20 November 2026. The set spans laboratory reports, preprints, peer-reviewed conference papers, and a survey. The source index in papers/README.md records institutional affiliations, venues, publication dates, and official links. Conference publication year is distinguished from an earlier arXiv posting where relevant.',
   'I extracted text from each PDF, read the full text, and reviewed figure and table pages using rendered contact sheets. I treated diagrams as evidence about the authors’ proposed mechanisms or experimental design, not as independent confirmation of the claims. The summaries below paraphrase the papers, label the evidence type, and identify interpretive limits.',
   'This is a focused, non-systematic review. It does not cover every AGI theory, safety framework, robotics result, or scaling study. Several papers are preprints, and rapidly changing model versions make exact leaderboard comparisons perishable. The sources are authored research, not independent proof. Publication by a prominent lab or conference is a provenance signal; it does not guarantee correctness.'],
  'Inclusion window: 20 Nov 2025–20 Nov 2026 · corpus size: 20 papers', 'evidence', '[R01–R20]'),
P('HOW TO READ THE EVIDENCE',
  ['Four evidence labels are used throughout. “Conceptual framework” organizes a problem but does not by itself demonstrate performance. “Benchmark construction” introduces tasks, environments, or metrics; its validity depends on coverage and leakage controls. “Empirical comparison” reports results under a defined setup; conclusions stay bounded by its models, baselines, and tasks. “Position or survey” maps arguments and gaps but does not establish a new capability.',
   'Claims receive stronger support when an experiment includes a suitable baseline, held-out evaluation, human-checked scoring, repeated trials, trace inspection, and transparent artifacts. These checks answer different questions. A high score can coexist with brittle execution. A clean trace can still be based on a narrow task sample. Replication matters because stochastic systems may yield different outcomes across runs.',
   'When reading a result, ask: Who authored and published it? What is the unit of evaluation? Which capabilities are isolated or bundled? Can the agent alter state? Is the test static or interactive? What does the metric reward? Which failure cases are counted? Are tools, prompts, and model versions specified? These questions make the evidence easier to compare.'],
  'Provenance is not the same as validation.', 'evidence', '[R05,R12,R19]'),
P('MAP OF THE REVIEW',
  ['Part I develops a working vocabulary and a cross-paper account of generality. It examines cognition, multimodal grounding, architectures, training, environments, evaluation, reliability, and integration. Part II profiles each source in the supplied corpus, preserving the paper’s stated contribution and showing how it fits the larger argument.',
   'Part III translates the synthesis into a proposed reference architecture, evaluation protocol, metrics, failure taxonomy, research roadmap, and glossary. These are recommendations developed in this review, not results claimed by the papers.',
   'Citation keys [R01]–[R20] identify the supplied papers. Additional authoritative sources are [A1]–[A3]. The full bibliography appears on pages 96–100. Original diagrams are conceptual schematics prepared for this review; they are not copied figures or measured results.'],
  '6 opening pages · 40 synthesis pages · 40 paper-profile pages · 9 technical annex pages · 5 reference pages', 'map', '[R01–R20,A1–A3]')
]

themes = [
('1 · Defining generality', [
('An operational question','The phrase “artificial general intelligence” carries more than one meaning. Some authors emphasize human-level performance across cognitive domains; others emphasize learning and adapting to unfamiliar tasks. A useful study begins with an operational definition: which tasks, environments, time horizons, and constraints count? Without that statement, a result can be impressive yet difficult to interpret. [R01,R02]'),
('Cognitive breadth as a profile','The cognitive framework in [R01] separates ten faculties and groups them into broader capacities. This makes a profile more informative than a single “AGI score”: systems may differ in perception, memory, learning, planning, metacognition, or social reasoning. Any composite score encodes weights and assumptions. Publish the underlying measures and justify the aggregation.'),
('Capability, autonomy, adaptation','A tool-using system may act autonomously within a narrow workflow. That is meaningful capability, but autonomy alone does not establish generality. A broader claim needs evidence that the system can infer new task structure, choose strategies, use feedback, and transfer across domains with limited task-specific engineering. [R05,R12]'),
('Necessary humility in thresholds','A threshold is useful for a decision only when its consequences and measurement error are clear. The papers do not establish a universal boundary between narrow AI and AGI. This review therefore uses “progress toward AGI” for evidence about breadth, transfer, adaptation, and sustained execution, while treating achieved-AGI claims as unsupported by this corpus.')
]),
('2 · Capability measurement and unevenness', [
('Why averages mislead','An average can rise while a critical capability remains weak. [R04] characterizes “jaggedness” as unevenness across tasks or faculties and proposes human-referenced normalization alongside profile analysis. The practical implication is to report the distribution: per-task scores, confidence intervals, low tails, and error categories.'),
('Profile construction','A useful profile separates dimensions that matter for deployment: task success, learning efficiency, robustness to variation, calibration, and policy compliance. Dimensions should remain visible before any summary score. Human comparison can calibrate scale, but a human baseline is not a universal intelligence unit and may vary with expertise and interface. [R01,R04]'),
('Difficulty and saturation','A benchmark can become less informative as models improve or as training data overlap increases. Static tests are easy to reuse and compare, but they invite saturation. Dynamic tests can refresh tasks and expose adaptation, yet may introduce evaluator noise. Papers such as [R08,R09] explore calibrated or generated tasks; calibration and verification determine whether harder means more diagnostic.'),
('Uncertainty belongs in the result','Agent runs vary with sampling, tool errors, latency, and environment state. Reporting one best run hides reliability. A stronger result reports mean and spread, the number of attempts, completion rate, and representative failure traces. Claims should specify whether the score is pass@1, best-of-N, average across runs, or a human-rated outcome. [R05,R09]')
]),
('3 · Visual and grounded intelligence', [
('From pixels to useful models','Visual intelligence involves more than recognizing objects. A system must select relevant evidence, infer spatial relations, track change, predict what actions will do, and revise its interpretation when observations contradict a plan. [R03] argues for learned visual abstractions that support downstream reasoning and interaction. This remains a research proposal rather than a demonstrated route to AGI.'),
('Active perception','In interactive tasks, the agent chooses what to inspect. Screenshots, camera motion, zoom, search, or a targeted query can reduce uncertainty. Evaluation should therefore score information gathering as part of behavior, not simply the final answer. Poor perception may be caused by attention allocation, representation, tool selection, or an outdated world model; error attribution needs trace evidence. [R03,R14]'),
('Grounding across modalities','Images, text, video, geometry, and action traces can provide complementary evidence. More modalities do not guarantee better grounding: a system may over-trust fluent text or miss a visual detail. Source-grounded evaluation in [R14] asks whether answers are actually supported by retrieved material. Provenance and entailment checks are essential when agents synthesize across formats.'),
('Embodiment and transfer','Embodied systems receive consequences through action and environmental feedback; text-only systems often rely on human abstractions. [R02,R03] discuss how these differences may shape learning. A research program should compare the same underlying goal across visual simulation, desktop interfaces, APIs, and physical settings, while reporting the interface and reset conditions.')
]),
('4 · Agent architecture and persistent state', [
('The agent as a closed loop','A useful abstraction is: observe, represent state, plan, act, verify, update. Each stage can fail independently, and feedback connects them. An architecture diagram should show data flow, tool boundaries, and recovery paths. The loop is a design scaffold, not evidence that the system reasons in a human-like way. [R05,R11,R16]'),
('External memory and files','Long context is not equivalent to durable state. [R11] studies a file-centric framework that persists plans and artifacts between bounded reasoning steps; [R16] examines memory for computer-use tasks. External state can support long runs, but stale files, corrupted summaries, and propagated hallucinations become new risks. Memory needs provenance and validation.'),
('Orchestration costs','Hierarchical agents can delegate subtasks and combine specialist routines. They also add coordination overhead, latency, and new failure points. Evaluation should compare a hierarchical system with a single agent under equal model, tool, and token budgets. Without cost-matched baselines, an apparent architectural gain may reflect more inference or a different environment. [R11,R18]'),
('The interface is part of the system','An agent’s capabilities depend on what tools it can call, how state is exposed, and how actions are checked. “Same model” comparisons can be unfair when scaffolds differ. Every report should identify model snapshot, system prompt, tool schema, memory policy, retry logic, permissions, and stopping rule. The complete deployed object is model plus scaffold plus environment.')
]),
('5 · Learning, curricula, and data synthesis', [
('Data quality shapes the frontier','Agent training data contains tasks, trajectories, feedback, and environmental responses. Synthetic data can scale coverage, but generated tasks may be invalid, duplicated, or trivially solved by shortcuts. [R08,R09] propose mechanisms for expanding task difficulty; a sound pipeline must calibrate task solvability and verify outcomes independently.'),
('The zone of proximal development idea','[R08] uses a ZPD-inspired loop: propose tasks near the learner’s current boundary, refine them with tools, then filter tasks based on observed solvability. This provides a concrete way to focus training. Its validity depends on the accuracy and independence of the verifier and on whether the generated distribution transfers beyond the pipeline that created it.'),
('Continual pretraining','[R07] studies agentic continual pretraining for deep research behavior. This line treats agent trajectories and intermediate behaviors as training material, extending beyond isolated instruction-response examples. Evaluation should distinguish memorization of research procedures from robust synthesis, evidence tracking, and correction when sources disagree.'),
('Curation as a research capability','[R13] tests whether agents can inspect datasets, write selection policies, train models, and improve policies from measured feedback. The benchmark reveals a difference between executing a scaffolded loop and inventing a method. Research automation should be judged by artifact quality, data integrity, repeatability, and justified decisions, not only a final metric.')
]),
('6 · Environments and transfer', [
('Environment diversity as coverage','[R06] and [R10] study scaling agent environments and tool ecosystems. Diverse environments can expose new action patterns, but counting tasks is a weak proxy for diversity. A meaningful coverage analysis compares state schemas, goals, tool dependencies, failure modes, and task horizons. More environments help only if they introduce informative variation.'),
('Simulation and real-world friction','Simulations enable resets, deterministic feedback, and controlled experiments; real APIs can fail, drift, rate-limit, or change without warning. Simulation may teach stable patterns that fail in production. Real systems may be difficult to reproduce. Good evaluation uses both and reports which properties of the target setting each environment captures. [R06,R10]'),
('Transfer as the core test','A useful test holds out a domain, task composition, or interface while preserving reusable underlying skills. Measure the gap from in-distribution to held-out performance, the amount of adaptation data required, and recovery after the first failure. Transfer can be positive, negative, or absent; the benchmark should reveal all three.'),
('Self-evolving tasks','Generated or self-play tasks can keep pace with a system, but the generator and solver may share blind spots. Human review, independent execution checks, and external test sets reduce this coupling. A benchmark that evolves should preserve versioned task snapshots so results remain comparable across model generations. [R08,R09,R17]')
]),
('7 · Evaluation science and benchmark validity', [
('Benchmark claims have a perimeter','Every score belongs to a defined task sample, interface, model version, and scoring rule. [R12] surveys benchmark dimensions including data, environment, interface, metric, and safety. This review adopts that decomposition to make hidden assumptions visible. A benchmark label should not stand in for a complete specification.'),
('End-to-end versus component tests','Component tests isolate a capability such as tool selection or visual grounding. End-to-end tests assess whether components work together. Component scores help locate bottlenecks; end-to-end tests reveal integration failures. Neither substitutes for the other. Report both where possible and avoid inferring a cognitive faculty from a narrow task metric. [R05,R12]'),
('Human and automated judging','Automated verifiers scale but may reward plausible-looking outputs or miss subtle violations. Human judges offer context but introduce cost and disagreement. Calibrate automated evaluators against human labels, report agreement and adjudication rules, and publish examples where judges disagree. Evaluator robustness is part of benchmark validity. [R09,R13]'),
('Reproducibility and contamination','Benchmarks can leak through public prompts, data, or training exposure. Reproducibility requires versioned tasks, documented model access, fixed budgets, random seeds where applicable, and explicit scoring code. Contamination audits reduce one risk but cannot prove the absence of exposure. Refreshes need stable anchors so progress remains interpretable.')
]),
('8 · Reliability, process, and safety', [
('Outcome is not the whole trace','An agent can reach the right answer by violating a constraint, using unsupported evidence, or performing risky intermediate actions. [R19] argues for process evaluation. A complete record includes observations, tool calls, intermediate state changes, verification attempts, and termination. Process metrics should reflect the actual harm model rather than reward procedural conformity for its own sake.'),
('Faithful grounding','A trustworthy research agent should make claims traceable to evidence and flag missing support. [R14] evaluates whether an agent reads sources faithfully. Citation presence alone is not enough; provenance should map each factual claim to a relevant passage or data point. Contradictory sources and uncertainty need explicit treatment.'),
('Risk as an execution dimension','For data and computer-use agents, actions can disclose information or alter external state. Permission boundaries, reversible actions, sandboxing, and human approvals are system properties. The task score should penalize prohibited actions even when the goal is achieved. Reports should state which tools had write access and how failures were contained. [R16,R20]'),
('Reliability needs repeated trials','A single successful trajectory says little about tail risk. Measure repeatability, rare but severe failure modes, robustness to minor changes, and recovery after tool or network errors. For consequential settings, the evaluation should include adversarial cases and independent monitoring. None of these checks prove safety in all deployments; they bound evidence to tested conditions.')
]),
('9 · Specialization, roles, and integration', [
('Specialists can complement one another','[R15] explores role-conditioned merging of specialized agents; [R17] studies dual-role evolution between agent and environment. These works treat specialization and interaction as possible routes to broader behavior. Integration should be evaluated on tasks requiring real coordination rather than a simple sum of isolated scores.'),
('Role labels are not competence','A role prompt may change style without changing capability. To test meaningful specialization, compare role assignment with matched general-agent baselines, examine trace quality, and swap roles on held-out tasks. Include coordination failures such as duplicated work, incompatible assumptions, and dropped constraints.'),
('Merging and interference','Parameter or neuron merging can combine useful behaviors, but may also cause negative transfer, conflict, or loss of calibration. Report pre-merge and post-merge profiles, not only the aggregate score. A specialist’s gain should be checked alongside its effect on unrelated skills and refusal behavior. [R15]'),
('Multi-agent economics','More agents can increase coverage while raising communication cost and error propagation. A fair comparison accounts for total inference, wall-clock time, tool calls, and human correction. Coordination topology is a design choice. Publish ablations that remove role allocation, shared memory, or the environment model to show which component drives the result.')
]),
('10 · Domain agents and enterprise workflows', [
('Data agents expose hidden assumptions','[R20] benchmarks agents that answer questions over structured data. Such tasks require schema understanding, query generation, execution, result interpretation, and communication of uncertainty. A plausible sentence can still be wrong because the query targeted the wrong table or filtered the wrong population. Tests should retain query and database traces.'),
('Enterprise architecture choices','[R18] compares agent architectures in enterprise workflows. Real workflows involve dependencies, permissions, partial outcomes, and tool-specific constraints. Architecture rankings may shift with task mix, model, and operational budgets. The value of a benchmark lies partly in making these variables inspectable.'),
('From task success to operational value','A deployed system must satisfy latency, cost, privacy, recoverability, access control, and user-experience constraints. These constraints can change the best architecture. Benchmarks should report resource usage alongside success, and include a human baseline when human work is the intended substitute.'),
('Generalization beyond the workflow','Domain expertise can look like generality when test tasks repeat known schemas and conventions. Hold out organizations, schemas, or tool versions while keeping the conceptual goal fixed. Measure graceful uncertainty and clarification behavior. An agent that asks a useful question can be better than one that confidently guesses.')
])
]
for theme_index,(sec, entries) in enumerate(themes):
    for i,(title,txt) in enumerate(entries,1):
        pages.append(P(f'{sec} · {title}',[txt,THEME_DETAIL[theme_index][i-1],THEME_DETAIL_TWO[theme_index][i-1]],
          f'Synthesis note {i} of 4 · based on the cited corpus',
          visual=('taxonomy' if sec.startswith('1') and i==2 else
                  'profile' if sec.startswith('2') and i==2 else
                  'vision' if sec.startswith('3') and i==2 else
                  'loop' if sec.startswith('4') and i==1 else
                  'zpd' if sec.startswith('5') and i==2 else
                  'environment' if sec.startswith('6') and i==1 else
                  'evaluation' if sec.startswith('7') and i==2 else
                  'trace' if sec.startswith('8') and i==1 else
                  'roles' if sec.startswith('9') and i==1 else
                  'data' if sec.startswith('10') and i==1 else None),
          refs='[R01–R20]'))

papers = [
('Measuring Progress Toward AGI: A Cognitive Framework','Google DeepMind · lab research paper · 17 Mar 2026','https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf',
 'The authors organize progress around ten cognitive faculties and propose comparisons with human performance. Its figures depict a capability taxonomy and hypothetical profiles, making explicit that systems can have different strengths rather than one scalar rank. The central contribution is a vocabulary and measurement proposal for discussion of breadth. [R01]',
 'The framework is conceptual and its dimensions do not create a settled AGI threshold. Human-referenced tasks inherit choices about population, expertise, and test conditions. The diagrams should be read as measurement design, not evidence that a given system has general intelligence. Follow-up work should validate reliability and construct coverage for each faculty.'),
('From AGI to ASI','Google DeepMind researchers · lab report / arXiv · 12 Jun 2026','https://arxiv.org/abs/2606.12683',
 'This report surveys possible transitions from AGI toward superintelligence, considering scaling, algorithmic shifts, recursive improvement, and collective systems alongside constraints. Tables and conceptual diagrams distinguish digital advantages from limits; the paper emphasizes that neither “all-knowing” nor “all-powerful” follows from superhuman capability. [R02]',
 'Scenario analysis is not a forecast. Timelines and pathways depend on technical, economic, and institutional assumptions. The useful contribution is to resist a single extrapolation and identify bottlenecks. Readers should separate the report’s possibility space from empirical evidence about current systems.'),
('Visual General Intelligence: A White Paper','Multi-institutional authors · white paper / arXiv · 26 Aug 2026','https://arxiv.org/abs/2608.25924',
 'The white paper argues that visual systems should learn abstractions useful for prediction, counterfactual reasoning, and action, rather than relying only on fixed labels. Its illustrations discuss active perception, world models, and visual learning as a route to broader competence. [R03]',
 'The work outlines an agenda more than a validated recipe. Visual competence does not automatically produce grounded physical understanding, and proposed abstractions need tests across distribution shifts and action consequences. Treat it as a research framework whose claims require controlled comparison with strong multimodal and embodied baselines.'),
('Characterizing Jaggedness Aids Safety & Usability','Google DeepMind research team · position paper / preprint · Jan 2026','https://cs.stanford.edu/~merrie/papers/jaggedness_preprint.pdf',
 'The paper studies uneven performance across tasks and proposes human-referenced normalization and a jaggedness index based on dispersion across standardized capability scores. Its figures contrast capability profiles and show how aggregate performance can obscure local weaknesses. [R04]',
 'A dispersion statistic depends on task selection, normalization, and population. It should complement the profile, not replace it. The paper’s strongest practical point is that users need actionable information about capability gaps. More evidence is needed on whether a given jaggedness measure predicts real-world failure or improves decisions.'),
('General Agent Evaluation','IBM Research and MIT-IBM Watson AI Lab · preprint · 26 Feb 2026','https://arxiv.org/abs/2602.22953',
 'The authors propose a common evaluation protocol and compare combinations of agent architectures, language models, and benchmarks. The design diagram connects tasks, environments, agent implementations, and metrics; results indicate that architecture and model effects vary by setting. [R05]',
 'The experiments are bounded by their selected models, agent implementations, and benchmarks. A factorial design improves comparison but does not establish universal rankings. The paper motivates standardized protocols and error analysis. Replication should broaden environments, include cost-matched baselines, and report run-to-run uncertainty.'),
('Agent-World: Scaling Real-World Environment Synthesis for Evolving General Agent Intelligence','Renmin University of China and ByteDance Seed · preprint · 20 Apr 2026','https://arxiv.org/abs/2604.18292',
 'This work builds diverse simulated tool environments from real-world services and studies how environment scale affects agent training. Diagrams show a pipeline from tool schemas to environments and task trajectories, alongside performance comparisons and scaling trends. [R06]',
 'The reported relationship between environment scale and performance is tied to the authors’ task generation, models, and benchmarks. Simulations enable repeatability but may miss live-system instability. The paper supports environment diversity as a research variable, not a general law that more environments always improve transfer.'),
('Scaling Agents via Continual Pre-training','Alibaba Tongyi Lab · ICLR 2026 peer-reviewed paper','https://openreview.net/forum?id=Dru5mm9anE',
 'The paper introduces AgentFounder, using agentic continual pretraining to cultivate deep-research behavior. Its training diagrams link data synthesis, model training, and downstream evaluation; results compare adaptability and research tasks. The peer-reviewed proceedings year is 2026, while an earlier arXiv version exists. [R07]',
 'Continual pretraining may expose models to broader interaction patterns, but improved benchmark performance does not isolate whether gains come from knowledge, procedure learning, or scaffold effects. Evaluate evidence tracking and transfer to unfamiliar research domains. Keep publication date distinct from the earlier preprint date.'),
('AgentFrontier: Expanding the Capability Frontier of LLM Agents with ZPD-Guided Data Synthesis','Alibaba Tongyi Lab · ICLR 2026 peer-reviewed paper','https://openreview.net/pdf/466f94ec94f21750830c728c1ba0a1097a75a66d.pdf',
 'The authors create an iterative synthesis engine inspired by the zone of proximal development. A tool-using agent refines questions, increases complexity, and filters items according to whether weaker and stronger systems can solve them. The diagrams clarify the pipeline and benchmark evolution. [R08]',
 'Automated difficulty calibration relies on the chosen learner and verifier. Shared blind spots can make a task appear appropriately difficult while missing important competencies. Report verifier validation and external test performance. The paper provides a scalable curriculum method, not proof of open-ended generalization.'),
('AgentSynth: Scalable Task Generation for Generalist Computer-Use Agents','UC Berkeley research team · ICLR 2026 peer-reviewed paper','https://openreview.net/forum?id=CoBxmXThM6',
 'AgentSynth generates computer-use tasks as verified sequences of subtasks, with increasing trajectory length and application variety. The paper’s pipeline diagram shows task proposal, execution, verification, and revision; tables compare human ratings and cost. [R09]',
 'Synthetic task realism, verifier reliability, and UI coverage bound the conclusions. Automated checking can mistake near misses for successes, as the authors’ stress tests illustrate. Human audit and independent tool-state checks are essential. Benchmark progress should be confirmed on tasks not generated by the same pipeline.'),
('Towards General Agentic Intelligence via Environment Scaling','Zhejiang University, Alibaba Tongyi Lab, Peking University · Findings of ACL 2026','https://aclanthology.org/2026.findings-acl.872/',
 'The paper constructs agent environments from tool schemas and stateful database interactions, then evaluates adaptation across domains. Figures explain schema grouping, simulated users, and state changes; results examine tool use in supported settings. [R10]',
 'A schema-based simulation gives controlled feedback but simplifies the failures of live services. Results across selected benchmarks do not establish broad real-world transfer. The contribution is a systematic environment-building method that enables controlled study of diversity and learning.'),
('InfiAgent: An Infinite-Horizon Framework for General-Purpose Autonomous Agents','University of Hong Kong and collaborators · Findings of ACL 2026','https://aclanthology.org/2026.findings-acl.1787/',
 'InfiAgent uses a hierarchical execution stack and file-centric persistent state to support long document-centered research tasks. The architecture diagram distinguishes workspace artifacts from bounded reasoning context; experiments examine coverage and stability over long runs. [R11]',
 'Externalized state can improve continuity but cannot correct weak reasoning or false intermediate claims. The paper itself notes latency, serial execution, and generalization limits. Its long-horizon literature task is informative but narrower than open-ended autonomy. Persistent state should include validation and provenance.'),
('A Survey on Evaluation of LLM-based Agents','IBM Research, Yale University, Hebrew University · Findings of ACL 2026 survey','https://aclanthology.org/2026.findings-acl.1330/',
 'This survey organizes agent evaluation across core capabilities, application-specific tasks, generalist benchmarks, benchmark dimensions, and development frameworks. Its overview diagram maps this landscape; the text highlights static versus dynamic environments and the importance of safety and robustness measures. [R12]',
 'A survey offers breadth rather than a controlled experiment. Benchmark coverage changes quickly, and taxonomies reflect the authors’ inclusion decisions. Its durable value is a comparison vocabulary: data, environment, interface, metric, and safety. Use it as a map, then inspect the primary benchmark papers.'),
('Can Generalist Agents Automate Data Curation?','Virginia Tech, UIUC, UW–Madison, UC Berkeley · EMNLP 2026','https://aclanthology.org/2026.emnlp-main.815/',
 'Curation-Bench evaluates whether coding agents can inspect datasets, propose data-selection policies, run training, and improve a policy from measured results. The diagrams show an agent-controlled loop and trajectory rubric; reported findings separate policy quality from execution. [R13]',
 'A scaffolded loop may measure adaptation to a benchmark’s interface more than independent research judgment. The authors observe local policy tuning and weakly grounded rationales. Further tests should vary datasets and training recipes, audit artifacts, and assess whether a policy’s improvement reproduces.'),
('Can Your Agent Read the Source Faithfully?','Academic and industry team · EMNLP 2026','https://aclanthology.org/2026.emnlp-main.1855/',
 'This benchmark tests whether multimodal agents support answers with retrieved source material. Tasks require reading tables, charts, visual layouts, or dispersed evidence; examples make source-grounding errors concrete. [R14]',
 'Faithfulness depends on retrieval coverage, question formulation, and the scoring rubric. A citation can point to a source without supporting the claim. The benchmark motivates claim-to-evidence alignment and explicit uncertainty when sources do not settle the question. Evaluate source selection as well as final wording.'),
('ARM: Role-Conditioned Neuron Transplantation for Training-Free Generalist LLM Agent Merging','Fudan University / Shanghai Innovation Institute · EMNLP 2026','https://aclanthology.org/2026.emnlp-main.2115/',
 'ARM proposes role-conditioned neuron transplantation to merge specialized agent behaviors without additional training. Its method focuses on selecting and transferring neuron groups conditioned on task role, with comparisons across merged capabilities. [R15]',
 'A merged score can hide interference on skills not emphasized in the target set. Analyze per-domain profiles, calibration, and negative transfer against both specialist and generalist baselines. The technique is a promising integration method; broader held-out evidence is needed before drawing generality conclusions.'),
('OS-Symphony: A Holistic Framework for Robust and Generalist Computer-Using Agents','Academic research team · ACL 2026','https://aclanthology.org/2026.acl-long.1021/',
 'OS-Symphony addresses computer-use agents through orchestration, memory, reflection, and tutorial-like visual traces. Its diagrams contrast memory mechanisms and show how milestone states connect to subsequent actions. The paper evaluates workflow performance and error handling. [R16]',
 'Computer-use performance depends on operating systems, applications, and access permissions. Added components create latency and security concerns; memory can also preserve bad assumptions. Test cross-platform transfer, adversarial UI changes, and write-action containment alongside task success.'),
('Role-Agent: Bootstrapping LLM Agents via Dual-Role Evolution','USTC and Alibaba AMAP · Findings of EMNLP 2026','https://aclanthology.org/2026.findings-emnlp.208/',
 'Role-Agent evolves both an acting agent and an environment model, using closed-loop interaction to generate training experiences. The paper’s diagrams show state prediction and environment response; experiments investigate how role interaction affects agent improvement. [R17]',
 'Self-generated environments can reinforce shared errors between simulator and agent. Independent evaluation and external tasks are necessary to establish transfer. The method’s contribution is a training framework for interaction, while environment fidelity remains an important boundary.'),
('AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows','ServiceNow AI Research · AACL 2026','https://aclanthology.org/2026.aacl-long.44/',
 'AgentArch studies architecture choices across enterprise workflows, where tasks involve dependencies, tools, and partial outcomes. Its benchmark compares combinations of models and system designs, making architecture an experimental variable. [R18]',
 'Architecture rankings depend on workflow sample, model, and budget. Enterprise task success can conceal brittle permission handling or weak recovery. Report the full interface and cost assumptions, and replicate across organizations or workflow families before generalizing.'),
('Process Evaluation for Agentic Systems','Huawei Noah’s Ark Lab and University College London · Findings of EACL 2026','https://aclanthology.org/2026.findings-eacl.140/',
 'This position paper argues that agent evaluation should inspect intermediate behavior as well as final answers. Its scenarios illustrate how a correct conclusion can arise from unsupported shortcuts or risky steps; the paper proposes process-oriented evaluation concepts. [R19]',
 'Process evaluation is only useful when the rubric captures relevant harms and can be applied consistently. More process data also raises logging and privacy questions. Treat the framework as a research agenda and test whether its labels predict real-world risk better than outcome-only scores.'),
('Can AI Agents Answer Your Data Questions? A Benchmark for Data Agents','UC Berkeley and industry collaborators · EMNLP 2026','https://aclanthology.org/2026.emnlp-main.1872/',
 'This benchmark evaluates agents answering questions over structured data. The task pipeline requires schema interpretation, query creation, execution, and explanation; retaining intermediate queries helps locate the source of mistakes. [R20]',
 'Database and schema choices shape performance, and answer fluency can hide a wrong query. Strong evaluations need held-out schemas, execution traces, access-control constraints, and uncertainty tests. Success on data questions measures a valuable domain capability, not general intelligence by itself.')
]
for i, rec in enumerate(papers,1):
    title,meta,url,claim,limit=rec
    pages.append(P(f'RESEARCH PROFILE {i:02d} · {title}',
        [claim, PAPER_DETAIL[i-1][0], f'Publication record: {meta}. Official source: {url}. The profile records the paper’s central design and its visual or experimental evidence as represented in the supplied PDF.'],
        f'Contribution and evidence · source key [R{i:02d}]',
        visual=('profile' if i in (1,4,5,11,12,16,19) else None), refs=f'[R{i:02d}]',kind='profile'))
    pages.append(P(f'RESEARCH PROFILE {i:02d} · INTERPRETATION',
        [limit, PAPER_DETAIL[i-1][1], f'Connection to the synthesis: this paper contributes one part of a larger research program. Its results should be compared with studies that vary the model, scaffold, task distribution, and environment independently. Keep this boundary visible when using the work to support a broader AGI claim.'],
        f'Limitations and research use · source key [R{i:02d}]',
        visual=('trace' if i in (9,13,14,16,19,20) else None),refs=f'[R{i:02d}]',kind='profile'))

# 87-95: technical annex
annex = [
P('ANNEX A · REFERENCE ARCHITECTURE','A research agent can be described as a set of inspectable components: task interpreter, world model, planner, tool adapter, state store, verifier, and policy monitor. Each component should have a documented input, output, and failure response. A trace must link a claim or action to observations and tool results.','Proposed design, synthesized from [R05,R11,R16,R18]','loop','[R05,R11,R16,R18]'),
P('ANNEX B · EVALUATION MATRIX','Evaluate breadth across task families, transfer across held-out compositions, autonomy across longer horizons, and reliability under perturbation. Cross these dimensions with environment types (static, dynamic, simulated, live) and interface types (text, visual, API, embodied). The matrix is a sampling plan, not a complete measure of intelligence.','A practical benchmark design','evaluation','[R05,R10,R12]'),
P('ANNEX C · METRIC DEFINITIONS','Task success: proportion meeting a preregistered goal rubric. Constraint compliance: proportion with no prohibited action. Transfer gap: held-out score minus matched in-distribution score. Recovery rate: proportion of introduced recoverable faults after which the system completes correctly. Run variance: dispersion across independent trials. Always define denominators, stopping rules, and adjudication.','Report units and baselines with every metric.','profile','[R04,R05,R12,R19]'),
P('ANNEX D · TRACE AND PROCESS RECORD','For each episode preserve task version, model identifier, prompt and scaffold version, tool schema, observation stream, action calls, return values, state changes, verifier decisions, retries, elapsed time, token or compute use, and final outcome. Redact sensitive content before release. A trace enables error analysis but does not prove internal reasoning.','Minimum research record for agent experiments.','trace','[R11,R13,R16,R19]'),
P('ANNEX E · FAILURE TAXONOMY','Classify failures by locus: perception, retrieval, task interpretation, planning, tool selection, execution, state tracking, verification, policy compliance, communication, or termination. Also mark severity, detectability, recoverability, and whether the evaluator caused or masked the failure. Multiple labels may apply to one trajectory.','Taxonomy proposed by this review.','loop','[R05,R14,R16,R19,R20]'),
P('ANNEX F · RESEARCH ROADMAP','Near-term work should validate measurement constructs and verifiers; medium-term work should test transfer under controlled shifts in environment and budget; long-term work should evaluate continual adaptation, embodied interaction, social settings, and safe autonomy with independent monitoring. Each stage needs preregistered claims and open evaluation artifacts.','Priorities inferred from the gaps in [R01–R20].','environment','[R01–R20]'),
P('ANNEX G · SAFETY AND GOVERNANCE QUESTIONS','Who can authorize an external action? Which operations are reversible? What state or source data is retained? How does the system disclose uncertainty? Which failures trigger escalation? How are updates audited? These questions connect system architecture to user impact. They should be answered in the experiment protocol, not inferred from benchmark score.','Deployment questions for controlled studies.','trace','[R16,R19,R20,A1,A2]'),
P('ANNEX H · GLOSSARY I','Agent: a system that selects actions in an environment. Benchmark: a defined task sample and scoring procedure. Calibration: agreement between stated confidence and observed correctness. Capability profile: a vector of performance across named dimensions. Environment: the task context and its state transitions. Generality: breadth and transfer under stated constraints.','Working definitions used in this review.','taxonomy','[R01,R04,R12]'),
P('ANNEX I · GLOSSARY II','Jaggedness: uneven capability across tasks or dimensions. Long horizon: task execution requiring persistent state over many steps. Process evaluation: assessment of intermediate actions as well as outcomes. Provenance: traceable origin of evidence. Scaffold: tools, prompts, memory, and control code around a model. Transfer: performance on a changed or held-out task distribution.','Terms complement, rather than replace, the definitions in each paper.','map','[R04,R11,R19]')
]
for j, entry in enumerate(annex):
    entry['body'].append(ANNEX_DETAIL[j])
pages += annex

# 96-100: bibliography and source notes
refs = [
('[R01] Measuring Progress Toward AGI: A Cognitive Framework','Google DeepMind research paper, 17 Mar 2026. https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf'),
('[R02] From AGI to ASI','Google DeepMind researchers. arXiv:2606.12683, 2026. https://arxiv.org/abs/2606.12683'),
('[R03] Visual General Intelligence: A White Paper','arXiv:2608.25924, 2026. https://arxiv.org/abs/2608.25924'),
('[R04] Characterizing Jaggedness Aids Safety & Usability','Google-hosted author copy, Jan 2026. https://cs.stanford.edu/~merrie/papers/jaggedness_preprint.pdf'),
('[R05] General Agent Evaluation','IBM Research / MIT-IBM, arXiv:2602.22953, 2026. https://arxiv.org/abs/2602.22953'),
('[R06] Agent-World: Scaling Real-World Environment Synthesis','Renmin University / ByteDance Seed, arXiv:2604.18292, 2026. https://arxiv.org/abs/2604.18292'),
('[R07] Scaling Agents via Continual Pre-training','ICLR 2026 / OpenReview. https://openreview.net/forum?id=Dru5mm9anE'),
('[R08] AgentFrontier: ZPD-Guided Data Synthesis','ICLR 2026 / OpenReview. https://openreview.net/pdf/466f94ec94f21750830c728c1ba0a1097a75a66d.pdf'),
('[R09] AgentSynth: Scalable Task Generation for Computer-Use Agents','ICLR 2026 / OpenReview. https://openreview.net/forum?id=CoBxmXThM6'),
('[R10] Towards General Agentic Intelligence via Environment Scaling','Findings of ACL 2026. https://aclanthology.org/2026.findings-acl.872/'),
('[R11] InfiAgent: An Infinite-Horizon Framework','Findings of ACL 2026. https://aclanthology.org/2026.findings-acl.1787/'),
('[R12] A Survey on Evaluation of LLM-based Agents','Findings of ACL 2026. https://aclanthology.org/2026.findings-acl.1330/'),
('[R13] Can Generalist Agents Automate Data Curation?','EMNLP 2026. https://aclanthology.org/2026.emnlp-main.815/'),
('[R14] Can Your Agent Read the Source Faithfully?','EMNLP 2026. https://aclanthology.org/2026.emnlp-main.1855/'),
('[R15] ARM: Role-Conditioned Neuron Transplantation','EMNLP 2026. https://aclanthology.org/2026.emnlp-main.2115/'),
('[R16] OS-Symphony: A Holistic Framework for Computer-Using Agents','ACL 2026. https://aclanthology.org/2026.acl-long.1021/'),
('[R17] Role-Agent: Bootstrapping LLM Agents via Dual-Role Evolution','Findings of EMNLP 2026. https://aclanthology.org/2026.findings-emnlp.208/'),
('[R18] AgentArch: A Benchmark for Agent Architectures','AACL 2026. https://aclanthology.org/2026.aacl-long.44/'),
('[R19] Process Evaluation for Agentic Systems','Findings of EACL 2026. https://aclanthology.org/2026.findings-eacl.140/'),
('[R20] Can AI Agents Answer Your Data Questions?','EMNLP 2026. https://aclanthology.org/2026.emnlp-main.1872/'),
('[A1] International AI Safety Report 2026','Independent international scientific report chaired by Yoshua Bengio. https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026'),
('[A2] International AI Safety Report 2026 · full report PDF','https://internationalaisafetyreport.org/sites/default/files/2026-02/international-ai-safety-report-2026.pdf'),
('[A3] Stanford HAI · 2026 AI Index Report','https://hai.stanford.edu/ai-index/2026-ai-index-report'),
('[A4] United Nations Independent International Scientific Panel on AI · preliminary report','https://www.un.org/independent-international-scientific-panel-ai/en/preliminary-report')
]
for i in range(0,len(refs),6):
    chunk=refs[i:i+6]
    pages.append(P('BIBLIOGRAPHY · '+('RESEARCH CORPUS' if i==0 else f'CONTINUED {i//5}'),
       [f'{k}. {v}' for k,v in chunk],
       'Official or primary publication links · accessed 20 November 2026',
       'map' if i==0 else None,'[R01–R20,A1–A4]'))
pages.append(P('SOURCE STATUS AND ACKNOWLEDGMENT',
 ['The paper index distinguishes peer-reviewed conference proceedings, institutional reports, position papers, surveys, and preprints. A conference publication date may be later than an earlier arXiv preprint. Authors, affiliations, venue, and date should be checked against the publisher record before formal citation in a thesis or submission.',
  'This resource paper draws on the twenty PDFs supplied in the local papers folder, the official links listed above, and the three external reference groups. The author wrote the synthesis and diagrams for this review. Dr. Vidya Mohanty is named as the intended academic reader only; no contribution or endorsement is implied.',
  'Suggested next revision: verify every reference against publisher metadata, replace broad corpus-level conclusions with a preregistered systematic search, record page-level citations for any claim intended for publication, and invite subject-matter review before formal academic submission.'],
 'Editorial and provenance note · 20 November 2026','map','[R01–R20,A1–A4]'))
# Check page count before output: exact 100 pages
assert len(pages)==100, f'Expected 100 pages; found {len(pages)}'

# Visual primitives: original conceptual schematics, no empirical values
def draw_visual(c, name, x, y, w=500, h=130):
    c.saveState()
    c.setFillColor(PALE); c.roundRect(x,y,w,h,10,stroke=0,fill=1)
    c.setStrokeColor(colors.HexColor('#A8BEC7')); c.setLineWidth(1)
    def box(bx,by,bw,bh,label,fill=colors.white,fs=8):
        c.setFillColor(fill); c.roundRect(bx,by,bw,bh,6,stroke=1,fill=1)
        c.setFillColor(INK); c.setFont('Helvetica-Bold',fs)
        lines=label.split('|')
        for j,line in enumerate(lines):
            c.drawCentredString(bx+bw/2,by+bh/2+(len(lines)-1-2*j)*5-3,line[:45])
    def arrow(x1,y1,x2,y2):
        c.setStrokeColor(TEAL); c.setFillColor(TEAL); c.setLineWidth(1.4)
        c.line(x1,y1,x2,y2)
        import math
        a=math.atan2(y2-y1,x2-x1)
        p=c.beginPath(); p.moveTo(x2,y2); p.lineTo(x2-6*math.cos(a-.45),y2-6*math.sin(a-.45)); p.lineTo(x2-6*math.cos(a+.45),y2-6*math.sin(a+.45)); p.close()
        c.drawPath(p,stroke=0,fill=1)
    if name in ('cover','map','taxonomy'):
        labels=['Perception','Learning','Memory','Reasoning','Planning','Action','Social inference','Metacognition']
        cx=x+w/2; cy=y+h/2
        import math
        for i,l in enumerate(labels):
            angle=2*math.pi*i/len(labels)-math.pi/2
            bx=cx+175*math.cos(angle)-42; by=cy+42*math.sin(angle)-10
            box(bx,by,84,20,l,colors.white,7)
        c.setFillColor(TEAL); c.circle(cx,cy,25,stroke=0,fill=1)
        c.setFillColor(colors.white); c.setFont('Helvetica-Bold',8); c.drawCentredString(cx,cy-3,'GENERALITY')
        c.setStrokeColor(TEAL); c.setDash(2,2)
        for i in range(8):
            a=2*math.pi*i/8-math.pi/2; c.line(cx+27*math.cos(a),cy+27*math.sin(a),cx+132*math.cos(a),cy+32*math.sin(a))
    elif name in ('loop','trace'):
        labs=['Observe','Represent|state','Plan','Act via|tool','Verify','Update|memory']
        bw=66; gap=14; sx=x+25; yy=y+58
        for i,l in enumerate(labs):
            bx=sx+i*(bw+gap); box(bx,yy,bw,30,l,colors.white,7)
            if i<len(labs)-1: arrow(bx+bw,yy+15,bx+bw+gap-2,yy+15)
        c.setFont('Helvetica-Oblique',7); c.setFillColor(MUTED)
        c.drawCentredString(x+w/2,y+20,'The trace links each action to an observation and a checkable state change.')
        c.setStrokeColor(TEAL); c.arc(x+42,y+27,x+w-42,y+103,0,180)
    elif name in ('profile','radar'):
        labels=['Breadth','Transfer','Learning','Autonomy','Reliability']
        bx=x+28
        for i,l in enumerate(labels):
            yy=y+95-i*18
            c.setFont('Helvetica',8); c.setFillColor(INK); c.drawString(bx,yy,l)
            c.setFillColor(colors.HexColor('#CFDCE0')); c.roundRect(bx+80,yy-3,260,9,4,stroke=0,fill=1)
            c.setFillColor(TEAL); c.roundRect(bx+80,yy-3,[190,115,220,90,165][i],9,4,stroke=0,fill=1)
        c.setFont('Helvetica-Oblique',7); c.setFillColor(MUTED); c.drawString(x+365,y+50,'Schematic profile;')
        c.drawString(x+365,y+38,'no measured scores.')
    elif name in ('vision',):
        labs=['Image / video','Attention','World model','Prediction','Action']
        bw=80; gap=18; yy=y+52; sx=x+15
        for i,l in enumerate(labs):
            bx=sx+i*(bw+gap); box(bx,yy,bw,32,l,colors.white,7)
            if i<len(labs)-1: arrow(bx+bw,yy+16,bx+bw+gap-2,yy+16)
        c.setFont('Helvetica-Oblique',7); c.setFillColor(MUTED); c.drawCentredString(x+w/2,y+22,'Perception is active: the agent chooses what evidence to gather.')
    elif name in ('zpd',):
        box(x+25,y+42,110,45,'Task pool',colors.white)
        box(x+195,y+42,110,45,'Difficulty|calibration',colors.white)
        box(x+365,y+42,110,45,'Learner|feedback',colors.white)
        arrow(x+135,y+64,x+193,y+64); arrow(x+305,y+64,x+363,y+64)
        arrow(x+415,y+38,x+80,y+30)
        c.setFont('Helvetica-Oblique',7); c.setFillColor(MUTED); c.drawCentredString(x+w/2,y+13,'Verifier quality and external transfer bound the inference.')
    elif name in ('environment',):
        box(x+20,y+45,105,45,'Tool schema',colors.white)
        box(x+180,y+45,130,45,'Stateful|environment',colors.white)
        box(x+365,y+45,110,45,'Task|trajectory',colors.white)
        arrow(x+125,y+68,x+178,y+68); arrow(x+310,y+68,x+363,y+68)
        c.setFont('Helvetica-Oblique',7); c.setFillColor(MUTED); c.drawCentredString(x+w/2,y+20,'Vary domains, state transitions, horizons, and failure conditions.')
    elif name in ('evaluation',):
        labs=['Task family','Environment','Interface','Metric','Safety']
        for i,l in enumerate(labs):
            xx=x+20+i*95
            box(xx,y+62,82,24,l,colors.white,7)
            for j in range(2):
                c.setStrokeColor(colors.HexColor('#B7C8CD')); c.line(xx+5,y+53-j*13,xx+77,y+53-j*13)
        c.setFont('Helvetica-Oblique',7); c.setFillColor(MUTED); c.drawCentredString(x+w/2,y+16,'A benchmark is the full measurement design, not only the task name.')
    elif name in ('roles',):
        box(x+45,y+57,100,35,'Specialist A',colors.white)
        box(x+200,y+57,100,35,'Coordinator',colors.white)
        box(x+355,y+57,100,35,'Specialist B',colors.white)
        arrow(x+145,y+74,x+198,y+74); arrow(x+355,y+74,x+302,y+74)
        arrow(x+250,y+54,x+100,y+37); arrow(x+250,y+54,x+405,y+37)
        c.setFont('Helvetica-Oblique',7); c.setFillColor(MUTED); c.drawCentredString(x+w/2,y+15,'Measure coordination cost and negative transfer as well as gains.')
    elif name=='data':
        labs=['Inspect','Propose|policy','Train','Evaluate','Revise']
        bw=75; gap=19; sx=x+23; yy=y+52
        for i,l in enumerate(labs):
            bx=sx+i*(bw+gap); box(bx,yy,bw,34,l,colors.white,7)
            if i<4: arrow(bx+bw,yy+17,bx+bw+gap-2,yy+17)
        c.setFont('Helvetica-Oblique',7); c.setFillColor(MUTED); c.drawCentredString(x+w/2,y+19,'Keep datasets, recipes, evaluation code, and logs auditable.')
    else:
        labs=['Claim','Evidence','Check','Limit']
        for i,l in enumerate(labs):
            bx=x+35+i*115; box(bx,y+50,90,34,l,colors.white,8)
            if i<3: arrow(bx+90,y+67,bx+113,y+67)
    c.restoreState()

# PDF with controlled one-page-per-entry layout.
pdf_path=OUT/'AGI_Research_Review_2026.pdf'
c=canvas.Canvas(str(pdf_path),pagesize=letter)
c.setTitle('General Intelligence as a Research Program: AGI Research Review 2026')
c.setAuthor('Rashmi Ranjan Behera')
c.setSubject('Independent synthesis of twenty recent papers on AGI, agents, evaluation, and reliability')
W,H=letter
for idx,p in enumerate(pages,1):
    c.setFillColor(colors.white); c.rect(0,0,W,H,stroke=0,fill=1)
    c.setFillColor(NAVY); c.rect(0,H-13,W,13,stroke=0,fill=1)
    c.setFont('Helvetica-Bold',7); c.setFillColor(MUTED)
    c.drawString(52,H-31,'AGI RESEARCH REVIEW · 2026')
    c.drawRightString(W-52,H-31,'RASHMI RANJAN BEHERA')
    title_style=ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=16,leading=19,textColor=NAVY,spaceAfter=4)
    sub_style=ParagraphStyle('sub',fontName='Helvetica-Oblique',fontSize=8.5,leading=11,textColor=TEAL,spaceAfter=6)
    body_style=ParagraphStyle('body',fontName='Helvetica',fontSize=9.1,leading=13.0,textColor=INK,spaceAfter=9,alignment=TA_LEFT)
    small_style=ParagraphStyle('small',fontName='Helvetica',fontSize=8.2,leading=11,textColor=INK,spaceAfter=6)
    x=54; width=W-108; y=H-52
    title=p['title']
    par=Paragraph(title.replace('&','&amp;'),title_style)
    tw,th=par.wrap(width,120); par.drawOn(c,x,y-th); y-=th+6
    if p['sub']:
        par=Paragraph(p['sub'].replace('&','&amp;'),sub_style)
        tw,th=par.wrap(width,60); par.drawOn(c,x,y-th); y-=th+4
    c.setStrokeColor(TEAL); c.setLineWidth(1.2); c.line(x,y,x+width,y); y-=12
    if p['visual']:
        draw_visual(c,p['visual'],x,y-132,width,130); y-=148
    body_start=y
    # adapt to available page height by reducing font on dense bibliography pages
    para_objs=[]
    for txt in p['body']:
        if '\n' in txt and p['title'].startswith('GENERAL INTELLIGENCE'):
            txt=txt.replace('\n','<br/>')
        txt=txt.replace('&','&amp;')
        sty=body_style
        if p['title'].startswith('BIBLIOGRAPHY'):
            sty=small_style
        para_objs.append((txt,sty))
    def measure(font_adj=0):
        total=0; built=[]
        for txt,sty in para_objs:
            s=ParagraphStyle('tmp',parent=sty,fontSize=max(7.2,sty.fontSize-font_adj),leading=max(9.3,sty.leading-font_adj))
            obj=Paragraph(txt,s); _,hh=obj.wrap(width,600); total+=hh+s.spaceAfter; built.append((obj,hh,s.spaceAfter))
        return total,built
    avail=body_start-58
    total,built=measure()
    adj=0
    while total>avail and adj<2:
        adj+=.7; total,built=measure(adj)
    yy=body_start
    for obj,hh,space in built:
        obj.drawOn(c,x,yy-hh); yy-=hh+space
    if p['refs']:
        c.setFillColor(MUTED); c.setFont('Helvetica-Oblique',7)
        c.drawString(x,48,'Sources: '+p['refs'])
    c.setStrokeColor(colors.HexColor('#D3DDE1')); c.line(x,42,W-x,42)
    c.setFillColor(MUTED); c.setFont('Helvetica',7)
    c.drawString(x,29,'Independent literature synthesis · Version 1 · 20 November 2026')
    c.drawRightString(W-x,29,f'{idx:03d} / 100')
    c.showPage()
c.save()

# Editable Word manuscript with the same 100-page sequence.
doc=Document()
doc.core_properties.title='General Intelligence as a Research Program: AGI Research Review 2026'
doc.core_properties.author='Rashmi Ranjan Behera'
doc.core_properties.subject='Independent literature synthesis of twenty recent papers'
sec=doc.sections[0]
sec.top_margin=Inches(.62); sec.bottom_margin=Inches(.58); sec.left_margin=Inches(.72); sec.right_margin=Inches(.72)
styles=doc.styles
styles['Normal'].font.name='Calibri'; styles['Normal'].font.size=Pt(9)
styles['Normal'].font.color.rgb=RGBColor(35,48,68)
styles['Normal'].paragraph_format.space_after=Pt(6)
styles['Normal'].paragraph_format.line_spacing=1.03
styles['Heading 1'].font.name='Calibri'; styles['Heading 1'].font.size=Pt(17); styles['Heading 1'].font.bold=True; styles['Heading 1'].font.color.rgb=RGBColor(18,37,63)
styles['Heading 2'].font.name='Calibri'; styles['Heading 2'].font.size=Pt(9); styles['Heading 2'].font.italic=True; styles['Heading 2'].font.color.rgb=RGBColor(8,126,139)
for idx,p in enumerate(pages,1):
    if idx>1: doc.add_page_break()
    h=doc.add_paragraph(style='Heading 1'); h.paragraph_format.space_after=Pt(3); h.add_run(p['title'])
    if p['sub']:
        q=doc.add_paragraph(style='Heading 2'); q.paragraph_format.space_after=Pt(7); q.add_run(p['sub'])
    for bi,txt in enumerate(p['body']):
        para=doc.add_paragraph()
        para.paragraph_format.keep_together=True
        if '\n' in txt and p['title'].startswith('GENERAL INTELLIGENCE'):
            for j,line in enumerate(txt.split('\n')):
                if j: para.add_run().add_break()
                para.add_run(line)
        else: para.add_run(txt)
    if p['refs']:
        q=doc.add_paragraph(); q.paragraph_format.space_before=Pt(5)
        r=q.add_run('Sources: '+p['refs']); r.italic=True; r.font.size=Pt(7); r.font.color.rgb=RGBColor(91,104,120)
docx_path=OUT/'AGI_Research_Review_2026.docx'
doc.save(docx_path)

# 20-slide PowerPoint deck. Native editable text, tables, and diagrams.
prs=Presentation(); prs.slide_width=PInches(13.333); prs.slide_height=PInches(7.5)
prs.core_properties.author='Rashmi Ranjan Behera'
prs.core_properties.title='General Intelligence as a Research Program'
blank=prs.slide_layouts[6]
DARK=PRGB(18,37,63); TEALP=PRGB(8,126,139); GOLDP=PRGB(201,154,59); WHITE=PRGB(255,255,255); PALEP=PRGB(234,241,243); TEXT=PRGB(35,48,68); GREY=PRGB(91,104,120)
def add_text(slide, text, x,y,w,h,size=18,color=TEXT,bold=False,font='Aptos',align=None):
    tb=slide.shapes.add_textbox(PInches(x),PInches(y),PInches(w),PInches(h))
    tf=tb.text_frame; tf.clear(); tf.word_wrap=True
    for i,line in enumerate(text.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=line; p.font.name=font; p.font.size=PPt(size); p.font.bold=bold; p.font.color.rgb=color
        if align is not None: p.alignment=align
    return tb
def add_bg(slide, cover=False):
    fill=slide.background.fill; fill.solid(); fill.fore_color.rgb=DARK if cover else WHITE
    if not cover:
        sh=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width,PInches(.12)); sh.fill.solid(); sh.fill.fore_color.rgb=TEALP; sh.line.fill.background()
def add_title(slide, title, n):
    add_text(slide,title,.62,.42,12.0,.7,30,DARK,True)
    add_text(slide,f'AGI RESEARCH REVIEW  ·  {n:02d}',10.55,.14,2.2,.22,8,GREY,True,align=PP_ALIGN.RIGHT)
    line=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,PInches(.62),PInches(1.23),PInches(12.0),PInches(.015))
    line.fill.solid(); line.fill.fore_color.rgb=TEALP; line.line.fill.background()
def add_bullets(slide, items, x=.8,y=1.55,w=5.6,h=4.9,size=18):
    tb=slide.shapes.add_textbox(PInches(x),PInches(y),PInches(w),PInches(h)); tf=tb.text_frame; tf.clear(); tf.word_wrap=True
    for i,item in enumerate(items):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.text=item; p.level=0; p.font.name='Aptos'; p.font.size=PPt(size); p.font.color.rgb=TEXT; p.space_after=PPt(15)
def shape_box(slide,x,y,w,h,label,fill=PALEP,size=15):
    s=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,PInches(x),PInches(y),PInches(w),PInches(h))
    s.fill.solid(); s.fill.fore_color.rgb=fill; s.line.color.rgb=TEALP
    tf=s.text_frame; tf.clear(); tf.vertical_anchor=1
    for i,line in enumerate(label.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.text=line; p.alignment=PP_ALIGN.CENTER; p.font.name='Aptos'; p.font.size=PPt(size); p.font.bold=True; p.font.color.rgb=DARK
    return s
def connect(slide,a,b):
    x1=a.left+a.width; y1=a.top+a.height/2; x2=b.left; y2=b.top+b.height/2
    csh=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,x1,y1,x2,y2)
    csh.line.color.rgb=TEALP; csh.line.width=PPt(2)
    csh.line.end_arrowhead=True
def new_slide(title,items,visual=None,source=''):
    s=prs.slides.add_slide(blank); add_bg(s); add_title(s,title,len(prs.slides))
    add_bullets(s,items,.75,1.55,5.65,4.95,17)
    if visual:
        boxes=[]
        labels=visual
        for i,lab in enumerate(labels):
            boxes.append(shape_box(s,7.02+i*1.14,3.05,1.0,1.25,lab,PALEP,12))
        for a,b in zip(boxes[:-1],boxes[1:]): connect(s,a,b)
    if source: add_text(s,'Sources: '+source,.75,6.95,11.8,.22,8,GREY)
    return s
# cover
s=prs.slides.add_slide(blank); add_bg(s,True)
add_text(s,'GENERAL INTELLIGENCE\nAS A RESEARCH PROGRAM',.8,1.1,11.8,1.5,34,WHITE,True)
add_text(s,'A critical synthesis of 20 recent papers',.84,3.0,10,.5,22,PRGB(180,220,224))
add_text(s,'Cognition · agents · environments · evaluation · reliability',.84,3.65,11,.4,16,WHITE)
add_text(s,'Rashmi Ranjan Behera\nPrepared for Dr. Vidya Mohanty\nLiterature review · 20 November 2026',.84,5.65,6.8,.85,14,WHITE)
add_text(s,'Independent synthesis; no co-authorship or endorsement is implied.',7.35,6.82,5.0,.3,9,PRGB(190,204,213),align=PP_ALIGN.RIGHT)
slide_data=[
('The question behind “AGI”',['Define tasks, environments, horizons, and constraints.','Treat generality as a testable research program.','This corpus does not demonstrate achieved AGI.'],['Breadth','Transfer','Adaptation','Reliability','Evidence'],'[R01–R05]'),
('A capability profile',['Averages conceal weak dimensions.','Publish component scores and uncertainty.','Human comparisons need explicit task and population choices.'],['Perception','Learning','Memory','Reasoning','Planning'],'[R01,R04]'),
('Why capability looks jagged',['Strong performance can coexist with simple failures.','Use profiles, tail outcomes, and task-level diagnostics.','Treat a summary index as a supplement.'],None,'[R04]'),
('Visual intelligence',['Perception supports prediction and action.','Active sensing is part of agent behavior.','Ground claims in the source actually inspected.'],['Observe','Attend','Model','Predict','Act'],'[R03,R14]'),
('An agent is a system',['Model, scaffold, memory, tools, and environment jointly shape outcomes.','Compare systems under matched budgets.','Show the complete execution trace.'],['Observe','Represent','Plan','Use tool','Verify'],'[R05,R11,R16]'),
('Persistent state',['Long context and durable state solve different problems.','External files help long runs but can preserve errors.','Validate provenance and state transitions.'],['Task','Working state','Artifact','Audit','Resume'],'[R11,R16]'),
('Training frontier tasks',['Calibrated difficulty can focus learning.','Synthetic tasks need independent verification.','Transfer beyond the generator is decisive.'],['Seed','Refine','Verify','Train','Test'],'[R08,R09]'),
('Environment scaling',['Diversity should be measured by task structure, not count alone.','Simulations aid control; live tools add friction.','Hold out domains and interfaces.'],['Schemas','Domains','Tasks','Trajectories','Transfer'],'[R06,R10]'),
('Agent evaluation map',['Specify data, environment, interface, metric, and safety.','Combine component and end-to-end tests.','Keep model and scaffold versions visible.'],['Data','Environment','Interface','Metric','Safety'],'[R05,R12]'),
('Process matters',['Correct answers can arise from unsafe or unsupported actions.','Score traces against explicit constraints.','Contain write actions and report permissions.'],['Intent','Evidence','Action','Check','Outcome'],'[R14,R16,R19]'),
('Reliability and uncertainty',['Repeat independent runs.','Report variance, recovery, and failure severity.','One successful trajectory is weak evidence.'],None,'[R04,R05,R09]'),
('Specialists and coordination',['Roles may help divide work.','Measure communication overhead and interference.','Test integration on held-out task combinations.'],['Specialist A','Coordinator','Specialist B','Shared state','Audit'],'[R15,R17]'),
('Domain agents',['Data agents combine schema understanding, querying, and explanation.','Retain executable traces.','Fluency does not guarantee a correct result.'],['Schema','Query','Execute','Interpret','Explain'],'[R18,R20]'),
('What counts as transfer?',['Hold out task compositions or environments.','Measure adaptation data and recovery.','Report positive and negative transfer.'],['Train tasks','Shift','Adapt','Repeat','Measure'],'[R06,R10,R12]'),
('A stronger experimental protocol',['Predefine claims and baselines.','Match tool, token, and time budgets.','Audit scoring with humans and independent checks.'],['Specify','Sample','Run','Inspect','Replicate'],'[R05,R09,R12]'),
('Research profile · cognition',['[R01] organizes ten faculties.','[R04] quantifies unevenness.','The constructs need validation against real decisions.'],None,'[R01,R04]'),
('Research profile · agents',['[R05] studies evaluation combinations.','[R11] externalizes state for long tasks.','[R18] examines enterprise architecture choices.'],None,'[R05,R11,R18]'),
('Research profile · learning',['[R07] studies agentic continual pretraining.','[R08] calibrates synthesized tasks.','[R13] tests automated data curation.'],None,'[R07,R08,R13]'),
('Research profile · safeguards',['[R14] tests source faithfulness.','[R19] argues for process evaluation.','[R20] retains data-query behavior.'],None,'[R14,R19,R20]'),
('Research agenda',['Validate constructs and verifiers.','Test transfer under controlled shifts.','Publish reproducible traces and cost.','Treat the AGI label as a conclusion requiring evidence.'],None,'[R01–R20]')
]
for item in slide_data: new_slide(*item)
pptx_path=OUT/'AGI_Research_Review_2026.pptx'; prs.save(pptx_path)

# Machine-readable content source
(OUT/'report_content.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(pages),'pdf':str(pdf_path),'docx':str(docx_path),'pptx':str(pptx_path)}))
