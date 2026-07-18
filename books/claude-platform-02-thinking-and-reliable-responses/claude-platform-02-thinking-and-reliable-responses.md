# Making Claude Think and Respond Reliably

_Reasoning, Multimodal Inputs, Structured Output, and Streaming_

by Dan Fakkeldy

Roughly 11,235 words.

---

## Chapter 1 — Capability Is a Request-Time Decision

Project Desk has been working for three weeks when someone asks it a deceptively simple question.

“Can we change the refund policy without making support slower?”

The policy lives in a forty-page PDF. A spreadsheet contains the last quarter’s support times. A screenshot shows the form agents use while speaking to customers. The product manager wants a short recommendation, a few exact citations, and a machine-readable risk rating that another service can store. She also wants to watch the answer take shape instead of staring at a spinner.

Volume 1 gave Project Desk a dependable way to exchange Messages with Claude. The application knows how to construct a request, choose conversation history, send ordered content blocks, and inspect the full response. It does not mistake fluent prose for the whole result. It reads the stop reason, model identity, and usage evidence before deciding what happens next.

That foundation is still intact. The new request does not require a different universe. It requires several deliberate additions to the same exchange.

Project Desk could ask Claude to spend more effort on the policy comparison. It could attach the PDF and the screenshot. It could request a structured result. It could enable citations. It could stream events to the screen. If the team later wants the same analysis for ten thousand cases, it could move the independent requests into a batch.

Each option sounds like “more capability.” That phrase is too vague for software.

Our first term is capability control: a request setting or content choice that changes how Claude performs a job or how the result comes back. The problem appears before the name. Project Desk needs to choose among deeper reasoning, visual input, structured shape, source grounding, live progress, and asynchronous throughput. Calling Claude “capable” does not make any of those choices for the application.

You can picture a control panel if it helps. One control changes how much work Claude tends to spend. Another adds an image. Another constrains the response shape. Another changes delivery from one complete response to an event stream. The comparison is useful because the controls are separate and visible to the operator.

The comparison stops there. An API is not a physical panel with permanent switches. Its available controls depend on the selected model, platform, account access, and current documentation. Some controls are stable. Others are beta or preview features. Some combinations are invalid. Project Desk has to construct a valid request every time.

This is the governing idea for the book: capability is a request-time decision, not a personality trait.

Suppose the team selects a powerful current model and sends the refund question with no PDF, no spreadsheet data, and no screenshot. The model may know general things about support policy. It does not know the company’s current refund language or last quarter’s support times unless Project Desk places that material inside the request or connects an approved retrieval path.

Model capability does not repair missing evidence.

Now suppose Project Desk includes every source but asks for ordinary prose. Claude may write a useful recommendation. The storage service still cannot assume the answer contains a field called risk level with one of three approved values. If downstream code needs a predictable shape, Project Desk must request that shape and then handle the cases where safety refusal or output truncation takes precedence.

Model capability does not create an unstated data contract.

Suppose the request asks for a structured report but the interface waits for one complete response. The schema can be excellent and the experience can still feel frozen during a long analysis. If the product needs progress, Project Desk has to choose streaming and implement an event-aware client. A typing animation painted over a non-streaming call would only decorate the wait.

Model capability does not choose the delivery experience.

The direct Messages API keeps one ownership rule from Volume 1: Project Desk constructs the request; Claude generates the next assistant contribution; Project Desk interprets the returned evidence. New features make the exchange richer. They do not move product accountability into the model.

That matters because several controls can point in different directions.

The product manager wants a careful policy comparison, which suggests spending more reasoning effort. She also wants a responsive screen, which suggests streaming. Finance wants a predictable cost ceiling. The storage service wants structured output. Legal wants citations. Support wants the result quickly.

There is no single “reliable mode” that satisfies all of them.

Project Desk needs a capability policy. That is the second and last new term for this chapter. A capability policy is the application’s rule for choosing controls from the job’s needs, then checking the evidence that comes back.

The word policy can sound grander than the mechanism. It may be a short decision function. If the input contains a PDF, add a document block. If the product needs exact fields, request structured output. If the response may run long or the interface needs progress, use streaming. If thousands of independent jobs can finish later, submit a batch. If a task is routine, do not automatically spend the highest effort available.

The useful part is not the number of branches. It is that each branch has a reason.

Project Desk starts this refund job by asking what the product needs to know, what material Claude needs to receive, and what evidence the application needs back.

The product needs a recommendation tied to current policy and observed support times. Claude therefore needs the PDF and the relevant spreadsheet rows. The screenshot may help explain the agent workflow, but its details are approximate visual evidence and will need checking. The application needs citations for source support and a structured risk record for storage. The user experience needs incremental progress. The team can tolerate several seconds of analysis but not an overnight queue, so a live Messages request fits better than batch processing.

Those decisions can be made before anyone argues about the “smartest” model setting.

Thinking controls come next. Current Claude models do not all expose thinking in the same way. Some use adaptive thinking, where Claude decides whether and how much to reason from the request. Some older configurations allow a manual thinking budget. An effort setting can influence how much work Claude tends to spend across thinking, text, and tool calls. The exact support matrix is changing quickly enough that an implementation should check the live documentation.

The durable choice is simpler. Does this task benefit from additional reasoning, and how will the team measure whether the added latency and cost improve the result?

For the refund policy, Project Desk may choose adaptive thinking at an effort level that has performed well on the team’s evaluations. For a one-sentence greeting classification, the same policy may choose a cheaper, faster path. “Always use maximum effort” is not a reliability strategy. It is a spending rule without evidence.

Task budget and maximum output belong nearby but do different jobs. A task budget can advise Claude about the amount of work available across a longer agentic loop. Maximum tokens remains a hard per-request ceiling on generated output. Neither setting proves that the work completed. Project Desk still reads the response and stop reason.

Fast mode is different again. On supported current models, it runs the same model with a faster inference configuration. It targets output speed, not greater intelligence, and current access and pricing are restricted. A speed control cannot substitute for reasoning depth, source grounding, or a complete response.

You can hear why the controls need separate names. Thinking mode selects a reasoning regime. Effort nudges how much work Claude spends. A task budget gives a longer loop an advisory allowance. Maximum tokens imposes a hard request ceiling. Fast mode changes output speed where supported. Streaming changes how delivery arrives.

Project Desk may combine several of them. The controls remain separate even when they share one request.

Now move to the material itself.

The policy PDF enters as a document content block. The screenshot enters as an image content block. They join text instructions inside the ordered message content that Volume 1 introduced. Claude can examine the page text, charts, and visual layout in a PDF, and it can interpret the screenshot. The application still owns file selection, request size, context pressure, and verification of the result.

Visual input deserves special caution. Claude may describe a small button incorrectly, miss text in a blurry crop, or return approximate coordinates for an interface element. Project Desk can use the interpretation to guide analysis. It should not treat a visual answer as a pixel-perfect measurement without checks.

Structured output solves another problem. Project Desk needs a risk rating, a recommendation, and a list of evidence items in predictable fields. A schema-constrained response can guarantee the ordinary shape and types. That removes a whole class of malformed JSON failures.

It does not guarantee that the recommendation is true.

It does not guarantee that every required source was considered.

It does not override a safety refusal or reconstruct an answer cut off at the maximum-token limit.

Grammar validity is one layer. Product validity is another.

Citations add source-location evidence. For document content, Claude can attach citations that identify the supporting passage or page range. Project Desk can display those references and let a reviewer return to the policy. A citation tells the application where the support came from. It does not make every inference drawn from that support correct.

Streaming adds time to the response contract. Instead of waiting for one finished object, Project Desk receives an ordered sequence of server-sent events. Content blocks open. Typed deltas arrive. Content blocks close. Message-level evidence arrives near the end. The stream stops.

Project Desk may display safe text as it arrives, but it should accumulate the complete Message before final validation. A paragraph appearing on screen is not proof that the stream ended cleanly. A refusal, overloaded error, network break, or maximum-token stop can change the correct product action.

The refund question now has a complete first-pass capability policy.

Use the direct Messages API because the person is waiting for this one analysis. Include the PDF, spreadsheet evidence, and screenshot. Ask for enough reasoning effort to compare tradeoffs. Request a structured report. Enable citations where compatible. Stream the response for progress. Accumulate the final Message. Then validate stop reason, schema, citations, visual claims, and product rules before storing or showing the recommendation as complete.

Nothing in that policy says, “Make Claude better.” Every line names a job.

Try the same reasoning in a different setting. A localization team has fifty thousand product descriptions and wants French, Spanish, and Japanese drafts by tomorrow morning. The source text is already available. No person is waiting for each response. The output shape is simple. Throughput and cost matter more than live progress.

Would streaming solve the main problem?

No. Streaming helps an application observe one response while it is happening. It does not turn fifty thousand independent jobs into a sensible overnight workflow.

Would a Message Batch fit?

Yes, if delayed completion, batch retention, and result reconciliation fit the product’s privacy and operational requirements. Each request still needs an explicit target language and an identifier that lets the application match results to source records. The team should evaluate quality in each real language instead of assuming equal performance everywhere.

The task changed, so the capability policy changed.

Return to the refund analysis. The difficult part is not remembering a catalogue of Claude features. The difficult part is asking a small set of product questions in the right order.

What job is the user waiting for? What evidence must cross the API boundary? What response shape does downstream software require? Does the interface need events or only a final Message? Can the work finish asynchronously? Which failure signals change the next action? Which current model and feature combination supports the chosen contract?

Project Desk owns the outer loop.

It answers those questions and constructs the request. After Claude responds, Project Desk checks the result.

Claude supplies capabilities inside the exchange. The application keeps the system accountable by choosing each capability for a stated reason.

The first control we will open is the one people most easily turn into mystique: extended thinking. What reaches the application when Claude thinks, what remains hidden, and why does more visible reasoning still fail to prove that the final answer is correct?

---

## Chapter 2 — Extended Thinking

Project Desk has to compare two support policies. One is easier for customers. The other is cheaper to operate. Both have exceptions, and the evidence is scattered across a policy document and a month of case notes.

This is the kind of request that tempts people to say, “Turn on the reasoning.” That is directionally useful and mechanically incomplete.

Extended thinking is a request mode that gives Claude room to work through a problem before producing the final answer. On models that support manual thinking budgets, the request includes a thinking configuration and a budget. The budget is measured in tokens. It creates room for reasoning; it does not promise that every token will be used, and it does not certify the answer.

The response can contain more than text. Thinking arrives in its own content blocks. The final answer arrives in text or other requested blocks. Project Desk must preserve their order just as it preserves other Message content.

That separation matters. A final answer is the product-facing result. A thinking block is evidence about the reasoning process made available by the platform. They are related, but they are not interchangeable.

Current documentation describes summarized thinking on current models rather than a promise to expose a complete private chain of thought. In some circumstances the platform can omit or protect parts of the reasoning. Signed or encrypted material may also be part of preserving thinking across tool-use turns. The durable lesson is simple: use the returned block according to its documented contract. Do not assume you have received every internal step Claude took.

Project Desk therefore gives thinking blocks a different job from citations. A citation points back to source material supplied to the request. A thinking summary describes reasoning. Neither one, by itself, proves that a claim is true. A convincing path can begin from a mistaken premise. A valid citation pointer can support a source that is outdated. Product validation still belongs outside the model.

Consider a policy comparison. Claude thinks through customer impact, staffing cost, fraud risk, and exception handling. The summary shows that it considered all four. That is useful. Project Desk can detect that the model ignored neither cost nor customer experience.

Then the final answer claims that weekend refunds take twice as long. The case notes do not establish that. A detailed thinking summary does not rescue the unsupported claim. Project Desk must check the answer against the supplied evidence or require citations that make the source path inspectable.

This gives us a clean boundary. Thinking is work allocation and reasoning evidence. Grounding is source evidence. Structured output is response shape. Business validation is the application’s decision about whether the result is fit for use.

Manual thinking budgets introduce another product decision. A larger budget can improve difficult work, but it can also increase latency and token use. The sensible budget depends on the task and the supported model. A two-sentence classification does not deserve the same reasoning allowance as a tangled policy migration. The application should choose from evaluation data, not from the belief that the largest number must be safest.

There is also a lifecycle rule. When a conversation continues through tool calls, Project Desk must preserve the thinking material required by the current API contract. It should not casually edit, splice, or manufacture those blocks. Volume 1’s lesson returns: the application owns history, so it must store the right history faithfully.

Imagine the team asks Claude to compare the policies, call a calculator, and then revise the recommendation. Project Desk receives thinking and tool-use blocks, executes the approved tool, adds the tool result, and sends the required prior blocks back in order. The reasoning capability lives inside the same Message exchange. It does not replace the exchange.

Now retrieve the mechanism with a fresh case. A maintenance planner asks Claude to choose which of three repairs should happen first. The request includes inspection notes but no photographs. Extended thinking can help compare urgency, cost, and dependencies. Can it reveal a crack that appears only in a missing image?

No. More reasoning cannot create absent visual evidence.

Can a visible thinking summary prove the chosen repair is correct?

No. It can make the path more inspectable, while the application still checks evidence, constraints, and the final result.

Extended thinking adds a reasoning layer to a Message. It does not dissolve the boundaries around that Message. Project Desk still chooses the inputs, the supported mode, the budget when one exists, the history it preserves, and the checks applied to the answer.

The team can test this layer without grading hidden thoughts. It builds cases with known evidence conflicts, missing inputs, and tempting but unsupported conclusions. It checks whether the final answer improves, whether the thinking summary reveals useful coverage, and whether latency and token use fit the product. The evaluation rewards correct outcomes and honest uncertainty. It does not reward a longer reasoning block simply for being long.

Project Desk also decides what to log. Thinking material can contain sensitive reasoning context and should follow the same retention and access controls as the rest of the request. A debugging benefit does not create unlimited permission to store it.

The next step is to remove an unnecessary burden from that choice. On supported current models, adaptive thinking lets Claude decide when reasoning is useful. A separate effort control tells it how much work the application prefers. Those sound similar. They govern different questions.

---

## Chapter 3 — Adaptive Thinking and Effort

A support queue contains two requests. One asks whether a receipt is required. The other asks how a new refund policy will affect staffing, customer trust, and fraud exposure.

Giving both requests the same fixed reasoning budget is possible. It is also clumsy. One is simple. The other deserves more work.

Adaptive thinking addresses the first question: should Claude think for this request, and how much thinking appears useful? On models that support it, the application selects adaptive thinking. Claude then adjusts reasoning to the apparent difficulty of each request.

Effort addresses a different question: how much overall work does the application want Claude to spend? It is a soft behavioral control that can influence thinking, tool use, and the final response. Current documentation offers named levels from lower effort through higher levels, with some upper levels available only on particular models.

The model matrix is volatile. The distinction is durable.

Adaptive thinking chooses reasoning dynamically inside the request. Effort expresses the application’s preference for how hard Claude should work across the task.

Think of a skilled mechanic. Adaptive thinking is the mechanic deciding whether a sound needs a quick inspection or a deeper diagnosis. Effort is the service manager saying whether this job calls for a light check or an exhaustive investigation. The analogy stops where software begins. Claude does not inspect a physical car, and named effort levels are not guaranteed quantities of labor.

Effort is not a hard token budget. A low setting does not promise zero thinking. A high setting does not promise a fixed number of reasoning tokens, tool calls, or output words. Claude can still spend more attention on a difficult request than a simple one at the same setting.

This is why evaluation matters. Project Desk should build a small set of representative tasks: easy policy lookup, ambiguous exception handling, multi-document comparison, and a case that requires a tool. The team measures answer quality, latency, token use, and failure modes at the supported settings. It then chooses a default and creates exceptions for jobs with different needs.

Suppose the quick receipt question works well with adaptive thinking and low effort. The policy redesign performs better at high effort. Project Desk can encode that difference in its capability policy. It does not need to tell users that one Claude is “smarter” than another. It can say that the application allocated more work to a harder job.

Adaptive thinking also helps mixed workloads. A single queue may contain routine and demanding requests. Claude can skip or reduce thinking for simple items while spending more on difficult ones. That can be a better fit than one manual budget copied across everything.

There are still reasons to prefer manual thinking where the selected model supports it. A team may need tighter latency planning or a specific experimental comparison. Manual budgets remain a model-dependent contract, and current documentation can deprecate them as newer models favor adaptive controls. Project Desk must verify support when it chooses the model, not rely on an old table embedded in application code.

Interleaved thinking adds one more layer. In a tool-using exchange, Claude may reason, request a tool, inspect the result, and reason again. That makes the agent loop more capable. It also increases the importance of ordered history, tool authorization, and stopping rules. More opportunities to think and act create more places where the surrounding system must remain accountable.

Now test the two controls. A legal-intake assistant has a short form with one missing field. The application wants Claude to identify the field and ask a concise follow-up. Which control answers whether Claude should spend reasoning on this particular easy request?

Adaptive thinking.

Which control tells Claude that the application generally wants a brief, economical pass?

Effort.

If the application chooses high effort, is it guaranteed to receive a particular number of thinking tokens?

No. Effort is a behavioral signal, not a meter.

If adaptive thinking decides little reasoning is needed, has the application lost control?

No. The application chose the adaptive contract, selected the model, set effort, supplied the evidence, and will validate the result. It delegated a narrow allocation decision, not product responsibility.

Project Desk can now choose how Claude reasons and how much work it prefers. Long agentic tasks create a larger problem. Reasoning, tool calls, tool results, and final output can all consume the task’s resources across many turns. For that, the platform offers an advisory task budget. “Advisory” is the word that prevents a costly misunderstanding.

In production, Project Desk records the chosen mode and effort beside the model identity and evaluation version. When the model or documentation changes, the team reruns representative tasks instead of assuming the old setting means the same thing. A setting name is part of a request contract, not a timeless quality score.

That record also helps explain a user-visible difference. If one job took longer because the product intentionally allocated more work, support can see the policy that made the choice. Observability turns an invisible tuning decision into something the team can test and revise.

---

## Chapter 4 — Task Budgets and Fast Mode

Project Desk is asked to review a hundred support articles, identify contradictions, propose edits, and produce a final migration report. Claude will need tools. One request may lead to many turns.

A per-request output limit cannot describe the whole job. It constrains one response. The agent loop includes thinking, tool requests, tool results, and later responses.

A task budget is an advisory token allowance for that larger loop on models and beta surfaces that support it. Claude sees a running countdown and can use the remaining amount to plan, prioritize, and finish.

The key word is advisory. A task budget is guidance to the model. It is not a billing cap, a security boundary, or a guaranteed stop. Project Desk still needs hard limits around the loop: maximum turns, allowed tools, timeouts, cost controls, and a clear rule for ending the job.

The ordinary maximum-output setting remains a hard per-request boundary. These controls operate at different layers. One helps Claude manage the whole task. The other limits how many tokens a particular Message response can generate.

Imagine giving a contractor an estimate of the hours available and also locking the building at six. The estimate helps the contractor plan. The lock is a hard boundary. The analogy is imperfect, but it catches the distinction: advice can shape behavior without enforcing the outer system.

Project Desk gives the article review a task budget large enough for discovery, comparison, and a final report. Claude sees that the budget is running down and may stop exploring minor wording differences so it can complete the migration plan. If the loop reaches the application’s hard turn limit first, Project Desk stops it anyway and records the incomplete state.

Task budgets are especially useful when the model must decide how to distribute work. They do not remove the need for checkpoints. Project Desk can require an inventory before edits, store intermediate results, and make the final report identify what was not reviewed. Graceful completion is a product design, not a magical property of a number.

Fast mode solves a different problem. It runs the same supported model weights with a faster inference configuration. The promise is higher output speed, not a different intelligence tier.

That distinction prevents two mistakes. First, fast mode does not mean the model has become shallow. Second, it does not guarantee that the first visible token arrives sooner in every network and workload condition. Current documentation frames the benefit around output speed. End-to-end latency still includes request setup, queueing, tools, network travel, and application work.

Fast mode can be attractive for interactive coding, live agents, and experiences where generated tokens themselves are the delay. It can carry different access, preview, or pricing conditions. Project Desk must check the current documentation and its response usage evidence instead of assuming the mode is always available or cheap.

The controls can coexist conceptually. Adaptive thinking decides when reasoning is useful. Effort expresses how much work Claude should tend to spend. A task budget advises a long loop about its total allowance. Fast mode changes how quickly supported inference runs. Hard application limits still enforce the outer boundary.

Try a case. A mail-order company wants fifty thousand independent product descriptions translated overnight. Should it turn on fast mode and stream every request to a dashboard?

That attacks the wrong layer. Faster tokens may help, but the workload is delayed, independent, and large. A Message Batch is the more coherent delivery pattern when its retention and timing fit.

Now consider a live troubleshooting assistant. It calls two diagnostic tools and explains each result to a waiting technician. Fast mode may improve the feel of the generated response. A task budget may help the whole loop finish before exhausting its allowance. The application still needs tool permissions and hard stops.

One more retrieval. If Project Desk sets a task budget of one hundred thousand tokens, can accounting assume the job will never exceed that number?

No. It is advisory.

If it sets a maximum output of two thousand tokens on the next Message, can Claude return a three-thousand-token response in that request?

The API’s hard response limit should stop generation first, with a stop signal Project Desk must handle.

Reasoning controls allocate work. They do not define the final shape of the result. The support system still needs a risk rating that downstream software can parse without guessing. That takes us from how Claude works to what Claude is allowed to return.

The article-review agent makes the boundary concrete. Its task budget encourages Claude to reserve enough room for a final report. Project Desk’s hard loop policy allows no more than a fixed number of tool rounds, forbids writes, and stops at a deadline. Its per-request output limit keeps any one response bounded. Monitoring records all three. If the agent ends early, the final report names the unchecked articles rather than pretending the review is complete.

Fast mode would change the generation-speed choice for a supported request, but it would not alter those tool permissions or completeness rules. Performance configuration and safety policy remain separate.

---

## Chapter 5 — Structured Outputs

Project Desk finishes a policy analysis with an elegant paragraph. The next service expects three fields: recommendation, risk level, and reasons. It cannot store elegance.

Structured outputs constrain Claude to produce data that follows a schema. A schema is a formal description of the permitted shape: which fields exist, which values are allowed, and how pieces nest.

The problem comes before the term. Without a declared shape, downstream code guesses. It searches prose for a risk label, hopes punctuation is consistent, and fails on the first unexpected answer.

The platform provides two related patterns. A structured final response constrains Claude’s answer to a JSON schema. Strict tool use constrains tool names and tool inputs to their declared schemas. One governs the result returned to the application. The other governs arguments Claude supplies when requesting a tool.

Under the hood, the platform compiles the supported schema into a grammar used during generation. The first use of a new schema can therefore carry extra latency. Reusing the same schema can benefit from caching. Project Desk should version important schemas deliberately rather than generating slightly different ones for every request.

Constrained decoding narrows what Claude can emit. It does not perform the company’s business validation.

Suppose risk level must be low, medium, or high. The schema can restrict the field to those values. It cannot decide whether Claude chose the correct one. Project Desk must still test the classification against evidence and policy.

The schema language also has limits. Not every possible JSON Schema feature is supported. A request with an unsupported or contradictory schema can fail before useful generation begins. The application should validate schemas during development and handle request errors in production.

Safety and length boundaries take precedence too. A refusal can prevent an ordinary schema-shaped answer. A maximum-token stop can leave an incomplete result. Project Desk must inspect the stop reason and response blocks before decoding and trusting the object.

This means “guaranteed JSON” has a precise boundary. For a successful, ordinary structured generation under the supported contract, constrained decoding provides schema-compliant output. It does not guarantee that every request ends in that ordinary success state.

Citations create an important combination rule. Citation blocks need to be interleaved with text. Strict JSON output requires a JSON-only shape. Current documentation treats those as incompatible in the same strict final response. Project Desk cannot simply enable every desirable feature at once.

One design is to choose citations for a human-readable report and store a separately validated application record. Another is to ask for structured claims and maintain source identifiers inside the schema without using the platform’s strict citation blocks. The correct design depends on what the user and downstream system need.

Project Desk chooses a simple report schema. Recommendation is text. Risk level is one of three values. Reasons is a short list. It also stores the model, stop reason, usage, request version, and source-set identity outside the generated object. The data contract and the operational evidence travel together.

Retrieve the distinction. A warehouse assistant calls a scheduling tool whose input requires a dock number and an arrival time. Which feature validates the arguments Claude sends to that tool?

Strict tool use.

The final Message must contain a machine-readable summary for the warehouse database. Which feature governs that final shape?

A structured output schema.

If the resulting object says dock twelve when dock twelve is closed, did the schema fail?

No. The shape is valid. The business claim is wrong.

Structured outputs turn a vague expectation into an explicit contract. They work best when the schema is small enough to understand, stable enough to version, and paired with handling for refusals, truncation, and validation. They make software integration more reliable without turning model output into trusted truth.

Project Desk tests the schema with three families of cases. Normal cases should decode directly. Boundary cases should exercise empty lists, optional fields, long text, and every allowed enum value. Failure cases should include a refusal and an intentionally small output limit. The test does not merely ask whether JSON parsing succeeded. It checks that the application followed the right branch for each response state.

When the schema changes, the application gives it a new version and migrates downstream readers deliberately. Prompt edits should not silently change a stored business record. The model is one producer inside a larger data lifecycle.

So far every input has been text or a named document. Project Desk also has a screenshot of the support form. Sending that image changes the evidence available to Claude, but vision has its own preprocessing, token cost, and coordinate boundaries.

---

## Chapter 6 — Claude Looks at an Image

The support manager says the form is confusing. Project Desk has the screenshot. Text alone cannot show where the buttons sit, which label is clipped, or whether the warning is visually easy to miss.

An image enters a Message as an image content block. Depending on the platform and current API surface, the source can be encoded data, a URL, or a previously uploaded file reference. The ordering of blocks still matters. A useful request can place a short text label before each image so Claude knows which view it is examining.

Vision turns pixels into model input. That conversion has a cost measured in visual tokens. Very large images can be resized before processing according to model limits. A tall screenshot that looks sharp on a monitor may not reach Claude at the same native dimensions.

This leads to a practical rule: resize deliberately when high resolution is unnecessary. Smaller images can reduce latency and token use. Preserve enough detail for the actual job. Reading tiny warning text and identifying a large red button are different tasks.

Claude can describe images, compare them, read visible text, and reason about layouts. It can also be wrong. Low contrast, tiny type, unusual diagrams, occlusion, and ambiguous objects all create risk. Project Desk should ask for uncertainty and use human or specialized validation where mistakes matter.

Coordinates add a subtle boundary. If Claude returns a point or bounding box, the coordinates refer to the image dimensions it actually processed. If the platform resized or padded the image, Project Desk must map the result back to the original before moving a pointer or cropping a region.

Coordinate answers are approximate. They are useful for guiding a review or initializing a tool. They are not a promise of pixel-perfect detection. An application that clicks a destructive control should not trust one approximate coordinate without guardrails.

Project Desk asks Claude to compare two screenshots of the refund form. The request labels them “current form” and “proposed form.” It asks which controls changed, where the policy warning appears, and what might confuse an agent on a phone.

Claude says the warning moved below the fold. That is a visual claim. Project Desk can display it with the screenshot and ask a designer to verify. If the application needs to highlight the warning, it can request a bounding box, translate that box through the known resize transform, and show it as an approximate overlay.

The image itself does not become a citation. Current citation support is text-based. Project Desk can identify the screenshot and record that a claim came from visual analysis, but it should not pretend the platform supplied a text citation to pixels.

Images also interact with privacy. Screenshots can contain names, account numbers, notifications, and location details outside the intended region. Cropping and redaction should happen before upload when possible. The capability policy includes what not to send.

Try a fresh example. A delivery app receives a photograph of a damaged parcel. Claude can describe a crushed corner and torn label. Can it determine the internal product is safe without evidence from inside the box?

No. Vision expands the input, not the laws of evidence.

Can Project Desk send ten unlabeled images and assume Claude will use the same numbering the application has in its database?

That is fragile. Label the images in the content sequence and preserve those identities in the result.

If Claude gives a bounding box around the torn label, should the application apply it directly to the original high-resolution photograph?

Only after accounting for the dimensions and transformation of the image Claude saw.

Vision is a content capability, not a separate conversation. The application still chooses the source, labels it, manages token cost, interprets the returned blocks, and validates consequential claims.

The team evaluates vision with the images users actually send. It includes sharp screenshots, small phone captures, rotated photographs, low contrast, and a case where the important detail is absent. Reviewers score both the answer and Claude’s handling of uncertainty. A model that guesses confidently on an unreadable label can be worse for the product than one that asks for a clearer image.

Project Desk stores the image identity and preprocessing facts beside the result. If a reviewer later sees a bounding box, the system can reconstruct which resized image Claude examined. Without that provenance, coordinates are numbers detached from their visual frame.

A screenshot is one image. A PDF can contain hundreds of pages, extracted text, charts, and page images. Claude’s document support combines those forms and can consume a large context quickly. The next policy is about choosing the right document path before the book disappears into its own evidence.

---

## Chapter 7 — Documents and PDFs

Project Desk receives the forty-page refund policy as a PDF. Some pages are ordinary text. Others contain tables and a flowchart. Copying only the text would lose part of the document.

PDF support gives Claude both extracted text and an image of each page. That combination allows it to reason about paragraphs, tables, charts, and visual layout. It also explains why PDFs can consume much more context than a plain text file.

The application can send a PDF through the supported document source forms, including encoded data, a URL, or a reusable file reference where available. Reusable uploads are valuable when the same document appears in many requests because the application does not need to transmit the bytes each time.

Current limits are operational facts, not eternal rules. At the verified documentation snapshot, the standard direct API path describes a thirty-two-megabyte request limit and a page limit that can reach six hundred pages on supported long-context models, while smaller context configurations use a lower page ceiling. Other cloud platforms can have different limits. Project Desk must check the platform it actually calls.

Encrypted or password-protected PDFs are not ordinary supported input. Scanned pages with poor image quality may yield weak text. A file that opens on a laptop is not automatically ready for model analysis.

Token cost grows with both extracted text and page images. A long, dense PDF can crowd out the instructions, conversation history, or other evidence. The application should select the relevant pages when it can. It can also split a document, create a retrieval index, or run a staged analysis rather than asking one Message to absorb everything.

Project Desk first identifies the policy sections about refunds, exceptions, and agent escalation. It sends those pages with the spreadsheet summary and asks for a comparison. The shorter evidence set is easier to inspect and cheaper to evaluate than the entire handbook.

Page identity matters. If the application wants citations, it should give the document a meaningful title and preserve page boundaries. A citation to page seventeen is useful only when the user can open the same document edition and find page seventeen.

PDF analysis also separates extraction from interpretation. The platform may successfully extract a sentence while Claude misunderstands its legal effect. Project Desk can verify that the words exist and still reject the conclusion.

Consider a chart. Claude reports that refund requests rose sharply in June. The page image supports visual reading, but Project Desk should prefer underlying numeric data for a consequential trend calculation. A chart is excellent orientation and sometimes the only evidence available. It is not automatically the best source for exact arithmetic.

The same rule applies to forms. Claude can locate a field and describe its label. If the application needs the exact value of every box, a dedicated extraction workflow plus validation may be safer than open-ended visual interpretation.

Now retrieve the mechanism. A three-hundred-page equipment manual contains one ten-page section relevant to a repair. Should Project Desk send the entire file because it fits today’s limit?

Fit is not the only criterion. The relevant section reduces context competition, cost, and review burden.

A scanned invoice has a faint total. Claude returns a number confidently. Has PDF support proved the number?

No. The application should compare the extracted value with the page image and use an appropriate validation path.

A team sends the same policy in fifty requests. What can reduce repeated transfer?

A reusable file reference on a supported platform, while the application still controls retention and access.

PDF support combines text and page images into one document contract. It expands what Claude can inspect without changing who owns selection, privacy, and verification.

Before analysis, Project Desk runs a document intake check. It verifies file type, size, page count, encryption status, and the edition identifier. It extracts a preview so a human can notice blank scans or upside-down pages. Only then does it choose the full document, a page range, or a retrieval path.

After analysis, the application preserves the source edition with the result. A recommendation tied to the July policy should not later open the September replacement and pretend the citation still refers to the same page. Document identity is part of reproducible evidence.

Project Desk now has source material and a response shape. The manager also asked for exact citations. Citations do more than paste a page number into prose: they return structured pointers to the supplied source. Search-result content extends the same grounding pattern to retrieved passages.

---

## Chapter 8 — Citations and Search-Result Content

The policy recommendation says an exception requires manager approval. The support lead asks a fair question: “Where does the document say that?”

Citations let Claude attach structured source pointers to claims. When enabled for a supported document, the response can interleave text with citation blocks. Project Desk can render the claim and make the source location inspectable.

The locator depends on the document type. Plain text can use character ranges. Documents with page structure can use page ranges. Custom content can use content-block positions. The important mechanism is that the pointer refers to material Project Desk supplied under a known source identity.

The platform extracts the cited text from that source. This makes the pointer valid as a location. It does not make the source true, current, or interpreted correctly.

A citation can support a sentence in an obsolete policy. Claude can cite the right paragraph and draw the wrong conclusion from it. Project Desk should distinguish locator validity from claim validity.

Source preparation affects citation quality. Clear titles, sensible chunk boundaries, and focused evidence make it easier to produce useful pointers. Giant undifferentiated text blobs make both generation and review harder. Image-only material is not currently a text citation source.

There is also a scanning boundary. A citation system can point into the text made available to it. If the application omitted a controlling appendix, no citation can reveal that missing rule. Source completeness remains an input decision.

Search-result content blocks bring retrieved material into the Message with an explicit structure. Each result can have a source identifier, title, content, and optional metadata. Claude can use those blocks for grounded answers, and citations can point back to the individual result.

The application controls retrieval. It chooses the search system, query, permissions, ranking, deduplication, and passages sent to Claude. Claude is not silently searching the company’s private index merely because the prompt asks for facts.

Granularity matters. One result containing an entire manual gives citations a broad target. Several coherent passages give the model and reviewer more precise source units. Too many tiny fragments can destroy context. Project Desk should tune chunking with real questions.

For the refund case, Project Desk retrieves the current policy section and the escalation procedure. It labels both with stable identifiers. Claude answers that manager approval is required and cites the escalation procedure. The interface opens that exact passage when the listener later reviews the written companion.

Then the team discovers the procedure was superseded yesterday. The citation system worked. The retrieval and freshness policy failed.

This is why grounded generation is a chain. Retrieval selects evidence. The Message carries it. Claude produces a claim. A citation points to the evidence. The application decides whether the evidence is authorized, current, and sufficient.

Try another case. A medical benefits assistant retrieves three plan documents from different years. Claude cites a deductible from the oldest one. Is the answer grounded?

It is grounded in a supplied source. It may still be operationally wrong because the application failed to resolve document version.

Can strict JSON output and native citation blocks be combined in one final response today?

Current documentation says no. Citation blocks interleave with text, while strict structured output requires the constrained JSON shape. The capability policy must choose a design.

Does a citation to a PDF page prove that Claude read a chart value correctly?

It proves a pointer to supplied material. Exact chart interpretation still needs validation.

Project Desk can now return an inspectable answer. The manager also wants to watch progress. Streaming does not send a half-finished Message object over and over. It sends an ordered event sequence that the application must assemble.

Grounding quality can be evaluated as a sequence of questions. Did retrieval include the controlling source? Did Claude attach a citation to the claim that needed one? Does the cited passage actually support the claim? Is the source current and authorized? Those questions locate different failures instead of calling the whole answer “hallucinated.”

Project Desk keeps retrieval logs that are useful without exposing unnecessary private content: query identity, filters, source versions, result identifiers, and the passages actually sent under the approved retention policy. That makes a bad citation diagnosable and a good answer reproducible.

---

## Chapter 9 — Streaming Is an Event Sequence

Without streaming, Project Desk sends a request and waits for the complete Message. With streaming enabled, it receives server-sent events over the open connection.

An event stream is a state machine, not a bag of text fragments.

The sequence begins with a message-start event. Content blocks then open by index. Typed deltas add material to the open block. The block closes. Near the end, a message-level delta can add the stop reason and usage information. A message-stop event ends the ordinary sequence. Ping events can keep the connection alive.

Text arrives as text deltas. Tool input can arrive as partial JSON. Thinking and signatures have their own delta types on supported requests. Each delta belongs to a content block. Project Desk must route it by event type and block index.

Partial JSON deserves special care. A fragment such as an opening brace or half a string is not a valid tool input yet. The application accumulates the fragments and parses only after the block is complete, or uses an official SDK helper that performs the accumulation.

The official SDKs provide convenient ways to iterate through events and recover the final Message. That final accumulation is valuable because it restores the ordinary response object with its content, stop reason, and usage evidence. A responsive interface and a complete operational record can coexist.

Project Desk may display safe text as it arrives. It should not mark the answer complete merely because a paragraph looks finished. The stream can still end with a refusal signal, a maximum-token stop, an overload error, or a broken connection.

Think of receiving a freight train one car at a time. The first cars can be unloaded while the train continues. The manifest is not final until the end-of-train signal and accounting arrive. The analogy stops at ordering: network events can fail, retry, or introduce new types that a physical train does not.

The application’s state machine might have four broad states: started, block open, awaiting completion, and finished or failed. It rejects impossible transitions, preserves unknown events for inspection, and does not assume every future event type is already known.

Suppose the refund report streams three paragraphs and then ends because the output limit was reached. The user saw useful text. Project Desk should label it incomplete, not store it as the approved report. The stop reason changes the product action.

Suppose the network breaks after a tool-use block opens but before its JSON closes. Project Desk must not execute the fragment. It can retry according to an idempotent request policy or ask the user to resume.

Usage evidence also changes during streaming. The start event can contain initial Message information. Later message deltas update usage and stopping information. Project Desk should rely on the accumulated final Message or the documented final events rather than a number observed halfway through.

Retrieve the mechanism. The interface has displayed the sentence, “Approve the policy change.” Has the Message completed?

Not necessarily. Only the event sequence and final stop evidence answer that.

A tool-input delta ends with a closing brace. Can the application execute it immediately?

Only when the content block has completed and the assembled input passes schema and authorization checks.

A new event type appears after a platform update. Should Project Desk crash because its switch statement has no case?

It should preserve forward compatibility, ignore or log unknown events where safe, and continue following the documented sequence.

Streaming changes delivery time. It does not weaken validation. The complete Message remains the evidence boundary for final product decisions.

A robust interface separates draft state from committed state. Draft text can update quickly and disappear if the stream fails. The committed result appears only after final accumulation and validation. The user can see progress without the database confusing “visible” with “finished.”

Project Desk tests the state machine with recorded event sequences. It removes the message-stop event, splits tool JSON at awkward positions, injects a ping, introduces an unknown event, and ends with a maximum-token stop. These deterministic tests are cheaper and more reliable than hoping rare network conditions occur during a manual demo.

Two failures deserve closer treatment: a safety refusal that appears during the stream, and an error that arrives after the HTTP connection originally succeeded. Both can surprise an application that watches only status codes and text deltas.

---

## Chapter 10 — Streaming Thinking, Refusals, and Errors

Project Desk opens a stream successfully. The server returned an ordinary success status. Halfway through generation, an error event reports that the service is overloaded.

The initial HTTP status did not guarantee that the whole stream would succeed. Once streaming begins, later failures travel inside the event sequence. The application must handle both connection-level errors and typed stream errors.

This is one reason the partial display cannot be the system of record. Project Desk accumulates content for the interface, but it records completion only after the final event and stop evidence pass validation.

Thinking streams through typed deltas too. A thinking block opens. Thinking deltas arrive. A signature delta can follow. The block closes. Project Desk preserves the sequence according to the model’s current contract rather than flattening every delta into visible prose.

The user may not need to see raw thinking. A product can show a neutral progress state or an approved summary. More disclosure is not automatically better, and returned thinking evidence is not a correctness proof.

Refusals create a different state change. Current guidance for streaming refusals describes a refusal stop reason arriving in a message-level delta. The application should stop treating earlier partial text as a normal answer, discard or clearly separate it, and reset the next conversational turn to a clean user context rather than feeding an incoherent partial assistant response back as accepted history.

That reset preserves conversation integrity. If Project Desk stores a half-answer as though Claude completed it, the next request begins from a false record. Volume 1’s history rule returns under pressure: store what actually happened.

Project Desk also distinguishes retryable service errors from content decisions. An overload may justify retry with backoff. A refusal is not a transient transport failure to hammer with automatic retries. A malformed request needs correction. A network interruption may require idempotency and careful reconciliation.

Suppose the policy report streams a confident recommendation and then the final message delta carries a refusal stop reason. Project Desk removes the draft from the “complete” view, records the refusal, and offers an appropriate next action. It does not keep the recommendation because it looked useful.

Suppose a stream error arrives after a tool has already changed external state. Blindly retrying the whole request could repeat the action. The application needs idempotent tools, operation identifiers, and a record of completed side effects. Streaming makes progress visible; it does not make retries harmless.

Unknown events are part of the compatibility contract. The platform can add event types. Project Desk should avoid treating every unfamiliar event as corrupt data. It can log it, safely ignore what it does not need, and continue when the protocol permits.

Now retrieve the boundaries. A stream began with a successful HTTP status. Can monitoring mark the request successful immediately?

No. Later event errors are possible.

Claude emitted two paragraphs before a refusal. Should they enter conversation history as a completed assistant turn?

No. Follow the refusal guidance and reestablish a clean context.

An overloaded stream failed after a read-only search tool. May Project Desk retry?

Possibly, with backoff and request reconciliation. The application should know which actions already happened.

The event state machine lets a live product remain honest. It can show progress, preserve typed reasoning and tool data, and still distinguish completed, refused, truncated, and failed work.

The team writes a retry table before shipping. Overload and some transport failures allow bounded retry with backoff. Authentication and malformed-request errors require repair. Refusals follow the product’s safety path. Any request that may have triggered a side effect must reconcile that action before retrying. The table turns a vague “try again” button into an explicit policy.

User-facing language follows the same evidence. “Still working,” “could not complete,” “needs different input,” and “completed” are distinct states. A responsive product earns trust when its labels match the protocol rather than the amount of text already on screen.

Live interaction is now covered. Some jobs do not need it. When thousands of independent requests can finish later, holding thousands of open streams is the wrong architecture. Message Batches change the timing, economics, and reconciliation contract.

---

## Chapter 11 — Batch Processing

The localization team has fifty thousand product descriptions. Nobody is waiting for each one. The drafts are needed tomorrow.

The Message Batches API accepts many independent Messages requests for asynchronous processing. The application creates a batch, polls its status, and later downloads results.

At the verified snapshot, batch processing offers a fifty-percent price reduction relative to standard Messages processing. Most batches finish in less than an hour, while the service allows a longer processing window. Those are current operating facts, not promises for every future model or workload.

Each request receives a custom identifier chosen by the application. That identifier is the reconciliation key. Results are not something Project Desk should match by list position or completion order.

The batch itself has current size limits for request count and total payload. The verified documentation describes up to one hundred thousand requests or two hundred fifty-six megabytes per batch. Project Desk checks those limits before upload and splits larger jobs deterministically.

The results arrive as line-delimited JSON. Each line corresponds to a request identifier and a result state. Some requests can succeed while others fail, expire, or be canceled. Batch completion does not mean every line contains a normal Message.

Project Desk therefore reconciles each source record separately. It validates the custom identifier, result type, stop reason, response shape, and usage. Failed items can enter a narrow retry batch. Successful items do not need to run again.

Retention matters. Current documentation makes results available for a limited period—twenty-nine days at this snapshot. Project Desk should download them promptly into an approved store and delete or retain them according to its own privacy policy. A hosted result window is not an archive plan.

The localization request still needs an explicit target language, a supported model, instructions, and a response contract. Batch changes when the work runs and how results return. It does not improve a vague prompt.

The team creates stable identifiers from the product-record IDs. It sends French, Spanish, and Japanese requests with the target language stated. The expected output has the translated description and a short review flag. When the batch completes, Project Desk joins each result back to the product and routes flagged drafts to human review.

One Spanish request fails. The other forty-nine thousand nine hundred ninety-nine are not discarded. The failed identifier enters a retry queue after the application inspects the error.

Batch processing is a poor fit when a user is waiting for immediate conversational progress, when later completion breaks the workflow, or when the retention and platform terms do not fit the data. Streaming and batching solve opposite timing problems.

Retrieve the choice. A user asks one policy question and watches the answer. Batch or streaming?

Streaming is the coherent delivery choice if progressive display matters.

An overnight evaluation runs ten thousand independent prompts. Batch or ten thousand live streams?

Batch is designed for that workload when its limits and retention fit.

Can Project Desk assume result line one belongs to request line one?

No. Reconcile by the custom identifier.

Does a completed batch prove every request succeeded?

No. Inspect every result state.

Batch processing completes the delivery side of the capability policy. The remaining boundary is easy to blur: Claude can generate and understand many languages, but Anthropic does not provide a native embeddings model. Generation and retrieval representation are different jobs.

Project Desk makes batch creation resumable. It writes a manifest of source record, custom identifier, request hash, and batch identifier before waiting for results. If the process restarts, it polls the existing batch rather than creating a duplicate. Downloaded result files receive their own checksum and reconciliation report.

Cost savings do not remove evaluation. The team samples completed drafts, measures each target language, and watches whether failed or expired requests cluster around a particular input shape. Batch is a transport and scheduling choice. Quality still belongs to the individual Messages inside it.

---

## Chapter 12 — Languages, Embeddings, and Capability Boundaries

Claude can work in many languages. The application should still state the target language explicitly.

Relying on inference makes a production contract weaker. A mixed-language conversation, a brand name, or quoted source text can pull the answer toward the wrong language. A stable system instruction can say which language to read and which language to produce across every turn.

Quality is not uniform across all languages, tasks, and cultural contexts. Project Desk evaluates the real language, not an English proxy. It checks fluency, terminology, tone, formatting, and the errors that matter to the product.

For the localization batch, French output is reviewed in French. Japanese politeness and product terminology are reviewed in Japanese. A high aggregate score across languages cannot hide a serious failure in one market.

Multilingual input also affects retrieval. A user can ask a Spanish question about an English policy. Project Desk must decide whether to search in Spanish, English, or both, and which language the answer should use. Claude can bridge language in generation; the retrieval system still needs a deliberate query and indexing strategy.

That leads to embeddings. An embedding is a numeric representation used to compare semantic similarity. Applications commonly use embeddings to retrieve passages that are meaningfully related to a query even when they do not share the same exact words.

Anthropic’s current documentation states that Anthropic does not offer its own embedding model. It points to external providers, including Voyage AI as one option. That is a capability boundary, not a missing parameter in the Messages request.

Project Desk can use an approved embeddings provider to index support documents. At question time it embeds the query, retrieves nearby passages, applies access and freshness rules, and sends selected text to Claude as document or search-result content. Claude then answers from that evidence and can cite it where supported.

The embedding does not become evidence for the final claim. It helps choose candidate evidence. The retrieved passage is what crosses the Message boundary.

Similarity is not authorization. A semantically close private document must still be excluded when the user lacks access. Similarity is not freshness either. An old policy can be the closest match. Project Desk filters by permissions, version, jurisdiction, and date before asking Claude to answer.

Multilingual embeddings add another evaluation problem. Some embedding models align languages well; others perform unevenly. The team tests real cross-language queries and documents. It does not infer retrieval quality from Claude’s ability to write fluent translations.

Try a fresh case. A Spanish-speaking employee asks about parental leave. The policy source is English. What should Project Desk make explicit?

The input and output language contract, the retrieval language strategy, and the current authorized policy version.

Can Claude’s multilingual generation replace an embeddings provider for semantic search over a million documents?

Those are different jobs. Claude can help formulate queries or judge retrieved passages, while the vector index requires an embedding system or another retrieval method.

If the nearest vector result is a confidential executive memo, may Project Desk send it because the similarity score is high?

No. Authorization is an application boundary.

This chapter closes a tempting category error. A powerful model does not mean one API owns reasoning, images, documents, schemas, retrieval, language policy, and storage. Project Desk composes several contracts and keeps each boundary visible.

The retrieval evaluation uses known questions with known controlling passages. It measures whether the correct passage appears near the top, whether permission filters hold, and whether cross-language queries behave acceptably. Only after retrieval passes does the team evaluate Claude’s grounded answer. Mixing both stages into one score would hide whether the vector search or the generation failed.

Provider choice also creates a privacy decision. Project Desk checks where embedding requests go, what data is retained, and whether the approved region and contract fit. An external capability remains part of the application’s threat model even when the final answer comes from Claude.

We can now return to the original refund decision and build the complete capability policy without turning it into a catalogue. Every control will answer one product question.

---

## Chapter 13 — Project Desk Becomes Responsive

Return to the support manager’s request.

The job is to decide whether a refund-policy change will help customers without slowing support. The evidence is a policy PDF, support-time data, and two screenshots. The manager wants an inspectable recommendation, a risk record, and visible progress.

Project Desk begins with evidence, not controls. It selects the current policy sections, the relevant support metrics, and the labeled screenshots. It records each source identity and removes unrelated private information.

Then it chooses reasoning. The comparison is difficult enough for adaptive thinking on a supported current model, with an effort setting justified by evaluation. If the selected model instead uses a supported manual thinking budget for this workload, the application uses that documented contract. It does not hard-code a stale model table into the policy.

The request asks Claude to compare customer impact, staffing time, fraud exposure, and exception handling. Thinking evidence can help Project Desk confirm that the analysis considered each dimension. It does not replace source validation.

The screenshots enter as labeled image blocks. Project Desk knows their original dimensions and any resize transform. Visual claims remain approximate and reviewable. The PDF contributes extracted text and page images, but the application sends only the relevant pages to control context and cost.

The manager needs citations. Project Desk enables citations for the human-readable recommendation and gives every source a stable title. Because strict JSON and native citation blocks do not share one final shape, the application does not demand both in the same response.

Instead, it treats the cited report as one product artifact. It derives a small risk record through a separate structured step, or uses an application-owned form that a reviewer confirms. The risk schema allows only the approved levels. Project Desk still validates whether the chosen level follows from the evidence.

The interface streams the report. Text deltas can appear as a draft. Project Desk assembles the complete Message in parallel. Tool-input fragments wait for their content block to close. A refusal, stream error, or maximum-token stop removes the draft from the completed state.

At the end, Project Desk checks the event sequence, stop reason, source citations, schema where used, visual claims, model identity, usage, and product rules. Only then does the interface label the recommendation complete.

This is the capability policy promised in Chapter 1. It is not a list of switches. It is a chain of decisions.

What job is being done? Which evidence must enter? How much work should Claude tend to spend? What response shape does software require? Does a person need live progress? Which sources make claims inspectable? Which failures change the next action? What must the application verify?

The policy also knows when to choose a different path. If the company later analyzes fifty thousand independent policies overnight, Project Desk uses batches with custom identifiers, per-result validation, and prompt download before the hosted retention window closes. It does not open fifty thousand streams.

If a Spanish-speaking manager asks the same question, Project Desk states the target answer language and evaluates that language. If retrieval uses embeddings, the application owns the external provider, permissions, freshness filters, and passage selection. Claude receives authorized evidence, not an unexplained similarity score.

Now retrieve the entire mechanism through a new case.

A city-maintenance team receives a complaint about a damaged playground. It has an inspection PDF, two photographs, a repair-cost table, and an urgent resident waiting for an update.

Should Project Desk begin by turning every capability on?

No. It begins by naming the job and evidence.

The safety comparison is difficult. Which controls can allocate reasoning work?

Adaptive thinking and effort on a supported model, or the documented manual thinking mode where that is the chosen contract.

The photographs show the damaged area. What boundary remains?

Visual interpretation can be approximate and cannot reveal evidence outside the images.

The application needs a repair category that another service can store. What helps?

A supported structured-output schema, followed by business validation.

The resident wants progress. What changes?

Project Desk streams typed events, displays a draft honestly, and accumulates the final Message.

The final report quotes the inspection rule. What makes that inspectable?

A citation to an authorized, current source. The application still checks the rule’s meaning and version.

That is the larger lesson of Volume 2. Claude’s capabilities become reliable product features only when the application gives each one a precise job and honors its contract.

Reasoning is not evidence. A schema is not truth. A citation is not freshness. A stream is not a completed Message. A batch is not an ordered list of successes. Multilingual fluency is not retrieval authorization.

Project Desk is responsive now because it can show progress, inspect richer evidence, and return predictable results. It is reliable because it never confuses those conveniences with proof.

Volume 1 built the Message boundary. Volume 2 has added the capability layers around it. The application still stands at the center: choosing, preserving, checking, and deciding what happens next.

---
