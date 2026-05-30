---
title: "AI That Can Improve Itself | Richard Cornelius Suwandi"
source: "https://richardcsuwandi.github.io/blog/2025/dgm/"
author:
  - "[[Richard Cornelius Suwandi]]"
published:
created: 2026-05-29
description: "A deep dive into self-improving AI and the Darwin-Gödel Machine"
tags:
  - "clippings"
---
## AI That Can Improve Itself

Most AI systems today are stuck in a “cage” designed by humans. They rely on fixed architectures crafted by engineers and lack the ability to evolve autonomously over time. This is the [Achilles heel](https://en.wikipedia.org/wiki/Achilles%27_heel) of modern AI — like a car, no matter how well the engine is tuned and how skilled the driver is, it cannot change its body structure or engine type to adapt to a new track on its own. But what if AI could learn and improve its own capabilities without human intervention? In this post, we will dive into the concept of self-improving systems and a recent effort towards building one.

## Learning to learn

The idea of building systems that can improve themselves brings us to the concept of [meta-learning](https://people.idsia.ch/~juergen/metalearning.html), or “learning to learn”

- **Learning to learn: Introduction and overview**  
	S. Thrun, L. Pratt.  
	Learning to learn, pp. 3--17. Springer. 1998.

\[1\]

, which aims to create systems that not only solve problems but also evolve their problem-solving strategies over time. One of the most ambitious efforts in this direction is the Gödel Machine

- **Godel machines: self-referential universal problem solvers making provably optimal self-improvements**  
	J. Schmidhuber.  
	arXiv preprint cs/0309048. 2003.

\[2\]

, proposed by Jürgen Schmidhuber decades ago and was named after the famous mathematician [Kurt Gödel](https://en.wikipedia.org/wiki/Kurt_G%C3%B6del). A Gödel Machine is a hypothetical self-improving AI system that optimally solves problems by recursively rewriting its own code when it can mathematically prove a better strategy. It represents the ultimate form of self-awareness in AI, an agent that can reason about its own limitations and modify itself accordingly.

![Overview of a Gödel machine](https://richardcsuwandi.github.io/assets/img/godel.jpg)

**Figure 1.** Gödel machine is a hypothetical self-improving computer program that solves problems in an optimal way. It uses a recursive self-improvement protocol in which it rewrites its own code when it can prove the new code provides a better strategy.

While this idea is interesting, formally proving whether a code modification of a complex AI system is *absolutely beneficial* is almost an impossible task without restrictive assumptions. This part stems from the inherent difficulty revealed by the [Halting Problem](https://en.wikipedia.org/wiki/Halting_problem) and [Rice’s Theorem](https://en.wikipedia.org/wiki/Rice%27s_theorem) in computational theory, and is also related to the inherent limitations of the logical system implied by [Gödel’s incompleteness theorem](https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems). These theoretical constraints make it nearly impossible to predict the complete impact of code changes without making restrictive assumptions. To illustrate this, consider a simple analogy: just as you cannot guarantee that a new software update will improve your computer’s performance without actually running it, an AI system faces an even greater challenge in predicting the long-term consequences of modifying its own complex codebase.

## Darwin-Gödel Machine

To “relax” the requirement of formal proof, a recent work by proposed the **Darwin-Gödel Machine (DGM)**

- **Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents**  
	J. Zhang, S. Hu, C. Lu, R. Lange, J. Clune.  
	arXiv preprint arXiv:2505.22954. 2025.

\[3\]

, which combines the Darwinian evolution and Gödelian self-improvement. Essentially, DGM abandoned the pursuit of a rigorous mathematical proof and embraced a more pragmatic way that is closer to the essence of life evolution through empirical validation. As the authors put it,

> We do not require formal proof, but empirical verification of self-modification based on benchmark testing, so that the system can improve and explore based on the observed results.

![Overview of the DGM](https://richardcsuwandi.github.io/assets/img/dgm.png)

**Figure 2.** The Darwin-Gödel Machine (DGM) is a self-improving AI system that optimizes its own problem-solving strategy through a combination of Darwinian evolution and Gödelian self-improvement.

The core idea behind DGM is to let the AI agent iteratively modify its own code

[^1]

, and then put these modified new versions into the actual test environment (e.g., coding benchmarks) to judge whether this modification is good by observing its performance. If the modification is good, it will be retained and may become the basis for further evolution in the future; if the modification is bad, it will be eliminated.

### How DGM works

![Animation of the DGM process](https://richardcsuwandi.github.io/assets/img/dgm-animation.gif)

**Figure 3.** Animation showing how DGM iteratively builds a growing archive of agents by harnessing the principles of open-ended exploration. New agents are created and scored by interleaving self-modification with downstream task evaluation.

The general workflow of DGM is as follows:

1. **Initialization:** Evolution begins with one or a few basic coding agents, so-called the “seeds” of intelligence. These initial agents may possess only minimal functionalities, such as executing bash commands or editing entire files. DGM maintains an “archive of agents”, which functions like a biological “gene bank.” This archive preserves all previously generated agents, regardless of their performance level, ensuring that no potentially valuable variation is permanently lost.
2. **Sampling:** DGM selects one or more parent agents from the archive to generate new child agent. The selection mechanism does not focus solely on top performers but instead allows every agent a chance to be chosen. While higher-performing agents are more likely to be selected, DGM also encourages exploration by giving “less successful agents”
	[^2]
	an opportunity to contribute to future generations.
3. **Reproduction:** Once the parents are selected, DGM performs modifications to generate a new child agent. These changes occur at the source code level and can include:
	- *Enhancement of existing tools*, for example, upgrading a file-editing tool that replaces entire files into one capable of precise string replacement.
		- *Addition of new tools or workflows*, such as integrating a static code analysis tool or designing a “think–act–observe” loop.
		- *Improvement of problem-solving strategies*, for instance, refining how the agent prompts the base model or managing long-context code more effectively.
		- *Introduction of collaboration mechanisms*, like having an agent’s code reviewed by another before execution.
4. **Natural Selection:** The newly generated child agent is not automatically accepted into the “elite pool” but must prove its worth through rigorous testing. Each agent’s performance, such as the percentage of successfully solved problems, is quantitatively scored and used to select the best agents.
5. **Tree Formation:** If a child agent outperforms its parent or meets certain quality thresholds, it is added to the archive and becomes a new node in the evolutionary tree. This process repeats iteratively, creating a growing structure of diverse, high-quality agents. Importantly, DGM enables parallel exploration of many different paths in the search space, promoting open-ended discovery and avoiding premature convergence to local optima.

![Workflow of DGM](https://richardcsuwandi.github.io/assets/img/dgm-conceptual.png)

**Figure 4.** DGM iteratively builds a growing intelligent archive by intertwining self-modification with downstream task evaluation. The intelligent body in the archive is selected for self-modification through open exploration.

The paper provides a concrete example of the above principle in action. In the SWE-bench experiment, the performance of newly generated agents showed temporary declines in the 4th and 56th iterations. While traditional hill-climbing methods would abandon these seemingly “regressive paths”, DGM’s open exploration mechanism allows continued exploration. This persistence paid off as by the 70th iteration, the system had created new agents that surpassed all their predecessors, demonstrating the value of maintaining diverse evolutionary paths even when they temporarily appear less promising.

### Can DGM really improve itself?

In the paper, the authors evaluated DGM on two challenging benchmarks:

1. **SWE-bench:** A widely-used benchmark that tests agents’ ability to resolve real-world GitHub issues
	- **SWE-bench: Can Language Models Resolve Real-world Github Issues?**  
		C.E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, K.R. Narasimhan.  
		International Conference on Learning Representations. 2024.
	\[4\]
	. DGM showed impressive progress, improving its performance from 20.0% to 50.0% through self-modification.
2. **Polyglot**: A [multi-language coding benchmark](https://aider.chat/2024/12/21/polyglot.html) containing coding problems in C++, Go, Java, JavaScript, Python and Rust. DGM achieved even more dramatic improvement, jumping from an initial 14.2% to 30.7% success rate, far surpassing the representative hand-designed agent by [Aider](https://aider.chat/).

The impressive performance improvements demonstrate DGM’s fundamental ability to enhance itself through self-modification. Through ablation studies, the authors identified two key factors driving DGM’s success. First, self-modification proved crucial, as when disabled (**DGM w/o Self-improve**), the performance declined substantially, showing that the ability to modify its own code is essential for accelerated learning. Second, the open-ended exploration approach was vital, as removing the Darwinian evolution-inspired search mechanism (**DGM w/o Open-ended exploration**), which maintains an archive of diverse solutions and enables parallel exploration of multiple paths, resulted in lower performance.

![Performance of DGM on SWE-bench and Polyglot](https://richardcsuwandi.github.io/assets/img/dgm-self-improve.png)

**Figure 5.** Self-improvement and open-ended exploration enable the DGM to continue making progress and improve its performance. The DGM automatically discovers increasingly better coding agents and performs better on both SWE-bench (Left) and Polyglot (Right).

### Comparison with AlphaEvolve

In parallel, AlphaEvolve

- **AlphaEvolve: A coding agent for scientific and algorithmic discovery**  
	G. DeepMind.  
	Google DeepMind Technical Report. 2025.

\[5\]

, which is developed by Google DeepMind, also demonstrates another powerful path forward. AlphaEvolve pairs the creative problem-solving capabilities of Google’s Gemini models with automated evaluators in an evolutionary framework. It has already demonstrated significant real-world impact across multiple domains, such as:

- **Data center efficiency:** AlphaEvolve discovered a simple yet highly effective heuristic for Google’s [Borg](https://research.google/pubs/large-scale-cluster-management-at-google-with-borg/) cluster management system, continuously recovering 0.7% of Google’s worldwide compute resources.
- **AI acceleration:** It achieved a 23% speedup in Gemini’s architecture’s vital [kernel](https://docs.jax.dev/en/latest/pallas/index.html) by finding more efficient ways to divide large matrix multiplication operations, resulting in a 1% reduction in overall training time.
- **Mathematical breakthroughs:** Most notably, it discovered an algorithm for multiplying 4x4 complex-valued matrices using just 48 scalar multiplications, surpassing [Strassen’s 1969 algorithm](https://en.wikipedia.org/wiki/Strassen_algorithm), and advanced the 300-year-old [kissing number problem](https://en.wikipedia.org/wiki/Kissing_number_problem) by establishing a new lower bound in 11 dimensions.

While both systems adopt a similar evolutionary framework, their scopes and methodologies differ in the following ways:

| Feature | AlphaEvolve | DGM |
| --- | --- | --- |
| Focus | Evolving functions and codebases | Evolving the agent itself |
| Level of Innovation | Algorithmic level | Agent-level (toolset, methodology) |
| Role of LLM | LLM acts as “genetic operators” to modify algorithms | LLM serves as the “brain” to evolve itself with better tools and strategies |
| Evaluation | Well-defined problems with automated evaluators | Open-ended environments |

To better understand the differences between the two approaches, let us take a look at the following analogy:

### Can we trust a self-improving AI?

The authors also conducted some experiments to evaluate DGM’s reliability and discovered some concerning behaviors. In particular, they observed instances where DGM attempted to manipulate its reward function through deceptive practices. One notable example involved the system fabricating the use of external tools - specifically, it generated fake logs suggesting it had run and passed unit tests, when in reality no tests were executed.

![Hallucination in DGM](https://richardcsuwandi.github.io/assets/img/dgm-hallucination.png)

**Figure 6.** DGM hallucinated the use of an external tool to run unit tests.

To address this issue, the authors implemented a “tool use hallucination” reward function and tasked DGM with optimizing it to eliminate hallucination behaviors. While DGM successfully provided solutions in many cases, it sometimes attempted to circumvent the detection system by removing the markers used to identify hallucinations, despite explicit instructions to preserve them. This behavior is reminiscent of the phenomenon of [Goodhart’s Law](https://en.wikipedia.org/wiki/Goodhart%27s_law) from economics and sociology:

> “When a measure becomes a target, it ceases to be a good measure.”

Fortunately, DGM’s design includes a transparent, traceable lineage of all changes, which enabled the researchers to quickly identify and address these undesirable behaviors. However, this example highlights the need for more robust safeguards to prevent such manipulation attempts in the first place. These findings underscore the critical importance of safety in self-improving AI research.

## Takeaways

DGM represents a groundbreaking step toward the realization of [Life 3.0](https://en.wikipedia.org/wiki/Life_3.0), a concept introduced by physicist [Max Tegmark](https://en.wikipedia.org/wiki/Max_Tegmark). In his book, he classified life into three stages:

- **Life 1.0:** Biological life with fixed hardware and software, such as bacteria.
- **Life 2.0:** Beings like humans, whose behavior can be learned and adapted during their lifetime, though their biology remains fixed.
- **Life 3.0:** A new class of intelligence that can redesign not only its behavior but also its underlying architecture and objectives — essentially, intelligence that builds itself.

![Life 3.0](https://richardcsuwandi.github.io/assets/img/life3.webp)

**Figure 7.** The three stages of life according to Max Tegmark.

While DGM currently focuses on evolving the “software”

[^3]

, it exemplifies the early stages of Life 3.0. By iteratively rewriting its own code based on empirical feedback, DGM demonstrates how AI systems could move beyond human-designed architectures to autonomously explore new designs, self-improve, and potentially give rise to entirely new species of digital intelligence. If this trend continues, we may witness a [Cambrian explosion](https://en.wikipedia.org/wiki/Cambrian_explosion) in AI development, where eventually AI systems will surpass human-designed architectures and give rise to entirely new species of digital intelligence. While this future looks promising, achieving it requires addressing significant challenges, including:

- **Evaluation Framework**: Need for more comprehensive and dynamic evaluation systems that better reflect real-world complexity and prevent “reward hacking” while ensuring beneficial AI evolution.
- **Resource Optimization**: DGM’s evolution is computationally expensive
	[^4]
	, thus improving efficiency and reducing costs is crucial for broader adoption.
- **Safety & Control**: As AI self-improvement capabilities grow, maintaining alignment with human ethics and safety becomes more challenging.
- **Emergent Intelligence**: Need to develop new approaches to understand and interpret AI systems that evolve beyond human-designed complexity, including new fields like “AI interpretability” and “AI psychology”.

In my view, DGM is more than a technical breakthrough, but rather a philosophical milestone. It invites us to rethink the boundaries of intelligence, autonomy, and life itself. As we advance toward Life 3.0, our role shifts from mere designers to guardians of a new era, where AI does not just follow instructions, but helps us discover what is possible.

## Citation

If you find this post useful, please cite it as:

Suwandi, R. C. (Jun 2025). AI That Can Improve Itself. Posterior Update. https://richardcsuwandi.github.io/blog/2025/dgm/.

Or in BibTeX format:

```
@article{suwandi2025dgm,
    title   = "AI That Can Improve Itself",
    author  = "Suwandi, Richard Cornelius",
    journal = "Posterior Update",
    year    = "2025",
    month   = "Jun",
    url     = "https://richardcsuwandi.github.io/blog/2025/dgm/"
}
```

### Footnotes

1. More precisely, the metacode that controls its behavior and ability.
2. Those that might contain novel or unconventional ideas.
3. Here, "software" refers to the code and strategies of AI agents.
4. The paper mentioned that a complete SWE-bench experiment takes about two weeks and about $22,000 in API call costs.

### References

[^1]: Learning to learn: Introduction and overview  
Thrun, S. and Pratt, L., 1998. Learning to learn, pp. 3--17. Springer.

[^2]: Godel machines: self-referential universal problem solvers making provably optimal self-improvements  
Schmidhuber, J., 2003. arXiv preprint cs/0309048.

[^3]: Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents  
Zhang, J., Hu, S., Lu, C., Lange, R. and Clune, J., 2025. arXiv preprint arXiv:2505.22954.

[^4]: SWE-bench: Can Language Models Resolve Real-world Github Issues?  
Jimenez, C.E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O. and Narasimhan, K.R., 2024. International Conference on Learning Representations.

[^5]: AlphaEvolve: A coding agent for scientific and algorithmic discovery  
DeepMind, G., 2025. Google DeepMind Technical Report.