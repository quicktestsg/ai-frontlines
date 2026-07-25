#!/usr/bin/env python3
"""
Translate blog post HTML by adding data-en/data-zh attributes to all text elements.
Also adds the lang toggle button to the nav.
"""
import sys
import re

# ─── Translations for Blog Post 1 ───
POST1 = {
    # Header
    "date": ("July 24, 2026", "2026年7月24日"),
    "read": ("5 min read", "5 分钟阅读"),
    "title": ("The Loop Is the New Function", "循环即新函数"),
    "deck": ("For 70 years the function was the atom of software. Now it's the loop. What changes when code stops running once and starts running forever?",
             "70年来，函数一直是软件的基本原子。现在轮到了循环。当代码不再运行一次就停止，而是永远运行下去时，会发生什么？"),

    # Body paragraphs
    "p1": ("Every programmer alive has internalized the same mental model: software is built from functions. You define an input, you write a transformation, you get an output. <code>f(x) = y</code>. The function is deterministic. It runs once. It stops. If it gives you the wrong answer, you debug the logic, fix it, run it again. This model is so deeply embedded in our tools, languages, and brains that we don't even question it anymore. It's just how software works.",
           "每一个在世的程序员都已内化了同样的心智模型：软件由函数构建。你定义输入，编写变换，得到输出。<code>f(x) = y</code>。函数是确定性的。它运行一次，然后停止。如果给出错误答案，你调试逻辑，修复，再次运行。这个模型深深嵌入我们的工具、语言和大脑中，我们甚至不再质疑它。软件就是这样的。"),
    "p2": ("But something is shifting underneath us. The software being built in 2026 doesn't work like that. AI agents don't transform an input into an output and stop. They observe, act, evaluate, adjust, and repeat. They run in loops that don't have a clean termination condition. The fundamental unit isn't a function call — it's a cycle. And the engineering discipline emerging to design those cycles has a new name: loop engineering.",
           "但某些东西正在我们脚下发生变化。2026年构建的软件不再是那样的。AI 智能体不会将输入变换为输出然后停止。它们观察、行动、评估、调整、重复。它们运行在没有清晰终止条件的循环中。基本单元不是函数调用——而是一个周期。而设计这些周期的工程学科有了一个新名字：循环工程。"),
    "caption1": ("The function runs and stops. The loop runs and learns. Different physics entirely.",
                 "函数运行后停止。循环运行后学习。完全是不同的物理规律。"),
    "h2_1": ("The death of determinism", "确定性的消亡"),
    "p3": ("Here's the uncomfortable truth nobody in the AI engineering discourse wants to say out loud: we lost determinism, and we're not getting it back. A function that calls an LLM is, by definition, not deterministic. The same input can produce different outputs on different days. This isn't a bug. It's the physics of the new substrate. And pretending otherwise — wrapping a model call in a function signature and hoping it behaves like <code>parseInt</code> — is the most common architectural mistake teams make in 2026.",
            "这是 AI 工程话语中没人愿意大声说出的令人不安的真相：我们失去了确定性，而且不会再找回来。调用 LLM 的函数，从定义上说，就不是确定性的。同样的输入在不同日期可能产生不同的输出。这不是 bug，而是新底层技术的物理特性。假装不是如此——把模型调用包装在函数签名中，希望它像 <code>parseInt</code> 那样运行——是2026年团队最常犯的架构错误。"),
    "p4": ("Loop engineering accepts this reality and builds around it. Instead of trying to make models deterministic, you design systems that converge on correctness through repetition. The agent writes code, runs tests, reads the errors, and tries again. Each iteration isn't guaranteed to be right — but the loop, as a whole, is designed to converge. The engineering isn't in the individual step. It's in the shape of the cycle.",
           "循环工程接受这个现实，并在此基础上构建。与其试图让模型变得确定，不如设计通过重复来收敛到正确性的系统。智能体编写代码、运行测试、阅读错误、再试一次。每次迭代都不能保证正确——但整个循环被设计为收敛的。工程不在于单一步骤，而在于周期的形状。"),
    "caption2": ("A single function call starts wrong and stays wrong. A loop starts wrong and converges.",
                 "单次函数调用从一开始就错了，而且一直错。循环从一开始就错了，但会收敛。"),
    "blockquote1": ("We spent 70 years optimizing for the fastest path from input to output. Now we're optimizing for the shortest path from wrong to right. Those are fundamentally different engineering problems.",
                    "我们花了70年优化从输入到输出的最快路径。现在我们要优化从错误到正确的最短路径。这是根本不同的工程问题。"),
    "h2_2": ("What a loop engineer actually does", "循环工程师到底做什么"),
    "p5": ('A traditional engineer asks: "How do I write the function that transforms this input into the correct output?" A loop engineer asks an entirely different set of questions: "How many iterations should this cycle take before I give up? What signal tells the agent it\'s done? What context needs to persist between iterations? Where does the feedback come from — tests, human review, another model? What\'s the cost ceiling per loop before this becomes uneconomic?"',
           '传统工程师会问："我如何编写一个将输入变换为正确输出的函数？" 循环工程师则问一系列完全不同的问题："这个周期应该迭代多少次我才放弃？什么信号告诉智能体它完成了？什么上下文需要在迭代之间持久化？反馈从哪里来——测试、人工审查，还是另一个模型？每个循环的成本上限是多少，超过多少就变得不经济？"'),
    "p6": ('These are not software engineering questions. They\'re closer to control theory — the discipline that gave us thermostats, autopilots, and cruise control. A thermostat doesn\'t "compute" the right temperature. It runs a loop: measure, compare, adjust, repeat. The correctness lives in the loop design, not in any single measurement. Loop engineering is essentially bringing control theory into software, whether we admit it or not.',
           '这些不是软件工程问题。它们更接近控制论——这门学科给我们带来了恒温器、自动驾驶和定速巡航。恒温器不会"计算"正确的温度。它运行一个循环：测量、比较、调整、重复。正确性存在于循环设计中，而不在任何单次测量中。不管我们承认与否，循环工程本质上就是将控制论引入软件。'),
    "p7": ("The practical implications are wild. Your test suite isn't just a quality gate anymore — it's the feedback signal that keeps the loop converging. Your CI/CD pipeline isn't just deployment infrastructure — it's the harness that decides whether the agent's output is safe to ship. Your codebase isn't just a set of instructions — it's the context window that shapes what the agent does next. Everything gets reinterpreted through the lens of the loop.",
           "实际影响是惊人的。你的测试套件不再只是质量关卡——它是保持循环收敛的反馈信号。你的 CI/CD 管道不再只是部署基础设施——它是决定智能体输出是否可以安全发布的测试框架。你的代码库不再只是一组指令——它是塑造智能体下一步行为的上下文窗口。一切都通过循环的视角被重新诠释。"),
    "h2_3": ("The harness is the product", "测试框架才是产品"),
    "p8": ('This is why "harness engineering" keeps coming up in the same conversations as loop engineering. The harness is the scaffolding around the model: the system prompt, the tool definitions, the retrieval pipeline, the evaluation criteria, the retry logic, the guardrails. When your core compute is probabilistic, the deterministic wrapper around it becomes the actual product. OpenAI knows this — it\'s why Codex and ChatGPT Work are built as harnesses, not models. Anthropic knows it — Claude\'s tool-use protocol is a harness specification. The model is a commodity. The loop is the moat.',
           '这就是为什么"测试框架工程"总是和循环工程在同样的对话中被提及。测试框架是围绕模型的脚手架：系统提示、工具定义、检索管道、评估标准、重试逻辑、安全护栏。当你的核心计算是概率性的，围绕它的确定性包装就变成了真正的产品。OpenAI 知道这一点——这就是为什么 Codex 和 ChatGPT Work 是作为测试框架而非模型构建的。Anthropic 也知道——Claude 的工具使用协议就是一个测试框架规范。模型是商品，循环才是护城河。'),
    "caption3": ("The harness: deterministic scaffolding around a probabilistic core. This is the actual product.",
                 "测试框架：围绕概率性核心的确定性脚手架。这才是真正的产品。"),
    "p9": ("I think most teams are still treating AI features as function calls with extra steps. They wrap a prompt in an API endpoint, ship it, and are confused when it works perfectly in testing and degrades in production. The degradation isn't a model problem. It's a loop problem. There's no feedback signal. No convergence criteria. No iteration. Just a single-shot function call that either works or doesn't, with no mechanism to improve itself.",
           "我认为大多数团队仍然把 AI 功能当作函数调用的额外步骤。他们把提示词包装在 API 端点中，发布它，然后在测试中完美运行、在生产环境中退化时感到困惑。退化不是模型的问题，而是循环的问题。没有反馈信号，没有收敛标准，没有迭代。只有一次性的函数调用，要么管用要么不管用，没有自我改进的机制。"),
    "p10": ('The teams winning at AI engineering in 2026 are the ones who stopped asking "how do I write this function?" and started asking "how do I design this loop?" The answer looks less like programming and more like gardening. You don\'t build a garden by placing each leaf. You design the conditions — soil, water, light — and let the system grow toward what you want. The loop is your garden bed. The model is the seed. Your job is to design the conditions for convergence.',
            '在2026年 AI 工程中获胜的团队，是那些不再问"我如何编写这个函数？"而是开始问"我如何设计这个循环？"的团队。答案看起来不太像编程，更像园艺。你不是通过放置每片叶子来建造花园。你设计条件——土壤、水、光照——让系统朝着你想要的方向生长。循环是你的花园床，模型是种子。你的工作是设计收敛的条件。'),
    "p11": ("That's the shift. And it's bigger than any individual model release. The function was a good run. But the loop is where we live now.",
            "这就是转变。它比任何单个模型发布都大。函数曾经很好。但循环才是我们现在生活的地方。"),

    # SVG text elements
    "svg_classic_label": ("CLASSIC SOFTWARE", "经典软件"),
    "svg_input": ("input", "输入"),
    "svg_fx_det": ("deterministic · runs once", "确定性 · 运行一次"),
    "svg_output": ("output", "输出"),
    "svg_wrong_q": ("Wrong answer?", "错误答案？"),
    "svg_debug": ("Debug the function.", "调试函数。"),
    "svg_code_product": ("The code is the product.", "代码就是产品。"),
    "svg_ainative_label": ("AI-NATIVE SOFTWARE", "AI原生软件"),
    "svg_observe": ("Observe", "观察"),
    "svg_observe_sub": ("read context", "读取上下文"),
    "svg_act": ("Act", "行动"),
    "svg_act_sub": ("call tools", "调用工具"),
    "svg_eval": ("Evaluate", "评估"),
    "svg_eval_sub": ("check result", "检查结果"),
    "svg_adjust": ("Adjust", "调整"),
    "svg_adjust_sub": ("update plan", "更新计划"),
    "svg_redesign": ("Redesign the loop.", "重新设计循环。"),
    "svg_harness_product": ("The harness is the product.", "测试框架才是产品。"),
    # convergence chart
    "svg_iterations": ("Iterations", "迭代次数"),
    "svg_error": ("Error", "误差"),
    "svg_converged": ("converged", "已收敛"),
    "svg_attempt1": ("Attempt 1", "尝试 1"),
    "svg_attempt2": ("Attempt 2", "尝试 2"),
    "svg_attempt3": ("Attempt 3", "尝试 3"),
    "svg_single_call": ("Single function call →", "单次函数调用 →"),
    "svg_high_error": ("high error, no recovery", "高误差，无恢复"),
    "svg_loop_converges": ("Loop converges →", "循环收敛 →"),
    "svg_error_zero": ("error → 0 over iterations", "误差随迭代趋近0"),
    # harness diagram
    "svg_harness_label": ("THE HARNESS (deterministic)", "测试框架（确定性）"),
    "svg_sysprompt": ("System Prompt", "系统提示"),
    "svg_tooldefs": ("Tool Definitions", "工具定义"),
    "svg_rag": ("Retrieval (RAG)", "检索 (RAG)"),
    "svg_guardrails": ("Guardrails", "安全护栏"),
    "svg_llm": ("LLM", "LLM"),
    "svg_prob": ("probabilistic", "概率性"),
    "svg_commodity": ("commodity", "商品"),
    "svg_testsuite": ("Test Suite", "测试套件"),
    "svg_evalcrit": ("Eval Criteria", "评估标准"),
    "svg_retrylogic": ("Retry Logic", "重试逻辑"),
    "svg_cicd": ("CI/CD Gate", "CI/CD 关卡"),
    "svg_feedback": ("feedback signal → next iteration", "反馈信号 → 下一次迭代"),
    "svg_context_in": ("context in", "上下文输入"),
    "svg_signal_out": ("signal out", "信号输出"),
}

# ─── Translations for Blog Post 2 ───
POST2 = {
    "date": ("July 25, 2026", "2026年7月25日"),
    "read": ("6 min read", "6 分钟阅读"),
    "title": ("Spaghetti With API Bills", "意大利面与 API 账单"),
    "deck": ("Most multi-agent systems aren't architectures. They're distributed prompts with a billing problem. The fix is older than AI itself.",
             "大多数多智能体系统不是架构。它们是带有账单问题的分布式提示词。解决方案比 AI 本身还要古老。"),
    "p1": ('Most teams building "multi-agent systems" in 2026 are not building systems. They have taken a single oversized prompt, sliced it across twenty agents, and called the result an architecture. The agents share ambiguous context. They return free-form text. They repeat each other\'s research and bill for the privilege. When one model\'s output format drifts — and it will drift — the entire chain collapses into a stack trace nobody can debug. This is not orchestration. It is spaghetti with API bills.',
           '大多数在2026年构建"多智能体系统"的团队并不是在构建系统。他们把一个过大的提示词切成二十个智能体，然后把这个结果叫做架构。智能体共享模糊的上下文。它们返回自由格式的文本。它们重复彼此的研究，还要为此付费。当某个模型的输出格式漂移时——它一定会漂移——整条链就崩溃成没人能调试的堆栈跟踪。这不是编排，这是意大利面加 API 账单。'),
    "p2": ('The pattern is common enough to be a punchline. A team reads that agents are the future, stands up a coordinator, fans out a dozen workers, wires them together with string and a JSON schema, and ships. For two weeks it looks like magic. Then reality arrives: token costs triple, latency balloons, outputs turn inconsistent, and nobody can explain why the system returned what it returned. The instinct is to blame the model. The model is rarely the problem. The problem is that there was never an architecture — only a distribution.',
           '这个模式已经常见到成为笑柄的程度。一个团队读到智能体是未来，搭起一个协调器，展开十几个工人，用线和 JSON schema 把它们连在一起，发布。前两周看起来像魔法。然后现实来了：token 成本翻三倍、延迟膨胀、输出变得不一致，没人能解释系统为什么返回了它返回的东西。直觉是怪罪模型。模型很少是问题所在。问题在于从来就没有架构——只有分发。'),
    "caption1": ("Distribution is not design. Tangled agents share ambiguity; a graph assigns each decision to exactly one node and every edge a contract.",
                 "分发不是设计。纠缠的智能体共享模糊性；图将每个决策分配给恰好一个节点，每条边都有一个契约。"),
    "h2_1": ("The two software crises", "两次软件危机"),
    "p3": ("The original software crisis, named in 1968, was defined by a single failure mode: systems had grown too large for any one person to understand. Code outgrew human comprehension, and the resulting bugs, overruns, and collapses felt existential. The discipline that emerged in response — modular decomposition, abstract data types, interfaces with contracts — was aimed at one specific terror. Every major idea in software engineering since, from objects to services to microservices, is a variation on the same move: break a large system into replaceable parts that speak to each other through strict contracts.",
           "1968年命名的原始软件危机，由一个单一的失败模式定义：系统变得太大，任何人都无法理解。代码超出了人类认知范围，由此产生的 bug、超支和崩溃让人感到存在性威胁。作为回应而兴起的学科——模块化分解、抽象数据类型、带契约的接口——瞄准的是一种特定的恐惧。此后软件工程中的每个重大理念，从对象到服务再到微服务，都是同一手法的变体：将一个大型系统拆分成通过严格契约相互交流的可替换部件。"),
    "p4": ("The new software crisis is the mirror image, and it is arriving faster. It is not too much code. It is too many agents with no architecture between them. An agent is a probabilistic component that produces unstructured output, drifts between versions, and costs money every time it runs. Wire enough of them together without contracts and you have rebuilt the 1968 crisis on a new substrate — except now the components lie, hallucinate, and send invoices.",
           "新的软件危机是镜像，而且来得更快。问题不是代码太多，而是太多智能体之间没有架构。智能体是一个概率性组件，产生非结构化输出，在版本间漂移，每次运行都要花钱。把足够多的智能体连在一起却没有契约，你就把1968年的危机在新的底色上重建了一遍——只不过现在这些组件会说谎、会产生幻觉、还会寄账单。"),
    "p5": ("The fix is the same fix, rediscovered. Graph engineering is the application of a fifty-year-old lesson to AI: one node owns one decision, one edge carries structured evidence, ordinary code handles the deterministic work, routers decide which branch continues, verifiers reject unsupported conclusions, and the strongest model sees only what survives.",
           "解决方案是同一个方案，被重新发现。图工程是将一个五十年的教训应用于 AI：一个节点负责一个决策，一条边承载结构化证据，普通代码处理确定性工作，路由器决定哪条分支继续，验证器拒绝无根据的结论，而最强的模型只看到幸存下来的东西。"),
    "caption2": ("The old crisis was unmanageable code; the new one is unmanaged agents. Both collapse into the same architectural cure.",
                 "旧的危机是无法管理的代码；新的危机是无法管理的智能体。两者都坍缩为同一个架构药方。"),
    "h2_2": ("Replaceability is the moat", "可替换性才是护城河"),
    "p6": ("Here is the claim that matters most. The next durable advantage in AI will not be a single permanent model. It will be a system that keeps working when the model changes. Models are being swapped, repriced, deprecated, and leapfrogged every quarter. A system whose correctness depends on one irreplaceable model is a system with an expiration date. A system in which every node is replaceable is a system with a future.",
           "这是最重要的论断。AI 领域下一个持久的优势不会是某个永久性的单一模型。它将是一个在模型变更时仍然能正常工作的系统。模型每个季度都在被替换、重新定价、弃用和超越。一个正确性依赖于某个不可替换模型的系统，是一个有保质期的系统。一个每个节点都可替换的系统，才是一个有未来的系统。"),
    "p7": ("This is what makes the graph, not the agent, the unit of value. In a well-designed graph, a cheap model handles extraction. A specialist inspects security. A skeptical agent attacks the result. A frontier model renders the final judgment — and it does so without ever carrying the entire workflow inside its context window. Each role is a slot. Each slot accepts any model that satisfies the contract. When a better model lands next month, it slides into the slot. When a vendor disappears, the slot survives.",
           "这就是为什么图，而不是智能体，才是价值单元。在一个设计良好的图中，廉价模型负责抽取。专家检查安全。怀疑论智能体攻击结果。前沿模型做出最终裁决——而且它不需要在整个工作流中携带完整的上下文窗口。每个角色是一个插槽。每个插槽接受任何满足契约的模型。当更好的模型下个月出现时，它滑入插槽。当供应商消失时，插槽依然存在。"),
    "caption3": ("Roles are owned; models are rented. The architecture is the only durable asset.",
                 "角色是拥有的，模型是租用的。架构是唯一持久的资产。"),
    "blockquote1": ("The original software crisis taught engineers to stop writing programs and start writing replaceable parts. The agentic crisis will teach the same lesson, again, to a generation that thought it had skipped the class.",
                    "原始的软件危机教会工程师停止编写程序，开始编写可替换的部件。智能体危机将再次教授同样的课程，给一代以为自己逃了课的人。"),
    "h2_3": ("The discipline returns", "纪律的回归"),
    "p8": ("What is being rediscovered is not glamorous. It is interfaces, contracts, typed edges, separation of concerns. The novelty is that these ideas now govern not just deterministic code but probabilistic components that must be governed more strictly precisely because they are not trustworthy on their own. The graph is a discipline of distrust: structure compensates for the unreliability of the nodes.",
           "被重新发现的并不是什么光鲜的东西。它是接口、契约、类型化边、关注点分离。新颖之处在于，这些理念现在不仅管理确定性代码，还管理概率性组件——而且恰恰因为它们自身不可信，需要被更严格地管理。图是一种不信任的纪律：结构弥补了节点的不可靠性。"),
    "p9": ("Notice what this discipline removes from the frontier model's shoulders. It no longer carries the whole workflow in one context window. It no longer has to be simultaneously the reader, the verifier, and the decider. The work is staged across a pipeline, and by the time a token reaches the strongest model, it has already been filtered, typed, and corroborated. The expensive model spends its budget on judgment, not on janitorial work. Costs fall. Latency falls. And, counterintuitively, quality rises — because every conclusion now arrives with a chain of evidence attached to it rather than the vibes of a single large prompt.",
           "注意这种纪律从前沿模型的肩上卸下了什么。它不再在一个上下文窗口中携带整个工作流。它不再需要同时充当读者、验证者和决策者。工作在管道中分阶段处理，当一个 token 到达最强的模型时，它已经被过滤、类型化和佐证过了。昂贵的模型把预算花在判断上，而不是清洁工作上。成本下降。延迟下降。而且反直觉的是，质量上升了——因为现在每个结论都附带了一条证据链，而不是单个大提示词的感觉。"),
    "p10": ("The teams that win will be the ones who stop measuring how clever their agents are and start measuring how replaceable they are. Cleverness is a property of the model, and the model is a borrowed asset. Replaceability is a property of the architecture, and the architecture is the only thing actually owned.",
            "获胜的团队将是那些停止衡量智能体有多聪明，开始衡量它们有多可替换的团队。聪明是模型的属性，而模型是借来的资产。可替换性是架构的属性，而架构是唯一真正拥有的东西。"),
    "p11": ("Spaghetti with API bills is the default state of multi-agent development in 2026. It is what happens when distribution is mistaken for design. The exit is older than the industry that needs it. Draw the graph. Type the edges. Make every node disposable. Then, and only then, does adding another agent make the system stronger instead of merely more expensive.",
            "意大利面加 API 账单是2026年多智能体开发的默认状态。这是分发被误认为设计时的结果。出口比需要它的行业还要古老。画出图。类型化边。让每个节点都可抛弃。然后，只有到那时，增加另一个智能体才会让系统更强，而不是仅仅更贵。"),

    # SVG elements for Post 2
    "svg_dist_label": ("DISTRIBUTED PROMPT", "分布式提示词"),
    "svg_dist_sub": ("ambiguous context · repeated work · invoice per hop", "模糊上下文 · 重复工作 · 每跳一张账单"),
    "svg_graph_label": ("GRAPH ENGINEERING", "图工程"),
    "svg_rawinput": ("raw input", "原始输入"),
    "svg_extract": ("extract", "抽取"),
    "svg_router": ("router", "路由器"),
    "svg_verify": ("verify", "验证"),
    "svg_judge": ("judge", "裁决"),
    "svg_evidence": ("evidence", "证据"),
    "svg_typed_edge": ("typed edge", "类型化边"),
    "svg_graph_sub": ("one node = one decision · every edge carries a contract", "一个节点 = 一个决策 · 每条边都承载契约"),
    # crisis diagram
    "svg_1968": ("1968 CRISIS", "1968年危机"),
    "svg_too_code1": ("too much code", "代码太多"),
    "svg_too_code2": ("for one mind", "超出一个人脑"),
    "svg_2026": ("2026 CRISIS", "2026年危机"),
    "svg_too_agents1": ("too many agents", "智能体太多"),
    "svg_too_agents2": ("no architecture", "没有架构"),
    "svg_replaceable": ("REPLACEABLE PARTS", "可替换部件"),
    "svg_strict_contracts": ("with strict contracts", "带严格契约"),
    "svg_same_lesson": ("the same lesson, twice", "同样的教训，两次"),
    # slot diagram
    "svg_any_model": ("ANY MODEL FITS THE CONTRACT", "任何模型都满足契约"),
    "svg_slot_extract": ("SLOT · extractor", "插槽 · 抽取器"),
    "svg_cheap_model": ("cheap model", "廉价模型"),
    "svg_slot_specialist": ("SLOT · specialist", "插槽 · 专家"),
    "svg_security": ("security", "安全"),
    "svg_slot_skeptic": ("SLOT · skeptic", "插槽 · 怀疑者"),
    "svg_attacker": ("attacker", "攻击者"),
    "svg_slot_survives": ("the slot survives", "插槽幸存"),
    "svg_roles_owned": ("roles are owned; models are rented", "角色是拥有的；模型是租用的"),
    "svg_vendor_disappear": ("vendor disappears → slide in another. model deprecated → slot unchanged.", "供应商消失 → 换一个。模型弃用 → 插槽不变。"),
}

def build_lang_toggle_nav(base_path_prefix):
    """Build nav HTML with language toggle for post pages."""
    return f'''        <div class="nav-right">
            <a href="{base_path_prefix}about.html" class="nav-link">About</a>
            <button class="lang-toggle" id="langToggle" aria-label="Switch language">
                <span class="lang-label">中文</span>
            </button>
            <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                <svg class="sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="3"/><line x1="4.2" y1="4.2" x2="5.6" y2="5.6"/><line x1="18.4" y1="18.4" x2="19.8" y2="19.8"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.2" y1="19.8" x2="5.6" y2="18.4"/><line x1="18.4" y1="5.6" x2="19.8" y2="4.2"/></svg>
                <svg class="moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            </button>
        </div>'''


def escape_attr(text):
    """Escape text for use in HTML attribute value."""
    return text.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


if __name__ == "__main__":
    print("Translation maps loaded.")
    print(f"Post 1: {len(POST1)} entries")
    print(f"Post 2: {len(POST2)} entries")
