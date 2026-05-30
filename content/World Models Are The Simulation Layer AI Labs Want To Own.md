---
title: "World Models Are The Simulation Layer AI Labs Want To Own"
source: "https://www.llmrumors.com/news/world-models-open-endedness-simulation-layer"
author:
  - "[[Plutonous]]"
published: 2026-05-29
created: 2026-05-29
description: "World models began with Schmidhuber's controller-plus-world-model loop. Genie 3, DreamerV3, GAIA-1, GameNGen, V-JEPA, and open-ended exploration show why…"
tags:
  - "clippings"
---
![World Models: The Simulation Layer AI Labs Are Racing To Own](https://www.llmrumors.com/_next/image?url=%2Fimages%2Fposts%2Fworld-models-open-endedness%2Fworld-models-newspaper-engine.png&w=3840&q=75&dpl=dpl_3UVcGSxAonodEyJpEtMJq9BeTfS2)

**TL;DR:** World models are not just better video prediction. They are the rehearsal substrate for agents that need to act before they can safely touch the real world. Schmidhuber sketched the controller plus world-model loop in 1990, Ha and Schmidhuber compressed CarRacing into a 32-dimensional latent state with an 867-parameter controller in 2018, DreamerV3 crossed 150+ tasks in 2023, and Genie moved the category to 11B parameters in 2024 before Genie 3 reached 24 FPS at 720p in 2025.<sup><a href="#source-1">[1]</a></sup> <sup><a href="#source-3">[3]</a></sup> <sup><a href="#source-6">[6]</a></sup> <sup><a href="#source-11">[11]</a></sup> <sup><a href="#source-13">[13]</a></sup> The real story isn't pixels. It is who controls the simulator where future agents learn what to try next.

Schmidhuber saw the strategic shape before the industry had the hardware to make it fashionable. In 1990, the point was not "generate a pretty future frame." The point was to train a controller beside a predictive model of the world, then use that learned model for planning through mental simulation.<sup><a href="#source-1">[1]</a></sup>

That framing matters again because AI is running out of cheap, static text as the dominant training surface. Text taught models to imitate human records. World models promise something more aggressive: agents that can produce environments, act inside them, fail cheaply, and search for stepping stones human curriculum designers would never think to specify.

Let's be clear. This is not a side quest for video teams. It is the next platform fight for labs that want agents, robotics, autonomous driving, games, scientific discovery, and open-ended exploration to become one stack.

NOTE

#### Why This Matters Now

World models turn prediction into infrastructure. They let a system ask, "What would happen if I did this?" before spending real-world time, money, data, or safety margin. That is why the category now spans DeepMind's Genie line, Dreamer-style reinforcement learning, Wayve and Waymo driving simulators, Meta's JEPA-style latent prediction, and open-ended systems that create their own curricula.

![Editorial illustration of a mechanical world-model engine producing simulated futures on newsprint](https://www.llmrumors.com/_next/image?url=%2Fimages%2Fposts%2Fworld-models-open-endedness%2Fworld-models-newspaper-engine.png&w=3840&q=75&dpl=dpl_3UVcGSxAonodEyJpEtMJq9BeTfS2)

A world model is not a video effect. It is a machine for turning experience into possible futures.

## Schmidhuber's Bet: Curiosity Was The First Product Spec

The uncomfortable truth is that world models are older than the current AI hype cycle. Schmidhuber's 1990 report, "Making the World Differentiable," described self-supervised recurrent networks for dynamic reinforcement learning and planning in non-stationary environments.<sup><a href="#source-1">[1]</a></sup> The system had a controller and a world model. The controller acted. The world model learned to predict what the environment would do next. The controller could then use the model to plan.

In 1991, Schmidhuber pushed the idea further with curiosity and boredom in model-building neural controllers. The agent was rewarded for actions that improved its world-model knowledge.<sup><a href="#source-2">[2]</a></sup> That sentence still sounds more ambitious than most modern product copy. The agent was not merely trying to maximize an external score. It was trying to find experiences that made its internal model less wrong.

The real story isn't that Schmidhuber anticipated the phrase "world model." It is that he connected three pieces that the industry is now rediscovering at scale: prediction, action, and self-directed exploration.

That is the missing bridge between today's generative video demos and tomorrow's agents. A video model predicts what comes next. A world model predicts what comes next if an agent does something. An open-ended world model asks what kind of world should be generated so the agent discovers a new capability.

#### The World Model Lineage

The category keeps changing surface form, but the strategic loop is consistent: learn dynamics, imagine futures, use those futures to act.

| Date | Milestone | Significance |
| --- | --- | --- |
| 1990 | Schmidhuber's differentiable world+ | Controller plus learned predictive model for mental simulation and planning. |
| 1991 | Curiosity and boredom+ | Intrinsic reward for actions that improve the world model's knowledge. |
| 2018 | World Models+ | A compact latent model lets simple controllers solve visual control tasks. |
| 2019 | POET and Dreamer+ | Open-ended environments and latent imagination become practical training mechanisms. |
| 2023 | DreamerV3 and GAIA-1+ | General world-model RL crosses 150+ tasks while driving labs scale neural simulation. |
| 2024 | Genie and GameNGen+ | Internet videos and diffusion models start behaving like interactive engines. |
| 2025 | Genie 3+ | Real-time promptable worlds reach 24 FPS at 720p with consistency for a few minutes. |

LLMRumors.com

## The 2018 Reset: Compression Became The Moat

Ha and Schmidhuber's 2018 "World Models" work made the idea feel newly legible because it separated the problem into three useful parts: a visual encoder, a memory model, and a tiny controller.<sup><a href="#source-3">[3]</a></sup>

The numbers were the message. The CarRacing agent used 10,000 random rollouts to train its visual and memory components. It compressed frames into a latent vector `z` with 32 dimensions. Its controller had just 867 parameters. Yet it scored 906 +/- 21 over 100 random tracks.<sup><a href="#source-3">[3]</a></sup>

Here's the genius: the controller did not need to be huge because the world model had already reorganized reality into a space where control was cheaper. The strategic asset was not the policy. It was the representation where the policy could think.

That point gets lost when the field talks about scale only as parameter count. Scale matters. But world models also expose a different kind of leverage: if you learn the right compressed state, acting can become dramatically simpler.

### Why The Category Suddenly Looks Real

Selected hard numbers from the world-model lineage.

867

World Models controller

Parameters in the CarRacing controller after the VAE and MDN-RNN learned the latent dynamics.

\+ Tiny policy, useful model

150+

DreamerV3 coverage

Diverse tasks reportedly handled with one configuration, including Minecraft diamonds from scratch.

\+ General RL signal

11B

Genie scale

Parameters in DeepMind's 2024 foundation world model trained from unlabelled Internet videos.

\+ Internet video enters

24 FPS

Genie 3 runtime

Real-time interactive worlds at 720p, with consistency for a few minutes.

\+ Simulation becomes interface

3.4M

XLand tasks

Unique tasks produced in DeepMind's open-ended play system.

\+ Curriculum at scale

9B+

GAIA-1 scale

Trainable parameters in Wayve's scaled autonomous-driving world model.

\+ Driving data compounds

LLMRumors.com

## Dreamer And Genie: Imagination Became A Training Loop

Dreamer changed the center of gravity from "learn a model" to "learn inside the model." Dreamer learns a latent dynamics model from images, then improves behavior by imagining future trajectories inside that latent space.<sup><a href="#source-4">[4]</a></sup> Plan2Explore sharpened the exploration side by planning to seek expected future novelty through a self-supervised world model.<sup><a href="#source-5">[5]</a></sup>

DreamerV3 was the important escalation. Hafner, Pasukonis, Ba, and Lillicrap reported a single configuration outperforming specialized methods across more than 150 tasks. More provocatively, DreamerV3 collected diamonds in Minecraft from scratch without human data or curricula.<sup><a href="#source-6">[6]</a></sup> That is not just a benchmark brag. Minecraft is a sparse-reward, open-world environment where the useful thing is often many steps away from the obvious thing.

Then Genie made the world itself generative. DeepMind's 2024 Genie paper introduced an 11B-parameter foundation world model trained from unlabelled Internet videos. It could be prompted with text, synthetic images, photographs, and sketches, then interacted with frame by frame despite training without ground-truth action labels.<sup><a href="#source-11">[11]</a></sup>

Genie 2 pushed toward action-controllable 3D environments from a single prompt image, with keyboard and mouse control and examples that could remain consistent up to one minute, though many lasted 10-20 seconds.<sup><a href="#source-12">[12]</a></sup> Genie 3 made the pitch more direct: text-prompted dynamic worlds navigable in real time at 24 FPS and 720p, with consistency for a few minutes and visual memory around one minute.<sup><a href="#source-13">[13]</a></sup>

![Editorial illustration of a paper theater simulator with future frames and a small mechanical explorer](https://www.llmrumors.com/_next/image?url=%2Fimages%2Fposts%2Fworld-models-open-endedness%2Fgenie-dreamer-playable-simulator.png&w=3840&q=75&dpl=dpl_3UVcGSxAonodEyJpEtMJq9BeTfS2)

Genie, Dreamer, and GameNGen point to the same transition: prediction becomes playable.

What's often overlooked is how different these systems are under the hood while still converging on the same economic role. Dreamer imagines latent futures for reinforcement learning. Genie learns action-controllable environments from video. GameNGen shows a diffusion model acting as a real-time game engine for DOOM at 20 FPS on a single TPU.<sup><a href="#source-14">[14]</a></sup> GAIA-1 and Waymo's 2026 World Model point the same concept at autonomous driving, where simulation is not entertainment. It is risk management.<sup><a href="#source-8">[8]</a></sup> <sup><a href="#source-15">[15]</a></sup>

The category is messy because the opportunity is broad. A world model can be a training environment, a planning module, a synthetic data generator, a robotics rehearsal room, a game engine, or an evaluation harness. That is exactly why it matters.

Interactive Simulation Desk

### The Rehearsal Loop, Rendered As A Timeline

This scene turns the article's core argument into a playable loop: observe traces, compress them into state, imagine futures, act cheaply, then route the error back into curriculum.

<iframe allow="autoplay; fullscreen" title="HyperFrames Composition" src="https://www.llmrumors.com/hyperframes/world-models-rehearsal/index.html?__hf_shader_loading=none"></iframe>

Preparing scene transitions

Rendering animated scene samples for shader transitions.

transition

A world model becomes valuable when the imagined branch changes what the agent tries next, not when the simulator merely looks convincing.

### The World-Model Flywheel

The same loop keeps reappearing across Schmidhuber, Dreamer, Genie, and modern simulator work.

1

#### Observe The World

Collect experience from pixels, actions, trajectories, videos, robot logs, driving scenes, games, or synthetic environments.

Scale:Raw experience

2

#### Compress Into State

Turn messy observations into a latent representation where dynamics and controllable variables become easier to model.

Scale:Latent structure

3

#### Predict Futures

Estimate what happens next, either as pixels, tokens, features, rewards, or action-conditioned latent states.

Scale:Possible next states

Key Step

4

#### Act In Imagination

Plan, train, or evaluate policies inside the learned model before touching the expensive or dangerous real environment.

Scale:Cheap trials

Key Step

5

#### Search For Novelty

Use errors, uncertainty, curriculum generation, or open-ended play to find new situations that improve the model and the agent together.

Scale:Open-ended curriculum

## Open-Endedness: The Missing Economic Primitive

Open-endedness is the part that makes world models strategically dangerous.

A static benchmark tells you whether an agent can solve yesterday's test. An open-ended system keeps producing new tests, new worlds, new failure cases, and new stepping stones. That turns evaluation into training and training into discovery.

POET made this idea explicit in 2019 by pairing environment generation with agent optimization. It did not just optimize one agent in one environment. It generated environments and solutions together, then used transfer between environments as a source of stepping stones.<sup><a href="#source-7">[7]</a></sup>

DeepMind's XLand made the scale feel different. The final agents experienced about 700,000 unique games in 4,000 worlds across 200B training steps, producing 3.4M unique tasks.<sup><a href="#source-10">[10]</a></sup> This is the curriculum problem inverted. Instead of humans hand-designing every lesson, the system generates a distribution of lessons and lets pressure accumulate.

The scarce asset is no longer just data. It is the ability to generate worlds where capability has somewhere to grow.

LLM Rumors

LLMRumors.com

The real story isn't that agents need "more environments." They need environments arranged in a productive frontier. Too easy, and the agent learns nothing. Too hard, and it thrashes. The valuable regime is the edge where the model is wrong in a useful way.

That is why Schmidhuber's old curiosity framing still matters. Reward the agent for improving its world model, and exploration becomes more than random wandering. Pair that with modern generative simulators, and you get a much more serious possibility: AI systems that generate their own research agendas inside worlds they can understand well enough to manipulate.

![Editorial illustration of a compass-like prediction apparatus over an unfinished paper map](https://www.llmrumors.com/_next/image?url=%2Fimages%2Fposts%2Fworld-models-open-endedness%2Fopen-ended-jepa-exploration.png&w=3840&q=75&dpl=dpl_3UVcGSxAonodEyJpEtMJq9BeTfS2)

Open-ended exploration is not about wandering forever. It is about finding the next world where learning pressure is highest.

## Pixels Versus Latents: The Split That Matters

There are two stories being bundled under "world models," and they should not be confused.

One story is visual simulation. Genie, GAIA-1, GameNGen, and Waymo's simulator work try to produce worlds humans can inspect and agents can interact with.<sup><a href="#source-8">[8]</a></sup> <sup><a href="#source-11">[11]</a></sup> <sup><a href="#source-14">[14]</a></sup> <sup><a href="#source-15">[15]</a></sup> This is commercially intuitive because buyers can see the thing. A generated driving scene, a playable game, or a navigable 3D environment looks like a product.

The other story is latent prediction. Dreamer does not need to reconstruct every pixel to learn useful behavior. V-JEPA pushes this further by learning visual representations through feature prediction from video, without pretrained image encoders, text, negative examples, reconstruction, or other supervision. The V-JEPA paper reports training on 2 million videos and a largest model scoring 81.9% on Kinetics-400, 72.2% on Something-Something-v2, and 77.9% on ImageNet1K with a frozen backbone.<sup><a href="#source-9">[9]</a></sup>

The uncomfortable truth is that pixel-perfect imagination can be the wrong goal. Agents often need causal affordances, object permanence, reward-relevant state, uncertainty, and controllable abstractions. A beautiful hallucinated video that gets physics wrong is worse than an ugly latent state that supports better action.

#### Three Ways To Read World Models

| Feature | Video Simulator | Latent Predictor | Open-Ended System |
| --- | --- | --- | --- |
| What it optimizes | Plausible interactive futures | Useful hidden structure | New learning frontiers |
| Representative systems | Genie, GAIA-1, GameNGen | Dreamer, V-JEPA, MuZero-style planning | POET, XLand, Plan2Explore |
| Business value | Synthetic environments and demos | Cheaper planning and control | Self-generating curriculum |
| Core risk | Looks right while dynamics drift | Abstract state misses key facts | Novelty becomes noise |
| Strategic question | Can users inspect it? | Can agents act with it? | Can it keep producing useful surprises? |

LLMRumors.com

Here is the strategic read: the winner may not be the lab with the prettiest simulator. It may be the lab that knows when not to render.

## The Platform War: Owning The Dream Means Owning The Data

While competitors ship chat endpoints, world-model labs are building rehearsal spaces.

That matters because rehearsal spaces compound. If you operate a robot fleet, a driving fleet, a game platform, a video platform, or a software-agent runtime, you can collect trajectories, train simulators, generate edge cases, test agents, and feed the failures back into the next model. The simulator becomes a data factory. The data factory becomes an evaluation system. The evaluation system becomes a moat.

Wayve's GAIA-1 shows the commercial logic in miniature. The scaled model had more than 9B trainable parameters, a 6.5B-parameter autoregressive world model, a 2.6B-parameter video decoder, and 4,700 hours of proprietary UK driving data.<sup><a href="#source-8">[8]</a></sup> Waymo's 2026 World Model pushes the same idea through a richer operational lens: simulate rare and complex autonomous-driving scenarios before the Waymo Driver encounters them in the real world.<sup><a href="#source-15">[15]</a></sup>

4,700

Hours of proprietary driving data

Wayve reported this dataset for scaled GAIA-1. That is the kind of domain-specific experience world-model companies can turn into simulation leverage.

LLMRumors.com

The same logic applies outside driving. Game studios have play logs. Robot companies have manipulation traces. Browser-agent companies have task trajectories. Coding-agent companies have repository edits, test failures, and terminal histories. The world model is the machine that can turn those traces into new situations.

That is why "open-ended exploration" sounds academic until it becomes a product primitive. If an AI system can generate the next useful task, the next rare failure, the next training world, or the next simulated customer workflow, then the bottleneck moves from human task design to machine curriculum design.

### Who Gets Leverage From World Models

The winners are not only model labs. They are organizations with action traces, simulatable domains, and feedback loops.

#### Autonomous systems

Driving and robotics companies can turn rare edge cases into repeatable evaluation scenarios.

+Synthetic long-tail scenes

+Lower-risk policy rehearsal

+Better stress tests before deployment

#### Game and simulation platforms

Interactive generation can turn content creation, testing, and agent training into one loop.

+Playable generated worlds

+Automated level variation

+Agent curricula from user behavior

#### AI agent platforms

Software agents need simulated workflows where they can fail cheaply before touching production systems.

+Repository sandboxes

+Synthetic customer tasks

+Regression suites built from agent mistakes

#### Research labs

Open-ended systems can search for tasks that reveal capability gaps faster than static benchmarks.

+Novelty pressure

+Automatic curriculum

+Evaluation that evolves with the model

LLMRumors.com

### The Catch: Hallucinated Physics Is Still Hallucinated Reality

Let's be clear. A world model is not a world.

It is a learned approximation with blind spots. The more convincing it looks, the easier it becomes to forget that it may be wrong in exactly the places that matter. Autonomous driving makes this painfully obvious. A simulator that mishandles a rare pedestrian behavior, a wet-road reflection, or a weird construction pattern can give false confidence at the worst possible time.

The same problem hits open-ended exploration. Novelty is not automatically useful. A system can generate infinite strange environments that teach nothing important. It can also overfit to the simulator's quirks, discovering policies that win in the dream and fail outside it.

WARNING

#### The World Model Trap

The danger is not that world models hallucinate. Every model does. The danger is that interactive hallucinations create confidence. If a simulator becomes the training ground, the lab must measure where the simulator is wrong, not just how impressive it looks.

Genie 2's own framing shows the constraint: worlds could remain consistent up to one minute, but most examples lasted 10-20 seconds.<sup><a href="#source-12">[12]</a></sup> Genie 3 improved that to a few minutes at 24 FPS and 720p, with visual memory around one minute, but the published claim is still bounded.<sup><a href="#source-13">[13]</a></sup> These are major achievements. They are not magic.

The next phase will be less about demos and more about calibration. Can the model represent contact physics, tool use, partial observability, delayed reward, other agents, and irreversible consequences? Can it produce worlds that are not just diverse, but educational? Can it tell an agent when the dream should not be trusted?

### Key Takeaways

1

Schmidhuber's early world-model work matters because it framed prediction as a control and curiosity problem, not a video-generation trick.

2

The modern category split into two useful branches: visual simulators that humans can inspect, and latent predictors that agents can plan inside.

3

Dreamer, Plan2Explore, POET, and XLand show why open-endedness is the strategic layer. The best training environment may be the one the system invents next.

4

Genie, GameNGen, GAIA-1, V-JEPA, and Waymo's World Model show that world models are becoming infrastructure for games, driving, robotics, and agent evaluation.

5

The hard problem is trust. A simulator that looks coherent but encodes bad dynamics can make agents more confident and more brittle.

LLMRumors.com

## The Bottom Line: Simulation Is Becoming The New Context Window

The first era of foundation models was about language. The second was about multimodality. The next one is about action under uncertainty.

World models matter because they offer a path from passive prediction to active rehearsal. They let agents ask counterfactual questions. They let labs manufacture rare situations. They let open-ended systems turn novelty into curriculum. They turn "what happens next?" into "what should I try next?"

The real story isn't that AI can generate worlds. The real story is that AI labs are trying to own the places where future agents practice being useful.

The company that owns the best dream may own the next training economy.

#### Sources & References

Key sources and references used in this article

| # | Source | Outlet | Date | Key Takeaway |
| --- | --- | --- | --- | --- |
| 1 | Making the World Differentiable: On Using Self-Supervised Fully Recurrent Neural Networks for Dynamic Reinforcement Learning and Planning in Non-Stationary Environments | IDSIA Technical Report  Juergen Schmidhuber | February 1990 | Early controller plus world-model framework using self-supervised recurrent networks for planning through mental simulation. |
| 2 | A Possibility for Implementing Curiosity and Boredom in Model-Building Neural Controllers | From Animals to Animats  Juergen Schmidhuber | 1991 | Introduced intrinsic reward for actions that improve a model's knowledge of the world. |
| 3 | World Models | Project Page  David Ha and Juergen Schmidhuber | March 27, 2018 | Showed how a VAE, memory model, and 867-parameter controller could solve visual control tasks through latent dynamics. |
| 4 | Dream to Control: Learning Behaviors by Latent Imagination | arXiv  Danijar Hafner et al. | December 3, 2019 | Dreamer learns latent world models from images and improves behavior by imagining future trajectories. |
| 5 | Planning to Explore via Self-Supervised World Models | ICML 2020  Danijar Hafner et al. | 2020 | Plan2Explore uses expected future novelty in a learned world model as the exploration objective. |
| 6 | Mastering Diverse Domains through World Models | arXiv  Danijar Hafner, Jurgis Pasukonis, Jimmy Ba, Timothy Lillicrap | January 10, 2023 | DreamerV3 reportedly outperforms specialized methods across 150+ tasks with one configuration and collects Minecraft diamonds from scratch. |
| 7 | POET: Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions | arXiv  Rui Wang et al. | January 7, 2019 | Paired environment generation with agent optimization, making stepping stones central to open-ended learning. |
| 8 | Scaling GAIA-1: 9-billion parameter generative world model for autonomous driving | Wayve  Rudi Rankin | October 3, 2023 | Wayve reported a 9B+ parameter driving world model trained on 4,700 hours of proprietary UK driving data. |
| 9 | Revisiting Feature Prediction for Learning Visual Representations from Video | arXiv  Adrien Bardes et al. | February 15, 2024 | V-JEPA trained on 2 million videos using feature prediction, avoiding pixel reconstruction and other supervision. |
| 10 | Generally capable agents emerge from open-ended play | Google DeepMind  Open-Ended Learning Team | July 27, 2021 | XLand agents experienced roughly 700,000 unique games in 4,000 worlds across 200B training steps. |
| 11 | Genie: Generative Interactive Environments | arXiv  Jake Bruce et al. | February 23, 2024 | DeepMind introduced an 11B-parameter foundation world model trained from unlabelled Internet videos with frame-by-frame interaction. |
| 12 | Genie 2: A large-scale foundation world model | Google DeepMind  Jack Parker-Holder et al. | December 4, 2024 | Genie 2 generated action-controllable playable 3D environments from a single prompt image. |
| 13 | Genie 3: A new frontier for world models | Google DeepMind  Jack Parker-Holder and Shlomi Fruchter | August 5, 2025 | Genie 3 generated real-time interactive worlds at 24 FPS and 720p with consistency for a few minutes. |
| 14 | Diffusion Models Are Real-Time Game Engines | arXiv  Dani Valevski, Yaniv Leviathan, Moab Arar, Shlomi Fruchter | August 27, 2024 | GameNGen simulated DOOM at 20 FPS on a single TPU and remained stable over multi-minute sessions. |
| 15 | The Waymo World Model: A New Frontier For Autonomous Driving Simulation | Waymo  Chiyu Max Jiang, Xander Masotto, Bo Sun | February 6, 2026 | Waymo framed its world model as a way to simulate rare and complex autonomous-driving scenarios before real-world exposure. |

15 sourcesClick any row to visit original

*Last updated: May 30, 2026*