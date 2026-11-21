from __future__ import annotations

import html
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    NextPageTemplate, Image, KeepTogether, CondPageBreak, Table, TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
FIGDIR = OUT / "figures"
PAPERS = ROOT / "papers"
OUT.mkdir(exist_ok=True)
FIGDIR.mkdir(exist_ok=True)
TARGET = OUT / "AGI_Research_Review_2026.pdf"
FIRST_AUTHOR = "Rashmi Ranjan Behera"
SECOND_AUTHOR = "Dr. Vidya Mohanty"
AUTHORS = f"{FIRST_AUTHOR} and {SECOND_AUTHOR}"

INK = colors.HexColor("#171C22")
BLUE = colors.HexColor("#183F7A")
TEAL = colors.HexColor("#1C7884")
MUTED = colors.HexColor("#566270")
RULE = colors.HexColor("#7B8792")
PALE = colors.HexColor("#EEF3F7")
PALETEAL = colors.HexColor("#EDF5F5")

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
pdfmetrics.registerFont(TTFont("TNR", str(FONT_DIR / "Times New Roman.ttf")))
pdfmetrics.registerFont(TTFont("TNR-Bold", str(FONT_DIR / "Times New Roman Bold.ttf")))
pdfmetrics.registerFont(TTFont("TNR-Italic", str(FONT_DIR / "Times New Roman Italic.ttf")))
pdfmetrics.registerFont(TTFont("TNR-BoldItalic", str(FONT_DIR / "Times New Roman Bold Italic.ttf")))
pdfmetrics.registerFontFamily("TNR", normal="TNR", bold="TNR-Bold", italic="TNR-Italic", boldItalic="TNR-BoldItalic")


# This review paraphrases source claims. Figures reproduced from the ACL
# Anthology are separately attributed; other diagrams are original schematics.
SOURCES = [
    dict(n=1, key="R01", title="Measuring Progress Toward AGI: A Cognitive Framework",
         authors="Ryan Burnell et al.", org="Google DeepMind", year="2026", status="lab research paper",
         date="16 March 2026", url="https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf",
         question="The paper starts from a measurement problem: “AGI” is used for systems with very different capability profiles, so a milestone claim cannot be compared or governed without first saying what counts as generality. Its authors use human cognition as a practical reference frame and propose ten faculties grouped in a cognitive taxonomy.",
         method="The proposed protocol samples targeted tasks for the named faculties, uses held-out tasks to reduce direct benchmark familiarity, and reports a cognitive profile rather than a single score. The paper discusses task design, human comparison, difficulty, and aggregation. The profile is meant to make both strong areas and gaps visible. The taxonomy draws on psychology, neuroscience, and cognitive science; it is a measurement scaffold, not a complete computational theory of intelligence.",
         evidence="The central contribution is conceptual and methodological. Its diagrams make the taxonomy and possible profile comparisons legible, but they do not show that a particular model has crossed a validated AGI threshold. The unit of evidence is a proposed way to organize future evaluations. The reader should distinguish the framework’s suggested measurement dimensions from empirically validated tests for each dimension.",
         appraisal="This framework is useful for defining the coverage of an evaluation before selecting benchmark tasks. A next study should publish operational task definitions for each faculty, check rater agreement, assess whether tasks actually isolate the intended construct, and test whether a profile predicts behavior on a separate task sample. Human comparison requires a clearly described population and expertise level. Any composite should be accompanied by raw scores and sensitivity to weighting choices. The source helps answer “what should we measure?”; it does not settle a universal definition of AGI.",
         diagram=["Cognitive domains", "Faculty-level tasks", "Held-out trials", "Capability profile"],
         figcaption="Reviewer schematic of the progression from a cognitive taxonomy to a measured profile; redrawn from [R01]."),
    dict(n=2, key="R02", title="From AGI to ASI", authors="Tim Genewein et al.", org="Google DeepMind and collaborators", year="2026", status="lab report / arXiv preprint",
         date="Version 3, 10 November 2026", url="https://arxiv.org/abs/2606.12683",
         question="This report asks what could happen after human-level artificial general intelligence, and how digital systems might move along a continuum toward superintelligence. It separates possible sources of advantage—such as speed, replication, and information sharing—from limits imposed by computation, physical resources, knowledge, and interaction with the world.",
         method="Rather than report a single forecast, the authors map pathways and bottlenecks. They discuss scaling and algorithmic change, internal processing, working memory, replication, coordination, and recursive improvement, while emphasizing that these advantages depend on conditions. The analysis considers theoretical endpoints such as universal AI as a point of reference and examines transitions from human-level capability to much stronger systems.",
         evidence="The work is a research report and scenario analysis, not a controlled experiment measuring a present-day system. Its diagrams and tables organize assumptions about possible advantages and constraints. The source PDF identifies the 10 November 2026 version; the arXiv record number begins with June 2026, but that identifier is not the publication date of the version used here.",
         appraisal="The report is valuable for resisting one-variable extrapolations. Digital speed or copyability does not itself imply broad competence, stable autonomy, or a rapid transition. Each scenario rests on technical and institutional assumptions that should be made explicit. To connect it to empirical work, researchers would need measurable precursor capabilities, dependency chains, and observations that would weaken a proposed pathway. It is useful for framing uncertainty and governance questions, but should not be read as a dated prediction or as evidence that AGI or ASI exists today.",
         diagram=["Capability growth", "Algorithmic change", "System integration", "Potential advantage"],
         figcaption="Reviewer schematic of a possible pathway with constraints; it is not a forecast or source result. Based on [R02]."),
    dict(n=3, key="R03", title="Visual General Intelligence: A White Paper", authors="Hirokatsu Kataoka et al.", org="Multi-institutional research team", year="2026", status="white paper / arXiv preprint",
         date="26 August 2026", url="https://arxiv.org/abs/2608.25924",
         question="The white paper reframes intelligence from a vision-centered perspective. It asks whether learning from images, video, geometry, and interaction can support a route toward broader intelligence, rather than treating vision only as a label-prediction module attached to a language system.",
         method="The authors assemble perspectives on visual representation, temporal observation, active perception, prediction, action, and connections to language. A recurring idea is that an intelligent visual system should recover useful structure from observations and use that structure to anticipate consequences. The paper discusses different positions—vision-only, vision-first, language-mediated, and multimodal—without prescribing one settled architecture.",
         evidence="This is an agenda-setting white paper, not a benchmark paper establishing an end-to-end visual-general intelligence result. Its diagrams illustrate candidate principles and research directions. Because the work deliberately brings together multiple viewpoints, its value lies in clarifying questions and experimental targets rather than reporting a unified empirical result.",
         appraisal="The agenda becomes testable when recognition is coupled to prediction and action. A useful experiment would hold task goals constant while changing viewpoints, occlusion, time, and available actions; it would test whether a representation supports counterfactual predictions and transfers to an unseen environment. Vision-language systems can use linguistic priors to answer visual questions without acquiring robust visual models, so ablations and source-grounded checks matter. The paper widens AGI measurement while leaving open how visual competence should combine with memory, language, planning, and embodiment.",
         diagram=["Observe scene", "Build state model", "Predict change", "Choose action"],
         figcaption="Reviewer schematic of a grounded perception–prediction–action loop discussed in [R03]."),
    dict(n=4, key="R04", title="Characterizing Jaggedness Aids Safety & Usability",
         authors="Meredith Ringel Morris et al.", org="Google DeepMind", year="2026", status="position paper / preprint",
         date="Version 2, 6 May 2026", url="https://cs.stanford.edu/~merrie/papers/jaggedness_preprint.pdf",
         question="The paper focuses on jaggedness: a model can perform exceptionally on demanding work and still fail at tasks people consider simple. Such unevenness matters for usability and safety because a fluent or strong overall score does not tell a user where a system may break.",
         method="The authors propose capability profiles and summary metrics, including a jaggedness index based on dispersion across standardized performance. Human-relative normalization is used to make uneven task performance easier to interpret. The paper connects capability measurement with deployment questions: users need to know both the system’s strong regions and its capability valleys.",
         evidence="This is a position paper proposing a way to measure an important phenomenon. Its plots and examples illustrate how a summary can hide local weaknesses. The index is a statistic over a chosen task sample; it depends on which skills are measured, how they are normalized, and how the scores are combined. A numerical index is therefore not a task-independent property of a model.",
         appraisal="The practical recommendation is to publish the full profile beside any summary. A follow-up should test whether jaggedness predicts real-world failure, whether users make better choices when given a profile, and how robust the index is to task selection and reference cohort. Researchers should include uncertainty and low-tail performance, not only the mean. This complements the cognitive taxonomy in [R01]: one organizes kinds of capability, while the other highlights unevenness across observed tasks. Neither alone defines an AGI threshold.",
         diagram=["Task sample", "Normalize scores", "Show profile", "Inspect dispersion"],
         figcaption="Reviewer schematic of a profile-first evaluation; concept redrawn from [R04]."),
    dict(n=5, key="R05", title="General Agent Evaluation", authors="Elron Bandel et al.",
         org="IBM Research and MIT", year="2026", status="research preprint",
         date="26 February 2026; version 2 dated 11 May 2026", url="https://arxiv.org/abs/2602.22953",
         question="The authors identify a comparability gap: studies of agents often pair different models, harnesses, protocols, and benchmarks, making it hard to attribute performance to architecture. The paper asks how agent implementation choices affect task performance across unfamiliar environments.",
         method="It proposes a unified protocol and evaluation harness intended to connect benchmarks to general-purpose agents and backbone models. The study compares tool-calling, MCP, code-generation, and command-line styles across benchmarks with matched models. The design supports a more factorial analysis of model, agent configuration, and task setting than isolated demonstrations allow.",
         evidence="The paper reports a systematic comparison and an open leaderboard. The results indicate that configuration effects vary with the task and benchmark; rankings and cost-performance tradeoffs are conditional. A unified interface is an enabling contribution, but it cannot make all benchmarks equivalent or remove differences in task coverage and scoring.",
         appraisal="The paper makes a strong case for recording the full agent system and for running matched comparisons. Reproductions should preserve budget, retries, tools, and prompt context while adding more models and environment families. Results should report per-task distributions, failure traces, cost, and run variance. Protocol adapters may introduce behavior of their own, so adapter fidelity also needs validation. This work provides a useful experimental foundation for comparing agents, not a single architecture that wins across all possible tasks.",
         diagram=["Benchmark", "Protocol adapter", "Agent design", "Model × task result"],
         figcaption="Reviewer schematic of the benchmark–protocol–agent comparison motivating [R05]."),
    dict(n=6, key="R06", title="Agent-World: Scaling Real-World Environment Synthesis for Evolving General Agent Intelligence",
         authors="Renmin University of China and ByteDance Seed team", org="Renmin University of China / ByteDance Seed", year="2026",
         status="research preprint", date="20 April 2026", url="https://arxiv.org/abs/2604.18292",
         question="Agent-World addresses a training bottleneck: tool-using agents need interactive, stateful environments, but manually creating realistic environments and verifiable tasks is expensive. The paper asks whether a scalable environment-generation and training pipeline can expand agent experience.",
         method="The system discovers tool and database environments, synthesizes tasks with controllable difficulty, and combines multi-environment interaction with continued agent training. The paper connects environment discovery, task construction, verification, and training into an evolving loop. Its use of service-like tools aims to provide more realistic state transitions than static question answering.",
         evidence="The authors report experiments relating environment scale and training to agent performance within their generated setup. The figures describe a synthesis pipeline and performance comparisons. Such results demonstrate behavior on the benchmark and generation process used; they do not establish a universal scaling law or show that simulated services reproduce all live-service behavior.",
         appraisal="Environment diversity is a meaningful experimental variable, but unique environment count is a poor proxy for coverage if many environments share the same schemas or action patterns. Good follow-up work should report overlap between train and test tasks, expose environment specifications, validate task verifiers independently, and test tool changes or service failures. Paired simulation-to-live tests could quantify the deployment gap safely. The paper treats environments as part of the learning distribution, not merely as an evaluation wrapper.",
         diagram=["Tool schemas", "Synthesize states", "Verify tasks", "Train and expand"],
         figcaption="Reviewer schematic of an environment-synthesis cycle described in [R06]."),
    dict(n=7, key="R07", title="Scaling Agents via Continual Pre-training", authors="Liangcai Su et al.",
         org="Alibaba Tongyi Lab", year="2026", status="peer-reviewed conference paper, ICLR 2026",
         date="ICLR 2026 proceedings; earlier arXiv posting in September 2025", url="https://openreview.net/forum?id=Dru5mm9anE",
         question="This paper argues that general-purpose foundation models can be poorly prepared for research-agent behavior. Post-training then asks them to learn diverse tool use and align to expert demonstrations simultaneously. The authors propose building an agentic foundation model through continual pre-training before downstream agent post-training.",
         method="AgentFounder is presented as an agentic training pipeline. The paper describes first-order action synthesis from knowledge and questions, planning and reasoning action construction, and higher-order trajectories with supervision. The pipeline aims to cultivate reusable agent behaviors and research skills from broader interaction data rather than relying only on final-answer demonstrations.",
         evidence="The paper is peer-reviewed at ICLR 2026; its arXiv version predates the conference. It reports evaluation on research and agent tasks and comparisons with post-training approaches. Because training changes knowledge, procedure, and exposure together, a score gain does not isolate which of these caused the change. The source diagrams communicate the training stages, not a guarantee of transfer.",
         appraisal="The key question is whether agentic pre-training teaches procedures that transfer, or primarily supplies more task knowledge and benchmark familiarity. Strong follow-up tests would hold knowledge exposure constant, test unfamiliar source types, require correction after contradictory evidence, and inspect citation provenance. The full training data and trajectory generation matter for interpreting results. This connects to environment scaling [R06], but emphasizes the model’s learned interaction patterns.",
         diagram=["Synthesize experience", "Pre-train actions", "Post-train research", "Test transfer"],
         figcaption="Reviewer schematic of a staged agentic training pipeline based on [R07]."),
    dict(n=8, key="R08", title="AgentFrontier: Expanding the Capability Frontier of LLM Agents with ZPD-Guided Data Synthesis",
         authors="Xuanzhong Chen et al.", org="Alibaba Tongyi Lab", year="2026",
         status="peer-reviewed conference paper, ICLR 2026",
         date="ICLR 2026 proceedings; arXiv version October 2025", url="https://openreview.net/pdf/466f94ec94f21750830c728c1ba0a1097a75a66d.pdf",
         question="AgentFrontier treats training difficulty as a curriculum problem. Drawing on the Zone of Proximal Development, it seeks tasks that a learner cannot solve unaided but could master with suitable guidance. The aim is to concentrate learning on a capability frontier rather than on tasks that are already easy or currently unreachable.",
         method="The AgentFrontier Engine synthesizes multidisciplinary data, increases question complexity, filters items using learner responses, and supports continued pre-training and targeted post-training. The paper also derives a dynamic ZPD Exam from the same general approach. These components make the learner’s measured performance part of the task-generation loop.",
         evidence="The authors report training and evaluation results for AgentFrontier models and describe the task-generation pipeline. Difficulty calibration depends on the learners, assistance conditions, and verifier selected by the authors. If generator and verifier share biases with the trained model, the resulting benchmark can favor idiosyncratic strengths without measuring broader capability.",
         appraisal="A curriculum result is more persuasive when task difficulty predicts outcomes across multiple independently selected learners and human experts. Verifier precision should be audited on near-miss and adversarial cases. Most importantly, gains should transfer to a test set created outside the synthesis engine. The contribution is a scalable approach to targeting learnable tasks; it does not establish that ZPD-guided data alone causes general intelligence. Evaluation should separate learning progress from adaptation to the dynamic exam.",
         diagram=["Seed problems", "Estimate frontier", "Synthesize guidance", "Train and re-test"],
         figcaption="Reviewer schematic of a ZPD-guided task and learning loop from [R08]."),
    dict(n=9, key="R09", title="AgentSynth: Scalable Task Generation for Generalist Computer-Use Agents",
         authors="Jingxu Xie et al.", org="University of California, Berkeley", year="2026",
         status="peer-reviewed conference paper, ICLR 2026",
         date="ICLR 2026 proceedings; arXiv version 2 dated 2 March 2026", url="https://openreview.net/forum?id=CoBxmXThM6",
         question="AgentSynth asks how to generate realistic computer-use tasks and trajectories at scale without paying for human construction of every long task. Its central idea is that tasks made of individually simple subtasks can become challenging when composed into a longer sequence with dependencies.",
         method="The pipeline synthesizes subtasks, composes them into long-horizon tasks, executes trajectories, and checks whether the task and outcome are valid. The authors describe varying complexity through the number of subtasks and report a corpus of more than 6,000 tasks. The paper reports an average trajectory-generation cost of about 0.60 US dollars and a success decline from 18% at difficulty level one to 4% at level six in the reported setup.",
         evidence="These numeric results describe the authors’ benchmark and agent set, not general computer use. The paper’s key empirical point is that long-horizon composition sharply reduces success for current systems. The generation pipeline and verifier determine what counts as a realistic solvable task. The source also examines verifier errors and human judgments, so automated correctness should not be assumed.",
         appraisal="Task composition is useful for measuring dependency handling, but subtask count is only one difficulty dimension. A task with many independent steps can be easier than one with a few ambiguous dependencies. Independent audits should check UI realism, solvability, hidden shortcuts, and verifier precision. Transfer should be tested on applications and task grammars absent from synthesis. The cost advantage is useful when paired with quality-control expense, human audit rates, and reproduction details.",
         diagram=["Generate subtasks", "Compose dependencies", "Run trajectories", "Verify and score"],
         figcaption="Reviewer schematic of the task synthesis and verification loop in [R09]."),
    dict(n=10, key="R10", title="Towards General Agentic Intelligence via Environment Scaling",
         authors="Runnan Fang et al.", org="Zhejiang University, Alibaba Tongyi Lab, Peking University", year="2026",
         status="peer-reviewed, Findings of ACL 2026", date="Findings of ACL 2026",
         url="https://aclanthology.org/2026.findings-acl.872/",
         question="This study examines how tool environments can be constructed and scaled to train more general agentic systems. It focuses on the relationship between environment diversity, tool schemas, simulated interactions, and agent performance.",
         method="The paper proposes an automatic construction process that matches tool schemas, builds stateful environments, and generates agentic tasks. Its figures show schema organization, environment building, and task construction. The design permits repeatable interaction and measurable state changes across domains, providing a setting in which environment variety can be studied systematically.",
         evidence="The work appears in Findings of ACL 2026 and reports experiments on the authors’ constructed environment set. It is evidence that environment creation can be organized and scaled under a shared methodology. Its conclusions are bounded by the fidelity of the tools and environment state model. Generated environments do not automatically reproduce authentication failures, latency, interface drift, or permissions in live services.",
         appraisal="The environmental focus complements model-centric training in [R07–R09]. A stronger generality test would hold the agent fixed while withholding entire tool families, task grammars, or database structures, then measure few-shot adaptation and recovery. Environment manifests and state-transition rules should be published. Researchers should measure how many distinct interaction patterns were added, rather than relying on raw environment count. This contributes a practical way to build experimental worlds, not proof of deployment-ready generality.",
         figcaption="Figure reproduced from [R10], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=11, key="R11", title="InfiAgent: An Infinite-Horizon Framework for General-Purpose Autonomous Agents",
         authors="Chenglin Yu et al.", org="The University of Hong Kong and The Hong Kong Polytechnic University", year="2026",
         status="peer-reviewed, Findings of ACL 2026", date="Findings of ACL 2026",
         url="https://aclanthology.org/2026.findings-acl.1787/",
         question="InfiAgent addresses a practical limit on long-running agents: a bounded context window and fragile handoffs can make document-heavy work lose continuity. The paper asks how persistent state can support long-horizon execution while keeping each reasoning step bounded.",
         method="The architecture uses a hierarchical execution stack and file-centric state. Files preserve intermediate artifacts and serve as an external workspace from which the agent can continue. The paper evaluates tasks requiring extended multi-step work and compares aspects of coverage, stability, and execution behavior. Its framework makes the distinction between transient context and persistent artifacts explicit.",
         evidence="The paper is a peer-reviewed ACL Findings work. Its architecture and task results offer evidence for a way to organize longer workflows. The phrase “infinite horizon” describes the framework’s intended capacity for continuation, not literal unlimited reliable autonomy. The evaluated task family and model setup bound the evidence; serial execution, latency, and failures in intermediate artifacts remain important.",
         appraisal="Persistence is not the same as dependable memory. A saved summary may be incomplete, stale, or false. Follow-up evaluations should inject corrupted files, contradictory notes, failed tools, and interruptions, then test detection and recovery. Persistent state should carry timestamps and links to its evidence. This connects to process evaluation [R19]: an audit trail makes continuation visible, but correctness still needs independent verification. The core contribution is a system design for continuity, not a solution to reasoning errors.",
         figcaption="Figure reproduced from [R11], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=12, key="R12", title="A Survey on Evaluation of LLM-based Agents",
         authors="Asaf Yehudai et al.", org="Hebrew University of Jerusalem, IBM Research, Yale University", year="2026",
         status="peer-reviewed survey, Findings of ACL 2026", date="Findings of ACL 2026",
         url="https://aclanthology.org/2026.findings-acl.1330/",
         question="This survey maps evaluation research as systems move from static language generation toward agents that plan, act, and receive feedback in dynamic environments. It argues that evaluation must address sequential action and environment interaction, not only textual outputs.",
         method="The authors organize the field across core abilities, application-specific tasks, generalist-agent benchmarks, benchmark design dimensions, and evaluation frameworks. The survey contrasts different task and environment forms, including web, coding, games, research, memory, and tool use. Its taxonomy provides a way to locate what a study measures and which areas it leaves uncovered.",
         evidence="A survey synthesizes existing research rather than testing a new agent. Its coverage is a function of search strategy, inclusion rules, and publication timing. The resulting map is useful, but the field changes quickly and categories may be revised as new systems appear. The paper’s framework is not itself a validated score or comprehensive benchmark.",
         appraisal="The most durable use is as a checklist for benchmark construction: name the task, environment, interface, metric, risk controls, and evidence available to an evaluator. Researchers should map their own suites onto the taxonomy and state omissions. Deployment decisions require inspecting primary studies and current versions rather than transferring a survey’s comparison table without context. This survey categorizes the landscape, while [R05] provides a specific cross-protocol comparison.",
         figcaption="Figure reproduced from [R12], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=13, key="R13", title="Can Generalist Agents Automate Data Curation?",
         authors="Feiyang Kang et al.", org="Virginia Tech, UIUC, UW–Madison, UC Berkeley", year="2026",
         status="peer-reviewed, EMNLP 2026", date="EMNLP 2026",
         url="https://aclanthology.org/2026.emnlp-main.815/",
         question="The paper tests whether a coding agent can automate data curation, a loop in which researchers propose a data policy, train a model, measure results, and revise the policy. It asks whether an agent can do more than execute a fixed script: can it select data based on measured downstream effects and improve its choices?",
         method="Curation-Bench fixes the target model, training recipe, and evaluation suite while giving the agent tools for changing the data policy and running experiments. The benchmark includes trajectory diagnostics and criteria for whether proposed changes are grounded and effective. This setup makes both the agent’s experiments and its reasons for selecting examples observable.",
         evidence="The authors report that generalist agents can automate substantial portions of the curation loop and compare them with human-designed baselines. They also analyze policy quality and rationales; the source describes cases in which execution succeeds while policy reasoning remains weak or locally tuned. These findings are specific to the benchmark’s task, model, data pool, and training cost.",
         appraisal="This paper distinguishes research judgment from tool execution. A follow-up should test policies on fresh datasets, replicate improvements with independent training runs, preserve manifests, and compare rationale with actual selection behavior. Automated success on one curated benchmark may reflect adaptation to its interface or reward. The task connects agent autonomy to scientific work, yet a general claim requires evidence that the agent selects useful interventions under new experimental conditions. Reproducibility and justification should be scored alongside outcome.",
         figcaption="Figure reproduced from [R13], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=14, key="R14", title="Can Your Agent Read the Source Faithfully? Benchmarking MLLM Agents on Source-Grounded Multimodal Retrieval",
         authors="Wentao Gao et al.", org="University of Texas at Arlington and collaborators", year="2026",
         status="peer-reviewed, EMNLP 2026", date="EMNLP 2026",
         url="https://aclanthology.org/2026.emnlp-main.1855/",
         question="RDQA targets a gap in multimodal agent evaluation: can a system autonomously search, parse, and extract precise evidence from raw documents, video, and audio? A final response can sound convincing even when retrieval missed the relevant segment or the evidence does not support the claim.",
         method="The benchmark contains 1,350 questions across document, video, and audio sources and twenty real-world task scenarios. Tasks require source searching, detail localization, and evidence retrieval. The paper introduces process-aware measures, including a process-localization rate, to identify failures in the chain rather than judging only the final answer.",
         evidence="The benchmark integrates retrieval and source interpretation into an end-to-end task. Its examples show how a system can miss precise evidence despite producing a plausible answer. Performance depends on the source collection, task wording, tools, and scoring procedure. Source presence or citation alone is not a complete measure of whether a claim is entailed by the retrieved passage, frame, or audio interval.",
         appraisal="The paper supports claim-level evidence alignment as a separate capability. Follow-up tests should alter source ordering, add distractors, change a chart value, or introduce conflicting sources, and check whether the answer changes appropriately. Evaluators should record page regions, timestamps, and audio spans. A model should be allowed to say that evidence is insufficient. This complements process evaluation [R19]: one makes source use measurable, the other argues that intermediate steps should be part of the judgment.",
         figcaption="Figure reproduced from [R14], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=15, key="R15", title="ARM: Role-Conditioned Neuron Transplantation for Training-Free Generalist LLM Agent Merging",
         authors="Zhuoka Feng et al.", org="Fudan University and Shanghai Innovation Institute", year="2026",
         status="peer-reviewed, EMNLP 2026", date="EMNLP 2026",
         url="https://aclanthology.org/2026.emnlp-main.2115/",
         question="ARM studies how task-specialized interactive agents can be merged into one checkpoint without additional training. The motivation is that specialists often transfer poorly, while conventional merging methods can vary considerably across environments and may damage role-critical behavior.",
         method="The authors propose role-conditioned neuron transplantation, using an answer-free activation-overlap signal to identify and transplant neurons associated with task roles. The method targets the multi-turn nature of agent tasks, where a small error in a role-critical output can cascade through later actions. The paper compares merging approaches across interactive benchmarks.",
         evidence="The paper presents an algorithmic approach and reports benchmark results on merged agent behavior. Its opening figure emphasizes that training-free merging baselines do not perform uniformly across environments. Evidence is bounded by the selected specialists, backbone models, roles, and tasks. Merging a finite set of specialist behaviors does not by itself show broad learning or adaptation to unseen domains.",
         appraisal="The most informative report is a before-and-after capability profile for each specialist and the merged model, including unrelated held-out tasks, calibration, and safety behavior. Evaluate negative transfer and repeatability across model pairs. An answer-free signal may reduce dependence on task labels, but its assumptions about activation overlap still require validation. ARM contributes a mechanism for consolidation; generality must be judged on transfer and retained capability rather than a single average score.",
         figcaption="Figure reproduced from [R15], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=16, key="R16", title="OS-Symphony: A Holistic Framework for Robust and Generalist Computer-Using Agents",
         authors="Bowen Yang et al.", org="Shanghai AI Laboratory and collaborators", year="2026",
         status="peer-reviewed, ACL 2026", date="ACL 2026",
         url="https://aclanthology.org/2026.acl-long.1021/",
         question="OS-Symphony focuses on long-horizon computer use. The paper identifies limitations in how systems curate visual history and retrieve useful demonstrations, which can impair robustness and performance in unfamiliar domains.",
         method="The framework coordinates a computer-use agent with memory, reflection, and tool components. It distinguishes short-term visual context from longer-term stored experience and uses milestones or tutorial-like traces to support later actions. The architecture is intended to make historical context more selective and usable during browser or operating-system workflows.",
         evidence="The ACL paper reports performance on selected computer-use tasks and describes the components through diagrams and experiments. The results support the proposed design within those settings, but do not settle how each component contributes without controlled ablations. Interface familiarity, operating system, permission model, screenshot resolution, and action budgets shape results.",
         appraisal="Memory and reflection can help, but can also preserve an incorrect assumption or add latency. Compare each component with a matched model-call and tool budget. Test interface drift, unseen applications, misleading visual history, stale tutorials, and safe handling of write actions. Provide exact traces so evaluators can separate perception, memory, planning, and execution errors. This complements persistent-state design in [R11] with computer-use-specific visual context.",
         figcaption="Figure reproduced from [R16], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=17, key="R17", title="Role-Agent: Bootstrapping LLM Agents via Dual-Role Evolution",
         authors="Xucong Wang et al.", org="USTC and Alibaba AMAP", year="2026",
         status="peer-reviewed, Findings of EMNLP 2026", date="Findings of EMNLP 2026",
         url="https://aclanthology.org/2026.findings-emnlp.208/",
         question="Role-Agent responds to limited interaction feedback and static training environments by letting one language model act in both agent and environment roles. The paper asks whether this dual-role setup can produce richer experience and support agent learning.",
         method="The framework combines an acting agent, a synthetic environment model, state prediction, and feedback. The system explores tasks, generates environment responses, and uses the resulting rollouts to train or refine behavior. Its central design is a co-evolution loop in which the environment is not fixed but adapts alongside the agent.",
         evidence="The paper reports experiments on the authors’ training tasks and illustrates the difference between static, synthetic, and co-evolving environments. The reported gain is evidence about that training loop and its tasks. Since the same model family can produce both action and feedback, agent and simulator may share failure modes; internal agreement can make an incorrect world model look self-consistent.",
         appraisal="Independent environment tests are essential. Compare the learned agent on externally authored tasks, with human-validated state transitions and tool outputs, and test whether performance survives a change in environment model. The environment should be scored separately for factual and state fidelity. Role-Agent contributes a potentially scalable training mechanism, while simulator validation and transfer determine how much the result supports generality.",
         figcaption="Figure reproduced from [R17], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=18, key="R18", title="AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows",
         authors="Tara Bogavelli, Hari Subramani, and Roshnee Sharma", org="ServiceNow AI Research", year="2026",
         status="peer-reviewed, AACL 2026", date="AACL 2026, pages 915–933",
         url="https://aclanthology.org/2026.aacl-long.44/",
         question="AgentArch targets enterprise workflows, where components that appear useful in isolation interact with dependencies, tools, and constraints. The authors note a lack of empirical guidance for choosing architecture combinations in business settings.",
         method="The benchmark compares eighteen agent configurations across two enterprise use cases and multiple design dimensions, including orchestration, agent style, and model choice. Tasks such as time-off requests or customer routing represent multi-step workflows. The paper records consistency and performance across configurations rather than evaluating a single architecture in isolation.",
         evidence="The study reports model and architecture comparisons, including differences in the conditions where particular designs help. Its results support the value of a structured enterprise benchmark. They remain tied to the selected workflows, tools, models, and scoring. An enterprise benchmark can test realistic dependencies without representing every organization’s policies, data, or exception patterns.",
         appraisal="Architecture guidance becomes more portable when studies report exact prompts, tools, budgets, and state transitions and replicate across workflow families. Add permission checks, partial completion, correction, rollback, and ambiguous requests. Measure cost and human review as part of system performance. AgentArch contributes an experimental basis for comparing design choices in enterprise tasks, but it does not certify an architecture as reliable across companies.",
         figcaption="Figure reproduced from [R18], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=19, key="R19", title="Process Evaluation for Agentic Systems",
         authors="Milan Gritta et al.", org="Huawei Noah’s Ark Lab and UCL Centre for Artificial Intelligence", year="2026",
         status="peer-reviewed position paper, Findings of EACL 2026",
         date="EACL 2026, pages 2678–2692", url="https://aclanthology.org/2026.findings-eacl.140/",
         question="The paper argues that outcome accuracy is insufficient for evaluating agents, especially in sensitive applications. A correct answer can follow from skipped steps, unsupported shortcuts, simulated tool use, or outdated knowledge, leaving a risky and hard-to-audit process invisible.",
         method="The authors categorize process risks and propose evaluating agent trajectories against recommended protocols. Their small-scale feasibility study uses a compliance checklist over intermediate actions and compares process scores with final outcomes. Examples cover behaviors such as checking source material, using appropriate tools, and following requested steps. The work distinguishes whether the answer is right from whether the method is reliable.",
         evidence="The paper reports a proof-of-feasibility study, not a universally validated process metric. It compares different models and shows that compliance and task success need not coincide. Checklist scores depend on the protocol, question weights, task design, and judge quality. In the source example, a model can receive high compliance while failing the final task, demonstrating that process and outcome capture distinct dimensions.",
         appraisal="This is a strong conceptual extension to outcome evaluation. Future work should validate process labels against expert reviewers, test whether labels predict downstream harm, and define when a safe alternative path is acceptable. Logging has privacy and retention costs; the protocol should capture only what is needed for the risk being studied. Process compliance should complement source grounding [R14], persistence [R11], and task success rather than collapse into a single score.",
         figcaption="Figure reproduced from [R19], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
    dict(n=20, key="R20", title="Can AI Agents Answer Your Data Questions? A Benchmark for Data Agents",
         authors="Ruiying Ma et al.", org="UC Berkeley, University of Washington, Hasura PromptQL", year="2026",
         status="peer-reviewed, EMNLP 2026", date="EMNLP 2026, pages 42651–42677",
         url="https://aclanthology.org/2026.emnlp-main.1872/",
         question="DAB examines an enterprise data problem: a natural-language question may require joining information across multiple databases, resolving inconsistent identifiers, extracting values from text, and applying domain knowledge. Existing benchmarks often cover only a narrow slice of this work.",
         method="The benchmark contains 104 questions over 17 datasets and four database systems. It targets four workload properties: multi-database integration, ill-formatted join keys, unstructured text transformation, and domain knowledge. Agents interact with databases and tools, and the benchmark retains setup details needed to test whether the answer follows from executable work.",
         evidence="The paper reports that the best evaluated agent reaches 57% pass@1 under the study’s setup, averaged over five trials per query. Its error analysis attributes most failures to incorrect planning or faulty implementation rather than data selection; agents rely heavily on regular expressions for free-text extraction and rarely use alternatives such as NLP libraries or subagents. These are results for the tested models and benchmark version.",
         appraisal="The benchmark makes intermediate computation observable and exposes failure classes that final-answer grading would miss. Future tests should hold out schemas, vary join-key corruption, include access controls, and separate query execution from explanation quality. Evaluation should check whether the agent asks for clarification when domain information is missing. Since the benchmark is assembled from open datasets transformed to resemble production messiness, external enterprise replications would strengthen deployment claims. DAB measures a demanding data-agent capability, not general intelligence as a whole.",
         figcaption="Figure reproduced from [R20], Fig. 1, under the ACL Anthology’s CC BY 4.0 policy; source figure and attribution note follow."),
]


CHAPTERS = [
    ("1. Introduction: from an AGI label to observable evidence", [
        ("The question this review can answer", [
            "This review asks what recent research makes observable about progress toward artificial general intelligence. Its twenty source papers do not share one operational definition of AGI, nor do they form a single controlled program. They examine adjacent empirical problems: capability breadth, multimodal grounding, tool use, persistent state, environment construction, learning, task evaluation, and reliability. The useful synthesis is therefore a map of evidence and dependencies, not a verdict that any system has reached AGI.",
            "The corpus is recent and intentionally mixed. It includes research reports and preprints as well as peer-reviewed proceedings papers and a survey. These categories are not interchangeable. A conceptual framework can clarify a measurement target; a benchmark can make a task reproducible; an experiment can compare systems on a sample; peer review documents scrutiny by a venue. None of these alone guarantees correctness, external validity, or deployment readiness."
        ]),
        ("Why the unit of analysis matters", [
            "A modern agent is not just a language model. It can include a model, prompts, a controller, tools, memory, an execution environment, a verifier, retry rules, and a human operator. A result attributed to “the model” may depend on any of these components. General Agent Evaluation [R05] and AgentArch [R18] make architecture choices visible; InfiAgent [R11] and OS-Symphony [R16] emphasize persistent context and memory; process evaluation [R19] asks whether the intermediate behavior is acceptable.",
            "A system claim should name the complete configuration. At minimum, a methods record identifies the model version, controller and prompt version, tool definitions, permissions, state reset policy, sampling settings, retries, stopping condition, evaluator, and compute or monetary budget. Without these details, a reader cannot tell whether two systems differ in the model, the scaffold, or the opportunity they had to retry."
        ]),
        ("What counts as a contribution", [
            "The papers offer different kinds of contributions. Some propose a construct, such as cognitive breadth [R01] or process compliance [R19]. Some build a task suite or environment, such as RDQA [R14], Curation-Bench [R13], AgentArch [R18], or DAB [R20]. Others develop a training or architecture method [R06–R09, R11, R15–R17]. This review keeps those contribution types distinct because a useful new instrument and a demonstrated capability are not the same claim.",
            "The strongest cross-paper conclusion is modest: evaluating generality requires observing behavior across task families, settings, time horizons, and constraints. Each paper illuminates a slice. Taken together they motivate a layered research program in which breadth, transfer, sustained action, grounding, and reliability are measured separately before being summarized."
        ])
    ]),
    ("2. Operationalizing generality", [
        ("A capability is conditional on a task distribution", [
            "Generality is not observed in the abstract. It is inferred from performance on a task sample and from the conditions under which a system adapts to changed tasks. A benchmark score therefore has an implicit denominator: a set of task families, interfaces, data sources, and allowed resources. The inference grows stronger when the sample covers distinct capabilities and when the test distribution is held apart from training and task synthesis.",
            "The cognitive taxonomy in Measuring Progress Toward AGI [R01] provides a way to name a broad range of faculties and to build a profile across them. Its value is organizational: it makes omissions and unevenness discussable. The proposed faculties still need task operationalization, reliable scoring, and evidence that the tasks represent the intended constructs. A taxonomy is a sampling map, not an intelligence meter."
        ]),
        ("Breadth, transfer, adaptation, autonomy", [
            "Four terms often collapse into “general.” Breadth means success across different families of tasks. Transfer means retained performance when a task, interface, or environment changes. Adaptation means improvement after feedback or examples. Autonomy means that the system selects and executes actions with limited intervention. They interact, but one cannot stand in for another. An autonomous agent may execute a narrow workflow reliably; a broad model may need substantial user direction; a system may transfer well only after many demonstrations.",
            "The source set has useful examples of these distinctions. Environment-scaled studies [R06, R10] ask whether varied interactive experience helps. ZPD-guided synthesis [R08] targets tasks at a learner’s current frontier. AgentSynth [R09] composes subtasks into longer trajectories. InfiAgent [R11] extends execution through persistent state. Each studies an important ingredient, but broad generality would require tests that combine them under controlled shifts."
        ]),
        ("Thresholds and the AGI-to-ASI question", [
            "A threshold can support a policy decision only if its measurement error and consequences are clear. A system may exceed a reference level on selected cognitive tasks while failing on untested settings. Composite scores make this problem harder because weights encode value judgments. A defensible report should show underlying scores, the reference population, the task composition, uncertainty, and the effect of alternative weights.",
            "From AGI to ASI [R02] discusses possible transition pathways and limits. It is best read as scenario analysis: it maps assumptions about capability, compute, replication, information flow, and institutions. It does not supply a clock or establish that present agents meet an AGI definition. This distinction matters because a plausible future mechanism is not empirical evidence that the mechanism is already operating."
        ]),
        ("A working operational definition for this review", [
            "For synthesis, progress toward AGI means evidence that a specified system can perform across varied cognitive and interactive tasks, transfer to held-out combinations, improve from limited feedback, sustain multi-step activity, and remain reliable under stated constraints. The list is a working review definition, not a field-wide standard. It sets a higher bar than fluent answers or strong scores on one benchmark, while avoiding an unsupported claim that all relevant human abilities must be replicated.",
            "This definition also makes exclusions visible. A benchmark of database questions can inform structured data work but does not establish social reasoning or visual planning. A computer-use result may reveal long-horizon fragility but cannot alone measure scientific judgment. Every inference should state what was tested, what was not tested, and what transfer remains hypothetical."
        ])
    ]),
    ("3. Capability profiles and jaggedness", [
        ("Why a mean score is incomplete", [
            "Average performance is a compact summary, but it can hide exactly the weakness that matters for a user. A system may solve hard coding questions, fail simple arithmetic, and produce plausible unsupported answers. If tasks are pooled, the high scores can overwhelm a small but consequential failure group. The jaggedness paper [R04] argues that these irregular profiles affect safety and usability; the AGI framework [R01] likewise recommends a profile across faculties.",
            "A useful report gives the mean and the distribution: per-task or per-family scores, low-tail performance, confidence intervals, run-to-run variation, and common failure types. The lowest score should not automatically define intelligence either; a single noisy item can dominate. The point is to preserve the shape of the evidence so a reader can identify where the system succeeds, where it fails, and how certain that estimate is."
        ]),
        ("Normalization and profile construction", [
            "Human-relative normalization can help communicate relative difficulty, but the human reference group is part of the measurement instrument. Expertise, language, accessibility, education, time limits, and interface familiarity all change results. A report should publish both raw scores and normalized values and explain how the reference cohort was selected. Sensitivity analysis can reveal whether the profile’s interpretation changes under a different baseline.",
            "Task weighting also matters. Equal task weights give each item equal influence; equal family weights give each capability category equal influence; risk-weighted scores privilege rare severe failures. Each answers a different question. Researchers should choose weights before examining results, justify them against the intended use, and show the unweighted profile alongside any weighted composite."
        ]),
        ("Jaggedness as a decision aid", [
            "A scalar jaggedness index can summarize dispersion, but it loses which capability is low. Two models can have the same spread and very different risk profiles. The index should therefore accompany the complete vector and the task inventory. It also should not be treated as a stable trait until test–retest reliability and sensitivity to task selection have been measured.",
            "The practical value of a profile is whether it changes a decision. Future user studies could provide people with a model card containing average performance only, then a profile with uncertainty, and measure task assignment, review effort, and error detection. This would test whether characterizing jaggedness improves usability rather than merely describing it."
        ]),
        ("Dynamic benchmarks and saturation", [
            "A static benchmark supports reproducible comparisons but can saturate, leak into training, or become a target for narrow optimization. Dynamic tests reduce reuse but introduce moving task distributions and evaluator variation. AgentFrontier’s dynamic exam [R08], AgentSynth’s generated tasks [R09], and Agent-World’s environment pipeline [R06] explore ways to expand or refresh evaluation.",
            "New tasks need quality controls. A changing benchmark should retain anchor items for longitudinal comparison, publish version history, audit generator and verifier behavior, and maintain a held-out set outside the synthesis loop. If the test changes, score changes may reflect the new items rather than improved capability. Both stable and rotating components are needed for a useful time series."
        ])
    ]),
    ("4. Visual grounding and multimodal work", [
        ("From recognition to world structure", [
            "Recognizing a label in an image is not the same as understanding how a scene changes. A grounded system should identify entities and relations, track movement, infer relevant state, predict the consequences of an action, and revise its model when observations disagree. Visual General Intelligence [R03] frames this broader question and argues for treating vision as a possible foundation of intelligence rather than a peripheral input channel.",
            "A useful experiment links perception to a downstream decision. The evaluator can vary viewpoint, occlusion, lighting, temporal sampling, or available actions while keeping the goal stable. It should score both the scene interpretation and the action selected from it. This lets researchers distinguish a recognition success from an operationally useful world model."
        ]),
        ("Active sensing and evidence selection", [
            "Agents often choose what to inspect: which page to open, which frame to replay, which region to zoom, or which tool to call. This makes information gathering part of the capability. A system that reaches a correct answer after a costly but targeted search behaves differently from one that guesses from its prior knowledge. Evaluation should record observation choices, time, and evidence omitted along the path.",
            "RDQA [R14] gives a concrete multimodal case. Its tasks ask an agent to search raw media, locate details, and retrieve evidence across documents, video, and audio. The process-aware framing is useful because a final answer may hide retrieval failure. Stronger tests would edit a source, reorder results, or add conflicting evidence and check whether the answer follows the changed source."
        ]),
        ("Grounding is a relation, not a citation string", [
            "A citation is only useful if it supports the claim attached to it. Claim-level grounding asks whether the cited passage, chart value, image region, video interval, or spoken phrase entails the statement. Retrieval accuracy, evidence localization, entailment, and uncertainty should be measured separately. A system should be able to say that the available material does not settle a question.",
            "Multimodal tasks also make provenance harder. A transcript may omit tone or visual context; a chart may be separated from axis labels; a document may contain a note that changes a table’s interpretation. Trace records should preserve source identifiers and coordinates or timestamps where possible. This supports independent review without claiming that visible traces expose a model’s private internal reasoning."
        ]),
        ("Limits of vision-first arguments", [
            "A vision-centered research agenda is a useful challenge to text-only accounts of intelligence, but visual experience does not automatically produce causal understanding or safe action. A system may rely on textual priors, exploit stable benchmark layouts, or misinterpret a scene under a small shift. Comparative work should include vision-only, language-mediated, and multimodal conditions with matched data and compute.",
            "The question is not whether every capability should be expressed visually. It is whether representations learned from visual and spatial data add measurable predictive and action competence, and under which conditions. Testing this requires carefully designed controls and transfer tasks, not only more image–text pairs."
        ])
    ]),
    ("5. Agent architecture, memory, and sustained action", [
        ("The scaffold is part of the system", [
            "Agent architecture covers the controller around a model: task interpretation, planning, tool selection, action execution, memory, reflection, verification, and stopping. When a system improves, that change may come from a stronger backbone, better tools, more retries, or a revised controller. General Agent Evaluation [R05] makes protocol differences comparable; AgentArch [R18] studies combinations in workflows. Both point to the value of matched conditions.",
            "A complete methods section should separate capabilities of the foundation model from those of the assembled agent. Record what the model sees, which tools are available, when tool outputs enter context, whether the system can inspect its own traces, and how errors or timeouts are handled. This allows the reader to reproduce the actual opportunity structure."
        ]),
        ("Persistent state and long horizons", [
            "Long-horizon tasks require more than a large context window. The system must preserve decisions, intermediate evidence, and unfinished work; notice contradictions; recover after interruptions; and avoid compounding stale summaries. InfiAgent [R11] uses file-centric state to support continuing work. OS-Symphony [R16] treats visual history and tutorial-like experience as useful memory for computer-use tasks.",
            "External files make state auditable, but persistence does not ensure truth. A memory benchmark should test both retention and correction: inject a wrong intermediate artifact, update a source, or change a task condition and see whether the agent notices. Recovery after state corruption is a distinct measure from the ability to resume a clean task."
        ]),
        ("Reflection, delegation, and control flow", [
            "Reflection can catch mistakes, but a second model call can also repeat the same error. Delegation can cover subtasks, but introduces coordination overhead, mismatched assumptions, and dropped requirements. A good ablation keeps model-call budget and tool access comparable and measures end-to-end quality, latency, failure severity, and human correction.",
            "A research trace should expose control flow: observations, plans, calls, outputs, state writes, checks, retries, and termination decisions. It should not be mistaken for a faithful transcript of hidden cognition. It is evidence about externally observable actions and tool results, which is sufficient for many process and reliability questions."
        ]),
        ("The meaning of an infinite horizon", [
            "An architecture that can store files or launch a new worker may continue indefinitely in principle. Reliability over an indefinite period is a much stronger empirical claim. Error accumulation, changing tools, resource limits, access changes, and state drift grow with time. “Infinite-horizon” should therefore describe an architectural objective, while evaluation reports the tested horizon and restart behavior.",
            "Useful long-horizon results report performance by task length, pause and resume conditions, tool-failure rate, state-recovery rate, context or storage usage, and required human interventions. The task should have clear completion criteria and enough checks to detect an agent that appears active while making no progress."
        ])
    ]),
    ("6. Learning from tasks and environments", [
        ("Environment variety is a training variable", [
            "An agent learns from the distribution of states, actions, and feedback it encounters. Environment count alone does not tell whether that distribution is broad. Many generated tools may share the same action grammar; a smaller set may cover distinct schemas, failure modes, and causal structures. Agent-World [R06] and environment scaling [R10] make environment generation a research problem in its own right.",
            "A credible scaling study should report task and environment overlap, unique state transitions, tool families, held-out domains, and changes in simulator fidelity. It should isolate environment diversity from model size, data volume, and training budget. Results on a generated simulator support a claim about that simulator unless an external validation bridges the gap."
        ]),
        ("Curricula and the learnable frontier", [
            "A curriculum can focus learning on tasks that are neither trivial nor unreachable. AgentFrontier [R08] operationalizes this through learner-guided synthesis and a dynamic exam. This is an attractive approach because it treats difficulty as relative to a learner, rather than assigning a fixed level in advance.",
            "The calibration loop can also create circular evaluation. If the generator, learner, and verifier share assumptions, a task can look frontier-level while testing a narrow shared convention. Use multiple learner families and human calibration, test grader errors, and evaluate on tasks built outside the training loop. Keep stable anchors to distinguish improved competence from a moving target."
        ]),
        ("Task composition and long-horizon difficulty", [
            "AgentSynth [R09] illustrates how composing simple subtasks can produce challenging computer-use trajectories. The reported decline from 18% success at difficulty one to 4% at difficulty six is a result for its test setup. It suggests that dependencies and accumulated action opportunities matter, but subtask count alone is not a full measure of difficulty.",
            "Future task generators should vary dependency depth, ambiguity, interface changes, feedback quality, and recoverable faults independently. They should report whether each task is solvable, whether alternative correct paths exist, and how often a verifier accepts a near miss. Human audit remains important even when generation cost is low."
        ]),
        ("Continual pre-training and self-generated experience", [
            "AgentFounder [R07] places agentic behaviors in a continual pre-training stage; Role-Agent [R17] lets an agent and a synthetic environment co-evolve. These approaches broaden the experience available during learning. They also raise causal questions: do gains come from new knowledge, action formats, reward structure, or the co-adapting simulator?",
            "A useful study separates exposure from procedure learning. It can match facts and task families across training conditions, hold out the interface or workflow structure, and test corrections after disconfirming feedback. Self-generated experience needs an independent oracle or simulator audit; otherwise the model may learn to satisfy its own environment rather than the external task."
        ])
    ]),
    ("7. Evaluation design for agents", [
        ("A benchmark is a measurement instrument", [
            "A benchmark consists of a task sample, environment, allowed interactions, scoring rule, and operational procedure. Its score is meaningful only with these pieces. The agent evaluation survey [R12] maps the range of capability and benchmark types; General Agent Evaluation [R05] demonstrates why common protocols are needed when comparing systems.",
            "Benchmark authors should state the target population of tasks and the inference they intend readers to make. They should describe how prompts were authored, how state resets work, whether tools are live or simulated, what partial success means, and how invalid runs are counted. These choices are part of the scientific claim, not administrative details."
        ]),
        ("Matched comparisons and factorial designs", [
            "A matched comparison changes one factor while holding others stable. A factorial design can vary backbone model, architecture, tool interface, and environment to identify interactions. AgentArch [R18] compares multiple architecture combinations in enterprise workflows; [R05] connects agent protocols and benchmarks. Neither study eliminates the need to report each task family and budget.",
            "The same configuration may rank differently across environments. A leaderboard compresses this variation into a stable ordering only by choosing a task mix and aggregation rule. Readers should inspect the per-task results and cost-performance tradeoffs before transferring a rank to a new task."
        ]),
        ("Dynamic, generated, and held-out tests", [
            "Generated tests can keep pace with changing systems and cover more variants, but the evaluator may share blind spots with the generator. Held-out tasks reduce direct optimization but can still be related to familiar task templates. Dynamic tests need versioned task rules, documented sampling, calibrated verifiers, and independently held-out evaluations.",
            "A benchmark should reserve a test set that is not used to tune the model, scaffold, or verifier. If public exposure is unavoidable, rotate only part of the suite and retain anchor tasks. Report scores separately for the stable set and the new set; otherwise the time series conflates capability gain with test renewal."
        ]),
        ("Stochasticity, retries, and cost", [
            "Agent outcomes vary across runs because of sampling, environment state, tool availability, and timeouts. One successful trajectory is not a reliable success rate. Report the number of independent trials, the denominator, mean and spread, and representative failure cases. If reporting best-of-N, include N and its cost; do not compare it directly with pass@1.",
            "Budget matters. Report model calls, tool calls, wall-clock time, tokens or compute where meaningful, monetary cost, and human corrections. A system that succeeds only after expensive retries differs from one that succeeds on its first attempt. Cost is not separate from capability when the claim concerns practical autonomy."
        ]),
        ("Outcome and process should be paired", [
            "End-state grading answers whether the task was completed under the rubric. It does not show whether the agent used valid evidence, respected constraints, or followed a safe procedure. Process Evaluation for Agentic Systems [R19] provides a concrete motivation for trajectory-level checks; RDQA [R14] tracks source retrieval and localization; DAB [R20] exposes data-query behavior.",
            "Outcome and process measures can disagree, and that disagreement is informative. A compliant but unsuccessful agent needs better problem solving; a successful but noncompliant agent may be too risky for the setting. Reporting the dimensions separately supports deployment decisions without pretending a single score captures both."
        ])
    ]),
    ("8. Process, reliability, and provenance", [
        ("A correct answer can hide a bad trajectory", [
            "An agent may arrive at a correct answer by guessing, reading a leaked fragment, skipping an important check, or fabricating tool use. In low-stakes tasks, that may waste time; in medicine, law, finance, infrastructure, or research, the same pattern can cause harm. Outcome-only evaluation cannot distinguish sound procedure from lucky coincidence.",
            "The compliance checklist in [R19] offers a way to specify expected actions for a task and score their presence. The paper’s small study shows why the process score and final correctness are separate. A checklist must be designed for the actual risk: mandatory steps, acceptable alternatives, and the relative severity of omissions should be explicit."
        ]),
        ("Reliability includes detection and recovery", [
            "A robust agent is not one that never encounters errors. It should notice when an input is missing, a tool call fails, a source conflicts with memory, or a result does not match expectations. It should recover when recovery is safe and escalate when it is not. A benchmark should create controlled perturbations and measure detection, recovery, and erroneous continuation.",
            "Failure classes can include perception, retrieval, task interpretation, planning, tool selection, execution, state tracking, verification, policy compliance, communication, and stopping. These labels help analysis but do not prove causal origin. A single visible failure may result from several components; attribution needs ablations or other targeted experiments."
        ]),
        ("Source provenance and claim support", [
            "Source-grounded behavior requires a chain from claim to evidence. A useful trace records source identity, retrieval query, exact passage or media location, transformations applied, and the claim that relies on it. This is particularly important when an agent handles multimodal documents or structured databases. A link attached to an answer is not enough if the relevant value was never read.",
            "Counterfactual tests can assess source dependence. Change a number in a chart, remove a key sentence, or reorder sources and check whether the agent’s conclusion changes for the right reason. When sources disagree, score whether the agent identifies the conflict and states what cannot be resolved."
        ]),
        ("Logging, privacy, and audit", [
            "Trajectory data can expose private prompts, account information, or sensitive documents. Process evaluation should therefore define retention, access, redaction, and release rules. The research record should preserve the minimum information required to reproduce the scoring while protecting data that is not needed for the claim.",
            "An audit trail is not a proof of internal reasoning. It records observable inputs, actions, tool returns, and state changes. The paper should not imply that a natural-language rationale is a faithful causal account unless that claim is independently validated. Observable process is still valuable: it can identify prohibited actions and unsupported evidence use."
        ])
    ]),
    ("9. Specialist integration and real workflows", [
        ("Merging, roles, and multi-agent systems", [
            "A system may combine specialists through prompts, routing, delegation, or parameter merging. ARM [R15] studies role-conditioned neuron transplantation; Role-Agent [R17] explores agent–environment co-evolution; AgentArch [R18] compares orchestration and agent styles in enterprise tasks. These approaches target different failure sources and should not be conflated.",
            "The key questions are whether the combined system preserves each specialist’s strengths, adds transfer to held-out tasks, and remains easier or harder to audit. A merger can suffer negative transfer; a team can duplicate work or lose requirements at handoff. Evaluate the combined system against its components under matched compute and report per-domain profiles, coordination errors, latency, and total cost."
        ]),
        ("Enterprise workflows are a test setting, not a universal proxy", [
            "Enterprise tasks often require permissions, multiple systems, structured data, and partial completion. AgentArch [R18] makes configuration interactions visible, while DAB [R20] targets messy data integration across databases, inconsistent keys, text transformations, and domain knowledge. These are valuable test conditions because they reveal failures hidden by clean, single-database questions.",
            "A benchmark result does not transfer automatically to a company’s live workflow. Access policies, data quality, tool versions, escalation rules, and user expectations vary. Responsible deployment tests should include read-only scopes where possible, reversible operations, confirmation for irreversible writes, audit logs, and human correction. The system should ask for clarification when essential business context is missing."
        ]),
        ("Scientific work and research agents", [
            "Curation-Bench [R13] asks whether an agent can propose and test data-selection policies. This is more than coding: it involves designing an experiment, interpreting noisy feedback, and deciding which intervention is worth running. A credible evaluation must check the artifact and the reasoning that motivates it, and replicate a discovered policy on a fresh dataset.",
            "Research-agent evaluation should distinguish the ability to gather material, synthesize it faithfully, formulate a hypothesis, choose an experiment, execute it, and interpret the result. Visual or multimodal source work [R03, R14], persistent project state [R11], and process checks [R19] address different steps in that chain. A single “research success” label hides where the contribution actually occurs."
        ])
    ]),
    ("10. Cross-paper synthesis", [
        ("Convergence: systems are the unit of capability", [
            "The corpus repeatedly treats capability as a property of an assembled system. The cognitive framework [R01] names dimensions; environment papers [R06, R10] make task settings scalable; continual and frontier training [R07, R08] modify model experience; AgentSynth [R09] extends task trajectories; agent architectures [R05, R11, R16, R18] change control and state; evaluation papers [R12, R14, R19, R20] change what is counted.",
            "This convergence does not imply that all components are equally important. It means that an empirical claim should identify them. A model may be strong while its controller is brittle; a memory layer may preserve incorrect summaries; a verifier may accept a shortcut. The system boundary is necessary for replication and causal interpretation."
        ]),
        ("Convergence: evaluation must preserve structure", [
            "Several papers make hidden structure observable: profiles preserve capability differences [R01, R04]; benchmark protocols align agent comparisons [R05, R12]; task generators expose dependency depth [R08, R09]; process measures capture intermediate behavior [R14, R19]; databases and workflows expose executable steps [R18, R20]. The shared lesson is not simply “use more metrics.” It is to preserve the structure that explains a result.",
            "A benchmark should report enough detail to explain where success comes from. If a task requires retrieval, planning, a tool call, and verification, one final pass label is a poor diagnostic. The event trace and outcome rubric should be available for independent scoring, subject to privacy and security safeguards."
        ]),
        ("Differences: reports, methods, and empirical results", [
            "The source set includes conceptual proposals, a scenario report, a survey, benchmarks, and experiments. They support different levels of inference. A framework can recommend dimensions; a survey can organize prior work; a benchmark can test whether tasks discriminate among systems; an experiment can estimate effects in its conditions. Describing all of these as “proof” would overstate the evidence.",
            "The peer-reviewed ACL, EMNLP, ICLR, and AACL papers provide venue-based review, while the lab reports and preprints contribute timely proposals. Publication status should be carried into any downstream citation. Review does not remove limitations in sample, evaluator, or construct validity; preprint status does not mean a result is false. The reader needs both provenance and methodological appraisal."
        ]),
        ("What the corpus does not establish", [
            "None of these twenty papers establishes a single agreed AGI threshold, broad human-level performance across all domains, or reliable autonomous behavior in arbitrary environments. Several source papers use titles that refer to general or infinite-horizon agents, but titles express framing, not the breadth of evidence. Each experimental result remains bounded by model versions, tools, task families, and evaluators.",
            "This review also does not treat all “general agent” benchmarks as direct measures of AGI. Tool use and enterprise tasks illuminate consequential capabilities, but other domains—robotic manipulation, scientific experimentation, social interaction, long-term learning, and real-world safety—need separate measurement. A research program should expand coverage while keeping claims specific."
        ]),
        ("A layered evidence ladder", [
            "A useful evidence ladder starts with provenance and a clear construct, then asks whether tasks are valid and reproducible, whether results replicate across runs, whether transfer holds on externally authored tasks, and whether process remains reliable under perturbation. Each stage adds a different form of support. Strong evidence is not a larger title or more complex diagram; it is a chain from operational definition to observable and repeatable behavior.",
            "The ladder should be applied claim by claim. A system might have strong evidence for multi-database querying and weak evidence for social interaction. The correct summary is a profile of bounded findings, not a single general-purpose label. This is the central recommendation of the synthesis."
        ])
    ]),
    ("11. Proposed reference architecture for research", [
        ("A modular system boundary", [
            "The following architecture is a proposal synthesized from the corpus, not a result claimed by any one source. The system contains a task interpreter, evidence store, planner, tool router, state manager, verifier, policy monitor, and reporting interface. Each module has a documented input, output, and failure behavior. The model may implement several functions, but the experimental specification should identify which roles it performs.",
            "The task interpreter converts the user request into goals, constraints, and unknowns. It preserves the source text and asks for clarification when the goal is under-specified. The evidence store records observations, retrieved material, and provenance. The planner proposes actions and dependencies. A tool router checks that the requested action is allowed before execution. This design makes information flow inspectable."
        ]),
        ("State and evidence management", [
            "State should separate stable task facts, tentative hypotheses, and completed actions. Every stored item should record when it was created, which source or tool output supports it, and whether it has been checked. A revision should not silently overwrite a conflicting result. This supports the persistent-state motivation in [R11] while addressing corruption and staleness as evaluation targets.",
            "The evidence store should retain source identifiers and relevant locations, such as page number, image region, database row key, or video timestamp. Derived claims should link to the source data and transformation that produced them. When a transformation is ambiguous, the system should preserve alternatives or request review rather than hard-code an unsupported assumption."
        ]),
        ("Planning, execution, and verification", [
            "The planner decomposes a task into observable milestones. The controller records actions and returns, checks preconditions before risky operations, and verifies each milestone using an independent source where possible. Verification should not simply ask the same model to repeat its answer. It can use execution results, schema constraints, human review, or a separately calibrated grader.",
            "The policy monitor checks permissions and task-specific constraints before execution. It should distinguish read, reversible write, and irreversible action. A stop or escalation condition should be explicit. The user-facing report summarizes completed work, unresolved questions, and evidence, while keeping the underlying audit record available to an authorized reviewer."
        ]),
        ("Component contracts and fault isolation", [
            "Each module should expose a contract that can be tested: planner outputs list actions and dependencies; the router records the selected tool and authorization; state writes include provenance; the verifier returns a structured decision with evidence; the policy monitor can veto an action; the reporter differentiates verified from inferred claims. Contracts permit targeted ablations and make responsibility clearer when a system fails.",
            "Fault injection can test isolation. Supply a stale memory file, malformed tool result, contradictory source, slow service, or ambiguous task. The system should detect which signal failed and recover or stop. The test should observe whether an error remains local or contaminates later state. This is a systems reliability question, not an introspection claim."
        ])
    ]),
    ("12. Proposed evaluation protocol", [
        ("Step 1: preregister the claim and scope", [
            "Before running the study, write a one-sentence target claim. Define the capability, system boundary, task population, environment, permitted assistance, and intended inference. For example, “system X transfers a database-query strategy to held-out schemas” is testable; “system X is general” is not. The preregistration should name the main metric, exclusions, number of runs, and stopping rules.",
            "Publish an evidence map that shows which source papers motivate the task family and which gaps remain. Keep the proposal’s novelty distinct from prior published results. If a result will be used for a deployment decision, state the consequence of false success and false failure."
        ]),
        ("Step 2: build an independent task sample", [
            "Sample tasks from several families that test the intended capability, including anchor tasks and held-out combinations. Keep task generation separate from final evaluation where possible. Record task version, source, difficulty rationale, admissible strategies, and success rubric. Have independent reviewers check ambiguity, leakage, hidden shortcuts, and the quality of the expected answer.",
            "For generated tasks, validate the generator and verifier separately. A task is not valid merely because it is hard for one model. Compare multiple systems and human experts, audit false passes and false rejections, and report task coverage. Maintain a reserved external set that has not been used to tune prompts, generation rules, or evaluation thresholds."
        ]),
        ("Step 3: define matched system conditions", [
            "Specify model and scaffold versions and freeze them for the primary comparison. Match tool access, budget, context, retries, and state reset. If the question concerns architecture, use the same backbone where possible; if it concerns training, control data, updates, and inference conditions. If exact matching is impossible, state the confound rather than bury it.",
            "Include a baseline that reflects the actual alternative: a human using the same tools, a simpler agent, or a specialist model with the same budget. A system with additional model calls should not be compared as if it had no extra resources. Report the baseline’s setup and uncertainty as fully as the target system’s."
        ]),
        ("Step 4: capture outcomes and process", [
            "For each run, store the task and system identifiers, observation stream, actions, tool calls, results, state changes, retries, elapsed time, and final answer. Redact sensitive content under a stated policy. The trace should be enough for a second evaluator to reproduce the scoring and locate failures; it need not claim to reveal hidden cognition.",
            "Score final success, partial completion, constraint compliance, source support, detection, and recovery separately. Preserve accepted alternatives and adjudication notes. For process labels, use a written checklist and measure judge agreement on a sample. Report where process and outcome diverge; those disagreements often carry the main scientific insight."
        ]),
        ("Step 5: test transfer and perturbation", [
            "Vary one dimension at a time: a new tool schema, changed UI, reordered evidence, missing data, conflicting memory, latency, or a recoverable tool failure. Then test combinations after the component effects are known. This prevents a vague “robustness” claim from hiding which shift was actually tested.",
            "Measure zero-shot transfer, adaptation examples, time to recover, human interventions, and cost. A successful answer after repeated hints is different from one after a small self-directed adaptation. The study should preserve all attempts rather than selecting only the best trajectory."
        ]),
        ("Step 6: report limits and release artifacts", [
            "Release the task specification, scoring code, prompts or controller descriptions, system versions, trace schema, and analysis scripts where licensing and privacy permit. If some artifacts cannot be shared, provide a precise access statement and a substitute reproduction path. Identify the known limits of the benchmark and the scenarios not evaluated.",
            "Report an uncertainty-aware result with per-family metrics, confidence intervals, variance, cost, and representative failures. Do not translate a bounded benchmark result into a field-wide AGI statement. State what further evidence would change the conclusion."
        ])
    ]),
    ("13. Metric suite and reporting template", [
        ("Success and transfer", [
            "Task success is the proportion of valid runs that meet a preregistered completion rubric. State whether success is binary or graded, the denominator, and how timeouts or invalid traces count. Report both first-attempt success and any best-of-N measure, together with the retry budget. A score without its denominator cannot be interpreted.",
            "Transfer gap is the held-out score minus the matched in-distribution score. Report the two scores separately as well as the difference, because the same gap can arise from two very different performance levels. Transfer should be indexed by the changed factor—schema, tool, domain, interface, or task composition—not described only as “generalization.”"
        ]),
        ("Process and safety", [
            "Constraint compliance is the share of trajectories with no prohibited action. Checklist adherence is the weighted or unweighted proportion of required process checks satisfied; publish item weights and examples. Recovery rate is the proportion of injected recoverable faults after which the agent returns to a correct state and finishes safely. Detection rate should be reported separately from successful recovery.",
            "Severity-weighted failure is useful only if severity categories are defined in advance and reviewers agree on them. The report should include raw counts for rare severe failures, not only an average that dilutes them. For high-stakes applications, include the cost of false passes and false alarms."
        ]),
        ("Grounding, calibration, and efficiency", [
            "Claim support should be measured at the claim level: whether the cited material supports the statement, whether relevant evidence was missed, and whether uncertainty was calibrated. Retrieval, localization, and entailment are distinct stages. If automated judges are used, compare them with human annotations and report disagreement.",
            "Efficiency includes model calls, tool calls, latency, monetary cost, tokens or compute, and human review time. Calibration compares confidence with observed correctness on a held-out sample; if confidence is not exposed reliably, evaluate the system’s decision to answer, search, clarify, or abstain. The metric must match what the user actually observes."
        ]),
        ("Minimum reporting table", [
            "For each study, the core report should identify: task family; environment and version; system boundary; model and scaffold; sample size; run count; success and uncertainty; transfer condition; process and constraint results; failure categories; cost; evaluator validation; artifact availability; and study limitations. This list draws on the comparison needs visible across [R05, R12, R14, R18–R20].",
            "No single dashboard can answer every decision. A capability paper might emphasize breadth and transfer; a deployment evaluation might weight constraint compliance and recovery; a training paper might measure retained and newly learned skills. Publish a profile first and justify any composite second."
        ])
    ]),
    ("14. Research roadmap and falsifiable questions", [
        ("Near term: validate the instruments", [
            "First validate the measurement tools. Test whether cognitive tasks isolate the intended faculties [R01], whether jaggedness measures are stable under task resampling [R04], whether source-grounding judges catch unsupported claims [R14], and whether process checklists achieve agreement across reviewers [R19]. Publish annotation guidelines and error audits.",
            "Benchmark teams should test their own verifiers against hard negatives, alternate valid paths, and adversarial task variants. A benchmark that cannot distinguish a plausible shortcut from a valid solution cannot support a strong capability claim. Instrument quality is part of the research result."
        ]),
        ("Medium term: disentangle system components", [
            "Run matched studies varying one of model, controller, memory, tool protocol, environment diversity, or training data. Include ablations with equal resources and report interactions. Several recent systems change multiple components together, which is useful for building systems but makes causal attribution difficult.",
            "Test long-horizon recovery under state corruption, simulator changes, and tool failures. Compare simulation and live systems on paired safe tasks. Measure not only whether the agent eventually completes, but which interventions and costs were required."
        ]),
        ("Long term: test adaptation beyond curated tasks", [
            "Long-term work should evaluate new combinations of skills, changing tasks, embodied interaction, and social or collaborative settings. Reserve external evaluators and independent task creators. The goal is not to invent an impossible universal benchmark, but to estimate transfer across multiple controlled shifts and understand where the estimate remains weak.",
            "Study whether capability profiles improve real decisions. Give users actionable strengths, limitations, and uncertainty, then measure task assignment, checking behavior, and error severity. If profile disclosure does not change decisions, the profile may need redesign even if its measurement is statistically sound."
        ]),
        ("Falsifiable hypotheses for a research program", [
            "H1: Agents trained across structurally distinct tool environments will transfer better to held-out tool schemas than agents trained on the same number of near-duplicate environments. H2: Externalized state improves completion on interrupted long tasks, but stale-state perturbations reduce reliability unless the system maintains provenance and validation. Each hypothesis names a measurable comparison and a potential disconfirming outcome.",
            "H3: Process compliance predicts a subset of severe failures not captured by outcome accuracy. H4: Claim-level evidence alignment predicts robustness to source edits better than citation presence. H5: A merged specialist preserves capabilities only when evaluation includes unrelated held-out tasks. These hypotheses can be tested without assuming that success on the experiment equals AGI."
        ])
    ]),
    ("15. Limits, responsible interpretation, and authorship", [
        ("Review limitations", [
            "This review is focused and non-systematic. It synthesizes twenty supplied PDFs rather than exhaustively searching all work on AGI, cognitive science, robotics, safety, learning theory, or scaling. Some sources are preprints or lab reports; others are peer-reviewed conference papers. The corpus spans different task types and evaluation standards, which limits direct score comparisons.",
            "Model versions, tools, benchmarks, and source metadata can change. Conference proceedings dates may differ from earlier preprint dates. The bibliography records the version or venue represented by the supplied PDFs and links to official records where available. Readers preparing a formal thesis or publication should verify venue metadata and consult the current source versions."
        ]),
        ("What cannot be inferred", [
            "The papers do not jointly prove that AGI has been achieved, provide a consensus AGI definition, or certify any agent as safe for unsupervised high-stakes work. A successful benchmark run supports a claim about that model, system, task set, evaluator, and resource budget. Broader claims require independent replication and new evidence.",
            "Rashmi Ranjan Behera and Dr. Vidya Mohanty authored this review. Dr. Mohanty served as Academic Research Guide. The authors propose the evaluation framework in this paper. Citations identify the studies that supplied each reported benchmark result, and figure captions credit the researchers whose work is reproduced or adapted."
        ]),
        ("Figures and source reuse", [
            "The diagrams for papers [R01–R09] are original reviewer schematics based on the described methods; they are not copied source figures and do not report new experimental data. Figures from ACL Anthology papers [R10–R20] are reproduced with source-paper attribution under the ACL’s stated CC BY 4.0 policy, subject to the policy’s exclusion of third-party material. The associated source captions and references identify each reproduced figure.",
            "The review paraphrases research findings and does not reproduce the papers’ full prose. The original PDFs remain the authoritative sources for methods, numerical details, and licensing. Figure reproduction should be rechecked before redistribution if the source PDF identifies third-party content or a different license."
        ])
    ]),
    ("16. Conclusion", [
        ("A practical standard for progress claims", [
            "The twenty papers show why progress toward AGI is better treated as a research program than as a headline score. Capability taxonomies and profiles clarify what is measured; environments and curricula shape what agents can learn; architecture and state management shape how long they can act; task and source benchmarks test whether they can transfer; process evaluation checks how outcomes are reached.",
            "The next practical step is to make each claim narrower and each experiment more informative. Publish the system boundary, task distribution, run variance, transfer conditions, process trace, cost, evaluator validation, and known limits. Preserve the profile instead of hiding it behind one number. A result that reveals a gap is valuable evidence when it is reproducible and clearly bounded."
        ]),
        ("What would strengthen the evidence", [
            "Evidence would strengthen if independent groups reproduced results with different models and task creators; if generated tasks were evaluated outside their own synthesis loop; if profiles predicted real-world failures and improved human decisions; and if long-horizon systems recovered safely from stale state and tool failure. These are testable extensions suggested by the corpus, not conditions already satisfied by all sources.",
            "No single paper or organization can settle the question of AGI by authority alone. The credible path is cumulative: clear constructs, diverse tasks, independent verification, transparent failures, and claims calibrated to evidence. This review offers a working synthesis and an evaluation proposal for that path."
        ])
    ])
]


TECHNICAL_NOTES = {
1: [
    "A useful way to turn the framework into a study is to begin with a construct map. For each faculty, write down the observable behavior that would count as evidence, the competing explanation for that behavior, the type of task needed to distinguish them, and the scoring rule. A memory task, for example, should separate recall from recognition and should state whether outside tools are permitted. A planning task should distinguish a valid plan from a plan that happens to work after lucky action selection. This map prevents a list of domains from being mistaken for a validated battery.",
    "The framework’s human comparison also needs a careful sampling plan. Human performance varies by age, language, expertise, time, and accessibility conditions. If the comparison is intended as a benchmark reference, these factors should be documented and results should include uncertainty for the reference group. A model’s advantage over one human cohort does not imply a general cognitive advantage. The contribution of [R01] is the case for multidimensional measurement; its empirical value depends on developing tasks that are reliable and representative."
],
2: [
    "The report’s scenario framing is most useful when each proposed pathway is treated as a conditional chain. If digital copies accelerate collective problem solving, the chain still depends on reliable execution, shared information quality, available compute, and control over deployment. If recursive improvement is proposed, one must specify which parts of the system can modify themselves, how improvements are measured, and what prevents a local change from degrading other capabilities. These dependencies are more informative than a single timeline because they create observations that can be checked.",
    "The report also separates theoretical endpoints from systems that can be engineered under practical limits. That distinction should be retained when discussing superintelligence: a formal upper bound or idealized agent does not imply a feasible design. Future work could build a public scenario ledger with assumptions, indicators, and disconfirming evidence. Such a ledger would help policymakers update beliefs without confusing expert judgment with observed capability. The version date in the local PDF is especially important because the report can change over time."
],
3: [
    "The paper suggests several research questions that can be made experimentally precise: which visual regularities support transferable prediction; whether active observation improves performance under uncertainty; how visual geometry interacts with linguistic knowledge; and what representation supports action beyond a fixed dataset. Each can be tested with held-out environments, counterfactual scenes, and paired observation conditions. A system should be asked not only to describe a scene, but to predict what changes after an action and explain which evidence supports that prediction.",
    "A practical benchmark can include static images, video, multi-view observations, and controlled interaction. The evaluator can hold object identities fixed while changing the arrangement, or hold the goal fixed while obscuring one critical view. Score the final task and the observation policy. This would distinguish recognition shortcuts from world-state inference. Since [R03] is a white paper with multiple contributors and viewpoints, the review treats its proposals as an agenda and does not attribute every position in it to a single consensus architecture."
],
4: [
    "A profile is most useful when it is tied to decisions. For a specific user, a capability profile might need to show the probability of failure on relevant tasks, not a broad index across unrelated benchmarks. The same model can be acceptably uneven for brainstorming and unacceptably uneven for a controlled workflow. Risk-weighted summaries can help, but the weights must be justified and the raw task-level evidence kept visible.",
    "An empirical validation agenda for the proposed jaggedness measure has at least three parts. First, estimate test–retest stability when tasks are resampled. Second, test whether the index predicts failure in independent real-world tasks. Third, assess whether presenting profiles changes user choices and review effort. If the index changes substantially with task selection, it may describe the benchmark more than the model. The paper’s central warning remains useful: average scores should not be interpreted as uniform competence."
],
5: [
    "The unified protocol matters because a benchmark can otherwise be reachable only through its original harness. Translating one benchmark into several agent interfaces creates a common comparison point, but the adapter must preserve the benchmark’s original action semantics. A tool-calling agent may be given a native function interface while a CLI agent sees a shell; these are not equivalent unless permission, feedback, and available operations are matched.",
    "The factorial logic should extend to evaluator and budget. Run each agent design with multiple backbones, task families, and repeated seeds; fit the interactions rather than ranking systems by a single pooled average. Include tool-call failures and invalid episodes in the analysis. The open leaderboard is a useful infrastructure contribution if it keeps configuration and version histories accessible. Researchers adopting [R05] should still document any local changes to its harness and avoid treating a leaderboard score as a context-free model property."
],
6: [
    "A generated world has at least four measurable qualities: task validity, environmental fidelity, interaction diversity, and reset reproducibility. A large count of tools is not evidence for large interaction diversity. Researchers can cluster state transitions and compare environment schemas, then report the effective number of distinct task patterns. Verifiers should be tested on independently authored trajectories so that a generator does not certify its own conventions.",
    "A strong environment-scaling experiment would fix the agent and training budget, vary the amount and structural diversity of training environments, and test on unseen domains and interfaces. It would also include a simulator-to-live bridge test on safe operations. If the scaling curve saturates or reverses under a shift, that is important evidence about the limits of synthetic variety. The results of [R06] should be interpreted within its environment generator and not as a universal relationship between environment count and intelligence."
],
7: [
    "AgentFounder’s staged pipeline raises a training attribution question. Continual pre-training may teach action syntax, procedural routines, research knowledge, or patterns of tool feedback. A controlled study can construct matched variants that receive the same facts but different action trajectories, then compare transfer to novel tool schemas. Another variant can receive the same trajectory structure with held-out knowledge. This separates procedural learning from knowledge exposure.",
    "The right transfer tests should penalize unsupported claims and evaluate research trace quality. An agent should identify sources, distinguish retrieved evidence from background knowledge, and revise conclusions after a contradictory result. Long-context tasks can expose failures where a large accumulated record becomes difficult to use. Since the conference paper and earlier preprint versions differ in date, a replication should cite the exact version and checkpoint used rather than treating the label “ICLR 2026” as a complete method description."
],
8: [
    "The Zone of Proximal Development is a useful analogy but must be operationalized for machines. “Cannot solve alone but can solve with guidance” depends on how much guidance, which evaluator, and the number of attempts. A benchmark should define the assistance condition and measure the learning gain after it. The same item may be in one system’s frontier and far above another’s, so a dynamic exam must preserve comparable anchors.",
    "A curriculum pipeline can improve training efficiency while creating evaluation leakage. If the same learner participates in task selection, training, and final assessment, it may adapt to task-generation patterns. Use multiple learner models for calibration, reserve externally created tasks, and report results on a static anchor set. Human reviewers can audit whether synthesized items require the intended skill or merely longer answers. These checks clarify what the reported AgentFrontier gains mean beyond the particular engine and exam."
],
9: [
    "The reported fall from 18% to 4% across the six difficulty levels is important because it shows how quickly end-to-end completion can degrade as tasks lengthen. It does not by itself identify the cause. A study should record success by subtask, dependency, application, and recovery opportunity; then compare whether the failure curve comes from planning, tool execution, state tracking, or compounding errors.",
    "The reported generation cost of approximately 0.60 dollars per trajectory makes scale possible, but the full evaluation cost also includes human audits, task filtering, verifier calibration, and failed generations. Cost comparisons should include this quality-control work. The task generator should also create alternate valid paths and hidden-shortcut traps. AgentSynth is a useful example of measuring trajectory-level difficulty, while its external validity depends on UI realism and how well its verifier recognizes genuine completion."
],
10: [
    "The environment construction figures provide a useful design vocabulary: tool schema, matching, stateful backend, user task, and agent trajectory. Researchers can use this vocabulary to report an environment more precisely. A paper should specify how tool names, descriptions, argument types, and response formats are generated, and whether the agent can infer state changes from return values or must query the environment again.",
    "A robust scaling study would independently vary the number of environments and their structural diversity, include an out-of-distribution tool family, and use a second evaluator. It should compare simulated-user behavior with scripted oracle tasks so agent improvements are not confused with a more helpful simulator. The main question is not whether a larger environment bank improves a benchmark score, but whether interaction policies transfer when the state schema and feedback structure change."
],
11: [
    "File-centric state enables artifacts to outlive a particular model call. This is useful for literature review and other tasks that produce notes, tables, and intermediate summaries. Yet an agent may create a durable artifact that contains an undetected error. A proper benchmark should follow provenance through the chain: source observation, extraction, summary, later decision, and final report. It should test whether the system can identify which conclusions depend on a corrected or deleted source.",
    "Long-horizon evaluation should report completion by horizon length and interruption pattern. A system that completes a long task in one uninterrupted session may fail after a restart, and a system that resumes successfully may simply reload a correct checkpoint. Inject pauses, corrupted files, missing tools, and conflicting outputs. This makes “infinite-horizon” a tested claim about state continuity and recovery, rather than an architectural metaphor."
],
12: [
    "A survey is especially useful when its categories are converted into a coverage map. A study can annotate its tasks by capability, environment, interaction mode, duration, metric, and safety treatment. The map then shows whether a benchmark suite mostly samples web tasks or also tests memory, planning, and adaptation. It can expose overrepresentation of easy-to-automate tasks and areas where no independent evidence exists.",
    "The taxonomy should be updated as systems change. New tool interfaces and benchmark types can make older categories ambiguous. A versioned survey dataset with inclusion rules and official paper records would enable later researchers to update the landscape instead of repeating a search from scratch. The survey does not validate a benchmark, but it helps explain where the benchmark sits and what its score cannot speak for."
],
13: [
    "Data curation is a demanding agent task because the action has delayed feedback. The agent proposes a policy, runs a training process, waits for evaluation, interprets a noisy outcome, and chooses the next experiment. A short-horizon code benchmark may reward command execution but miss this experimental loop. Curation-Bench’s fixed target model and recipe are useful controls, yet the measured policy can still exploit the benchmark’s particular data and feedback.",
    "The strongest follow-up result would reproduce an agent-discovered policy on an independently held-out dataset and across multiple random seeds. It should retain selected-item manifests and training logs so improvement can be attributed to the policy rather than accidental data composition. A human-designed baseline should receive the same compute and evaluation budget. This would show whether the agent’s experimentation transfers, rather than only whether it can operate the benchmark interface."
],
14: [
    "RDQA’s three modalities make several pipeline stages visible: locating a source, finding the relevant detail, extracting evidence, and constructing an answer. Each stage can fail independently. A benchmark report should include stage-level recall and precision and then end-to-end task success. Otherwise a retrieval miss and an inference error appear as the same wrong answer, which makes system improvement harder to target.",
    "Process-localization metrics are promising if they map to actual evidence. Human reviewers can annotate the source span or media timestamp needed for each answer and compare it with the agent’s retrieval trace. Test whether the agent uses the correct evidence when several sources contain similar content. Add source edits and answerable/unanswerable controls so systems are rewarded for abstaining when the evidence is missing."
],
15: [
    "A neuron-transplantation method should be evaluated at more than one level. Intrinsic activation overlap is a method signal; benchmark performance is an outcome; robust transfer and retained specialties are the broader system questions. The first does not guarantee the second or third. A clear report should describe expert model selection, checkpoint compatibility, role definitions, merge hyperparameters, and failures during multi-turn interaction.",
    "Negative transfer may be asymmetric: a merged model might preserve common behavior but damage a rare specialist action that matters only at one point in a long trajectory. Report per-action and per-role diagnostics, not just end-task completion. Test new combinations of roles and tasks not used to choose neurons. If gains vanish when the task distribution changes, the method may be a useful specialist ensemble substitute without supporting a generalist claim."
],
16: [
    "OS-Symphony makes memory selection central to computer-use reliability. Short-term visual history can overflow; long-term memory can preserve stale screenshots or omit a critical change. A useful benchmark should compare the agent’s stored representation with the raw visual trajectory and ask whether a milestone summary preserves task-relevant state. It should measure what memory saves, what it discards, and whether the agent can recover omitted details.",
    "Ablation experiments should distinguish the effect of orchestration, reflection, memory, and tutorial retrieval. Match model calls and context budgets so a component is not credited simply for additional inference. Include UI variations, changed button locations, unexpected dialogs, and permission prompts. The published source figure illustrates an architecture problem; the reproduction in this review preserves that source figure and its caption, while the evaluation still needs independent tests of each design choice."
],
17: [
    "A co-evolving agent and environment can generate more varied feedback than a fixed simulator, but the co-evolution objective needs an independent anchor. If the simulator is rewarded for generating challenging tasks and the agent for solving them, both may adapt to an unrealistic convention. External task authors, real tool logs, or a separately validated state transition model can constrain this drift.",
    "Evaluate the environment as a predictive model. For a sampled set of states and actions, compare its predicted response with a reference environment or expert annotation. Report error by action family and state complexity. Then test the trained agent with a different simulator. If it retains performance, that is stronger evidence of learned strategy; if it fails, the original result may depend on idiosyncratic environment cues."
],
18: [
    "The eighteen configurations in AgentArch create an opportunity to study interactions, but the effective sample is limited by the number and diversity of workflow instances. Two workflow families can reveal architecture effects while leaving domain coverage narrow. Replication should add workflow families and hold out complete process templates, not only new surface wording.",
    "Enterprise agents must be evaluated on correct action boundaries. A workflow can be completed while an agent accesses or changes data it should not. Include permission constraints, confirmation requirements, partial execution, rollback, and audit visibility. Operational cost should include human review and rework. These extensions would keep the benchmark’s architecture focus while making reliability and governance part of the observed system behavior."
],
19: [
    "The feasibility study provides a concrete reason to keep process and outcome scores separate. In the reported example, GPT-4.1 receives a compliance score of 84/100 and solves the task, GPT-4.1-mini receives a compliance score of 97/100 but fails the task, and o3-mini receives 25/100 and also fails. These values are specific to one benchmark scenario and checklist; they are not general model rankings. The example demonstrates that following steps and reaching the right answer are related but distinct.",
    "The checklist itself remains a measurement proposal. Reviewers must decide whether a required action is truly mandatory, whether an alternative is acceptable, and how to weight a high-risk omission. Inter-annotator agreement and judge calibration should be reported. A process evaluator should be tested against intentionally flawed traces and good alternative traces, including cases where the final answer is wrong despite a sound procedure."
],
20: [
    "DAB’s contribution is to model messiness that clean text-to-SQL tasks can miss: multiple database systems, non-matching keys, unstructured text, and domain knowledge. Those properties produce dependencies between retrieval, transformation, querying, and explanation. The benchmark’s 104 questions across 17 datasets give a defined test bed; future work can measure which property accounts for the largest share of failures by controlled ablation.",
    "The error analysis points to planning and implementation as common failure sites and to regular-expression overuse for free-text extraction. A useful diagnostic benchmark would provide the same underlying data through alternative interfaces, compare schema descriptions with and without hints, and test whether the agent chooses a suitable extraction method. It should also check access rights and whether returned explanations match the executed query. DAB demonstrates that structured enterprise questions can require more than SQL generation."
]
}


REPLICATION_PLANS = {
1: "A replication should use the paper’s faculty definitions as the starting inventory and publish a task specification for every test item. Separate measures of knowledge, perception, planning, learning, and metacognitive awareness rather than inferring them from one end task. For each item, preserve the exact prompt, allowed tools, time limit, scoring rubric, and admissible alternatives. Recruit more than one human reference cohort where relevant and estimate variation by expertise and language. Then test a different task set from the same construct to see whether a profile is stable. The study should report the raw capability vector before any summary score and show whether conclusions change under alternative normalization or weighting. If the profile is intended to guide a threshold decision, estimate false classification rates near that boundary. A successful replication would establish measurement reliability for a particular battery, not a universal AGI scale.",
2: "A useful empirical follow-up to the report is a versioned scenario ledger. For each pathway—scaling, algorithmic improvement, faster replication, or recursive research—list required conditions, observable indicators, plausible blockers, and evidence that would weaken the pathway. Ask independent experts to rate assumptions separately from likelihood. Where a proposed advantage depends on replication or information sharing, test the measured precursor behavior in current systems rather than presuming it. The analysis should distinguish a possible pathway from a forecast and explain how institutional, economic, and physical constraints enter. Compare multiple scenarios using the same set of assumptions so that one pathway is not given more favorable treatment. This makes the report’s conceptual work more usable for governance while avoiding unsupported precision about dates.",
3: "A controlled visual-intelligence study could vary four factors independently: view availability, temporal continuity, action feedback, and language assistance. Use a set of scenes with stable ground truth and include unseen object arrangements. Ask the agent to predict a state change before executing an action, then compare prediction with observed outcome. Add counterfactual pairs where a small visual change should change the action. Include tasks where language priors are misleading and tasks where they are helpful. Human annotators should label the minimum visual evidence needed for each decision. Report perception, prediction, action, and correction separately. This study would convert the white paper’s broad agenda into measurable hypotheses and help determine whether the learned visual representation carries information beyond a text-based prior.",
4: "To validate a jaggedness measure, sample tasks from several domains and compute the index on repeated stratified samples. Report confidence intervals for both task scores and the index, and test sensitivity to the human cohort and normalization procedure. Then compare the index with two external outcomes: task-specific deployment failure and user review burden. A useful measure should retain meaning when the test set changes modestly and should add predictive value beyond the mean score. Present profiles to users in a randomized study and see whether they assign tasks more appropriately. If a single number does not improve decisions, keep the multidimensional profile and discard the summary. This would test the paper’s practical claim that jaggedness characterization aids safety and usability.",
5: "A replication of the unified agent comparison should freeze model snapshots where possible and record all protocol adapters. Run every agent style on the same task instances with the same tool permissions, context limits, retry rules, and cost ceiling. Include a native benchmark harness as a reference condition to quantify any distortion introduced by the unified interface. Use multiple backbones and multiple task families and analyze interaction effects rather than only aggregate rank. Report failure traces, invalid tasks, latency, tool errors, and cost per verified completion. Add an independent benchmark written after the adapter is frozen. This will reveal whether an apparent protocol advantage comes from the agent design, the adapter, or benchmark compatibility.",
6: "An environment-scaling replication should independently manipulate environment volume and structural diversity. Construct training banks with the same task count but different numbers of unique schemas, state transitions, and error types. Hold the model, training compute, and data exposure constant. Test on an unseen tool family and on paired simulated and live-safe tasks. Measure whether improvements transfer to changed argument names, missing fields, rate limits, and state resets. Publish the environment manifest, generator rules, and task overlap statistics. This design can test whether the scale effect reported in [R06] comes from more data, more diverse interactions, or repeated structures.",
7: "To isolate continual pre-training effects, create matched models with equal token and compute budgets. One group receives factual material, another receives agent trajectories with the same facts, and a third receives a mixture. Test on unfamiliar research domains and tools, and require the system to revise a report after evidence changes. Measure source selection, tool use, citation accuracy, error correction, and final answer quality. Use a fixed controller during the comparison so scaffold improvements do not confound training. Include a held-out benchmark created by an independent group. This will show whether continual pre-training provides reusable action knowledge rather than simply more facts or familiarity with the evaluation format.",
8: "For ZPD-guided synthesis, calibrate items with multiple learner models, a human panel, and a verifier that is not used in training. Define the guidance condition, number of trials, and the criterion for “learnable with help.” Keep a stable anchor set and reserve a dynamic task set. Evaluate training gains on external tasks that were neither generated nor scored by the same engine. Audit whether difficulty increases by cognitive demand rather than answer length or obscure knowledge. A reproduction should publish discarded items and verifier errors as well as retained data. These controls test whether the curriculum targets a general learning frontier or a boundary specific to one model and evaluator.",
9: "A follow-up to AgentSynth should separate task length from dependency depth. Create paired trajectories with equal numbers of actions but different dependency structure; vary recoverability, interface changes, and evidence ambiguity one at a time. Annotate success at the subtask level and classify failures by planning, retrieval, tool use, state tracking, and verification. Use a human-audited sample to estimate false verifier passes. Report all-in cost, including generation, filtering, failed attempts, and manual review. Finally, test the policy on applications and task grammars absent from synthesis. This can clarify whether the steep success drop reflects long sequence length, non-independent dependencies, or fragile UI execution.",
10: "Replicate environment-scaling results with a held-out environment grammar, not just new values in familiar schemas. Randomize tool names, nesting, optional parameters, and return formats while preserving task semantics. Include a second simulator and a small safe live set to estimate the fidelity gap. Ask independent experts to check state transitions and task solvability. Report the number of independent schemas and unique action patterns, not only tool count. Test zero-shot and limited-feedback adaptation separately. These additions can determine whether the paper’s environment pipeline improves transfer beyond its own simulated task family.",
11: "A long-horizon replication should compare file-centric state with context-only, structured-memory, and human-maintained baselines under equal storage and model-call budgets. Include interruptions at random milestones, corrupted notes, contradictory sources, updated documents, and missing tools. Measure accurate resume, time to recovery, state repair, and whether dependent conclusions are revised. For each task, retain a provenance graph from source to artifact to final claim. Report horizon length and failures per thousand actions, not only completion on one long task. This will clarify which parts of InfiAgent’s framework contribute to continuity and where persistent state introduces risk.",
12: "A survey update can be made reproducible by publishing its search queries, inclusion rules, benchmark metadata, and coding scheme. Two independent reviewers should classify a sample of papers by capability, environment, interaction, metric, and risk treatment, then resolve disagreements. Version the taxonomy and link each category to primary sources. A survey can also identify blind spots by estimating the share of work concentrated in static web or coding tasks compared with dynamic, embodied, or social settings. This would make the survey a maintained map of evaluation coverage rather than a one-time list of benchmarks.",
13: "A curation-agent replication should run the discovered policy on new datasets, new random seeds, and at least one different training recipe. Preserve the selected examples, rationale, code diff, training log, and evaluation outputs. Compare to a human curator with equal compute and feedback, and to a scripted baseline. Score whether each experiment is justified and whether the next policy change follows from observed outcomes. Include a no-improvement control and verify that benchmark feedback is not leaked to the agent through hidden metadata. The result would show whether agents can conduct reproducible data research rather than optimize a single curation score.",
14: "A replication of RDQA should evaluate retrieval, localization, evidence extraction, and answer construction separately. For documents, annotate page and bounding region; for video, annotate timestamps; for audio, annotate spans and speaker when relevant. Use source edits, conflicting sources, irrelevant high-ranking pages, and unanswerable questions. Measure unsupported claims and appropriate abstention, not only answer exact match. Have independent reviewers verify evidence spans. Report modality-specific results and the failure stages contributing to end-to-end errors. This would identify whether a model needs better search, perception, reasoning, or calibration.",
15: "An ARM replication should evaluate a matrix of expert checkpoints, role definitions, and held-out tasks. Before merging, document each specialist’s profile; after merging, measure both retained skills and new combinations. Compare with weight averaging, task arithmetic, a router, and a general model under equal compute. Test multi-turn tasks where one early role-critical action can affect later completion. Report activation selection, transplant ratios, and failures by role. If the merge score improves while rare specialist skills regress, that tradeoff should be explicit. The replication can establish the scope of role-conditioned transplantation without conflating merging with training.",
16: "For OS-Symphony, reproduce each memory and orchestration component with an ablation that matches model calls and visual context. Test across unseen applications, interface drift, pop-ups, permission dialogs, and changed layouts. Measure whether the memory accurately retains task-relevant visual state, whether tutorial retrieval is correct, and whether reflection catches an error before a write action. Use an independent verifier and keep rollback available for actions. Record latency and context consumption. This will establish whether the framework generalizes across computer-use environments or primarily improves the tasks and interfaces represented in its benchmark.",
17: "A Role-Agent replication should validate the generated environment independently. Compare predicted state transitions with an external oracle, human annotation, or a separately implemented simulator. Train an agent in the co-evolving environment and test it in a fixed external environment with changed dynamics. Run a control where the environment model is frozen and a control where the agent does not update. Measure reward, task completion, state prediction accuracy, and failure type. This will reveal whether co-evolution teaches reusable action policies or primarily aligns the agent to a particular synthetic world.",
18: "AgentArch can be extended with additional workflow families and organizational policies. Preserve the original eighteen configurations while adding held-out templates, varied permission models, partial completion, and exception handling. Ask a second organization to map its process into the benchmark and measure adaptation cost. Report not just successful end states but unauthorized actions, duplicated work, escalations, and human corrections. Cost should include review and rework. This would test whether the benchmark’s architecture findings are stable beyond its initial use cases.",
19: "A process-evaluation replication should use a larger set of tasks and at least two independent judges. Publish the checklist, applicability rules, risk weights, and examples of acceptable alternative paths. Measure inter-rater agreement and false compliance scores on deliberately flawed traces. Repeat with current models but preserve the source task and source versions. Analyze whether compliance predicts errors not captured by accuracy, and whether compliance criteria change by application risk. The reported model scores in the paper are useful feasibility evidence, but a validated risk measure needs more than one task and one checklist.",
20: "A DAB replication should hold out whole database schemas and vary each of the four workload properties independently. Add queries with ambiguous business definitions and cases where the correct action is to request clarification. Save SQL, intermediate rows, transformations, and final explanations. Audit joins and text extraction manually on a sample. Test access control and compare tool-assisted execution with a human data analyst using the same data. Report pass@1, repeated-run variance, and cost per correct answer. This will show whether performance transfers to a new data estate or depends on the benchmark’s particular open-source datasets."
}


DEEPER_SYNTHESIS = [
    ("A. Construct validity is a chain, not a label", [
        "A paper’s capability label is the beginning of the argument. The chain proceeds from construct to task, from task to observation, from observation to score, and from score to inference. A break at any stage weakens the claim. A task may contain the target ability but also reward an easier shortcut; a score may be reliable but measure the wrong thing; a well-measured benchmark may not represent deployment. The cognitive framework [R01], jaggedness proposal [R04], and survey [R12] help name the measurement space, but validity still depends on tested tasks.",
        "The practical repair is a construct-to-item table. For every capability, state its definition, example behavior, distractor explanation, test variation, score, and known confound. Independent reviewers can judge whether the test actually probes the construct. A second task family can test convergent behavior, while a control task checks that the score is not driven by unrelated reading or tool skills. This kind of evidence is more persuasive than broad language in a paper title.",
        "Construct maps should be versioned because capabilities and interfaces change. A benchmark that once isolated search may later be solved from memorized data. Researchers should monitor performance on fresh items and identify when a score no longer discriminates among systems. This is a measurement maintenance problem, not a reason to abandon benchmarks."
    ]),
    ("B. Evidence classes should not be collapsed", [
        "A framework, a benchmark, an experiment, a survey, and a scenario report answer different questions. Frameworks propose how to organize an idea; benchmarks create a repeatable instrument; experiments estimate system behavior under particular conditions; surveys map prior evidence; scenario reports examine possibilities and assumptions. The review therefore does not give each source one undifferentiated authority rank.",
        "A peer-reviewed venue adds editorial and reviewer scrutiny, but the evidence still depends on sample, design, and analysis. A preprint can be technically strong, but a reader should know it has not necessarily completed peer review. Lab affiliation is provenance, not a substitute for independent replication. These distinctions let readers use useful work without overstating it.",
        "A source record should include publication status, version, date, and official link. It should also record whether the paper is conceptual or empirical. A source with a carefully designed framework may be valuable despite having no experiment; a benchmark paper may be empirical but narrow. Evidence quality is multidimensional, and a single “professor or authority published this” test cannot answer whether the claim is supported."
    ]),
    ("C. Training and evaluation can become coupled", [
        "The corpus includes task-generation and curriculum approaches where a learner’s performance helps define what is generated next [R06, R08, R09, R17]. This can make training more adaptive, but it couples the training distribution to the evaluator. If the same verifier selects tasks, labels outcomes, and scores final performance, a model can improve at the evaluator’s conventions without gaining the broader skill intended.",
        "A clean experiment separates development, calibration, and final test. Task generators can use one learner set; verifiers can be checked against humans and hard negatives; final evaluation can use external task creators and preserved anchors. If the intended claim is open-ended learning, a static held-out set is not sufficient by itself, but an independent evaluator is still needed.",
        "The paper should report the full path from generation to evaluation: seeds, filtering, retries, discarded items, verifier accuracy, and test exposure. This information helps readers understand whether the result came from a new learning mechanism, a favorable task distribution, or both."
    ]),
    ("D. A capability profile should include cost and uncertainty", [
        "A system profile that records only success misses the resources used to obtain it. An agent may rely on a long chain of model calls, repeated searches, high token budgets, and human cleanup. For practical autonomy, these are part of performance. Report cost per verified completion and time to successful recovery, not simply the best achieved answer.",
        "Uncertainty should be shown for task families and overall scores. Repeated runs estimate stochastic variance; stratified task samples estimate coverage uncertainty; judge comparisons estimate scoring uncertainty. These are different sources of uncertainty and should not be collapsed. Small samples can produce precise-looking but unstable rankings.",
        "If a system uses a best-of-N strategy or retries until a verifier passes, the evaluation should count all attempts and resources. Report first-attempt performance separately. This allows readers to compare systems with different retry strategies without confusing capability with budget."
    ]),
    ("E. Process checks need task-specific risk models", [
        "Process evaluation [R19] raises an important idea: correct outcomes can hide unacceptable behavior. A checklist must nonetheless be tied to the application. A medical task may require current source retrieval; a simple unit conversion may not. A financial transfer may require confirmation before a write action; a read-only summary may not. The same omission can have different risk depending on context.",
        "Checklist design should distinguish mandatory steps, recommended steps, and acceptable alternatives. Weights should reflect risk, and high-risk violations should be reported as counts or gates rather than diluted by many low-risk checks. A high compliance average should not be interpreted as safe if one critical step was skipped.",
        "The evaluator should also consider user intent and permissions. A system that refuses an unauthorized action may be correct even if it does not complete the requested workflow. Task success definitions should reward safe clarification, deferral, and refusal when appropriate."
    ]),
    ("F. The strongest claim is often a bounded profile", [
        "A general intelligence label invites broad interpretation, while the evidence in these papers is usually bounded. The most accurate conclusion is often a capability profile: which task families were tested, where transfer occurred, which constraints were satisfied, how often failures happened, and what budget was used. This is not a retreat from ambitious research; it is a way to make progress comparable.",
        "A profile can support sharper hypotheses. If a system transfers across schemas but fails after an interruption, memory reliability becomes the next target. If it retrieves a source but makes unsupported claims, evidence interpretation becomes the bottleneck. If a merged model gains overall score but loses rare actions, integration needs targeted work. Each failure narrows the problem.",
        "The profile format also reduces incentives to overclaim. It permits meaningful contributions without declaring a universal milestone. The field can accumulate evidence across cognition, visual learning, tools, environments, and human oversight while remaining honest about what remains unknown."
    ])
]


CROSS_STUDY_ANALYSES = [
    ("Constructs to tasks: connecting cognitive frameworks to benchmarks", [
        "The cognitive map in [R01] and jaggedness analysis in [R04] operate at a higher level than any single task. A benchmark needs to connect these ideas to observable actions. One practical chain is: name a construct, state the hypothesized behavior, choose task variants that challenge it, identify competing explanations, define the score, and check whether the score predicts performance beyond the original items. This chain makes construct validity testable rather than rhetorical.",
        "For example, “memory” can refer to retaining a fact, locating it in an external artifact, updating it after correction, or knowing when it is absent. A long-context benchmark tests only part of this space. An external-file agent may solve a retrieval task while failing to detect stale state. A capability profile should therefore label subskills and conditions rather than publish one undifferentiated memory value.",
        "The survey [R12] can help map such tasks to the broader field, but survey categories do not replace direct validation. A coherent test suite needs both variety and interpretability: enough task families to avoid narrow overfitting, and enough control to explain which capability changed. When one task is reused across many papers, the paper should still document its current version and exposure."
    ]),
    ("Architecture comparisons: separating model, controller, and budget", [
        "Agent comparisons are difficult because the architecture is often bundled with the model, interface, and task wrapper. A model may appear better because its tool adapter retries automatically; an agent may appear more autonomous because the environment offers richer feedback. General Agent Evaluation [R05] addresses interface comparison, while AgentArch [R18] varies architectural dimensions in workflow settings. The next step is to carry matched comparisons across additional settings and budgets.",
        "An informative design varies a small factorial set: backbone, interaction protocol, memory policy, and tool budget. Not every combination is affordable, so authors should justify the selected contrasts. Results can be summarized with interaction plots or per-task tables. The paper should describe how the adapter translates each tool call and whether errors are exposed equally. Without this, a “protocol” effect may be a difference in information supplied to the agent.",
        "Budget matching must count more than model parameters. Total reasoning calls, retries, context length, tools, execution time, and human interventions influence success. If a system is intended for practice, cost per verified completion is a useful metric. If it is intended to test a capability in principle, the report should still show the resources used so readers know what kind of evidence they are seeing."
    ]),
    ("Environment scaling: diversity, fidelity, and evaluator independence", [
        "Environment-scaling papers [R06, R10, R17] raise three distinct questions. Does more environment data improve performance? Does structural diversity matter beyond volume? Do learned behaviors transfer to environments whose dynamics differ from those used in training? A simple count answers none of these by itself. Report environment families, action schemas, state variables, reset behavior, and overlap between training and evaluation.",
        "Fidelity is a separate dimension. A simulator can be useful without being realistic in every detail, provided the inference is limited to its scope. To claim transfer toward live services, compare paired tasks and classify mismatches such as rate limits, authentication, latency, unexpected state, or missing feedback. The agent should be evaluated without granting access to hidden simulator state unavailable in deployment.",
        "Evaluator independence guards against self-confirming benchmarks. A generator, agent, and verifier that share a model or prompt family can agree for the wrong reason. Independent task authoring, human spot checks, alternative verifiers, and external test sets each reduce a different risk. These procedures cost time, so an evaluation report should include the cost of quality assurance as part of benchmark construction."
    ]),
    ("Long-horizon state: persistence is capability and liability", [
        "Persistent state can make a long task possible by reducing repeated work and preserving decisions [R11, R16]. It also creates a path for error propagation. An inaccurate note may be reused, become a premise for later plans, and survive after the source changes. The evaluation target must therefore include provenance, freshness, contradiction handling, and recovery, not only recall.",
        "A controlled test can seed an agent with a correct note, a stale note, or a note that conflicts with a new source. The agent then receives a task whose answer depends on choosing the current evidence. Measure whether it detects the conflict, updates the artifact, revises dependent conclusions, and reports uncertainty. Repeat after interruption to test whether recovery depends on hidden short-term context.",
        "Storage also increases security and privacy considerations. A system may retain more user data than needed or expose a prior task through a shared file. The experimental protocol should state retention scope, access control, redaction, and deletion. These are system behaviors that should be tested alongside throughput and completion."
    ]),
    ("Grounding and process: the source-to-action chain", [
        "Source-grounded tasks [R14, R20] and process evaluation [R19] can be joined as a chain: the agent chooses a source, localizes evidence, transforms it, makes a claim, and selects an action. A failure may occur at any link. Outcome-only scoring hides the path; a process checklist without evidence support may reward mechanical compliance. An integrated trace can score each stage while preserving separate metrics.",
        "The trace schema should include source identifiers, retrieval queries, quoted or extracted spans, transformations, intermediate values, tool outputs, and final claims. For databases it can include SQL text, row counts, and schema assumptions; for video it can include timestamps; for documents it can include page and region. A reviewer can then evaluate support without inferring private internal reasoning.",
        "Risk should shape the required process. A brainstorming task may permit approximate evidence gathering. A medication or financial transaction may require current authoritative sources, a second check, and user confirmation. Checklists need explicit task-specific conditions, and acceptable alternatives should be represented. A universal process score would erase these differences."
    ]),
    ("Specialization versus generality: preserve capability during integration", [
        "Training, merging, roles, and delegation all attempt to combine capabilities [R07, R15–R18]. The resulting system should be evaluated both for new task coverage and for retained skills. A single aggregate can hide regressions on infrequent tasks. Compare a combined model with each specialist, a general backbone, and a simple router under matched budgets.",
        "The integration itself can introduce new risks. Teams can create incompatible state; role prompts can encourage confident but narrow behavior; merging can alter outputs in high-dependency actions; co-evolving environments can distort objectives. Failure analysis should inspect the handoff or merge mechanism, not only the final answer.",
        "Generality should be tested on a novel combination of roles or tasks, not just the union of specialist benchmarks. If a system can route familiar requests but cannot adapt when two capabilities must be combined, it may be a useful collection of specialists without being a general agent. Reports should describe this distinction without diminishing the practical value of specialization."
    ])
]


APPENDICES = [
    ("Appendix A. Sampling a benchmark that can support transfer claims", [
        "A benchmark intended to support a transfer claim should sample task families before the final model is evaluated. Begin with the target capability and list the conditions that may change: domain vocabulary, tool schema, observation format, dependency structure, data quality, and feedback. Select several representative changes and reserve at least one outside the development loop. This sampling plan should be documented as a table or task manifest.",
        "A useful design includes anchors, controlled variants, and external tasks. Anchors support longitudinal comparison. Controlled variants isolate one factor, such as a changed join key or altered UI. External tasks test whether the system carries a strategy to a new author or environment. None alone is sufficient: anchors can saturate, variants can be too artificial, and external tasks can be poorly matched. A combination gives more interpretable evidence.",
        "Task difficulty should be reviewed for construct relevance. Extra steps, long prompts, or unusual formatting can make a task harder without measuring the intended capability. Human experts can identify shortcuts, ambiguity, and alternate correct paths. Pilot studies should estimate whether the task distinguishes systems and whether the verifier agrees with expert judgments. A paper should report this validation rather than treating item count as a quality measure."
    ]),
    ("Appendix B. Trace schema for tool-using and multimodal agents", [
        "A minimal episode record includes an episode identifier, task version, model and controller version, tool schema, initial state, sequence number, timestamp, observation, action, tool result, state change, retry or error, verifier decision, and final outcome. Each state write should identify its source and whether it was validated. For multimodal tasks, preserve the source file identifier and the relevant page coordinates, frame interval, or audio segment.",
        "The trace should distinguish raw observation from the agent’s extracted representation and from a later summary. If sensitive data are present, store a redacted copy for analysis and document which fields were removed. Redaction should not silently change the task evidence. Access, retention, and deletion rules should be specified before data collection.",
        "A trace is not a transcript of hidden thought. It is a record of external behavior and system state. Authors should avoid claims that the trace reveals all internal reasoning. Its purpose is more modest and more reproducible: another evaluator can determine which tools were called, which evidence was available, which steps were skipped, and how the final result was scored."
    ]),
    ("Appendix C. Worked metric definitions", [
        "Let each task have n independent runs, with success indicator s_i in {0,1}. First-attempt success is the number of successful first runs divided by the number of valid first runs, with invalid runs and timeouts reported separately. If repeated attempts are allowed, report both the probability that any of N attempts succeeds and the total resource cost. A best-of-N score must not be compared to a single-attempt result without stating N.",
        "Transfer gap is the held-out success rate minus the in-distribution success rate under matched resources. Report the two rates and the exact shift. A small gap at low performance is not equivalent to a high held-out score. Recovery rate is successful safe recovery after an injected fault divided by runs with recoverable faults. Detection rate is the fraction of those faults that the agent explicitly identifies; a detected but mishandled fault remains a recovery failure.",
        "Process adherence can be defined as the sum of satisfied checklist weights divided by the sum of applicable weights. If weights vary by risk, publish the weights, applicability rules, and sensitivity to equal weighting. Constraint compliance is stricter: report the share of episodes with no prohibited action, plus counts by violation severity. Do not mix a process adherence average with an all-or-nothing safety gate without explaining the decision rule.",
        "Grounding can be decomposed into retrieval recall, evidence localization, claim support, and uncertainty calibration. For each claim, a human or validated evaluator identifies the evidence that supports it. Report unsupported-claim rate and missed-evidence rate. Citation precision measures whether cited locations support the claims; citation presence alone does not. The evaluator’s agreement with human judgment must be stated."
    ]),
    ("Appendix D. Verifier and judge validation", [
        "A verifier should be evaluated on a stratified sample that includes straightforward successes, plausible near misses, alternate correct solutions, malformed outputs, and prohibited actions. Human annotators should apply the same rubric independently. Estimate agreement and inspect disagreements, because a single aggregate agreement statistic can hide systematic errors on critical cases.",
        "For an automated judge, report the underlying model, prompt, temperature or deterministic settings, and any evidence shown to it. Test paraphrased trajectories and changed ordering. A judge that sees the final answer but not the trace cannot validate process compliance. A judge that sees an answer and its citation but not the source cannot validate grounding. The evaluation input must contain the evidence required by the claim.",
        "False passes and false failures should be reported by category. In a safety evaluation, a false pass on a prohibited action may matter more than a false failure on a harmless alternate path. If a benchmark’s central claim changes under plausible adjudication alternatives, report that sensitivity. The verifier is part of the instrument and deserves the same scrutiny as the agent."
    ]),
    ("Appendix E. Reproducibility and version control", [
        "A reproducible agent study records immutable identifiers for the model, prompt, code, tool API, environment, task data, evaluator, and analysis. If a provider updates a model behind a stable name, record the access date and any available revision. Pin tool dependencies where possible. A changed benchmark rubric should create a new version rather than silently overwriting the old one.",
        "The released package should include a manifest that maps each reported result to exact task IDs and run IDs. Keep failed runs, invalid episodes, and timeouts in the package or explain why they cannot be shared. A result table should state whether it uses all valid attempts, an average, or a selected run.",
        "If commercial or privacy constraints prevent release, provide a precise reason and a substitute route such as a controlled evaluator endpoint, synthetic data with the same schema, or a trusted replication protocol. Reproducibility is not binary; clear boundaries let readers understand what can be independently checked."
    ]),
    ("Appendix F. Deployment-oriented threat model", [
        "Threat modeling begins with action scope. List which operations read data, create reversible changes, or cause irreversible effects. Identify who can authorize each operation, what confirmation is required, and how the action can be undone. A benchmark should include cases where the correct behavior is to ask for permission, refuse an unsafe action, or stop because a source is missing.",
        "Consider data threats such as stale, conflicting, or adversarial documents; tool threats such as changed APIs, denied permissions, and malicious outputs; and system threats such as memory leakage, hallucinated tool use, or failure to stop. The evaluation should measure prevention, detection, escalation, and recovery separately.",
        "A deployment claim should be bounded by tested permissions and user population. A read-only sandbox does not establish safe behavior when write access is enabled. A short controlled task does not establish reliability over long workflows. Report which incidents were simulated and which were not observed; absence of failure in a small sample is not evidence that rare failure is impossible."
    ]),
    ("Appendix G. Source quality and evidence-status rubric", [
        "For each source, record the official publication venue or institution, version date, author list, peer-review status, and stable link. Then record the paper type: framework, report, survey, benchmark, or experiment. These fields describe provenance and method. They should not be compressed into a single “authority” score.",
        "For empirical claims, also record the model and version, task set, sample size, baseline, repetitions, evaluator, cost, and artifacts. For conceptual claims, record definitions, assumptions, scope, and falsifiable implications. For benchmark papers, record task construction, verification, exposure, and external validation. This rubric helps distinguish a useful proposal from evidence of system behavior.",
        "Conference review is a meaningful quality-control signal, but it does not guarantee that every result replicates or transfers. A preprint can contain valuable and accurate work, but its status should be transparent. The review uses source status as context while judging the claims by what the paper actually tests."
    ]),
    ("Appendix H. Figure and diagram provenance", [
        "Review schematics for [R01–R09] were drawn for this document to explain the central relationship described in each paper. They are simplified diagrams and do not reproduce the source figure or any experiment output. Their captions identify the related paper and their schematic status.",
        "Figures from [R10–R20] are cropped reproductions of Fig. 1 from the supplied ACL Anthology PDFs and retain the source paper’s figure content and caption within the crop. Each is followed by an attribution. The ACL Anthology copyright FAQ states that ACL Anthology papers are under CC BY 4.0, while third-party content can be excluded; the paper-specific source should be checked where a figure includes material credited to another party [L1].",
        "For any further redistribution, check the applicable source license and any third-party credit visible in the original paper. The reproduced figures are not evidence generated by this review. Their purpose is to preserve the source authors’ visual explanation alongside a separate, critical synthesis."
    ])
]


APPENDIX_WORKED_EXAMPLES = [
    ("Appendix I. Building a multidimensional task sample", [
        "A practical task sample can be organized as a matrix with capability on one axis and task condition on the other. Candidate capability families may include perceptual grounding, memory, learning from feedback, planning, tool use, source evaluation, and communication. Conditions may include static versus dynamic state, familiar versus held-out interface, single-step versus dependent sequence, clean versus noisy evidence, and supported versus unsupported answerability. Not every cell needs equal representation, but every inclusion choice should be visible.",
        "Choose task items to test the intended claim rather than to fill a visually complete grid. A study about transfer across tool schemas should include multiple held-out schemas and matched familiar schemas. A study about long-term memory should include interruption, state update, and contradiction conditions. A study about grounded answers should include source conflicts and unanswerable questions. The matrix is a coverage aid, not an implicit claim that all cells represent one latent intelligence measure.",
        "For each task, maintain a specification containing prompt, initial state, allowed actions, evidence, completion condition, alternative valid paths, known shortcuts, scoring rules, and version. A separate reviewer should attempt to solve the task through shortcuts and identify ambiguous criteria. If a task is changed after pilot results, record the revision and preserve the original version for comparison."
    ]),
    ("Appendix J. Statistical reporting for stochastic agents", [
        "Run-level variance is part of the result when systems sample outputs or interact with nondeterministic tools. Report the number of runs and independent task items. Do not treat repeated runs of one task as independent task samples; they estimate run variability, not coverage uncertainty. When tasks are clustered by family, uncertainty estimates should respect that structure rather than resampling individual trajectories as though every item were unrelated.",
        "For a binary completion result, show the observed proportion and an interval estimate. For continuous rubric scores, report the distribution, central tendency, and dispersion. Include per-task-family estimates so the aggregate does not hide a weak category. If only a small sample is feasible, state the resulting interval width and avoid precise rank claims.",
        "For best-of-N evaluation, present success at each attempt budget and total resources. A retry curve can show whether a system improves steadily or only rarely finds a successful trajectory. Compare systems at matched budgets. If the verifier drives retries, validate it because a false pass or fail changes the observed curve.",
        "When reporting training gains, use multiple seeds where possible and retain pre-training capability baselines. Measure both new performance and forgetting in unrelated families. A positive gain on the target benchmark can coincide with calibration loss or safety regressions; these dimensions should appear in the same result table."
    ]),
    ("Appendix K. Failure annotation and adjudication protocol", [
        "Start with an annotation manual that defines each failure category and gives positive, negative, and borderline examples. Separate the observable event from its inferred cause. For example, “the agent executed a query without checking the join key” is observable; “the planner failed” is a causal hypothesis that needs additional evidence. This distinction reduces overconfident blame assignment.",
        "Annotators should label stage, severity, detectability, recoverability, and policy relevance. Multiple labels can apply to one trajectory. The protocol should state whether a failure is counted when it is self-corrected before the final answer. An action that is corrected may still matter if it caused an irreversible state change or exposed private data.",
        "Double-annotate a stratified subset and report agreement by category. Resolve disagreements with a documented adjudication step, and retain the original labels. For process evaluation, include alternate valid procedures so judges do not penalize a safe path simply because it differs from the template. For grounding, adjudicate whether the evidence entails the claim, not just whether it is topically related.",
        "Publish uncertainty around rare failures. A small study with no observed severe violations cannot establish that the true rate is zero. Provide the denominator and, where appropriate, an upper confidence bound. Describe simulated violations separately from live incidents."
    ]),
    ("Appendix L. Factorial design for transfer studies", [
        "A compact transfer study can use a baseline environment and several shifts: a renamed or reorganized tool schema, a new domain with the same action grammar, a changed interface, a multi-step dependency, and a recoverable tool fault. First measure each shift independently. Then combine selected shifts to test interaction effects. This sequence helps identify whether a model fails because of one unfamiliar feature or because several demands compound.",
        "Use a matched training and evaluation design. Keep model, controller, and tool budget fixed while changing the environment. If the agent adapts from demonstrations, control the number and content of examples. Report zero-shot, few-shot, and post-feedback results separately. A transfer claim should specify what information the system receives at each stage.",
        "The evaluation should include a task family not authored by the team that built the training environment. Where possible, use a second simulator or a safe live service for a bridge test. A discrepancy between synthetic and live results is useful evidence about environment fidelity. Do not conceal it by averaging the two settings.",
        "Analysis should preserve both completion and behavior. An agent may fail safely by asking for clarification, or complete by violating a constraint. Report completion, process, recovery, and resources as separate axes. This distinguishes capability gaps from good refusal and unsafe success."
    ]),
    ("Appendix M. Cost accounting for agentic work", [
        "Agent cost includes more than model tokens. Record model calls, tool calls, context and output tokens where available, code execution, search or API usage, wall-clock time, monetary charges, storage, and human review or repair. If the system uses parallel workers, report peak concurrency and total consumed resources. This allows readers to compare both economic and operational efficiency.",
        "Calculate cost per verified completion using the same adjudication procedure across systems. A system that returns many plausible but incorrect answers may appear cheap if only raw output volume is counted. A system that refuses when uncertain may have lower completion but lower rework. The intended use determines which tradeoff matters.",
        "Report amortized training cost separately from inference cost. For training papers such as [R07] or environment-generation work such as [R06, R08, R09], construction and filtering costs can be large relative to a single evaluation run. Include human annotation and failed generation attempts. An apparently low cost per trajectory should not exclude quality assurance necessary to make the trajectory useful."
    ]),
    ("Appendix N. A source-grounding audit", [
        "For each answer, break it into atomic claims and record the source span that supports each one. Label evidence as direct, inferential, conflicting, or absent. Direct support restates an explicit source fact; inferential support combines evidence under a stated rule; conflicting evidence requires qualification; absent evidence should lead to uncertainty or retrieval. This gives evaluators a common rubric.",
        "A grounding audit should inspect both evidence selection and evidence use. A system may retrieve the correct passage but misunderstand it; it may cite a passage that mentions the right topic but not the claimed number; or it may correctly reason from a table while citing only the accompanying abstract. These are different failure modes and need separate labels.",
        "Test grounding with counterfactual source edits. Change a value or remove a key sentence and ask the same question. The agent should update its claim if the altered evidence matters. Use distractor sources that contain similar entities but different facts. Include cases where sources conflict and where no source supports a definitive answer. These conditions test whether the system is conditioned on evidence rather than producing a fluent prior answer.",
        "For multimodal sources, preserve location metadata. Include page coordinates for document regions, timestamp ranges for video, and time spans or speakers for audio. Human auditors should be able to open the exact evidence. The benchmark should publish scoring examples and automated-judge validation."
    ]),
    ("Appendix O. A persistent-state audit", [
        "Persistent memory should be audited as a data product. For every stored item, record source, time, confidence or validation status, and the task context in which it was created. Identify whether it is a raw observation, derived fact, hypothesis, or task plan. This makes it easier to detect when a derived claim no longer follows from the current source.",
        "A test suite can seed the workspace with correct, stale, incomplete, and contradictory artifacts. The agent should classify the state, seek confirmation where necessary, update dependencies, and document the correction. Measure propagation: how many later decisions rely on a corrupted note before the agent detects it? Also measure whether the agent can resume after a planned interruption without repeating costly work.",
        "Privacy and retention should be in scope. Test whether one task’s state leaks into another user’s session, whether secrets are retained unnecessarily, and whether deletion removes derived artifacts. A memory system that improves continuity but widens data exposure has a different risk profile from a context-only baseline.",
        "Persistent-state results should report storage size, retrieval cost, update frequency, correction rate, and human cleanup. The performance measure should distinguish a clean resume from successful recovery after a fault."
    ]),
    ("Appendix P. A human review and escalation protocol", [
        "Human review is not a single binary switch. Define which events require confirmation: irreversible write actions, low-confidence evidence, source conflicts, permission changes, high-severity process deviations, or uncertain identity. The agent should communicate what is known, what remains unresolved, and which action needs approval. The confirmation prompt should make the consequence clear.",
        "A study should measure the quality of escalation. Does the agent ask at the right time, provide relevant context, and avoid nudging a user toward an unsafe action? Does it continue to act while waiting? Does it respect a denial? These behaviors can be tested in controlled tasks and should be part of process evaluation for consequential workflows.",
        "Human intervention also changes the task budget. Record time spent reviewing, corrections made, and whether the reviewer had enough evidence to decide. Compare end-to-end workflows with human-only baselines. If a person must redo most of the work, the agent’s raw completion score overstates practical autonomy.",
        "Escalation rules should be auditable and updated when tools or data change. A benchmark can evaluate whether the system pauses when a required confirmation is absent and whether it can resume safely once approval is granted."
    ]),
    ("Appendix Q. Translating benchmark evidence into a bounded claim", [
        "A bounded claim has five parts: the named system, the task population, the conditions, the observed result, and the known exclusions. For example, “The tested configuration completed a given fraction of held-out database tasks under a fixed tool budget, with these failure classes” is more informative than “the model is a general data agent.” The former can be compared, replicated, and updated.",
        "Avoid implying that a publication venue or author affiliation validates results outside the paper’s scope. Cite provenance and methods separately. A peer-reviewed conference paper is important evidence that the work passed a review process; external replication and construct validity determine how far its result can be generalized.",
        "When communicating to users, explain what task families the system is suited for, what review remains necessary, and what changes would invalidate the evidence. A benchmark profile can support conditional deployment guidance, but it cannot guarantee future behavior after a model update or tool change.",
        "A strong report also includes the observation that would change the conclusion. If the paper claims transfer across tools, a failure on an unseen tool family matters. If it claims safe process, a critical skipped step matters. This makes limitations falsifiable and helps the next study advance the evidence."
    ])
]


SOURCE_INTERPRETATIONS = {
1: "A point of comparison with [R04] is that cognitive breadth and jaggedness answer different measurement questions. The taxonomy gives a structured set of domains; the jaggedness profile describes dispersion across observed performance. A study could combine them by sampling multiple tasks per faculty and reporting within-faculty and between-faculty variation. This would reveal whether unevenness is concentrated in one broad domain or spread across tasks. It would also prevent a global dispersion score from masking the structure that the taxonomy is intended to preserve. Any such combined instrument would need validation and should not be attributed to the original authors as a completed result.",
2: "The scenario report sits at the edge of an empirical literature review because it considers future system transitions rather than benchmark performance. Its connection to the other papers is through dependencies: model capability, environment interaction, reliability, and autonomy could shape the pace and effects of a transition. Those dependencies are not measured by the scenario itself. A research program can use the report to formulate precursor questions—whether capabilities improve across tasks, how quickly systems replicate work, how much human review remains, and how stable improvements are—while keeping the scenario’s assumptions separate from measured facts.",
3: "The visual agenda differs from most agent papers in the corpus because it considers representation and world modeling before a particular tool workflow. This raises a measurement challenge: if a model answers a visual question using text priors, success may not reflect robust visual inference. Paired examples with controlled edits, visual-only and language-assisted conditions, and predicted action consequences can help identify the source of performance. The resulting evidence would complement source retrieval work [R14] and computer-use frameworks [R16], which examine visual information within tasks rather than defining a broad theory of visual intelligence.",
4: "The index proposed in the jaggedness paper is most interpretable when the tasks are sampled from a declared population. If a capability sample is expanded to include many near-duplicate tasks, the calculated dispersion may shift even though the system has not changed. A bootstrap over task families and item subsets can show this sensitivity. Reports should show which dimensions drive the index and whether the same ranking remains under alternate normalization. That analysis would clarify whether a number is a stable model descriptor or a convenient summary for a particular task suite.",
5: "The central methodological implication of the unified protocol is that interaction adapters are experimental components. Translating a benchmark from a web API to a command line changes the information and errors available to the agent. An adapter may hide state, introduce retries, or normalize outputs. Documenting this translation and validating it against the original harness protects comparisons. The benchmark can also be used to test reproducibility: a result should be repeatable through the common harness and remain qualitatively similar through a native interface when semantics match.",
6: "The environment synthesis study connects to curriculum generation and task synthesis [R08, R09], but its main variable is the breadth of interactive worlds. To compare these approaches, measure the structures that each generator changes: number of tools, state schema, task dependency, feedback density, and fault behavior. A task generator can increase item count without increasing interaction diversity; an environment generator can increase tool count while retaining the same decision pattern. A common descriptor would make it easier to explain what “scale” means and compare effects across systems.",
7: "The ICLR paper’s significance depends on whether continued pre-training changes how the model acts, not only its factual knowledge. A trajectory-level evaluation should inspect whether the agent plans, selects sources, calls tools, checks outputs, and revises claims. Downstream task performance alone cannot identify which behavior was acquired. This makes process evaluation [R19] relevant even when the intervention is training: the system should show that its improved result follows a reliable and transferable procedure.",
8: "ZPD-guided synthesis is closely related to a moving measurement scale. If the test is recalibrated as the model improves, scores from different versions are not directly comparable unless stable anchor tasks remain. The paper’s engine can be studied as both a training method and a benchmark generator, but those two roles should be separated. Calibration tasks select training data; independent test tasks estimate capability. The stronger the separation, the more persuasive a claim that the model has expanded its competence rather than learned the exam.",
9: "AgentSynth highlights trajectory composition as a source of difficulty. This is related to the execution and state problems in [R11] and [R16], but it emphasizes how a task is constructed. A long trajectory may fail because one dependency is misunderstood, because the interface is brittle, or because a small error propagates. Recording subtask state and action dependencies would make success decline more interpretable. It would also distinguish a useful benchmark of long-horizon planning from a stress test of repeated low-level interaction.",
10: "The environment scaling paper and Agent-World [R06] share a focus on synthetic interaction, while [R17] adds co-evolution. A comparison across them should identify whether the simulator is fixed, generated once, or changed by agent behavior. These settings give different kinds of feedback and can create different forms of leakage. A controlled study could train identical agents across the three setup types and evaluate all of them in an external environment. That would clarify whether co-evolving environments provide better learning signals or merely a better fit to the training generator.",
11: "Persistent files are especially useful when the task produces multiple deliverables, as in literature review, data analysis, or long investigations. They also create a provenance obligation: an artifact may be reused long after the original observation. Evaluation should distinguish raw saved evidence from derived summaries and identify what is no longer current. A file-based approach can become more trustworthy when combined with source-grounded checks [R14], process evaluation [R19], and validation of each completed milestone.",
12: "A survey can support cumulative science if the underlying metadata are machine-readable and versioned. Benchmark titles often conceal differences in interface, scoring, access, and model version. A structured record can capture task family, modality, horizon, environment type, metric, release date, and evaluation conditions. The survey’s taxonomy would then help researchers identify coverage gaps and compare similar instruments. Such a record should link to official versions, since secondary summaries may lag behind changes.",
13: "Automated curation sits between software engineering and experimental science. An agent can execute a script correctly while choosing a poor intervention, or choose a sensible policy that fails because training noise overwhelms the effect. The benchmark therefore needs multiple seeds, uncertainty intervals, and a record of decisions. A human baseline should include time spent checking results. These additions distinguish engineering autonomy from useful scientific reasoning.",
14: "The RDQA process localization metric makes the search path an object of measurement. It will be useful if it distinguishes evidence located correctly from evidence merely accessed. A source may have the right timestamp but the wrong speaker, or the right table but the wrong row. Annotation must specify the granularity needed for each question. Grounding can then be evaluated on retrieval and interpretation separately, and abstention on insufficient evidence can be scored as appropriate behavior.",
15: "Role-conditioned merging should be compared with a router that keeps specialists separate. Merging can reduce runtime and coordination cost, while routing can preserve distinct expert weights but incur selection errors. Evaluate both on the same task distribution, including a new role combination and a task where specialists disagree. This comparison measures the practical question—whether one generalist checkpoint is beneficial—rather than only whether a proposed merge algorithm improves on previous merge formulas.",
16: "Computer-use systems combine visual perception with state changes that may be irreversible. A successful task on a static benchmark can understate interface drift and action risk. The framework’s memory and reflection components should be tested with adversarial or accidental state changes, not only clean demonstrations. Combine accuracy with safe-action constraints, rollback behavior, and explicit confirmation. This connects system architecture to the process and governance concerns in [R19].",
17: "The dual-role setup can be understood as a bootstrapped data-generation method. The key scientific variable is the quality of the environment feedback. It should be tested against external state transitions and expert ratings before agent improvement is attributed to learning. If the environment model becomes more accurate as the agent learns, measure that separately from task completion. Otherwise the joint system may improve because the simulator becomes more accommodating rather than because the policy becomes more general.",
18: "AgentArch’s comparison of eighteen configurations is valuable because individual architecture components often interact. A planner can help with dependency-heavy workflows but add overhead to simple cases; a tool-use style can suit one API better than another. Report effects by workflow type and complexity. Two use cases offer a test bed, not a complete enterprise population. External organizations can test whether the measured interaction effects survive different process rules and data conventions.",
19: "Process scores should be linked to risk rather than treated as a generic proxy for good reasoning. The paper’s checklist asks whether an agent follows a protocol, and its examples expose failures that final accuracy misses. A later study should test whether checklist violations predict incident severity or user distrust. It should also test safe alternative paths to avoid penalizing a system that reaches the same evidence through a valid route. More process observation improves accountability only when the scoring rule is itself reliable.",
20: "DAB is important because real data questions combine multiple operations that are benchmarked separately elsewhere. A natural-language answer can depend on database discovery, schema understanding, joins, transformation of unstructured text, and domain assumptions. This makes it an end-to-end task, but attribution is difficult without intermediate artifacts. Saving queries and validation results helps locate failure. The benchmark’s 57% pass@1 result for its best tested system is a useful baseline in that setting, not a measure of general competence across domains."
}


TECHNICAL_EXTENSIONS = [
    ("Benchmark granularity and task-family structure", [
        "Task families should be defined at the level that preserves meaningful variation. Grouping every web task together may hide differences between locating information, filling a form, managing state, and recovering from an error. Grouping by surface interface alone can also obscure shared reasoning structure across apps. A benchmark can describe each task on multiple axes: goal, action space, observation type, dependency, state change, and risk.",
        "The task taxonomy should be empirically useful. If two categories produce the same error patterns and transfer behavior, they may be too fine-grained; if one category contains unrelated behaviors, it may be too broad. Cluster analyses can help, but human interpretation is needed to explain what the clusters mean. Reports should publish the task assignments so another group can challenge them.",
        "This granularity matters for the profile proposed in [R01] and the evaluation map in [R12]. A profile is only as interpretable as its categories. A table of scores by a well-specified family can help identify the next experiment and can guide deployment more effectively than a single score."
    ]),
    ("Open-ended task completion versus bounded success criteria", [
        "Open-ended tasks resemble real work but are difficult to score consistently. A user may accept several reports or workflows; a benchmark needs criteria for completeness, correctness, evidence, and format. Strict exact-match evaluation can reject valid answers, while a broad model judge can accept unsupported claims. The right rubric is specific to the task’s use.",
        "A robust design separates required outcomes from optional quality dimensions. For a research report, required outcomes might include coverage of specified sources and supported claims, while clarity and organization are rated separately. For an enterprise workflow, a correct state change and policy compliance may be hard requirements, while efficiency is a secondary measure. The rubric should explain how partial completion affects the score.",
        "Source papers on curation [R13], multimodal retrieval [R14], and data questions [R20] show how rich tasks can be decomposed into observable stages. That decomposition does not make every open-ended problem fully objective, but it improves agreement and error analysis."
    ]),
    ("Benchmark exposure and contamination", [
        "Public benchmarks create a tension: release supports reproducibility, while repeated exposure can reduce their diagnostic value. Contamination can be direct, through training examples, or indirect, through task templates and known answer formats. A benchmark should record what is public, check for suspiciously sharp gains, and include refreshed tasks without discarding stable anchors.",
        "A dynamic test can reduce memorization but risks moving the measurement target. Version history should show which items were added, removed, or re-scored. Comparisons across versions should identify the overlapping anchor set and analyze it separately. Otherwise a year-to-year trend may reflect different tasks rather than improved capability.",
        "Generated tests such as [R08] and [R09] should preserve private or externally authored test data where possible. The generator itself can be public, but final evaluation items should be sampled independently. This maintains scientific scrutiny while limiting direct optimization against the exact score."
    ]),
    ("Learning efficiency, retention, and forgetting", [
        "Training papers often emphasize newly acquired performance, but a general agent must also retain existing abilities. Continual pre-training [R07], frontier curricula [R08], environment training [R06, R10], and self-generated experience [R17] should be evaluated for both acquisition and forgetting. Test a fixed suite before training, immediately after, and after additional learning stages.",
        "Learning efficiency can be measured as gain per training example, feedback event, time, compute, or human intervention. These denominators answer different questions. Few-shot adaptation asks how much a new task improves after examples; continual learning asks whether the improvement persists and whether older abilities degrade. Report both.",
        "A durable evaluation can include a retention curve: score on the new task and on prior tasks after each stage. It should also measure calibration and refusal behavior because training can change when the model answers confidently. A capability increase with a large safety regression should not be described as an unqualified improvement."
    ]),
    ("Realistic simulations and the simulator gap", [
        "Simulators provide control, repeatability, and safe resets. Their limitations are often different from those of live services: real APIs have authentication, latency, rate limits, missing values, evolving schemas, and partial failures. The existence of a simulator is not a weakness; the inference boundary is the issue.",
        "A bridge study pairs a subset of tasks across simulated and live environments. It reports where state transitions and error feedback match, where they differ, and whether agent behavior changes under the mismatch. When live tests are risky, use read-only access or a safe staging account and define rollback procedures.",
        "For generated environments in [R06, R10, R17], publish which properties are simulated and validate the environment independently. A high score in a clean simulator can establish competence in that setup and support controlled research; it should not be silently converted into a claim about production reliability."
    ]),
    ("Human baselines and the meaning of comparison", [
        "Human performance is a useful reference, but not a context-free scale. People differ in expertise, language, disability, familiarity with tools, and time availability. The interface can advantage either people or agents. A fair comparison describes the cohort and ensures that both groups receive comparable instructions and resources.",
        "A human baseline can serve different purposes: estimate task difficulty, compare practical completion, or calibrate a capability scale. These goals require different designs. An expert baseline may be appropriate for medical review but not for typical office workflows. A time-bounded baseline can measure productivity, while an untimed baseline may measure answer quality.",
        "Where a human baseline is used in [R01] or human-designed curation in [R13], report distribution and expertise rather than a single number. The goal is not to define intelligence by human imitation; it is to make the comparison meaningful for the question at hand."
    ]),
    ("Agent identity, updates, and reproducible checkpoints", [
        "A model name may refer to a service that updates over time. A reproducible study should capture checkpoint identifiers or access dates, inference parameters, and any provider-side model changes. If exact weights are unavailable, the paper should state that independent reproduction may require a substitute model.",
        "Agent identity includes the scaffold and tool setup. A result can change when a prompt, memory format, browser version, or data source changes even if the backbone is unchanged. Version these components together and provide a system manifest. Training methods also need data and checkpoint lineage to interpret gains.",
        "When updated models are evaluated, maintain an anchor task set and report new results beside the prior version under the same protocol. If the system changes materially, create a new configuration identifier. This prevents a public leaderboard from treating a moving service as a fixed experimental subject."
    ]),
    ("From benchmark profile to deployment decision", [
        "A benchmark profile can support a conditional recommendation only if the task population and risk are relevant to the intended deployment. A model may be suitable for drafting, where a human reviews output, but not for executing irreversible changes. The action boundary and reviewer role should be explicit.",
        "The profile should distinguish capability, reliability, and operating constraints. Capability describes what the agent can do; reliability describes how consistently it does it and how it handles failures; constraints describe required permissions, tools, human confirmations, and data policies. A high success score in one dimension cannot substitute for another.",
        "After deployment, monitor changes in tools, user population, data, and model version. A model card or initial benchmark result can become stale. Re-evaluate when the system boundary changes and maintain a route for users to report errors. These steps make evidence useful without treating a benchmark as a guarantee."
    ])
]


APPENDIX_EXTRA = [
    ("Appendix R. Invalid runs, timeouts, and tool failures", [
        "The study protocol should define invalid-run criteria before evaluation. A run may be invalid because the benchmark itself failed to initialize, the evaluator lost state, or the task was malformed. A timeout caused by the agent’s behavior is usually a system outcome, not an invalid run. Authors should report counts and reasons instead of silently removing all unsuccessful episodes.",
        "Tool failures should be recorded by type: agent-call error, service error, permission denial, timeout, malformed arguments, or environment reset issue. The agent’s response to a failure is part of the evaluation. A graceful retry within budget differs from an unsafe repeated write or an unsupported final answer.",
        "When infrastructure failures are excluded, publish the exclusion rule and a sensitivity analysis that counts them as failures. This shows whether conclusions depend on the denominator. A reliable benchmark should log enough state to distinguish evaluator faults from agent faults.",
        "For repeated attempts, state whether the system receives the same task state, a reset environment, or the partial state from a prior attempt. These conditions can drastically change the meaning of pass@N. All attempts and resource use should remain visible."
    ]),
    ("Appendix S. Human baseline design", [
        "Choose the human population based on the intended comparison. If the task requires domain expertise, recruit qualified participants and measure relevant experience. If the task represents a general office workflow, an expert-only cohort may exaggerate the human baseline. Describe language, accessibility, prior tool familiarity, and compensation.",
        "Match the information and interface available to human and agent groups. If agents receive structured APIs while people use a graphical interface, the comparison measures different workflows. This may still be useful, but the paper should state that the target is system utility rather than intrinsic capability.",
        "Measure human completion time, correctness, uncertainty, and review effort. Human performance is variable, so report distributions and confidence intervals. Where users can consult documentation, provide comparable source access to the agent or state why the settings differ.",
        "Human baselines should not be framed as the universal definition of intelligence. They provide a reference for a specific task population and condition. This is especially important when [R01] uses cognitive performance as an organizing reference."
    ]),
    ("Appendix T. Ablation design for agent architecture", [
        "An architecture ablation should begin with a working system and remove or replace one component at a time. Candidate components include planner, memory, reflection, verifier, delegation, environment hints, and automatic retries. The ablation should preserve other components and match the total inference budget where possible.",
        "For each condition, report task-family scores, process traces, latency, model calls, tool calls, and failure severity. A component may improve success but add cost or create a new failure mode. These tradeoffs matter when selecting an architecture for a known workflow.",
        "Interaction effects require combinations. A memory component may help only when paired with a verifier; delegation may help only on tasks with independent subtasks. A full factorial experiment can be expensive, so select combinations based on explicit hypotheses and report untested interactions.",
        "Ablations do not prove mechanism by themselves. If removing a component also changes prompt length or context availability, the effect may be caused by the changed information rather than the component’s intended function. Describe each variant precisely."
    ]),
    ("Appendix U. Reading a leaderboard responsibly", [
        "A leaderboard rank is conditional on task composition, scoring, aggregation, and system versions. Before using a rank, inspect whether the score is first-attempt, best-of-N, human-rated, or model-judged. Check whether all submissions received the same tools and budget.",
        "Look for per-task results, score variance, confidence intervals, and benchmark version. If small differences in rank are within run uncertainty, the ordering may be unstable. A leaderboard that reports only a mean and rank can overstate precision.",
        "Ranks are useful for navigating a benchmark but should not be converted into a general capability ordering across unrelated tasks. A high position on one tool-use suite can coexist with weak source grounding or process compliance. Compare profiles rather than assuming one benchmark represents all agent behavior.",
        "When a leaderboard is used for a deployment decision, rerun the candidate system on tasks that match the actual workflow and constraints. The local system may have different tools, permissions, latency, and user needs."
    ]),
    ("Appendix V. Updating the evidence after model changes", [
        "When a foundation model changes, rerun a stable anchor set and preserve the earlier scores. Record model access dates and any known behavior changes. If the agent scaffold also changes, separate the two modifications or identify the comparison as a full-system update.",
        "Check for regression in weak but high-risk task families, not only average improvement. Reassess calibration, refusal behavior, tool constraints, memory, and failure recovery. A model update can change how often the system takes an action even if the benchmark score remains similar.",
        "If tasks or tools also change, define a new evaluation version and report overlap with the prior one. Do not present a continuous line chart without noting where comparability breaks. A stable anchor suite can preserve some continuity while new tests address updated capabilities.",
        "A monitoring plan should specify what change triggers a full evaluation, what can be checked continuously, and how users can report unexpected behavior. This makes the benchmark evidence part of a lifecycle rather than a one-time certificate."
    ]),
    ("Appendix W. Communicating uncertainty to users", [
        "User-facing capability information should say what tasks were tested and where the system may fail. Use plain examples: the agent can retrieve a source passage but may miss conflicting evidence; it can finish a workflow in a test environment but has not been evaluated with live writes. This is more actionable than a broad statement that the system is advanced.",
        "Report uncertainty at the level the user needs. A low score on an irrelevant task family may not matter for a narrow use, while a small but severe failure risk may dominate a high-stakes workflow. Explain confidence intervals, sample size, and rare-event limits without implying guarantees.",
        "If a system is uncertain, it should be able to request clarification, abstain, or ask for review. Evaluate those behaviors as choices, not just failed completion. A useful system may safely stop when the evidence is inadequate.",
        "Communication should be updated when the model, tools, or task distribution changes. A profile based on an older system can mislead users if it is still displayed without version information."
    ])
]


FINAL_ANALYSES = [
    ("A systems view of evidence", [
        "Evidence for an agent begins before the final answer. The system receives an instruction and observations, selects information, forms a plan, calls tools, updates state, verifies intermediate work, and communicates an outcome. Each stage can introduce a distinct error. A task score is an endpoint measure; process, provenance, and recovery explain how the endpoint was reached. The corpus contains different ways of making these stages visible, from tool protocols [R05] to source retrieval [R14], process checklists [R19], and executable data workflows [R20].",
        "A systems-oriented report should therefore specify input conditions, available evidence, action space, feedback, memory, evaluator, and user intervention. If one component changes, record it. This avoids attributing a scaffold effect to the model and makes failures actionable. The architecture proposal in this review uses component contracts as a practical device: each component has a declared input, output, and failure response that can be tested.",
        "The same view applies to safety. A policy violation can originate in ambiguous instructions, weak source grounding, a permissive router, or a missing verification step. A log may identify where the event occurred without proving the internal cause. Targeted ablations and counterfactual inputs can test causal explanations. This distinction supports useful diagnosis without overclaiming interpretability."
    ]),
    ("A research standard for environment claims", [
        "“Environment scaling” can mean more task examples, more tools, more unique schemas, more state transitions, or more realistic service behavior. These are different manipulations. A study should report them separately and show which one changed. The environment manifests in [R06, R10] and co-evolution in [R17] point toward a shared reporting vocabulary.",
        "A useful environment record includes initial state, tool definitions, transition rules, reset behavior, user model, permitted actions, failure modes, and train/test overlap. It should say which outputs are simulated and how the simulator was validated. This lets other groups reproduce an experiment and identify which properties may transfer to live systems.",
        "Claims about scaling should be tested on held-out structures. A training set can grow while retaining the same interaction pattern; that is a volume result, not necessarily a diversity result. A system that transfers to new schemas or state dynamics provides stronger evidence of generalization. A live bridge test can then estimate the distance between the simulator and deployment conditions."
    ]),
    ("A research standard for long-horizon claims", [
        "A long-horizon result should report length, interruptions, tool failure exposure, state size, and human interventions. It should distinguish uninterrupted completion from resume after a restart and recovery after corruption. The term “infinite horizon” should be tied to a measured continuation protocol rather than interpreted literally [R11].",
        "Long tasks create more opportunities for small errors to compound. Evaluate milestone accuracy and final completion, but also check whether later steps depend on stale or invalid state. Track the number of times the agent verifies, revises, or ignores earlier information. Where external memory is used, audit what is retained and whether source provenance survives summarization.",
        "A robust result should include safe stopping behavior. An agent that recognizes an unrecoverable conflict and asks for help may be more dependable than one that completes every task at any cost. Evaluation should reward appropriate escalation and count the cost of human support. This is especially relevant to enterprise systems [R18, R20] and computer use [R16]."
    ]),
    ("A research standard for source-grounded claims", [
        "A grounded-answer claim should identify what constitutes evidence and how support is judged. It should separate finding a source from reading it correctly and using it in the answer. The paper should report unsupported claim rates and evidence omissions, not just citation recall. RDQA [R14] and process evaluation [R19] make the intermediate path visible, while DAB [R20] provides executable intermediate work.",
        "Test robustness by editing sources, changing ordering, adding distractors, and asking unanswerable questions. A grounded agent should update when a relevant source changes and should qualify an answer when sources conflict. These tests are more diagnostic than citation presence because they examine whether the system is causally using the evidence.",
        "For multimodal materials, annotations need location and time. A reviewer should be able to reopen the exact page, chart region, frame interval, or audio span. For structured data, preserve query text, joins, filters, and validation output. These practices support independent verification and connect source use to process compliance."
    ]),
    ("A research standard for generalist claims", [
        "A system should not be called general solely because its benchmark suite contains many tasks. The task families should differ in underlying demands, and the evaluation should test transfer to new combinations. A suite with hundreds of surface variants can still sample one narrow capability. Report both the number of tasks and the number of structurally distinct families.",
        "Generalist claims are stronger when a system handles tasks without domain-specific manual customization, adapts to unfamiliar interfaces, preserves core behaviors under change, and knows when it lacks evidence. Each component should be evaluated separately before a combined headline is offered. The survey [R12] and cognitive framework [R01] help identify coverage, while empirical tests provide the actual evidence.",
        "A profile is not an inferior substitute for a generality claim. It is the evidence from which a future, better-validated claim could be built. It shows where capabilities overlap and where gaps remain. This supports cumulative research and prevents a strong result in one family from being mistaken for universal competence."
    ]),
    ("A research standard for authority and provenance", [
        "The identity of the authors and venue helps readers locate and evaluate a source, but authority alone does not validate a result. A paper should be read for its method, data, baselines, error analysis, limitations, and relation to prior work. This review records author affiliations and publication status because the corpus includes both peer-reviewed proceedings and preprints.",
        "For peer-reviewed conference papers, the venue and proceedings record should be cited alongside the source PDF. For preprints and lab reports, use their version and date. Where a paper has multiple versions, cite the version whose results and figures were reviewed. The corrected date for [R02] demonstrates why this matters.",
        "Each figure caption identifies its source and records whether the figure was reproduced or redrawn. Readers can follow the reference to the original paper to check how the researchers defined the task and interpreted their findings."
    ])
]


WORKED_DESIGNS = [
    ("Worked design 1: testing transfer across tool schemas", [
        "Research question: does agent training across structurally diverse tool environments improve transfer to an unseen schema? Begin with three training conditions at equal interaction and compute budgets: a single schema repeated many times, several surface variants of one schema, and structurally distinct schemas with different state transitions. Hold model initialization, controller, and evaluator fixed.",
        "Evaluation: use a fourth schema family written by an independent group. Include an in-distribution anchor, a renamed-schema task, a task with changed optional fields, and a task with a recoverable API failure. Run multiple independent trials. Record actions, arguments, tool returns, state changes, and final answer. Score completion, invalid calls, recovery, latency, and cost.",
        "Interpretation: improvement on the anchor but not the held-out schema supports better familiarity rather than transfer. Improvement on renamed schemas but not changed state transitions suggests transfer of interface syntax without broader world modeling. Improvement on both, with safe recovery, supports a stronger claim about reusable interaction policy. It still does not imply generality outside the tested tool families.",
        "Threats: the independent test author may unknowingly reuse familiar task patterns; a verifier may accept a shortcut; and one schema may be unusually easy. Use alternate task sets, human audit, and a second evaluator. Publish training environments and the exact held-out transformations. This design connects the claims in [R06, R10] with the task synthesis and benchmarking work in [R08, R09]."
    ]),
    ("Worked design 2: separating process compliance from correctness", [
        "Research question: does a process checklist identify risky behavior that outcome accuracy misses? Select tasks with authoritative sources, tool requirements, and a known safe procedure. Define mandatory checks and safe alternatives before testing. Create trajectory pairs with the same final answer: one follows the protocol; the other reaches the answer through a shortcut or unsupported memory. Include wrong-answer trajectories with both compliant and noncompliant processes.",
        "Scoring: independent reviewers score the final answer, source support, checklist adherence, and severity. A separate automated judge can be tested against those ratings. Report agreement and false-compliance rates. Preserve task-level data so that a high average cannot hide an omitted critical step.",
        "Interpretation: if process labels catch shortcut trajectories with correct outcomes, they add information beyond accuracy. If judges disagree about safe alternative paths, the checklist requires revision. If process score predicts nothing about downstream errors, the proposed measure may be descriptive rather than predictive. These distinctions extend the feasibility results in [R19] without treating one task’s scores as universal.",
        "Ethics and operations: traces may contain sensitive data. Use a sandbox, restrict access, redact only what is unnecessary, and state retention rules. For irreversible actions, never create a real harmful consequence to test compliance; use a safe simulator or supervised environment. Report what conditions were simulated."
    ]),
    ("Worked design 3: evaluating persistent memory and stale evidence", [
        "Research question: does external state improve long-task completion without propagating stale or false notes? Give the agent a multi-part task with documents that can be updated. Compare context-only execution with file-based memory under matched budgets. Insert an interruption and, in separate conditions, a stale note, a corrupted summary, or a contradictory new source.",
        "Measurements: task completion, source freshness, state repair, claim provenance, time to resume, repeated work, and human interventions. Track which later claims depend on a changed source. A correct answer produced from an outdated artifact should be distinguished from a correct answer based on current evidence.",
        "Interpretation: file memory may improve resume performance while increasing stale-state risk. A system that detects conflict and revises dependencies demonstrates a more useful property than one that merely reloads its workspace. A safe abstention may be preferable where no source resolves the conflict. The test links persistence [R11, R16] with source grounding [R14] and process evaluation [R19].",
        "Reproducibility: release sanitized task manifests, state snapshots, update timestamps, and scoring rules. Report model version, memory format, retrieval policy, and whether the agent sees raw documents after resume. These details are necessary to compare memory systems fairly."
    ])
]


RESEARCH_ROADMAP = [
    ("Months 0–3: instrumentation", "Publish task manifests, source-grounding rubrics, process checklists, and environment specifications. Run judge audits and measure agreement. Establish anchor sets and record the current model and scaffold versions."),
    ("Months 3–6: matched comparisons", "Replicate selected agent architectures under matched budgets. Compare tool protocols and memory choices across at least two task families. Report per-family outcomes, variance, trace classes, and cost."),
    ("Months 6–9: transfer and recovery", "Evaluate held-out interfaces, schemas, task compositions, and environment failures. Inject safe recoverable faults and measure detection, recovery, and escalation. Use independent task authors."),
    ("Months 9–12: external validity", "Run paired simulation and safe live tests where appropriate. Test whether capability profiles improve user decisions and whether process indicators predict errors beyond outcome accuracy. Publish limits and update guidance when systems change.")
]


IMPLEMENTATION_BLUEPRINT = [
    ("1. Preregister the inference", [
        "Write the target inference in a way that can be falsified. State whether the study concerns a model, a complete agent, a benchmark, or a human–agent workflow. Specify the task population, primary comparison, resource budget, and the observation that would weaken the claim. Avoid selecting a headline metric after results are visible.",
        "Separate exploratory and confirmatory work. Exploratory experiments can help discover useful task variants, but the final evaluation should use a reserved sample and a fixed analysis. If the same benchmark is used for both model development and final reporting, say so and add independent evidence before making a transfer claim.",
        "A preregistration should also define exclusions, retries, and stopping rules. Decide how invalid environment runs differ from agent timeouts, whether partial completion earns credit, and how human intervention is recorded. These choices determine the denominator and should not be selected after seeing the system’s result."
    ]),
    ("2. Specify the system manifest", [
        "The system manifest records model and version, prompting strategy, controller, memory policy, tool schemas, permissions, environment, evaluator, and compute or monetary budget. Include inference settings, context limits, retry behavior, and termination rules. If a component is a managed service that can change, record an access date and known version identifier.",
        "For a multi-agent system, identify each role, communication channel, shared state, delegation policy, and failure recovery. For a computer-use system, record operating system, browser or application versions, screenshot resolution, and action API. For a database agent, record schema descriptions, query permissions, and whether results can be written.",
        "The manifest should be machine-readable when possible and included in the artifact package. A model name alone cannot reproduce an agent. System configuration is part of the unit under study."
    ]),
    ("3. Sample tasks independently", [
        "Define the task population and draw a representative sample. Stratify by task family, dependency depth, modality, environment, and risk where needed. Include routine and edge cases but do not let rare extreme items dominate a general capability estimate unless the use case calls for risk-weighted scoring.",
        "Use separate development, verifier-calibration, and final-test sets. The final set should not guide prompt iteration or task generation. Include stable anchors for comparison across model versions and hold out some task structures or authors for external evaluation.",
        "For every item, document the intended skill, accepted outcomes, valid alternate paths, potential shortcuts, and evaluation evidence. Human reviewers can test solvability and ambiguity. Keep a record of rejected tasks so the benchmark’s scope is transparent."
    ]),
    ("4. Run controlled comparisons", [
        "Select baselines that answer the research question. If the question is about an architecture, keep the backbone fixed. If it is about training, match the inference scaffold. If it is about practical utility, compare with a human or simpler system using comparable information and access. Explain any unmatched factors.",
        "Set resource ceilings in advance. Match model calls, tool access, context, retries, wall time, and compute where possible. If the intended question concerns best achievable performance, present best-of-N separately from first-attempt success and count the additional cost.",
        "Randomize task order and run seeds when environment state can affect outcomes. Reset environments consistently. Log infrastructure failures and do not silently remove episodes where the agent itself caused a timeout or malformed action."
    ]),
    ("5. Capture traces and outcomes", [
        "Each run should capture task ID, model and scaffold version, observations, actions, tool calls, returned values, state changes, memory writes, evaluator outputs, retries, timestamps, cost, and final result. Separate raw inputs from derived summaries and note where sensitive data were redacted.",
        "Score outcome, process, evidence grounding, constraints, recovery, and calibration as separate dimensions. A trajectory can be correct but noncompliant, compliant but incomplete, or grounded but poorly communicated. Preserve these differences in the result table.",
        "If a human is part of the workflow, record when they intervene, what information they receive, how long they spend, and whether they correct the system. This makes assisted performance comparable with realistic alternatives."
    ]),
    ("6. Validate the evaluators", [
        "Before scoring the full test set, validate automated judges and process checklists on a diverse sample. Include near misses, valid alternatives, adversarial traces, wrong answers with good process, and correct answers with shortcuts. Compare with independent human annotations.",
        "Report agreement, error types, false-pass rate, and false-fail rate. The judge should see the evidence needed to make a decision. A final answer alone cannot support a source-grounding judgment; a citation string alone cannot validate entailment; a benchmark score cannot establish safe tool use.",
        "If reviewers disagree, retain the original annotations and use a documented adjudication method. Test whether the main result changes under reasonable alternative labels. This uncertainty belongs in the paper."
    ]),
    ("7. Analyze uncertainty and tradeoffs", [
        "Report task-level and family-level distributions, run variance, confidence intervals, and sample sizes. If tasks are clustered, account for clustering in uncertainty estimates. Do not claim a stable rank from score differences smaller than expected variation.",
        "Analyze failure classes and their severity. Track whether the agent detects a failure, attempts recovery, and stops safely. A single successful completion can be less informative than a distribution of partial outcomes and error modes.",
        "Plot success against cost or latency when tradeoffs matter. Compare at matched budgets and show first-attempt and retry curves. Include human review and rework cost if the claim concerns practical workflow efficiency."
    ]),
    ("8. Release and update the evidence", [
        "Release the task manifest, scorer, prompts or controller specification, environment version, and sanitized traces where permitted. Include exact IDs for all reported runs. If an artifact is unavailable, explain the limitation and give a realistic reproduction path.",
        "Record benchmark and model changes. When a task or rubric changes, create a new version and publish overlap with the previous test. If the model service updates, rerun anchors and preserve prior results. Do not present discontinuous versions as a smooth trend.",
        "When evidence is used for deployment, define the conditions that trigger reevaluation: model updates, tool changes, new permissions, new user populations, altered data, or significant incident reports. A benchmark is part of a maintenance process, not a permanent certification."
    ])
]


DOMAIN_EXAMPLES = [
    ("Research assistant", "Measure source discovery, evidence localization, citation support, conflict handling, and correction after new evidence. Preserve an audit trail from source to claim. A report that is well written but unsupported should not pass."),
    ("Computer-use agent", "Measure visual interpretation, action correctness, state changes, permission handling, recovery from interface drift, and safe stopping. Include reversible actions and a sandbox for any write operation. A completed task with an unauthorized action is a failure."),
    ("Data agent", "Measure schema discovery, joins, unstructured-text extraction, execution, result validation, and explanation. Preserve queries and intermediate records. Test held-out schemas and changed identifiers; assess whether the agent requests business context it cannot infer."),
    ("Enterprise workflow agent", "Measure dependency tracking, orchestration, handoffs, access rights, partial completion, rollback, latency, and human review. Use realistic exceptions and policy changes, not only happy paths. Compare complete workflows against human baselines.")
]


RESEARCH_QUESTIONS = [
    ("RQ1 · Profile validity", "Do cognitive profiles predict performance on external tasks better than a single aggregate score? Sample several tasks per faculty, use held-out task authors, and test prediction of real workflow failures. The claim weakens if the profile is unstable under modest task resampling."),
    ("RQ2 · Jaggedness stability", "How sensitive is a jaggedness index to task choice, normalization, and human reference cohort? Bootstrap task families and compare alternative baselines. A stable decision aid should retain its interpretation and add predictive value beyond mean performance."),
    ("RQ3 · Environment volume or diversity", "Does agent transfer improve from more interactions, more structurally diverse environments, or both? Match total training budget while manipulating schemas and state transitions. Test on a new tool family and report simulator fidelity."),
    ("RQ4 · Curriculum independence", "Do tasks selected by a ZPD engine improve capability outside that engine’s own exam? Use several learner models, an independent verifier, and externally authored tests. Measure learning gain separately from adaptation to item templates."),
    ("RQ5 · Persistent-state recovery", "Does external memory improve completion after interruption, and how often does stale state propagate into later decisions? Inject corrected and conflicting sources, then measure detection, revision, provenance retention, and safe abstention."),
    ("RQ6 · Process value", "Do process-compliance labels predict important failures beyond outcome accuracy? Use independent reviewers, multiple task types, hard negative traces, and risk-specific checklists. Test whether the labels predict downstream error or only describe the trajectory."),
    ("RQ7 · Evidence grounding", "Does claim-to-source alignment predict robustness to source edits better than citation presence? Track exact passages, chart regions, timestamps, or database rows and measure answer changes after counterfactual edits."),
    ("RQ8 · Specialist integration", "Does merging specialist models preserve rare capabilities and improve novel combinations relative to a router? Match cost and test held-out roles, tasks, calibration, and safety behavior before and after integration."),
    ("RQ9 · Computer-use transfer", "Which memory, reflection, and orchestration components improve computer-use performance under interface drift? Use matched ablations, unseen applications, permission prompts, and safe write-action tests."),
    ("RQ10 · Cost and reliability", "At what resource budget does an agent achieve a target rate of verified completion with acceptable process compliance? Plot first-attempt and retry curves against total model, tool, latency, and human-review costs.")
]


RISK_ANALYSIS = [
    ("Threat model and task boundaries", "A responsible evaluation begins by stating which assets, users, actions, and failure consequences are in scope. An agent that summarizes public material has different exposure from one that can send messages, edit enterprise data, or execute code. The threat model should identify where untrusted input enters, which tools can change state, what information is sensitive, and who can authorize an action. Evaluators should classify actions by read, reversible write, and irreversible effect. This makes the required safeguards concrete and supports the process-evaluation argument in [R19]. A benchmark without an explicit action boundary may reward a system for completing the task while ignoring the consequences of its method."),
    ("Untrusted content and instruction conflict", "Documents, web pages, database fields, and tool outputs can contain misleading or adversarial instructions. Source-grounding evaluation should test whether the agent distinguishes task instructions from quoted or retrieved content. Create safe examples that include conflicting directions in source material and score whether the agent preserves the user’s goal and policy constraints. The evaluator should inspect the actual source selected and the action that followed. A fluent answer is not evidence that the system recognized the conflict. This test is relevant to multimodal retrieval [R14], research agents [R07, R13], and enterprise data workflows [R20]. Report the exact content pattern and do not expose a live system to harmful instructions or real data changes."),
    ("Tool permissions and side effects", "Tool access determines the space of possible outcomes. Evaluation should record the least privilege needed, distinguish read-only operations from writes, and require confirmation for irreversible actions. A system should be tested in a sandbox before any live operation. If a task includes a write, the test should verify that the action changes only the intended state and that rollback works. Permission errors should be visible to the agent and included in its process trace. These controls are part of computer-use evaluation [R16], enterprise architecture tests [R18], and tool environments [R05, R10]. Report safe refusal or escalation as a valid outcome when the system lacks authority or necessary evidence."),
    ("Persistent memory and information exposure", "Long-lived state can preserve useful context but also retain secrets, outdated facts, or information from another task. Audit what is stored, how it is retrieved, when it expires, and how deletion works. Test task isolation, stale-state updates, and access boundaries. When a stored item is corrected, the system should update dependent summaries or flag them for review. These concerns extend the persistent-work design in [R11] and the memory mechanisms in [R16]. A deployment claim should include retention and access rules, since a memory layer changes both capability and the privacy surface."),
    ("Verifier and reward manipulation", "An agent trained or retried against an automated verifier may learn to satisfy the judge rather than the user’s goal. This can happen through formatting exploits, task shortcuts, or exploiting missing checks. Verifier audits should include adversarial and alternate-valid trajectories, and independent human review should test high-impact outcomes. Where possible, separate the tool that generates tasks from the one that scores them. This is relevant to ZPD task synthesis [R08], computer-use task generation [R09], and evolving environments [R17]. Report the verifier’s false-pass rate and describe how reward or feedback was used during training."),
    ("Human oversight and automation bias", "Human review can reduce risk only if reviewers have enough evidence, time, and authority to challenge the agent. A reviewer who sees only a polished answer may be more likely to accept an unsupported claim. Evaluate review interfaces with evidence links, uncertainty, and failure warnings. Measure correction time and whether users detect planted errors. Escalation should be specific: identify what is uncertain, what the system proposes, and what permission is needed. Compare the assisted workflow with a human-only baseline, including review and rework. This makes human oversight a measurable system component rather than a generic mitigation statement."),
    ("Benchmark security and privacy", "Benchmark tasks can contain private records, proprietary schemas, or user-generated media. The study should state what data are collected, how they are redacted, who can access logs, and how long they are retained. Release only sanitized artifacts needed for reproduction. If a live service is used, scope credentials narrowly and document cleanup. For multimodal tasks, preserve evidence location while removing personal information. For enterprise tasks, synthetic or de-identified data may preserve schemas without exposing records. These choices affect the validity of the benchmark and the safety of the study; they should be planned before collecting traces."),
    ("Change management and post-deployment evidence", "A system’s behavior can shift when the model, prompt, tool, data, user population, or permissions change. Record these version changes and define which ones trigger re-evaluation. Use stable anchor tasks to compare versions and refresh the task set to address new behavior. Monitor failures in the intended workflow and update the capability profile when evidence changes. A benchmark is a snapshot of a configuration, not a permanent certificate. This point applies to all twenty papers, especially studies of evolving agents and environments [R06–R10, R17].")
]


DEPLOYMENT_SCENARIOS = [
    ("Literature and research assistant", "Evaluate search coverage, source selection, claim-level support, treatment of disagreement, citation accuracy, and update behavior when a source changes. A long-horizon task should preserve a source-to-claim trail and test resume after interruption. Useful evidence includes the multimodal retrieval work [R14], persistent-state design [R11], and process checks [R19]. The result should describe the tested source types and review needs. It should not generalize to all scientific judgment or claim that a well-formatted report represents novel discovery."),
    ("Computer-use agent", "Test navigation, visual grounding, form entry, state verification, recovery from interface changes, permission handling, and safe stopping. Use a sandbox with reversible operations and require confirmation for write actions. Report the operating system, application versions, screen configuration, tools, and interaction budget. OS-Symphony [R16] and AgentSynth [R09] provide relevant system and task-generation evidence, while process measures [R19] help reveal unsafe shortcuts. Completion on one interface does not show transfer to another."),
    ("Enterprise data agent", "Measure schema understanding, multi-source joins, text extraction, query execution, result validation, and explanation. Preserve every query and intermediate output so errors can be diagnosed. Include malformed identifiers, contradictory records, and questions with missing business definitions. DAB [R20] motivates these task properties. A deployment evaluation should use held-out schemas and realistic access restrictions, and compare the agent’s complete workflow with a data analyst’s time and review burden."),
    ("Automated data curator", "Assess whether an agent forms a grounded data policy, runs a controlled experiment, interprets noisy feedback, and reproduces the improvement on new data. Keep data-selection manifests, training seeds, recipes, and evaluation logs. Curation-Bench [R13] motivates this loop. The evaluation should compare with a human curator under equal compute and test whether the policy transfers beyond the benchmark’s data pool. Running code successfully is not enough to establish sound experimental judgment."),
    ("Enterprise workflow agent", "Evaluate request interpretation, dependent actions, orchestration, permission checks, partial completion, rollback, audit, and human escalation. Use multiple workflow families and hold out complete process templates. AgentArch [R18] gives a basis for comparing configurations, but each organization has its own data and exceptions. Report workflow success together with unauthorized actions, duplicated work, human corrections, latency, and cost. Safe refusal or clarification should count as a valid outcome when required information or authority is missing.")
]


FIGURE_REGISTER = [
    (1, "Cognitive taxonomy to capability profile", "Reviewer-redrawn schematic", "No source artwork copied."),
    (2, "Possible capability pathway and bottlenecks", "Reviewer-redrawn schematic", "Scenario illustration; not a forecast."),
    (3, "Visual perception–prediction–action loop", "Reviewer-redrawn schematic", "Conceptual synthesis from the white paper."),
    (4, "Capability profile and dispersion", "Reviewer-redrawn schematic", "Conceptual synthesis of jaggedness measures."),
    (5, "Benchmark–protocol–agent comparison", "Reviewer-redrawn schematic", "Not a result from the source experiment."),
    (6, "Tool environment synthesis and training", "Reviewer-redrawn schematic", "Schematic based on the paper’s method."),
    (7, "Agentic continual pre-training stages", "Reviewer-redrawn schematic", "Schematic based on the training pipeline."),
    (8, "ZPD task generation and re-evaluation", "Reviewer-redrawn schematic", "Schematic based on the paper’s method."),
    (9, "Subtask composition and verification", "Reviewer-redrawn schematic", "Schematic based on the task pipeline."),
    (10, "Environment construction overview", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (11, "InfiAgent framework", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (12, "Agent evaluation landscape", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (13, "Agentic data-curation loop", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (14, "RDQA source-grounding example", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (15, "Agent-merge performance variation", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (16, "Computer-use agent memory limitations", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (17, "Dual-role environment evolution", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (18, "AgentArch benchmark overview", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (19, "Example agentic process workflow", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material."),
    (20, "DAB tool interaction overview", "Source Fig. 1 reproduced", "ACL Anthology CC BY 4.0; author-created material.")
]


ABSTRACT = (
    "An agent can complete a familiar task and still struggle when the interface changes "
    "or when an early mistake affects later decisions. This paper proposes a framework "
    "for evaluating how broadly an agent’s capabilities transfer and how reliably it "
    "acts over time. It draws on twenty research papers and technical reports dated "
    "between November 2025 and November 2026. The corpus covers cognitive capability profiles, "
    "visual grounding, agent architectures, persistent state, training and environment synthesis, "
    "benchmark design, process evaluation, data curation, and enterprise workflows. Across these "
    "works, progress is best understood as a systems property that must be measured across "
    "task families, held-out settings, longer horizons, and explicit constraints. Aggregate "
    "success scores can conceal uneven skills, unsupported evidence use, fragile memory, and "
    "unsafe intermediate actions. The review distinguishes conceptual frameworks, benchmark "
    "contributions, empirical comparisons, surveys, and reports; it does not treat them as "
    "equivalent evidence. It then proposes a reference architecture, evaluation protocol, "
    "reporting template, and research roadmap that keep capability, transfer, process, and "
    "reliability visible. None of the twenty sources establishes a universal AGI threshold or "
    "shows that AGI has been achieved. The contribution of this document is a critical synthesis "
    "and a set of testable recommendations for more transparent claims about progress. The "
    "review asks four connected questions: which capabilities are represented in current "
    "evaluations; how much performance transfers beyond familiar tasks; what happens during "
    "long, tool-mediated work; and how should reliability, cost, and uncertainty be reported? "
    "The supplied corpus is focused rather than systematic, so inclusion should not be read as "
    "a complete map of the field. Findings are weighted according to the design that produced "
    "them: a proposed framework can organize measurement, a benchmark can reveal performance "
    "on its task population, and a replicated experiment can support a stronger comparison."
)

FIRST_PAGE_INTRO = (
    "Recent systems can call tools, search documents, operate software, and continue work "
    "through external state. Those abilities matter, but each is conditional on its model, "
    "controller, tools, environment, budget, and scoring rule. A benchmark result therefore "
    "supports a bounded claim about a configured system under specified conditions. It does "
    "not by itself establish generality across settings. The twenty papers reviewed here "
    "approach that problem from different directions: cognitive taxonomies describe what might "
    "be measured; agent and environment studies make action observable; training papers alter "
    "the experiences available to a learner; and evaluation work asks whether both outcomes "
    "and intermediate behavior are trustworthy. The synthesis treats these contributions as "
    "complementary evidence, not as interchangeable demonstrations of AGI. Its central question "
    "is practical: what should researchers measure and disclose before claiming that an agent "
    "has transferred a capability, acted reliably over time, or used evidence faithfully? "
    "The answer developed below is a layered one. Define the task population, specify the full "
    "system, test variation beyond training, preserve outcome and process measures, and report "
    "uncertainty and cost. These steps do not create a universal AGI test; they make narrower "
    "claims easier to compare and falsify. This review therefore separates a system’s observed "
    "capability from the conditions that enabled it. Model choice, scaffolding, retrieval, "
    "tool permissions, environment fidelity, demonstrations, and retry budgets all affect what "
    "a reported score means. They should be treated as part of the evaluated system and "
    "recorded with enough detail for a reader to understand the result. Where a source omits a "
    "detail, the review marks the limit rather than inferring a favorable configuration. "
    "The analysis first sets out scope and evidence standards, then compares themes across the "
    "corpus before reviewing each source in a common format. A proposed architecture and "
    "measurement protocol follow, with appendices covering task design, budgets, failure "
    "classification, replication, and communication of uncertainty. The closing argument is "
    "deliberately bounded: broad capability claims require diverse task families, meaningful "
    "held-out transfer, sustained execution, and process evidence, while deployment claims also "
    "require explicit constraints and a description of what remains untested."
)

KEYWORDS = "Keywords: artificial general intelligence; agent evaluation; transfer; environment scaling; multimodal grounding; process reliability"


def cite_markup(text: str) -> str:
    def convert(match: re.Match) -> str:
        ids = re.findall(r"R\d{2}", match.group(1))
        if not ids:
            return match.group(0)
        return "[" + ", ".join(f'<link href="#{key}" color="#183F7A">{key}</link>' for key in ids) + "]"
    text = re.sub(r"\[(R\d{2}(?:\s*[–-]\s*R\d{2}|,\s*R\d{2})*)\]", convert, text)
    return html.escape(text, quote=False) if "<link" not in text else text.replace("&", "&amp;").replace("&amp;lt;", "&lt;")


def clean_text(text: str) -> str:
    # Source text is authored here; escape XML-significant characters while
    # preserving the inline links added for source keys.
    safe = html.escape(text, quote=False)
    safe = re.sub(r"\[R(\d{2})\]", r'<link href="#R\1" color="#183F7A">[R\1]</link>', safe)
    safe = re.sub(r"\[(R\d{2})[–-](R\d{2})\]", lambda m: "[" + ", ".join(
        f'<link href="#R{i:02d}" color="#183F7A">[R{i:02d}]</link>'
        for i in range(int(m.group(1)[1:]), int(m.group(2)[1:]) + 1)), safe)
    safe = re.sub(r"\[(R\d{2}),\s*(R\d{2})\]", lambda m: "[" + ", ".join(
        f'<link href="#{k}" color="#183F7A">[{k}]</link>' for k in m.groups()), safe)
    safe = re.sub(r"&(?!(?:amp|lt|gt|quot|apos);)", "&amp;", safe)
    return safe


def make_source_figure(source_number: int) -> Path | None:
    """Crop a source paper's Fig. 1 and caption as a high-resolution image."""
    source_pdf = next(iter(sorted(PAPERS.glob(f"{source_number:02d}_*.pdf"))), None)
    if not source_pdf:
        return None
    out = FIGDIR / f"R{source_number:02d}_source_fig1.png"
    if out.exists() and out.stat().st_mtime >= source_pdf.stat().st_mtime:
        return out
    raw = subprocess.run(
        ["pdftotext", "-bbox-layout", str(source_pdf), "-"],
        check=True, capture_output=True, text=True,
    ).stdout
    raw = "".join(c for c in raw if ord(c) >= 32 or c in "\n\r\t")
    raw = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", raw)
    root = ET.fromstring(raw)
    candidate = None
    for page_index, page in enumerate(root.findall(".//{*}page"), 1):
        for block in page.findall("./{*}flow/{*}block"):
            words = " ".join(w.text or "" for w in block.findall(".//{*}line/{*}word"))
            if re.match(r"\s*(?:Figure|Fig\.)\s*1\s*[:.]", words, re.I):
                candidate = (page_index, page, block)
                break
        if candidate:
            break
    if not candidate:
        return None
    page_num, page, block = candidate
    pwidth, pheight = float(page.attrib["width"]), float(page.attrib["height"])
    x0, y0 = float(block.attrib["xMin"]), float(block.attrib["yMin"])
    x1, y1 = float(block.attrib["xMax"]), float(block.attrib["yMax"])
    span = x1 - x0
    if span > 350 or (x0 > 140 and x1 < 450):
        crop_x0, crop_x1 = 52, pwidth - 50
    elif x0 < pwidth / 2:
        crop_x0, crop_x1 = 55, pwidth / 2 - 8
    else:
        crop_x0, crop_x1 = pwidth / 2 + 2, pwidth - 52
    crop_heights = {10: 230, 11: 235, 12: 235, 13: 225, 14: 215,
                    15: 175, 16: 275, 17: 245, 18: 205, 19: 185, 20: 185}
    crop_y0 = max(50, y0 - crop_heights[source_number])
    crop_y1 = min(pheight - 45, y1 + 4)
    scale = 240 / 72
    full = FIGDIR / f"_page_{source_number:02d}.png"
    subprocess.run(
        ["pdftoppm", "-f", str(page_num), "-l", str(page_num), "-singlefile",
         "-r", "240", "-png", str(source_pdf), str(full.with_suffix(""))],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not full.exists():
        full = full.with_suffix(".png")
    im = PILImage.open(full).convert("RGB")
    box = tuple(round(v * scale) for v in (crop_x0, crop_y0, crop_x1, crop_y1))
    crop = im.crop(box)
    if crop.width > 1700:
        new_h = round(crop.height * 1700 / crop.width)
        crop = crop.resize((1700, new_h), PILImage.Resampling.LANCZOS)
    crop.save(out, optimize=True)
    full.unlink(missing_ok=True)
    return out


def flow_drawing(labels: list[str], index: int) -> Drawing:
    """Small original vector schematic, intentionally distinct from source art."""
    w, h = 245, 102
    d = Drawing(w, h)
    d.add(String(2, 91, "REVIEW SCHEMATIC", fontName="TNR-Bold", fontSize=6.8, fillColor=MUTED))
    gap = 8
    box_w = (w - 8 - gap * (len(labels) - 1)) / len(labels)
    box_y, box_h = 29, 43
    for i, raw in enumerate(labels):
        x = 4 + i * (box_w + gap)
        fill = PALE if i % 2 == 0 else PALETEAL
        d.add(Rect(x, box_y, box_w, box_h, rx=4, ry=4, fillColor=fill, strokeColor=BLUE, strokeWidth=.65))
        words = raw.split()
        lines = []
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > 13 and line:
                lines.append(line)
                line = word
            else:
                line = (line + " " + word).strip()
        if line:
            lines.append(line)
        top = box_y + box_h / 2 + (len(lines) - 1) * 4
        for j, value in enumerate(lines[:3]):
            d.add(String(x + box_w / 2, top - 8 * j, value, textAnchor="middle",
                         fontName="TNR", fontSize=7.0, fillColor=INK))
        d.add(String(x + box_w / 2, 16, str(i + 1), textAnchor="middle",
                     fontName="TNR-Bold", fontSize=6.5, fillColor=TEAL))
        if i < len(labels) - 1:
            ax = x + box_w + 1
            bx = ax + gap - 2
            yy = box_y + box_h / 2
            d.add(Line(ax, yy, bx - 2, yy, strokeColor=TEAL, strokeWidth=.8))
            d.add(Polygon([bx - 3, yy + 2, bx, yy, bx - 3, yy - 2],
                          fillColor=TEAL, strokeColor=TEAL))
    d.add(String(3, 3, "Conceptual reconstruction from the cited paper; not experimental data.",
                 fontName="TNR-Italic", fontSize=6.2, fillColor=MUTED))
    return d


def page_decor(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(.45)
    if doc.page > 1:
        canvas.line(46, h - 34, w - 46, h - 34)
        canvas.setFont("TNR-Bold", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(46, h - 27, "AGI RESEARCH REVIEW · LITERATURE SYNTHESIS")
    header_author = FIRST_AUTHOR if doc.page % 2 else SECOND_AUTHOR
    canvas.setFont("TNR", 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(w - 46, h - 27, header_author.upper())
    canvas.line(46, 33, w - 46, 33)
    canvas.setFont("TNR-Italic", 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(46, 21, "Independent literature synthesis")
    canvas.setFont("TNR", 7.2)
    canvas.drawRightString(w - 46, 21, f"{doc.page:02d}")
    canvas.restoreState()


def make_styles():
    body = ParagraphStyle(
        "Body", fontName="TNR", fontSize=10.0, leading=12.2, textColor=INK,
        alignment=TA_JUSTIFY, firstLineIndent=8, spaceAfter=4.1, allowWidows=0, allowOrphans=0,
    )
    firstbody = ParagraphStyle("FirstBody", parent=body, fontSize=9.9, leading=12.1, firstLineIndent=0, spaceAfter=5)
    abstract = ParagraphStyle("Abstract", parent=body, fontSize=9.9, leading=12.1, firstLineIndent=0, spaceAfter=5)
    h1 = ParagraphStyle("H1", fontName="TNR-Bold", fontSize=11.2, leading=13.0, textColor=INK,
                        spaceBefore=10, spaceAfter=4, keepWithNext=True)
    h2 = ParagraphStyle("H2", fontName="TNR-Bold", fontSize=9.8, leading=11.4, textColor=INK,
                        spaceBefore=6, spaceAfter=2.4, keepWithNext=True)
    paper = ParagraphStyle("PaperTitle", fontName="TNR-Bold", fontSize=10.4, leading=12.0,
                           textColor=INK, spaceBefore=9, spaceAfter=3, keepWithNext=True)
    meta = ParagraphStyle("Meta", fontName="TNR-Italic", fontSize=8.1, leading=9.4,
                          textColor=MUTED, spaceAfter=4)
    caption = ParagraphStyle("Caption", fontName="TNR", fontSize=7.5, leading=8.8,
                             textColor=MUTED, alignment=TA_LEFT, spaceBefore=2, spaceAfter=5)
    title = ParagraphStyle("Title", fontName="TNR-Bold", fontSize=17.4, leading=20.5,
                           textColor=INK, alignment=TA_CENTER, spaceAfter=8)
    byline = ParagraphStyle("Byline", fontName="TNR-Bold", fontSize=10.5, leading=12.3,
                            alignment=TA_CENTER, textColor=INK, spaceAfter=3)
    affiliation = ParagraphStyle("Affiliation", fontName="TNR", fontSize=9.0, leading=10.5,
                                 alignment=TA_CENTER, textColor=INK, spaceAfter=3)
    keywords = ParagraphStyle("Keywords", fontName="TNR-Italic", fontSize=8.2, leading=9.8,
                              alignment=TA_LEFT, textColor=MUTED, spaceBefore=3, spaceAfter=2)
    ref = ParagraphStyle("Ref", fontName="TNR", fontSize=8.1, leading=9.7, leftIndent=13,
                         firstLineIndent=-13, spaceAfter=3, textColor=INK, allowWidows=0, allowOrphans=0)
    note = ParagraphStyle("Note", fontName="TNR", fontSize=8.3, leading=10.1,
                          textColor=INK, borderColor=RULE, borderWidth=.45, borderPadding=5,
                          backColor=PALE, spaceBefore=3, spaceAfter=5)
    small = ParagraphStyle("Small", fontName="TNR", fontSize=7.6, leading=8.9, textColor=INK)
    return dict(body=body, firstbody=firstbody, abstract=abstract, h1=h1, h2=h2,
                paper=paper, meta=meta, caption=caption, title=title, byline=byline,
                affiliation=affiliation, keywords=keywords, ref=ref, note=note, small=small)


def add_paragraph(story, text: str, style):
    story.append(Paragraph(clean_text(text), style))


def figure_flowable(source: dict, styles: dict, column_width: float):
    num = source["n"]
    if num < 10:
        drawing = flow_drawing(source["diagram"], num)
        img = drawing
        caption = source["figcaption"]
    else:
        path = make_source_figure(num)
        if path:
            img = Image(str(path))
            img._restrictSize(column_width, 166)
            caption = source["figcaption"]
        else:
            img = flow_drawing([source["title"][:20], "Method", "Evidence", "Limit"], num)
            caption = f"Reviewer schematic based on [{source['key']}]; original source figure crop unavailable."
    return [img, Paragraph(clean_text(caption), styles["caption"])]


def build_document():
    page_w, page_h = letter
    left_margin, right_margin = 48, 48
    gutter = 18
    col_w = (page_w - left_margin - right_margin - gutter) / 2
    bottom = 42
    top = page_h - 42

    doc = BaseDocTemplate(
        str(TARGET), pagesize=letter, leftMargin=left_margin, rightMargin=right_margin,
        topMargin=42, bottomMargin=bottom, title="General Intelligence as a Research Program",
        author=AUTHORS,
        subject="Independent synthesis of twenty recent papers on AGI, agents, evaluation, and reliability",
    )
    first_frame = Frame(48, bottom, page_w - 96, page_h - 84, id="first",
                        leftPadding=0, rightPadding=0, topPadding=2, bottomPadding=0)
    f1 = Frame(left_margin, bottom, col_w, top - bottom - 4, id="left",
               leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    f2 = Frame(left_margin + col_w + gutter, bottom, col_w, top - bottom - 4, id="right",
               leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="First", frames=[first_frame], onPage=page_decor),
        PageTemplate(id="Body", frames=[f1, f2], onPage=page_decor),
    ])
    st = make_styles()
    story = []
    story.append(Paragraph("General Intelligence as a Research Program", st["title"]))
    story.append(Paragraph("A Framework for Evaluating Capability, Transfer, and Reliability in AI Agents", st["affiliation"]))
    story.append(Spacer(1, 3))
    story.append(Paragraph(f"Author:{FIRST_AUTHOR}", st["byline"]))
    story.append(Paragraph(f"Co-Author:{SECOND_AUTHOR}", st["byline"]))
    story.append(Paragraph("20 November 2026", st["affiliation"]))
    story.append(Spacer(1, 7))
    left = [
        Paragraph("Abstract", ParagraphStyle("AbsHead", fontName="TNR-Bold", fontSize=11.1, leading=13, alignment=TA_CENTER, spaceAfter=6)),
        Paragraph(clean_text(ABSTRACT), st["abstract"]),
        Paragraph(clean_text(KEYWORDS), st["keywords"]),
    ]
    intro = [
        Paragraph("1 Introduction", ParagraphStyle("IntroHead", fontName="TNR-Bold", fontSize=11.1, leading=13, alignment=TA_CENTER, spaceAfter=6)),
        Paragraph(clean_text(FIRST_PAGE_INTRO), st["firstbody"]),
    ]
    cover_table = Table([[left, intro]], colWidths=[col_w, col_w], hAlign="LEFT")
    cover_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(cover_table)
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    # Main synthesis. The first page already contains the abstract and opening.
    for title, subsections in CHAPTERS[1:-1]:
        story.append(CondPageBreak(72))
        story.append(Paragraph(clean_text(title), st["h1"]))
        for heading, paragraphs in subsections:
            story.append(Paragraph(clean_text(heading), st["h2"]))
            for p in paragraphs:
                add_paragraph(story, p, st["body"])

    story.append(Paragraph("Corpus map and publication status", st["h1"]))
    source_focus = {
        1: "cognitive profile", 2: "ASI scenarios", 3: "visual intelligence",
        4: "jaggedness", 5: "agent protocols", 6: "environment synthesis",
        7: "continual pre-training", 8: "ZPD curriculum", 9: "computer-use tasks",
        10: "tool environments", 11: "persistent state", 12: "evaluation survey",
        13: "data curation", 14: "multimodal grounding", 15: "agent merging",
        16: "computer use", 17: "dual-role learning", 18: "enterprise workflows",
        19: "process evaluation", 20: "data agents"
    }
    short_status = {
        1: "Lab paper", 2: "Report / preprint", 3: "White paper", 4: "Position paper",
        5: "Preprint", 6: "Preprint", 7: "ICLR 2026", 8: "ICLR 2026", 9: "ICLR 2026",
        10: "Findings ACL", 11: "Findings ACL", 12: "Findings ACL",
        13: "EMNLP 2026", 14: "EMNLP 2026", 15: "EMNLP 2026",
        16: "ACL 2026", 17: "Findings EMNLP", 18: "AACL 2026", 19: "Findings EACL", 20: "EMNLP 2026"
    }
    map_cell = ParagraphStyle("MapCell", fontName="TNR", fontSize=7.1, leading=8.2, textColor=INK)
    map_rows = [[
        Paragraph("<b>Key</b>", map_cell), Paragraph("<b>Paper</b>", map_cell),
        Paragraph("<b>Status</b>", map_cell), Paragraph("<b>Focus</b>", map_cell)
    ]]
    for src in SOURCES:
        key_link = f'<link href="#{src["key"]}" color="#183F7A">[{src["key"]}]</link>'
        map_rows.append([
            Paragraph(key_link, map_cell),
            Paragraph(clean_text(src["title"]), map_cell),
            Paragraph(clean_text(short_status[src["n"]]), map_cell),
            Paragraph(clean_text(source_focus[src["n"]]), map_cell),
        ])
    corpus_table = Table(map_rows, colWidths=[27, 115, 60, 43], repeatRows=1, hAlign="LEFT")
    corpus_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("GRID", (0, 0), (-1, -1), .3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(corpus_table)
    story.append(Spacer(1, 4))
    add_paragraph(story,
        "The index distinguishes peer-reviewed proceedings from reports, preprints, and position work. Status identifies publication context; it does not replace appraisal of each paper’s design and evidence. Official links and full source keys appear in the references.", st["body"])

    story.append(Paragraph("17. Source-by-source technical review", st["h1"]))
    story.append(Paragraph(
        "The following source notes preserve a common comparison frame—research question, method, evidence, and appraisal—while keeping each paper’s contribution bounded to its actual design. “Figure reproduced” identifies an original figure from an ACL Anthology source paper; the figure itself is not presented as new work by this review.",
        st["body"]))
    for source in SOURCES:
        story.append(CondPageBreak(130))
        story.append(Paragraph(f"{source['n']}. {clean_text(source['title'])}", st["paper"]))
        story.append(Paragraph(
            clean_text(f"{source['authors']} · {source['org']} · {source['status']} · {source['date']}"),
            st["meta"]))
        for label, key in [("Question and scope", "question"), ("Method and system", "method"), ("Evidence in the source", "evidence")]:
            story.append(Paragraph(clean_text(label), st["h2"]))
            add_paragraph(story, source[key], st["body"])
        for item in figure_flowable(source, st, col_w):
            story.append(item)
        story.append(Paragraph("Critical appraisal and next test", st["h2"]))
        add_paragraph(story, source["appraisal"], st["body"])
        story.append(Paragraph("Technical reading note", st["h2"]))
        for note_text in TECHNICAL_NOTES[source["n"]]:
            add_paragraph(story, note_text, st["body"])
        story.append(Paragraph("Replication design", st["h2"]))
        add_paragraph(story, REPLICATION_PLANS[source["n"]], st["body"])
        story.append(Paragraph("How this source connects to the corpus", st["h2"]))
        add_paragraph(story, SOURCE_INTERPRETATIONS[source["n"]], st["body"])

    story.append(Paragraph("18. Evidence matrix across the corpus", st["h1"]))
    matrix_rows = [
        ["Evidence family", "Sources", "What the evidence can support", "Main boundary"],
        ["Conceptual framework", "[R01–R04]", "Constructs, dimensions, and questions for future measurement.", "Does not validate a universal AGI threshold."],
        ["System / protocol comparison", "[R05, R18]", "Matched comparisons within selected models, agents, and tasks.", "Configuration and benchmark choice remain decisive."],
        ["Environment and task synthesis", "[R06, R08–R10, R17]", "Repeatable tasks and training settings; evidence about those distributions.", "Generator, simulator, and verifier can share blind spots."],
        ["Training and integration", "[R07, R15–R17]", "Changes associated with specific training or merging methods.", "Knowledge, scaffold, and exposure effects may be confounded."],
        ["Benchmark and source grounding", "[R13, R14, R20]", "Capability on defined curation, retrieval, and data workflows.", "Task coverage and scoring limit external inference."],
        ["Survey and process evaluation", "[R12, R19]", "Evaluation landscape and process-level criteria.", "Taxonomy and checklist validity need further testing."],
    ]
    cell = ParagraphStyle("MatrixCell", fontName="TNR", fontSize=7.25, leading=8.5, textColor=INK)
    table_data = [[Paragraph(clean_text(c), cell) for c in row] for row in matrix_rows]
    matrix = Table(table_data, colWidths=[45, 42, 87, 71], repeatRows=1, hAlign="LEFT")
    matrix.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("TEXTCOLOR", (0, 0), (-1, 0), BLUE),
        ("FONTNAME", (0, 0), (-1, 0), "TNR-Bold"),
        ("GRID", (0, 0), (-1, -1), .35, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(matrix)
    story.append(Spacer(1, 5))
    for p in [
        "The matrix makes a distinction that is easy to lose when all papers are summarized under “AGI research”: some papers define constructs, some measure a bounded task, and some organize prior results. The evidence families can complement one another but cannot be combined by simply adding their scores. Each claim has to travel with its own task distribution and system boundary.",
        "A useful cross-study comparison reports which capabilities overlap, which system factors differ, and which results replicate under a matched evaluation. For example, a source-grounding benchmark and a process checklist can examine the same trajectory from different angles: the former asks whether a claim follows from retrieved evidence; the latter asks whether the agent followed an acceptable procedure. Agreement strengthens a diagnosis; disagreement reveals that the metrics measure different things.",
        "The corpus is strongest on tool-using agents, benchmark construction, and evaluation design. It has thinner coverage of physical robotics, social learning, developmental adaptation, and robust interaction outside simulated or controlled software environments. The absence of such evidence is a limit of this reading set, not evidence that these fields are unimportant."
    ]:
        add_paragraph(story, p, st["body"])

    story.append(Paragraph("19. Cross-study technical analyses", st["h1"]))
    for heading, paragraphs in CROSS_STUDY_ANALYSES:
        story.append(Paragraph(clean_text(heading), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])
    story.append(Paragraph("Additional measurement analysis", st["h2"]))
    for heading, paragraphs in DEEPER_SYNTHESIS:
        story.append(Paragraph(clean_text(heading), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])
    story.append(Paragraph("Technical extensions", st["h2"]))
    for heading, paragraphs in TECHNICAL_EXTENSIONS:
        story.append(Paragraph(clean_text(heading), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])

    story.append(Paragraph("20. Failure analyses and worked cases", st["h1"]))
    cases = [
        ("Case A: correct answer, unsupported process",
         "An agent returns the correct medication fact after relying on parametric memory instead of checking the current prescribing source. Outcome accuracy marks success. A process checklist may flag that the system failed to consult the required source. The user risk depends on whether the remembered answer is current, whether the source was available, and whether the task requires traceable evidence. The evaluation should record both the final result and the actual retrieval path. It should distinguish a harmless alternative from an unsafe shortcut before assigning a violation. This case operationalizes the motivation in [R19] and shows why the task protocol must specify which checks are mandatory."),
        ("Case B: citation present, claim not supported",
         "A multimodal agent cites a long document but uses a nearby paragraph rather than the relevant table value. The answer may be plausible and the citation technically valid, yet the evidence does not entail the claim. A source-grounding test should locate the exact passage or media region and evaluate the relation between evidence and statement. Counterfactual edits provide a strong test: alter the table value and observe whether the answer updates. RDQA [R14] motivates this decomposition into search, localization, and retrieval; DAB [R20] similarly preserves query execution for audit."),
        ("Case C: long task with stale state",
         "A persistent agent resumes a research task from a saved summary. The summary predates a source revision, so the next plan treats an outdated result as settled. A simple resume benchmark may score continuity as success. A stronger test injects stale or conflicting files, checks whether the system detects the mismatch, and records whether it updates dependent conclusions. State provenance, timestamps, and re-validation can reduce silent error propagation. This case joins the file-centric approach of [R11] with the visual memory concerns in [R16]."),
        ("Case D: self-generated benchmark loop",
         "A task generator creates examples that its own verifier and training agent find difficult, then rewards trajectories that satisfy the verifier. Over time, the agent may learn the verifier’s conventions while the tasks drift away from the intended real-world skill. Calibration with multiple learner systems, human review, external benchmark tests, and reserved task grammars can expose this failure. The issue applies to frontier curricula [R08], synthetic computer-use tasks [R09], environment scaling [R06, R10], and co-evolving environments [R17]."),
        ("Case E: capability lost during specialist merging",
         "A merged checkpoint gains a score on the target role but loses a low-frequency behavior that one specialist handled well. An average across benchmarks may show a small net gain and hide this regression. The evaluation should compare per-task profiles before and after merging, include unrelated tasks and calibration, and measure how the change affects safety constraints. This is the central measurement concern for methods such as ARM [R15]: consolidation is useful only if retained and new abilities are both visible."),
        ("Case F: enterprise answer with a hidden join error",
         "A data agent returns a fluent revenue summary after joining tables on similar-looking but non-equivalent identifiers. The user sees a plausible answer, but the underlying query duplicates records. Keep the executable query, intermediate row counts, schema assumptions, and validation outcome. Hold out altered schemas and corrupted join keys. DAB [R20] identifies ill-formed joins and text transformations as real workload properties; an answer-only rubric would miss the source of the mistake.")
    ]
    for title, body in cases:
        story.append(Paragraph(clean_text(title), st["h2"]))
        add_paragraph(story, body, st["body"])

    story.append(Paragraph("21. Detailed benchmark construction checklist", st["h1"]))
    benchmark_notes = [
        ("Construct definition", "State the capability claim in observable terms. List neighboring constructs that could produce the same score and explain how the benchmark separates them. Name the intended unit of analysis: model response, agent trajectory, environment interaction, or human–agent workflow."),
        ("Task sampling", "Describe the task population, inclusion criteria, sampling frame, number of tasks per family, and any stratification by difficulty. Preserve alternative correct paths. Report how task authors were trained and how ambiguous items were adjudicated."),
        ("Environment", "Version the tool schema, initial state, reset behavior, data, permissions, timing, rate limits, and failure modes. Mark every simulated feature. For live tools, describe safe account scope, state rollback, and user authorization."),
        ("Scoring", "Publish the primary rubric, partial-credit rules, denominators, timeout handling, and evaluator version. Separate correctness from process, grounding, calibration, and policy constraints. Provide examples of accepted and rejected trajectories."),
        ("Verifier audit", "Sample easy, hard, near-miss, adversarial, and alternate-valid cases. Compare automatic judgments with independent human ratings. Estimate false-pass and false-fail rates, especially for errors that would change the central conclusion."),
        ("Leakage and versioning", "Track benchmark visibility, updates, and any use in training or prompt iteration. Maintain stable anchor items and an independently held-out component. Record when task modifications break direct comparability."),
        ("Uncertainty and resources", "Report independent runs, distribution summaries, confidence intervals, model calls, tool calls, latency, retries, and human intervention. For stochastic or costly systems, predefine run count and stopping rules."),
        ("Reproducibility", "Release task manifests, controller code or equivalent specification, prompts, tool descriptions, scoring scripts, system identifiers, and sanitized traces where licensing permits. If access is restricted, state why and provide a practical replication route.")
    ]
    for heading, body in benchmark_notes:
        story.append(Paragraph(clean_text(heading), st["h2"]))
        add_paragraph(story, body, st["body"])

    story.append(Paragraph("22. Researcher’s reporting worksheet", st["h1"]))
    worksheet = [
        ("Claim", "What capability is being asserted? What is the smallest observation that could falsify it?"),
        ("System", "Model and version; controller; prompt; memory; tool set; permissions; evaluator; budget."),
        ("Sample", "Task families; sample size; task source; held-out condition; benchmark version."),
        ("Protocol", "Reset policy; attempts; retries; stop rule; human assistance; failure handling."),
        ("Results", "First-attempt rate; mean and spread; profile by family; confidence intervals; partial completion."),
        ("Process", "Required checks; tool and evidence trace; policy violations; detection and recovery."),
        ("Resources", "Model/tool calls; wall time; tokens or compute; monetary cost; human review time."),
        ("Validity", "Verifier audit; human agreement; contamination checks; external replication; known omissions."),
        ("Conclusion", "What does the evidence support? Which stronger conclusions remain untested?")
    ]
    worksheet_data = [[Paragraph(clean_text(a), cell), Paragraph(clean_text(b), cell)] for a, b in worksheet]
    worksheet_table = Table(worksheet_data, colWidths=[48, 197], hAlign="LEFT")
    worksheet_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PALE),
        ("GRID", (0, 0), (-1, -1), .35, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(worksheet_table)
    story.append(Spacer(1, 5))
    add_paragraph(story,
        "A reader can use this worksheet to compare studies without forcing unlike tasks into a single rank. It also makes missing information visible: if no run count, budget, or evaluator validation is given, the reader should not silently assume these factors are controlled.", st["body"])

    story.append(Paragraph("23. Glossary for cross-paper reading", st["h1"]))
    glossary = [
        ("Agent", "A configured system that selects actions and receives observations in an environment."),
        ("Benchmark", "A task sample, environment, protocol, and scoring procedure used for comparison."),
        ("Calibration", "Agreement between confidence or answer/abstain behavior and observed correctness."),
        ("Capability profile", "A vector or distribution of performance across named task families or faculties."),
        ("Construct validity", "Evidence that the tasks and scores measure the capability the study names."),
        ("Environment", "The state, interface, tools, and transition rules in which an agent acts."),
        ("Generality", "Breadth and transfer under explicitly stated task, environment, and resource conditions."),
        ("Jaggedness", "Uneven performance across tasks or capability dimensions."),
        ("Long horizon", "An activity requiring sustained state and action across many steps or interruptions."),
        ("Process evaluation", "Assessment of intermediate actions and evidence use as well as the final outcome."),
        ("Scaffold", "The prompts, controller, tools, memory, and execution code surrounding a model."),
        ("Transfer", "Performance retained on a task or setting changed from the training or tuning distribution."),
        ("Verifier", "An evaluator that checks task validity, trajectory correctness, or policy compliance.")
    ]
    for term, definition in glossary:
        story.append(Paragraph(f"<b>{clean_text(term)}.</b> {clean_text(definition)}", st["body"]))

    story.append(Paragraph("24. Scope and provenance of the source set", st["h1"]))
    for p in [
        "The source set comprises twenty PDFs supplied in the local papers folder. The date window used here is 20 November 2025 through 20 November 2026. A conference publication date is kept distinct from an earlier arXiv posting. Sources [R01–R06] are lab papers, white papers, position papers, or preprints; [R07–R20] are ICLR, ACL, Findings of ACL, EMNLP, Findings of EMNLP, EACL, or AACL conference and survey publications as recorded in their official proceedings.",
        "The date printed in the supplied PDF for [R02] is 10 November 2026 (arXiv version 3). The arXiv identifier 2606.12683 is not the version date. This review corrects the earlier local index entry that treated June as the publication date. Versioning matters for a rapidly updated report and should be preserved in future citations.",
        "Text extraction and rendered-page inspection were used to check the supplied papers, diagrams, and key tables. Figure reproductions from the ACL Anthology are credited to their source papers under the ACL’s reuse policy, excluding any third-party material. Diagrams for the other sources are review schematics. This document links to official records rather than republishing the entire source papers."
    ]:
        add_paragraph(story, p, st["body"])

    story.append(Paragraph("Additional cross-study analyses", st["h1"]))
    for heading, paragraphs in FINAL_ANALYSES:
        story.append(Paragraph(clean_text(heading), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])

    story.append(Paragraph("Worked evaluation designs", st["h1"]))
    for heading, paragraphs in WORKED_DESIGNS:
        story.append(Paragraph(clean_text(heading), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])

    story.append(Paragraph("One-year research roadmap", st["h1"]))
    for phase, work in RESEARCH_ROADMAP:
        story.append(Paragraph(clean_text(phase), st["h2"]))
        add_paragraph(story, work, st["body"])

    story.append(Paragraph("Implementation blueprint", st["h1"]))
    for heading, paragraphs in IMPLEMENTATION_BLUEPRINT:
        story.append(Paragraph(clean_text(heading), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])
    story.append(Paragraph("Domain-specific evaluation examples", st["h2"]))
    for title, text in DOMAIN_EXAMPLES:
        story.append(Paragraph(f"<b>{clean_text(title)}.</b> {clean_text(text)}", st["body"]))

    story.append(Paragraph("Open research questions", st["h1"]))
    for title, text in RESEARCH_QUESTIONS:
        story.append(Paragraph(f"<b>{clean_text(title)}.</b> {clean_text(text)}", st["body"]))

    story.append(Paragraph("Risk analysis for agent evaluation", st["h1"]))
    for title, text in RISK_ANALYSIS:
        story.append(Paragraph(f"<b>{clean_text(title)}.</b> {clean_text(text)}", st["body"]))
    risk_rows = [
        ["Risk", "Observable signal", "Evaluation check", "Control"],
        ["Instruction conflict", "Agent follows text from a retrieved source.", "Safe conflicting-source tasks; inspect action trace.", "Separate user instruction from untrusted content."],
        ["Tool side effect", "Unexpected or irreversible state change.", "Permission, write, and rollback cases.", "Least privilege; confirmation; sandbox."],
        ["Stale memory", "Old evidence reused after an update.", "Inject revised and contradictory artifacts.", "Provenance, timestamps, refresh, isolation."],
        ["Unsupported claim", "Citation does not entail the statement.", "Claim-level source-span audit.", "Evidence links; uncertainty; abstention."],
        ["Verifier gaming", "High score with a shortcut or malformed outcome.", "Hard negatives and independent adjudication.", "Separate generator, judge, and test set."],
        ["Privacy exposure", "Sensitive content persists in logs or memory.", "Retention and cross-task isolation tests.", "Redaction, access limits, deletion."],
        ["Version drift", "Behavior changes after a model or tool update.", "Rerun stable anchor tasks.", "Version manifest and reevaluation trigger."]
    ]
    risk_cell = ParagraphStyle("RiskCell", fontName="TNR", fontSize=6.8, leading=7.9, textColor=INK)
    risk_table = Table(
        [[Paragraph(clean_text(c), risk_cell) for c in row] for row in risk_rows],
        colWidths=[46, 62, 72, 66], repeatRows=1, hAlign="LEFT"
    )
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("GRID", (0, 0), (-1, -1), .3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 5))

    story.append(Paragraph("Deployment-specific evaluation scenarios", st["h1"]))
    for title, text in DEPLOYMENT_SCENARIOS:
        story.append(Paragraph(f"<b>{clean_text(title)}.</b> {clean_text(text)}", st["body"]))

    story.append(Paragraph("Figure register and provenance", st["h1"]))
    figure_rows = [[
        Paragraph("<b>Source</b>", risk_cell),
        Paragraph("<b>Figure subject</b>", risk_cell),
        Paragraph("<b>Use in this review</b>", risk_cell),
        Paragraph("<b>Provenance note</b>", risk_cell),
    ]]
    for number, subject, use, note_text in FIGURE_REGISTER:
        key = f"R{number:02d}"
        figure_rows.append([
            Paragraph(f'<link href="#{key}" color="#183F7A">[{key}]</link>', risk_cell),
            Paragraph(clean_text(subject), risk_cell),
            Paragraph(clean_text(use), risk_cell),
            Paragraph(clean_text(note_text), risk_cell),
        ])
    figure_table = Table(figure_rows, colWidths=[26, 86, 72, 62], repeatRows=1, hAlign="LEFT")
    figure_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("GRID", (0, 0), (-1, -1), .3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(figure_table)
    story.append(Spacer(1, 5))

    story.append(Paragraph("Conclusion", st["h1"]))
    for heading, paragraphs in CHAPTERS[-1][1]:
        story.append(Paragraph(clean_text(heading), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])

    story.append(PageBreak())
    story.append(Paragraph("Appendices: measurement and implementation detail", st["h1"]))
    for appendix_title, paragraphs in APPENDICES:
        story.append(CondPageBreak(80))
        story.append(Paragraph(clean_text(appendix_title), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])
    for appendix_title, paragraphs in APPENDIX_WORKED_EXAMPLES:
        story.append(CondPageBreak(80))
        story.append(Paragraph(clean_text(appendix_title), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])
    for appendix_title, paragraphs in APPENDIX_EXTRA:
        story.append(CondPageBreak(80))
        story.append(Paragraph(clean_text(appendix_title), st["h2"]))
        for p in paragraphs:
            add_paragraph(story, p, st["body"])

    story.append(Paragraph("References", st["h1"]))
    for source in SOURCES:
        label = source["status"]
        if source["n"] == 10:
            detail = "Findings of the Association for Computational Linguistics: ACL 2026, pp. 17610–17621."
        elif source["n"] == 11:
            detail = "Findings of the Association for Computational Linguistics: ACL 2026, pp. 35884–35894."
        elif source["n"] == 12:
            detail = "Findings of the Association for Computational Linguistics: ACL 2026, pp. 26690–26714."
        elif source["n"] == 13:
            detail = "Proceedings of EMNLP 2026, pp. 18960–18995."
        elif source["n"] == 14:
            detail = "Proceedings of EMNLP 2026, pp. 42175–42194."
        elif source["n"] == 15:
            detail = "Proceedings of EMNLP 2026, pp. 48104–48118."
        elif source["n"] == 16:
            detail = "Proceedings of ACL 2026, pp. 22300–22330."
        elif source["n"] == 17:
            detail = "Findings of EMNLP 2026, pp. 4360–4379."
        elif source["n"] == 18:
            detail = "Proceedings of AACL 2026, pp. 915–933."
        elif source["n"] == 19:
            detail = "Findings of the European Chapter of ACL: EACL 2026, pp. 2678–2692."
        elif source["n"] == 20:
            detail = "Proceedings of EMNLP 2026, pp. 42651–42677."
        else:
            detail = label + ", " + source["date"] + "."
        ref_text = (
            f'<a name="{source["key"]}"/><b>[{source["key"]}]</b> '
            f'{clean_text(source["authors"])}, <i>{clean_text(source["title"])}</i>. '
            f'{clean_text(detail)} '
            f'<link href="{html.escape(source["url"], quote=True)}" color="#183F7A">Official source</link>.'
        )
        story.append(Paragraph(ref_text, st["ref"]))
    story.append(Paragraph(
        '<b>[L1]</b> ACL Anthology. “Copyright FAQ.” <link href="https://aclanthology.org/faq/copyright/" color="#183F7A">https://aclanthology.org/faq/copyright/</link>. Reuse of source figures is limited to author-created content covered by the applicable license; third-party material is excluded.',
        st["ref"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Document status: independent literature synthesis. The bibliographic records and source links should be checked against the current publisher versions before formal academic submission.",
        st["note"]))

    story.append(Paragraph("Supplementary guide: structured reading protocol for the source papers", st["h2"]))
    for p in [
        "Begin by recording provenance: exact title, authors, affiliations, publication or preprint status, version, date, and official source. For a conference paper, distinguish the proceedings year from an earlier preprint. This prevents a convenient citation from silently referring to a different version than the PDF actually reviewed.",
        "Next, state the paper’s central question in one sentence and identify the paper type. A framework, survey, benchmark, experiment, and scenario report support different inferences. Mark whether the question concerns a model, a complete agent, an environment, an evaluation method, or a future possibility. Keep the authors’ stated claim separate from your interpretation.",
        "Read the method before accepting the headline. Record task population, system configuration, controls, baseline, budget, evaluator, and repeat count. For benchmark papers, inspect task construction and verification; for training papers, note what changed in the data and model; for architecture papers, identify components and ablations. This creates a compact methods record that can be compared across papers.",
        "For each main result, write down the metric, denominator, uncertainty, and exact conditions. Separate a reported observation from the broader conclusion the authors discuss. A score on one task family does not establish performance in another, and a single successful trajectory is not a success rate. Preserve table and figure context when interpreting a result.",
        "Treat diagrams as explanations of the authors’ proposed system or experimental setup. Check whether a diagram is conceptual, depicts a measured pipeline, or summarizes results. Trace its caption and surrounding text to the relevant method. A diagram may clarify a claim, but it is not independent evidence that the mechanism works.",
        "Finish with limitations and one replication question. Identify the strongest alternative explanation, the task or population omitted, and the smallest experiment that would distinguish those explanations. Then compare the paper with other sources in this review. The goal is not to agree with a paper’s framing, but to place its evidence accurately in the cumulative research record.",
        "Maintain an evidence ledger with one row per claim that matters to the synthesis. Record the page, section, table, or figure where the claim appears; the exact measurement being reported; and whether the statement comes from the authors or from this review. A compact ledger makes it possible to check a citation quickly and reduces the risk that an abstract-level summary is mistaken for a result demonstrated in the experiments.",
        "When comparing two reported scores, check that the task units match. A task, episode, subtask, trajectory, and user request can each be counted differently. Note whether success is binary, partial, judged by a model, or verified against an external state change. If the evaluator is model-based, inspect the rubric and any human agreement study. A numerical difference is meaningful only after the outcome definition and evaluation conditions are aligned.",
        "Track assistance as part of the system boundary. Record the foundation model, prompt, demonstrations, retrieval corpus, tools, environment hints, human intervention, and retry policy when the paper provides them. Missing details should be marked as unreported rather than silently filled with assumptions. This matters especially when a paper compares agents: a stronger underlying model, larger context, or extra tool budget may explain some of the observed gain.",
        "Separate average performance from tail behavior. When repeated runs or per-task results are available, examine variance, failure concentration, and the hardest task families. A mean can improve while a specific group becomes less reliable. For a safety-relevant task, record both frequency and severity: a rare irreversible action may deserve more attention than a common, easily corrected formatting error. Avoid treating a small sample as evidence that rare failures do not occur.",
        "A useful cross-paper comparison has a narrow claim. For example, one benchmark may support the statement that a tested system handled a defined set of browser workflows under a stated tool budget. It cannot, by itself, show broad transfer, durable autonomy, or safe behavior in a live service. Link every synthesis sentence to the dimensions actually measured and state where evidence from another source is needed to extend the conclusion.",
        "Before circulating a literature review, make one final traceability pass. Follow each in-text source key to the bibliography and official record; confirm author names, title, venue or preprint status, version, and publication date. Check that each figure has a source or is clearly labeled as an original schematic, and that each table distinguishes reported values from proposed measures. This final pass improves the usefulness of the document for readers who want to reproduce or challenge its conclusions.",
        "Record stopping rules and resource limits as part of the method. An agent evaluated with a fixed action budget should be compared with another agent under the same limit, and unfinished tasks should remain visible in the results. Report wall-clock time, model calls, tool calls, and recovery attempts where possible. A system that succeeds only after many retries may be useful in some settings, but the cost and failure opportunities belong in the evidence record.",
        "Preserve enough material for a later replication: task instructions, environment version, tool schema, prompts, scoring rules, and analysis code, subject to privacy and security constraints. If a benchmark cannot release live data, it can still publish a stable task specification, synthetic examples, or a controlled access procedure. Version identifiers matter because changing a tool API or environment can alter the difficulty even when the task name remains constant.",
        "Finally, note disagreement within the corpus. If one paper reports broader transfer while another finds sharp performance drops on compositional or long-horizon tasks, retain both observations and compare their task definitions, systems, and evaluation budgets. A review should make the boundary of agreement explicit, then identify the evidence that could resolve it. This keeps the synthesis open to revision as new replications and stronger baselines appear."
    ]:
        add_paragraph(story, p, st["body"])

    doc.build(story)
    return TARGET


if __name__ == "__main__":
    result = build_document()
    print(result)
