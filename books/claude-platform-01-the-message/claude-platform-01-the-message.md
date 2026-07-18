# The Message

_Conversations, Content Blocks, and the Messages API_

by Dan Fakkeldy

Roughly 16,006 words.

---

## Chapter 1 — The Crossing

A request arrives at Project Desk on an ordinary Tuesday morning. A customer has written three paragraphs about a damaged shipment. The useful facts are scattered through frustration, dates, and a long description of the box. You want Claude to draft a calm reply that acknowledges the problem and asks for the missing information.

Nothing has crossed into Claude yet.

The customer's words are sitting inside your application. Project Desk may show them on a screen. It may have stored them in a database. It may have trimmed an email signature or attached the customer's account number. All of that work is happening on your side of a line.

Then your Python program makes a call.

That line between Project Desk and the Claude service is our first useful term: the API boundary. An API is an agreed way for one piece of software to ask another piece of software to do something. The boundary is where responsibility changes hands. Project Desk decides what to send. Claude generates a response from what it receives. Project Desk then decides what to do with the result.

The official route has a mechanical name: post, slash v one, slash messages. In Python, the corresponding SDK method is called messages dot create. You do not need to memorize either spelling during this drive. Their job matters more: they send a structured request to the direct Messages API and ask Claude to generate the next assistant contribution.

That last phrase needs care. Project Desk is not mailing a loose sentence across the boundary and waiting for another loose sentence to float back. It sends a message.

A message is a structured unit in a conversation. For now, picture it as one contribution with two basic facts attached. First, who contributed it. Second, what that contribution contains. The customer's request becomes a user message because it carries the user's side of the exchange. Claude's reply comes back as an assistant message because it carries the assistant's next contribution.

Project Desk still owns the surrounding job. It chose the customer's text. It chose the instruction to draft a calm reply. It chose which Claude model to call and how much output to permit. Those choices travel in one request, but they are not all the same thing. The message carries the conversational contribution. Other request settings tell the service how this call should run.

You can hear the division of labour in one sentence: Project Desk constructs the request; Claude generates the next message.

The distinction may sound fussy until something goes wrong. Suppose Project Desk accidentally sends only the words, “Please help with this.” The customer's three paragraphs remain in your database, but Claude never receives them. Claude cannot reach backward across the API boundary and inspect whatever Project Desk forgot to include. It can only work from the request that actually crossed.

The failure belongs to the application. Claude may produce a perfectly fluent answer to the thin request it received. Fluency does not restore the missing shipment details.

Now let the complete request cross. It names the model. It sets a maximum possible output. It includes a user message containing the customer's account of the damaged shipment. Claude processes that request and sends back an assistant message.

If Project Desk were a toy script, it could print the answer text and stop. A dependable application needs to inspect more than the paragraph the customer might eventually read. What came back is our third term: a structured response.

A structured response is the full result object returned by the API. It contains Claude's generated content, but it also carries operational evidence about the event. It identifies the assistant role. It identifies the model that answered. It reports why generation stopped. It records usage information. Later chapters will give each of those fields its own job. For the moment, the useful distinction is smaller: the response contains the answer, but it is not merely the answer.

Imagine that Claude returns a thoughtful draft ending with, “Please send a photograph of the shipping label.” The text looks complete. Project Desk checks the rest of the response and learns that generation stopped because it reached the maximum output allowed by the request. The final sentence may happen to end with a period, but the stop evidence says the generation was cut off by a limit. A program that reads only the prose could mistake a tidy-looking fragment for a finished reply.

Now imagine the same draft with a stop reason indicating that Claude ended the turn naturally. The visible paragraph might be identical. The application decision can still differ because the structured response tells Project Desk how the generation ended.

This is why response handling is application work. Claude generates. Project Desk interprets.

There is another boundary worth placing now. Anthropic also offers Claude Managed Agents. Managed Agents supplies a pre-built harness for longer-running, asynchronous work. The Messages API is the more direct route: your application controls the loop and the details around each model call. Project Desk is using that direct route because we want to understand the pieces it owns. Later in the series, when managed infrastructure becomes the subject, this contrast will return with more consequences.

For this request, Project Desk now has two useful objects on its side of the boundary. It has the user message it sent, and it has the assistant response it received. If the draft passes the application's checks, Project Desk can show it to a person, store it with the case, or ask Claude for another turn. Claude does not make those product decisions merely because it wrote the paragraph.

The shape repeats outside customer support.

Suppose Project Desk is replaced by a document-extraction service. A person uploads an invoice and asks for the supplier name, invoice date, and total. The application prepares the material and sends a user message through the same API boundary. Claude returns an assistant response containing the extraction result and the operational evidence around it.

Which side owns the uploaded file before the call? The application side.

Which object carries the person's contribution across the boundary? The user message.

Which object returns with both generated content and evidence about the generation? The structured response.

The business purpose changed from drafting a reply to extracting fields. The crossing did not. One application prepares a request. One message carries the user's contribution. One structured response returns. The application decides what the result means for the product.

That repeated shape is the route we will follow through this book. We will open it piece by piece without losing sight of the whole exchange. The next useful question comes from the message itself. If software once sent Claude one specially formatted prompt string, why does the modern API bother separating conversations into structured messages at all?

Before we answer that, let us replay the crossing slowly enough to notice what Project Desk can control.

On the application side, the damaged-shipment request is still ordinary data. Project Desk can remove a repeated email footer. It can reject an empty case. It can add the order number that the customer supplied through a separate form. It can also decide that a photograph is sensitive and should not be included in this request. None of those choices are Claude's choices. They happen before the API boundary.

Project Desk then assembles the message. The message needs to carry enough of the customer's contribution for Claude to do the requested work. If Project Desk includes the complaint but leaves out the order number, Claude does not possess an invisible copy of the order record. If Project Desk includes yesterday's complaint by mistake, Claude may answer the wrong case with complete confidence. The boundary is unforgiving in a useful way: it gives us a precise place to ask what was actually sent.

After the call, Project Desk receives the structured response. This is another moment for deliberate application work. The program can preserve the response beside the case. It can check that the generation ended in an expected way. It can choose the generated text intended for the customer while retaining the other evidence for monitoring. It can send the draft to a staff member instead of sending it directly. Once again, Claude supplies a contribution; the application owns the consequence.

Think of a restaurant pass. A server writes an order, the kitchen prepares a plate, and the server checks the plate before it reaches the table. The pass is not a perfect copy of the API boundary, because software does not have a physical kitchen. The comparison is useful for one narrow point: responsibility changes at a known handoff, and the receiving side still has work to do. A finished-looking plate is not proof that it belongs to table twelve. A polished paragraph is not proof that it belongs in this customer's case.

Now change the application again. A teacher has fifty short reflections from students and wants help grouping them by recurring concern. The application sends one student's reflection as a user message and asks for a compact classification. Claude returns a structured response. The application checks the result, stores the selected category, and moves to the next reflection.

Consider the fresh question. The returned text says, “The student is mainly concerned about time management.” Where should the student identifier live while the call is being prepared: only in Claude's generated prose, or in the application that already knows which record it is processing?

It belongs in the application. Project Desk's cousin in this example already owns the student record. Asking Claude to reproduce the identifier does not transfer ownership of that fact. The message should contain the material Claude needs. The application should keep the reliable link between the response and the record that produced the request.

That separation prevents a subtle mistake. If the generated prose misspells a name or invents an identifier, the application can still attach the response to the correct source record because it never surrendered that relationship. The structured response is evidence from one generation event. It is not a replacement for the application's own records.

So, across three jobs—customer support, invoice extraction, and reflection grouping—the same mental route holds.

Before the crossing, ask: what does the application know, and what must the message carry?

At the crossing, ask: what request did the application actually send?

After the crossing, ask: what does the structured response say happened, and what should the application do next?

If those questions feel almost too simple, that is a strength. They remain useful when the request becomes more elaborate. Later, the message may contain several kinds of material. The response may contain several pieces of generated content. Project Desk may make another call based on the first one. The crossing gains detail, but responsibility does not become mysterious.

Try the route once without the story. Your Python program prepares a message. The message crosses the API boundary in a request. Claude generates the assistant contribution. A structured response crosses back. Your program inspects that response and decides the next action.

The central idea is not that Claude sits inside Project Desk. It is that Project Desk and Claude exchange structured objects across a defined boundary. Project Desk owns the conversation around each call because Project Desk decides what history to send, what result to trust, and whether another call should happen.

Keep that route in mind as we move forward. It will let us explain why modern messages are separated, how a conversation continues, and why a dependable Claude application is built from more than a clever prompt.

---

## Chapter 2 — When the Conversation Was One String

Project Desk has crossed the boundary once. It sent a structured user message and received a structured assistant response. That arrangement may already feel natural. A person contributes something. An assistant contributes something. The application can tell which is which.

But software did not have to be designed that way.

Imagine building an earlier version of Project Desk around a simpler bargain. Instead of sending an explicit series of conversational contributions, the application sends one long piece of text and asks the model to continue it.

The customer speaks first, so Project Desk writes the customer's words into that text. The assistant is supposed to speak next, so Project Desk adds a marker that means the assistant's contribution should begin here. If the customer and assistant have already exchanged several turns, Project Desk places those earlier turns into the same string in the right order. It also places any instructions where its chosen formatting convention expects them.

The model sees text to continue. Project Desk sees a conversation only because Project Desk built the text to resemble one.

That older contract is called Text Completions. The name is useful because it describes the mechanism directly. The application supplies text; the model produces a completion of that text.

Text Completions is now a legacy API. Anthropic directs future models and features toward the Messages API. We are not learning the legacy route so you can start a new project with it. We are looking backward because the older shape exposes a problem that modern structure solves.

Suppose Project Desk has this exchange in its case file.

The customer says the replacement parcel arrived, but one item is still missing.

The assistant previously asked for the name of the missing item.

The customer answers, “The blue travel mug.”

With the legacy approach, Project Desk turns those three contributions into one formatted prompt string. The application must preserve the speaker changes through formatting. It must make the boundary between the earlier assistant text and the new customer text unambiguous. It must end the prompt at exactly the place where a new assistant completion belongs.

The conversation is real to the people involved. Inside the request, however, its structure is encoded by a convention inside text.

Conventions can work. Software has always used agreed formatting to make one thing stand for another. The weakness is not that the string is fake or useless. The weakness is that the application and the model must infer the conversational structure from the same packed representation.

Project Desk knows there were three contributions because it assembled them. The receiving API gets one prompt. If a separator is missing, a speaker marker is malformed, or an instruction lands in the wrong place, the string still remains a string. The application may have damaged the conversational meaning without producing an obviously invalid request.

This is bookkeeping hidden inside prose.

The modern Messages request changes the bargain. Project Desk does not merely make text look conversational. It sends a list of messages whose structure is explicit. Each input message identifies which side contributed it and carries its content. The order of the messages supplies the order of the exchange.

Take the same missing-item case. Project Desk can prepare the earlier customer's report as one user contribution, the earlier assistant question as one assistant contribution, and “The blue travel mug” as the next user contribution. The application no longer needs one giant prompt string whose punctuation secretly performs all three speaker changes.

The text still matters. Claude cannot answer without the actual words. What changed is where the conversational bookkeeping lives. Speaker and content boundaries moved out of an application-invented text convention and into the request's explicit structure.

That shift gives Project Desk a cleaner place to reason.

If the latest contribution is accidentally labelled as coming from the assistant side, the defect is attached to a specific message. If an earlier contribution is omitted, the history list shows the omission. If the application wants to remove one irrelevant exchange before the call, it can remove that message rather than cut a fragile substring out of one growing prompt.

The application still has to make correct choices. Structured messages do not rescue bad data. Project Desk can attach the wrong customer case, reverse two contributions, or send too little context. The improvement is that the request represents the choices in parts the application can inspect.

Think of the difference between writing an entire mailing address as an unlabelled line and keeping separate fields for recipient, street, community, province, and postal code. Both forms eventually produce visible text on an envelope. The separated form gives software named places to validate, replace, and compare.

The comparison has a limit. A conversation is not a mailing address, and messages can contain richer material than address fields. Keep only the useful relationship: explicit structure gives the application handles for information that would otherwise be encoded by position and punctuation inside one string.

This matters when Project Desk grows beyond one developer and one experiment.

An early script may build a prompt in five lines and print the result. Months later, a production application may need to store selected history, redact private material, audit what a person contributed, test alternative instructions, and route the response into another system. When everything is packed into one text value, each of those jobs begins by reconstructing the meaning that the application previously flattened.

With messages, Project Desk can retain the distinction throughout its own code. Customer text remains a customer contribution. Earlier assistant text remains an assistant contribution. The request builder chooses which contributions cross the API boundary this time.

That last phrase is important. Messages make structure explicit, but they do not create memory inside the service for Project Desk. The application still selects and sends the history it wants Claude to receive. Chapter 4 will make that stateless arrangement concrete. For now, the historical lesson is smaller: a structured conversation is assembled from explicit contributions rather than smuggled through one specially formatted prompt.

The same improvement appears outside support work.

Consider an internal coding assistant. A developer asks why a test is failing. The assistant suggests checking a date conversion. The developer replies that the conversion is already covered and provides the failing assertion.

Packed as one legacy completion string, the application must format the developer, assistant, and developer contributions into a single piece of text and signal where the next answer should begin.

Represented as messages, the application carries three ordered contributions. It can inspect the last user contribution before sending. It can preserve the earlier assistant suggestion as history without pretending that the developer wrote it. It can test what happens when that suggestion is omitted. The conversational units already match the units the product cares about.

Now consider a summarization job with no apparent conversation at all. A user gives Project Desk a long incident report and asks for a five-line summary. Even there, a message remains useful. It says, in effect, this is the user's contribution to this exchange. Claude's result returns as the assistant contribution. The structure does not require a chatty interface. It supplies a consistent contract for a one-turn job and a multi-turn conversation.

This is one reason the Messages API is the forward path for models and features. A model service can support richer conversational inputs when the request exposes meaningful parts instead of requiring every application to invent and maintain its own prompt-string convention. The API can evolve around explicit messages while a Text Completions call remains tied to the older continue-this-text bargain.

There is a practical migration lesson here. Moving an old integration to Messages is not just changing the endpoint name. Project Desk must identify what the old prompt string was doing.

Which pieces were the person's actual contributions?

Which pieces were earlier assistant contributions?

Which pieces were instructions added by the application?

Which punctuation or labels existed only to make the old completion format work?

The modern request gives those responsibilities different homes. The conversation becomes a message list. Starting instructions receive their own request-level treatment, which we will examine in Chapter 5. Formatting that existed only as scaffolding for the legacy prompt can disappear.

A careless migration might place the entire old prompt string inside one user message. The new endpoint would accept a structured message, but the application would still be hiding all of its old conversational bookkeeping inside that message's text. The outside container would be modern while the inside remained one legacy bundle.

That can be a temporary bridge, but it misses the main benefit. The useful migration decomposes the old prompt according to meaning.

Return to the missing travel mug. Project Desk has an earlier user report, an earlier assistant question, and a new user answer. Those contributions become three messages in order. The application can now ask ordinary product questions about them.

Should the earlier shipping discussion be included?

Does the assistant need the customer's account number, or should that remain in Project Desk's own record?

Is the new answer meaningful without the earlier question?

Those are decisions about conversation and product responsibility. They are easier to see when the request is not one uninterrupted block of formatted prose.

Structured messages also give tests a better target. A test can verify that Project Desk sends three contributions in the intended order. It can check that the latest contribution belongs to the user side. It can confirm that a private internal note never enters any message. The test does not have to prove these facts by searching a long assembled string and hoping the same words do not appear elsewhere.

The structure does not make the application dependable by itself. It makes dependable behavior easier to specify and inspect.

We can now answer the question that ended the crossing in Chapter 1. Why does the modern API bother separating a conversation into structured messages?

Because a conversation has parts that matter independently. Who contributed something matters. What they contributed matters. The order matters. Project Desk needs to select, test, store, remove, and resend those parts without repeatedly decoding its own prompt formatting.

Text Completions asked the application to represent those parts inside one string. Messages gives them an explicit shape.

Project Desk has stopped treating the conversation as one ever-growing piece of prose. The next step is to look closely at the smallest complete Python call: what the request must name, what crosses the boundary, and what evidence the response brings back.

---

## Chapter 3 — The Smallest Complete Trip

Project Desk now has a better way to represent a conversation. It can keep the person's contribution as a user message instead of packing the whole exchange into one specially formatted string.

That leaves a practical question. What does the smallest useful Python call actually have to say?

Return to the damaged-shipment case. The customer's words are ready. Project Desk wants Claude to draft a reply. Before the call can cross the API boundary, the application has to answer three questions.

What model should do the work?

How much output may this call produce at most?

What conversation should Claude receive?

Those three decisions become three parts of the request: the model, the maximum-output setting called max tokens, and the messages list. The official Python SDK places them inside a call to messages dot create.

You can understand that call without holding a screenful of punctuation in your head. Project Desk creates an Anthropic client. It asks that client's messages service to create the next assistant message. In the request, it supplies a model identifier, a max-tokens value, and a list containing the user's message.

That bounded collection is the request envelope. An envelope, in this sense, is the complete set of information sent for one API operation. It is not only the customer's prose. It includes the settings and structured input that tell the service what this particular call is asking for.

The envelope comparison has a limit. A paper envelope does not control how a recipient writes back, and an API request is not literally mail. Keep only the useful relationship: Project Desk gathers the material for one trip, closes the boundary around it, and sends that exact package. Anything left outside does not silently accompany it.

The model field answers the first question. It names the model Project Desk wants the service to use. This is an application choice, not a fact hidden in the user's message. Two requests can carry the same customer text while naming different models. The wording of the support case has not changed, but an operational dependency of the application has.

Later, we will treat that model name as a versioned dependency and discuss what to store when the returned model identity differs from a vague product label. For this trip, its role is simple. The request has to identify the model being asked to generate the assistant contribution.

The messages list answers the third question. It carries the conversation Project Desk has chosen to send. In the smallest one-turn call, that list contains one user message: the customer's request for help with the damaged shipment.

Project Desk may have much more information in its own records. It may know the customer's account tier, the courier tracking number, the warehouse involved, and the private note left by a supervisor. None of that becomes model input merely because the application knows it. Only information placed into the request envelope crosses the API boundary.

This is the same responsibility we met in Chapter 1, now attached to a concrete Python call. The client library can transmit the envelope Project Desk builds. It cannot repair an envelope that omitted the facts needed for a good answer.

The middle question, how much output may this call produce at most, needs a more careful name. Max tokens establishes an output ceiling.

An output ceiling is a hard upper bound on how many tokens Claude may generate for that response. Tokens are the units the model processes and produces. Ordinary words may be one token, several tokens, or part of a token depending on the text. We do not need token arithmetic yet. The important point is the direction of the limit: Claude may generate up to the ceiling.

The ceiling is not a target.

If Project Desk permits a generous response, Claude does not have to fill the entire allowance. A reply that naturally finishes well below the limit can stop there. Setting a higher maximum does not mean asking for padding, repetition, or a response of exactly that size.

Think of the height limit inside a delivery van. A parcel must fit below it, but every parcel is not expected to touch the roof. The limit describes what cannot be exceeded. It does not predict the size of the next parcel.

That distinction protects the application from a common mistaken assumption. Suppose Project Desk allows enough output for a detailed customer reply. Claude returns a concise, complete draft. The difference between the allowance and the actual response is not missing content that the service owes Project Desk. The allowance was capacity, not a reservation.

The opposite case matters too. If the ceiling is too low for the requested job, generation may reach that limit before the answer is complete. The response carries a stop reason that lets Project Desk distinguish that outcome from a natural ending. Chapter 8 will turn stop reasons into application branches. Here, the max-tokens field has one job: it bounds possible generated output for this call.

We can now narrate the whole outgoing side.

Project Desk calls messages dot create. It names the model. It establishes an output ceiling. It supplies the selected conversation as messages.

Model, possible output, conversation.

That is the smallest practical mental model for the request envelope.

The Python SDK handles the network mechanics around the call. It turns the application-level arguments into the service request, sends it to the Messages API, and gives Project Desk a result or an error. The client library saves the developer from manually constructing the raw web request, but it does not erase the contract. Project Desk still chose every meaningful part of the envelope.

Now follow the call across the boundary.

Claude receives the request and generates the next assistant contribution. When the call succeeds, Project Desk does not receive a bare string. The SDK returns a structured assistant Message object.

The generated prose is inside that response, stored as content. In the simple support example, the first content item contains text: the proposed reply to the customer. Project Desk can extract that text for display, editing, or storage.

But printing the first text item is not the same as understanding the complete result.

The response also identifies the message. It says that the contribution belongs to the assistant side. It reports the model associated with the result. It contains an ordered collection of content items. It reports why generation stopped, includes a stop sequence when one applies, and records usage counts.

Together, those fields make up the complete returned assistant Message object. In this book, response envelope is our short name for that complete object. It is not a second wrapper around the message.

Chapter 1 called it a structured response. Response envelope gives us a paired way to reason about the trip. The request envelope records what Project Desk sent for one operation. The response envelope is the returned assistant Message object with all of its fields.

The visible answer is one part of the return package.

This separation matters even in a tiny script. Imagine that a developer runs the official-style example and prints the response object. The screen shows more than the support reply. It shows a message identifier, the assistant role, a content collection, a model identity, stop information, and usage information.

The extra fields are not clutter added around the real answer. They are the application's evidence about the generation event.

Project Desk may eventually store different parts for different reasons. It can store the generated customer-facing text with the case. It can store the message identifier and returned model with an operational record. It can use the stop reason immediately to decide whether the text is acceptable. It can send usage information to cost and capacity tracking.

Those product decisions belong to later chapters, but the shape comes first. A dependable integration does not pretend the response is only whatever prose a person will read.

Consider a second application: a meeting-notes assistant. A manager pastes rough notes and asks for three decisions and three action items. The Python request still answers the same three questions. It names a model, sets an output ceiling, and supplies the user's contribution in the messages list.

Claude may return six clean bullet points. The meeting app can display those points, but the full response tells it more. The assistant role identifies the contribution. The returned model records which model handled the call. The stop reason describes how generation ended. The usage fields describe the input and output processed.

The support draft and the meeting summary have different business purposes. Their request and response envelopes use the same route.

This regular shape makes small experiments easier to grow into real applications. A first Python file may do only two visible things: send a user message and print the resulting text. That is a reasonable way to prove the connection works. The risk comes when the shortcut hardens into the application's complete model of the API.

If the program keeps only the text, later code has no stop evidence to inspect. If it records only the model requested and ignores the model returned, it loses part of the event record. If it treats the output ceiling as an expected length, it may flag concise answers as failures or budget incorrectly. If it assumes all useful content will forever be one plain text value, richer response content will surprise it.

A better first integration can remain small while preserving the boundary between two jobs. One part of the code makes the request. Another part handles the returned message.

The request-making part knows what Project Desk intended to send: model, output ceiling, messages.

The response-handling part knows what actually came back: identity, assistant role, ordered content, returned model, stop information, and usage.

This does not require building a large framework before the first call. It requires keeping the complete response available long enough for the application to make deliberate choices.

Return once more to the three questions on the outgoing side.

What model?

How much possible output?

What conversation?

Project Desk answers them in the request envelope. Claude's service returns the response envelope: the complete assistant Message object. The answer text is available for the customer, while the object's other fields remain available for the software.

At this point, Project Desk has enough information to store the first assistant result responsibly. It knows what it asked for and it has the complete return object from that call.

It does not yet have a continuing conversation.

The API has returned one assistant contribution, but nothing in this single trip guarantees that a later call will remember it. If the customer replies, Project Desk has to decide what history crosses the boundary next. That is the route ahead: how a stateless API produces an experience that can still feel conversational.

---

## Chapter 4 — The Clerk Who Carries the Case File

The first support draft is complete. Project Desk sent the damaged-shipment request, Claude returned an assistant message, and the application stored the result with the case.

The next morning, the customer replies with one sentence: “Yes, please make it more apologetic and mention the replacement.”

Project Desk makes another Messages call. It sends only that new sentence as a user message.

What does Claude know about the draft from yesterday?

Nothing from the earlier call has been supplied here. Claude receives a request to make something more apologetic and mention a replacement, but the thing to revise is absent. The service cannot tell which draft the customer means, what happened to the shipment, or which replacement was discussed.

Project Desk has the missing material in its case record. The Messages API does not reach into that record. A new call receives the input attached to that call.

This is what stateless means. The API does not retain Project Desk's conversational state between these requests and automatically restore it for the next one. Each call must contain the conversational context Claude needs for that operation.

Stateless does not mean Claude cannot participate in a multi-turn conversation. It means the continuity is assembled by the application.

Project Desk tries the follow-up again. This time, its messages list contains three contributions in order.

First comes the customer's original description of the damaged shipment.

Second comes the assistant draft returned yesterday.

Third comes the customer's new request to make the reply more apologetic and mention the replacement.

Now Claude can generate the next assistant contribution from the exchange Project Desk supplied. The response may feel like the continuation of one conversation because the request contains the relevant conversation so far.

The memory is in the request.

More precisely, Project Desk stored earlier contributions, selected the ones that mattered, and sent them again. Claude did not retrieve yesterday's exchange by recognizing the customer. The application carried the case file across the boundary.

That record of selected earlier contributions is conversation history. History is not a magical transcript floating beside the API. It is data owned by the application: user messages, assistant messages, and whatever product metadata Project Desk keeps around them.

The product metadata and the model-visible history are not necessarily the same thing. Project Desk might store a timestamp, a database identifier, an approval state, and the employee who edited a draft. Those facts can remain application records. The messages list contains the conversational material chosen for Claude to receive.

This distinction gives Project Desk control, but it also gives Project Desk responsibility.

If the application omits a necessary earlier turn, Claude lacks it.

If the application includes an irrelevant turn, Claude receives it.

If the application sends history from the wrong customer case, Claude may answer from that incorrect context.

The service sees the assembled conversation, not the database query that assembled it.

Compare the two versions of the follow-up. “Make it more apologetic and mention the replacement” is ambiguous when it travels alone. Attached to the original user request and the earlier assistant draft, it becomes a precise revision instruction.

The new message did not change. The history changed what the message meant in context.

This is why a working chat interface can create a misleading intuition. On screen, a person sees a continuous column of bubbles. The earlier exchange remains visible while the newest answer appears underneath it. The interface looks like one persistent conversation.

Underneath, Project Desk may be making a fresh API request for every new assistant turn. For each request, it assembles the history it wants Claude to consider. The visual continuity belongs to the product. The model input continuity belongs to the request.

Think of Project Desk as a clerk carrying a case file into a new consultation. The specialist can reason from the pages placed on the desk. When the consultation ends, the clerk takes the updated file back, records the new material, and later decides what pages to bring to the next consultation.

The comparison breaks down if it suggests that Claude is a person who remembers other cases between appointments. It does not. Keep the operational relationship: the application maintains the file and presents relevant material for each separate call.

That gives us a concrete reset for any multi-turn design. Compare a follow-up with its case file attached and the same follow-up alone.

If the follow-up works only with earlier material, Project Desk must include that material or replace it with a faithful form that still supplies what Claude needs.

The first version of Project Desk might resend the complete conversation every time. That is often the clearest way to learn the mechanism. The customer contributes, the assistant responds, the customer contributes again, and the application sends those contributions in order when it asks for the next assistant message.

As the case grows, complete replay becomes a product decision rather than an automatic rule. An exchange may contain forty turns, repeated signatures, abandoned ideas, sensitive details, or long attachments that no longer matter. Sending everything can waste input capacity and place distracting material in front of the model.

Sending too little creates the opposite problem. A customer writes, “The second option works for me,” but Project Desk omits the earlier assistant message that listed the options. Claude sees a reference with no referent. A concise follow-up becomes unusable because its meaning depended on a turn the application left behind.

The job is selective resend: preserve enough history for the current contribution to make sense and for the requested work to be done, while excluding material that should not cross this time.

This is application design, not merely an optimization.

Suppose the damaged-shipment case includes an internal employee note: “Customer has complained three times; do not promise a refund until a supervisor approves.” Project Desk may need that fact for its workflow. Whether any part of it should be model input is a deliberate policy choice. The note does not belong in conversation history merely because it sits beside the messages in the same database row.

Or suppose the customer pasted a credit-card number in an early message. Project Desk may redact that value before storing or resending model-visible history. A chat transcript shown to staff, an audit record retained for compliance, and the exact messages sent to Claude can be related records without being identical copies.

Statelessness makes these boundaries visible. The application cannot assume a hidden service-side conversation will remember the right facts and forget the wrong ones. Project Desk constructs the input anew.

There is another useful consequence. Earlier assistant contributions in the messages list do not have to be text that Claude generated in a previous API call. The application can supply an assistant message as part of the history it wants the next generation to continue from.

That ability can support testing, migration, or a product workflow in which a human edited the earlier draft. If an employee changes yesterday's assistant reply before it is sent to the customer, Project Desk can store the approved version and include that version in later history. Claude then receives the conversation that actually matters to the product, rather than an invisible claim that only untouched model output counts as history.

This does not give the application permission to mislabel arbitrary instructions carelessly. Roles shape the conversational record, and Chapter 5 will separate user and assistant contributions from starting system instructions. The point here is narrower: conversation history is an application-assembled sequence. An earlier assistant turn can represent the assistant side of that sequence whether it was originally generated, edited, imported, or created for a test.

That makes testing stateless behavior straightforward.

A Project Desk test can build a follow-up request with the prior draft included and confirm that the outgoing messages contain all three expected contributions in order. A second test can intentionally omit the prior draft and verify that the request builder detects the dangling phrase “make it more apologetic.” A privacy test can confirm that the internal supervisor note never enters the messages list.

The tests do not prove what Claude will say word for word. They prove what Project Desk owns: the history selected for the call.

The same mechanism appears in a coding assistant. A developer asks for help with a failing test. Claude suggests inspecting a date conversion. The developer then writes, “I checked that; the parsed date is correct.”

Sent alone, the new message does not identify what “that” means. Sent after the earlier developer question and assistant suggestion, it becomes the next step in a specific investigation. The coding application carries the working context forward by resending the selected exchange.

It also decides when not to carry context forward. If the developer opens a new repository and starts a fresh debugging session, the assistant should not automatically receive messages from the previous company's codebase. A new visible conversation should correspond to a new history policy in the application.

This is one reason conversation identifiers inside a product should not be mistaken for model memory. A Project Desk case number helps the application locate stored records. The identifier does not, by itself, cause the Messages API to retrieve those records. Project Desk still has to load the right material and place it into the new request.

The boundary is now operational rather than abstract.

Before the call, Project Desk owns the stored history.

For the call, Project Desk selects and sends the relevant contributions.

After the call, Project Desk receives a new assistant message and decides whether to add it to the case history.

Then the cycle can repeat.

The Messages API remains stateless through every cycle. The application creates the continuity.

Return to the customer who asked for a more apologetic reply. The successful request included the original user message, the earlier assistant draft, and the new user instruction. Claude returns a revised assistant message. Project Desk can show that revision to an employee, store the approved text, and prepare for a possible next turn.

The product now feels conversational because the clerk carried the right case file.

One part of that file still needs a sharper boundary. Project Desk may want every support reply to be calm, concise, and forbidden from promising refunds. Those are not quotations from the customer, and they are not earlier assistant contributions. They are starting instructions supplied by the application.

The next chapter separates those instructions from the user and assistant roles, so the conversation can carry both its history and its governing rules without pretending they are the same kind of message.

---

## Chapter 5 — The Conversation and the Office Policy

Project Desk can now carry a support conversation from one call to the next. It stores the customer's contributions, stores the assistant's contributions, and resends the history needed for the current task.

But the application also has rules of its own.

Every proposed reply should be calm. It should be concise. It should never promise a refund without approval. Those rules are not words the customer contributed. They are not an earlier reply from the assistant. They are instructions from Project Desk about how Claude should handle the exchange.

If the application hides those instructions inside the customer's message, the request blurs two different facts: what the person said and how the application wants Claude to respond.

The Messages API gives those facts different places.

Inside the conversation, a role says which side contributed a message. The user role marks a contribution from the user side of the exchange. The assistant role marks a contribution from the assistant side.

Role does not mean job title. A user message may have been assembled by Project Desk from a form rather than typed into a chat box. An assistant message in the history may have been edited by an employee. The role identifies the contribution's place in the modeled conversation: user side or assistant side.

That is why the customer's damaged-shipment report belongs in a user message. The earlier draft belongs in an assistant message. The customer's follow-up belongs in the next user message.

The office policy belongs somewhere else.

A system instruction is application-supplied guidance that governs Claude's behavior for the request. When a rule should apply from the beginning, the normal home is the top-level system field in the request.

Top-level means it sits alongside the model, maximum-output setting, and messages list. It is not the first conversational message. Project Desk can therefore say, in effect, “Write calm, concise support replies and do not promise refunds,” without pretending the customer said those words.

The separation improves the request's honesty and its maintainability.

The messages record the exchange.

The system field records the governing instruction.

Project Desk can change an office policy without rewriting the customer contribution. It can test two instruction versions against the same conversation. It can log which policy was active for a generation. It can prevent the policy text from appearing as though it were part of the customer's complaint.

Return to one rule that applies before the first user turn and one that becomes relevant later.

The starting rule is simple: every support reply should be calm and concise. Project Desk knows that rule before the customer says anything. It belongs in the top-level system field from the first call.

The later rule appears only if the case is escalated: include a short handoff summary for the supervisor and stop offering self-service steps.

The starting rule and the later rule are both application instructions, but they become relevant at different times. The ordinary, widely applicable design is still straightforward. Project Desk can construct the system instruction needed for the current call and place it in the top-level system field. On the escalated call, that field can include both the durable support policy and the new escalation guidance.

This approach works with the stable request shape we have already learned. The application owns the instruction just as it owns the history. For each call, it builds the governing system text and the conversational messages deliberately.

The durable rule is now complete: conversational contributions use user and assistant roles; instructions that govern the exchange from the start use the top-level system field.

Now consider how these distinctions improve a support audit.

A reviewer opens a case and asks why Claude wrote a short escalation summary instead of another troubleshooting reply. Project Desk can show four separate pieces of evidence.

The customer message triggered escalation.

The earlier assistant messages show what had already been tried.

The governing instruction says how escalated cases should be handled.

The model record says which placement behavior the request relied on.

If all of that material had been flattened into one user message, the audit would begin by guessing which sentences came from the customer and which were application policy. Explicit roles and a distinct system instruction preserve the provenance of the request.

The same boundary matters in a coding assistant. A developer's message might say, “Refactor this function.” The application instruction might say, “Preserve the current public API and explain any behavior change.” Both influence the answer, but they come from different authorities. The developer supplied the task. The application supplied the operating rule.

Mixing them into one user contribution can still produce useful output. The problem is not that Claude becomes unable to read the text. The problem is that Project Desk loses a clean representation of who supplied what and where durable policy belongs.

The distinction also helps when instructions change. Suppose the coding product begins in review mode, where Claude should identify risks without editing. Later, the user explicitly switches to implementation mode. On a model and request path that supports a mid-conversation system instruction, the application may add the new operating guidance at the permitted point. On the general path, it can rebuild the top-level system instruction for the next stateless call.

Either way, the application makes the mode transition explicit. It does not rewrite the user's earlier words to manufacture the new policy.

We can now sort the Project Desk case without ambiguity.

“My parcel arrived damaged” is a user contribution.

The proposed reply is an assistant contribution.

“Make it more apologetic” is the next user contribution.

“Remain calm, concise, and do not promise a refund” is a starting system instruction.

“This case is now escalated; provide a supervisor handoff” is a later instruction. The general implementation can place the current combined guidance in the top-level system field.

One production note qualifies that general path. Current Opus 4.8 documentation allows a system-role message after a user turn, subject to placement rules; it cannot be the first message. Use that model-specific branch only with a measured reason and tests. Otherwise, rebuild the top-level system guidance for the next call.

Roles tell us where conversational contributions belong. System instructions tell Claude how to handle them.

Project Desk now has both a case file and an office policy, without pretending they are the same document.

So far, we have spoken about each message's content as though it were simply text. That shorthand works for the examples we have used, but the actual content field can carry an ordered collection of typed blocks. The next chapter opens that collection and shows why content is built from parts rather than guaranteed to be one string.

---

## Chapter 6 — What One Message Can Carry

Until now, the content of a message has sounded like one piece of text. The customer writes a complaint. Project Desk places that text in a user message. Claude returns reply text in an assistant message.

That simple form is real, but it is shorthand.

A message's content can be an ordered collection of typed content blocks. When Project Desk supplies an ordinary string instead, the API treats it as the convenient form of one text block.

The shortcut lets a first Python call remain small. The fuller structure lets the same Messages API carry richer material without pretending that every input is one undifferentiated paragraph.

The need becomes clear when Project Desk takes on a document-extraction job.

A person uploads a PDF invoice and asks for the supplier, invoice date, purchase-order number, and total. One user contribution now contains at least two meaningful pieces: the PDF document to inspect and the text instruction describing what to extract.

Project Desk could try to flatten everything into one string. It might copy any readable document text, paste the instruction underneath, and invent separators between them. That can work for a narrow experiment. It also throws away a fact the request already knows: one piece is the source document, and another piece is the person's instruction about that document.

A content block preserves one meaningful piece inside the message. Each block carries a type that tells the API what kind of piece it is. Text is one type. Other supported material can use other types rather than masquerading as text.

Type is our second term. A type is an explicit label for how a piece of data should be interpreted. It helps the request distinguish text from an image, a PDF document, or another supported kind of content.

The type does not explain the business purpose by itself. A text block might contain a question, a caption, an instruction, or quoted source material. It says that the block is text. The words and their position supply the more specific meaning.

Return to the invoice. Project Desk constructs one user message. Inside its content collection, the document comes first. The extraction instruction comes second.

Those blocks belong to one message because they form one user contribution: here is the material, and here is what I want done with it.

They remain separate blocks because their kinds and functions differ.

Their order is also part of the input. Content is not a bag whose pieces may be rearranged without consequence. It is an ordered collection. Project Desk sends one block, then the next, in the sequence it intends Claude to receive them.

For the invoice case, document first and instruction second creates a natural reading: inspect this; then perform this extraction. Another application may choose text before an image, perhaps introducing what the image represents before supplying it. The point is not that one universal order always wins. The point is that the application owns the order and should treat it as meaningful.

This gives us a useful four-part distinction.

A role identifies the user or assistant side. A turn is one side's stretch of the back-and-forth.

Each message is one structured contribution supplied by the application.

The block separates the meaningful pieces inside that contribution.

The type identifies how each piece should be interpreted.

For example, Project Desk could send two consecutive user messages: first the document, then a correction about the document. Those are two message objects, but together they form one user turn. The assistant's reply begins the next turn.

Side, turn, message, blocks. The role names the side. The turn marks that side's stretch. A message carries one structured contribution. Its blocks carry the ordered pieces.

The distinction helps Project Desk avoid two opposite modeling errors.

The first error is making a separate message for every fragment merely because multiple blocks exist. The invoice and the request to extract its fields can belong to one user turn. Separate blocks do not automatically mean separate speakers or separate conversational turns.

The second error is forcing several unlike pieces into one text value merely because they belong to one turn. One message can contain several blocks. Conversational unity does not require data flattening.

Think of a message as a tray prepared for one recipient, with several labelled items arranged on it. The tray keeps the contribution together. The labels distinguish the items. Their left-to-right order preserves how they were arranged.

The comparison stops before it becomes literal. Content blocks are structured data, not physical objects, and different block types have their own required fields. Keep the useful relationship: grouping, labelling, and order can all matter at once.

The plain-string shortcut now fits into the same model. Suppose the user says only, “Draft a polite shipping-delay apology.” Project Desk can supply that sentence directly as the message content. Conceptually, it is still one text block. The SDK accepts the shorter form because there is only one text piece to represent.

This means the application does not have to build a block collection manually for every simple request. It also means developers should not mistake the convenient syntax for the complete data model.

If Project Desk later adds an image of the damaged parcel, the message content can grow from one text block into an ordered collection containing the image material and the text question. The user contribution remains one message while its content becomes richer.

The same structure appears on the returned side. In Chapter 3, the response envelope contained an ordered content collection. A simple reply may contain one text block, which makes extracting the visible answer feel like reading a single string. The complete response model still treats content as blocks.

That matters because response handling should inspect what was returned rather than assume every content item is plain text forever. Project Desk may want to collect text blocks for display while preserving other supported block types for their own handlers. The exact response possibilities belong to later feature chapters. The durable lesson is that content has structure inside the message.

Consider a maintenance-inspection assistant. A technician submits a photograph of a corroded fitting and adds, “Describe only visible conditions. Do not diagnose the cause.” The photograph and text belong to the same user contribution. Their types differ. Their order gives Claude the material and the instruction as an intentional sequence.

Project Desk can test that structure directly. A request-builder test can confirm that the first block carries the inspection image and the second carries the limiting instruction. It can confirm that both blocks remain inside one user message. It does not have to search a giant encoded string for a separator invented by the application.

The block model also improves transformations. If Project Desk must remove an image before sending a text-only fallback request, it can remove or replace the image block. If it needs to change the extraction instruction, it can update the text block without rebuilding the source document. If it wants to preserve the original order for an audit, that order is available as data.

Explicit structure does not eliminate judgment. Project Desk can still put the wrong document beside the instruction, reverse a sequence that should remain stable, or attach a vague question. Blocks make those choices inspectable. They do not make the choices correct on the application's behalf.

The invoice example now gives us a boundary for deciding what belongs together.

The uploaded invoice and the request to extract four fields participate in one user turn, so they belong in one message.

The document and the instruction are different meaningful pieces, so they belong in separate blocks.

Their types tell the API how to interpret each piece.

Their order records the sequence Project Desk chose.

The customer's account metadata still may not belong in the message at all. Content blocks are not a reason to send every available record. The API boundary remains selective.

This structure scales without requiring the listener to memorize the complete catalog of block types. Supported features add their own block shapes and requirements. The common mechanism remains the same: a message carries ordered content; blocks divide that content into typed pieces; a plain string is shorthand for one text block.

Claude returns the next assistant message using the same broad content idea, surrounded by the operational fields in the response envelope.

We have named those fields but not yet walked through them as one complete arrival record. The next chapter follows the response from its message identifier through content, model, stop information, and usage, so Project Desk can store more than the visible answer without confusing evidence with prose.

---

## Chapter 7 — Reading the Arrival Record

Claude has returned a support draft. The first text block contains exactly what Project Desk hoped to see: a calm apology, an acknowledgement of the damaged shipment, and a request for the photograph needed to continue the claim.

The prose is the part an employee may edit and a customer may eventually read. It is not the whole event.

The response envelope records several different facts about what happened. Project Desk can keep them straight by asking six short questions.

What was said?

Which side contributed it?

Which returned message is this?

Which model served it?

Why did generation stop?

What did the call use?

The content blocks answer the first question. In this case, a text block carries the proposed reply. Project Desk can select the text for display while preserving the full content collection in its operational record.

The role marks this as the assistant contribution. The message identifier distinguishes this response instance from other returned messages. The model field reports which model served the response. These are three identity questions, not three spellings of the same fact.

That response field is the returned model. It is evidence about the dependency that produced the result, not merely a copy of the product name shown to the user.

Project Desk also knows which model it requested. The request records intention; the returned response records the result supplied by the service. A dependable event log can retain both rather than treating one as a substitute for the other.

Chapter 10 will examine model identifiers as versioned dependencies. Here, the returned model answers a smaller operational question: which model does this response say answered?

The stop information answers why generation ended. The stop reason records the cause. An optional stop sequence identifies a matching sequence when that kind of stop applies.

Stop information is completion metadata: structured evidence about how generation concluded. It is separate from the semantic quality of the prose.

That separation matters because text can look finished when generation was cut off. A sentence may happen to end with a period just as the output ceiling is reached. Another response may contain awkward prose even though Claude ended the turn naturally. Punctuation and writing quality do not replace stop metadata.

The usage object answers what the call used. Usage records input and output token counts associated with the completed call. It describes what the operation used, not what Project Desk guessed beforehand and not the maximum output that the application permitted.

This gives us another useful distinction.

The output ceiling belongs to the request. It limits what may be generated.

Usage belongs to the response. It reports what the completed operation processed and produced.

A large ceiling and a concise answer can coexist without contradiction. Capacity was available; actual usage remained lower.

Return to the six response questions.

What was said? Read the content.

Which side contributed it? Read the role.

Which returned message is this? Read the message identifier.

Which model served it? Read the returned model.

Why did it stop? Read the stop metadata.

What did it use? Read the usage counts.

Each field supports a different application observation. None should be asked to prove what another field proves.

Consider two support drafts that end with the same pleasant sentence: “Once we receive the photograph, we can arrange the next step.”

The first response reports that Claude ended the turn normally. The second reports that generation reached the output limit.

To an employee scanning only the visible prose, both drafts may appear complete. To Project Desk, they are not the same operational result. The second response carries evidence that the generation was bounded by the ceiling. The application should not discard that evidence merely because the final words look tidy.

Chapter 8 will turn that difference into explicit branches. For now, the comparison establishes the rule: response text describes the proposed answer; response metadata describes the generation event.

The same distinction helps when the prose is poor. Suppose Claude ends naturally but produces a reply that violates Project Desk's support policy. A normal stop reason does not certify the answer as correct, safe, or useful. It says how generation stopped. Product validation still belongs to the application and the people reviewing the reply.

Operational metadata is evidence with a limited job.

The message identifier does not prove the answer is good.

The returned model does not prove the prompt was complete.

The stop reason does not prove the facts are accurate.

Usage does not prove the tokens were well spent.

Clear boundaries make the fields more useful, not less. Project Desk can log what each one actually establishes and add separate checks for policy, factuality, formatting, and human approval.

Consider an internal research assistant. An employee asks for a comparison of three supplier proposals. The visible answer is a table-like summary. The operational log records the response identifier, returned model, stop reason, and usage. The product may retain the source documents and request separately.

If someone later asks why the comparison ends after the second supplier, Project Desk has more than a fragment of prose. It can inspect whether generation hit the output ceiling, whether the request omitted the third document, and which model handled the call. Different evidence points to different failure paths.

That is the practical value of a complete response envelope. It preserves clues the answer text cannot supply by itself.

Project Desk does not have to expose all of those clues to the customer. The person awaiting a replacement may see only the approved support reply. An internal support employee may see the draft plus a warning if generation ended at a limit. An observability system may receive identifiers, model information, stop metadata, and usage.

One response can feed several product layers because its fields retain their distinct meanings.

The arrival-record comparison is useful here. Opening a parcel reveals its contents. A delivery record identifies the shipment and describes its arrival. The record does not tell whether the contents are beautiful or correct, but discarding it would remove evidence about the trip.

The response envelope works the same way up to that boundary. Content is what Claude produced. The surrounding fields help Project Desk identify and interpret the operation that produced it.

We can now state the complete arrival in one pass.

Claude returns an assistant message with an identifier. Its ordered content blocks carry the generated material. Its model field records the returned model. Its stop fields describe why generation ended. Its usage fields report token counts for the call.

Project Desk reads the text and keeps the evidence.

The next decision begins with the stop reason. A natural ending, an output limit, a tool request, a refusal, and an invalid request do not all lead to the same application action. Some belong to successful response handling; one belongs to request error handling; each needs its own branch.

Chapter 8 turns the arrival record into a control point: accept, continue, run a tool, fall back, or repair the request.

---

## Chapter 8 — Classify Before You Act

Project Desk receives an assistant message with polished text. Before displaying, retrying, or continuing anything, the application reads the stop reason.

This order matters. Classify the event before choosing the next action.

A stop reason is the response field that says why Claude stopped generating. It belongs to every successful Messages response. Successful here means the API processed the request and returned a structured response; it does not mean the answer is automatically suitable for the product.

The stop values are easier to retain as action families than as a catalog.

The finished family contains a natural end of turn. Claude finished generating, so Project Desk can move on to product checks such as policy, completeness, factual review, or human approval.

The truncated family contains an output-limit stop and a model-context-window stop. The limiting resource differs, but the immediate handling agrees: do not present the result as complete. Project Desk may continue under an appropriate policy or make a new request with different bounds.

The configured-boundary family contains a custom stop sequence. Project Desk checks which sequence fired and handles the boundary it deliberately created.

The continuation family contains tool use and pause turn. Both mean that Project Desk should not display the response as a finished answer. Their mechanics belong to later volumes.

The declined family contains refusal. Claude processed the request but declined to answer, so Project Desk enters its refusal policy.

An unfamiliar future value enters a safe unknown branch. The application should not convert a stop reason it does not understand into a natural ending.

Finished, truncated, configured boundary, continuation, refusal, or unknown: the action family comes first. The exact stop value then selects the detailed handler.

Now contrast all of those with a request error.

A request error means the service did not return a successful assistant response for Project Desk to classify in the same way. The request may be invalid. Authentication may fail. The application may be rate limited. The service may be overloaded or encounter another processing failure. These cases arrive through HTTP error handling rather than as a successful response carrying a stop reason.

The difference is structural.

With a stop reason, Project Desk has a successful response envelope and evidence about how generation ended.

With a request error, that successful response does not exist. Project Desk handles the error status and error body instead.

This prevents a common retry mistake. Suppose Project Desk receives a rate-limit error. There is no assistant message whose stop reason says rate limit. The application should follow its rate-limit policy, such as respecting retry guidance and controlling request pace. It should not search for useful prose inside a response that was never generated.

Now suppose a successful response carries a refusal stop reason. Project Desk has a structured assistant response, but Claude declined the request. The application should enter its refusal policy, not report a networking failure.

That policy may return the refusal to the user, reframe a legitimate request, or use an eligible fallback path. It must not treat fallback as permission to evade safety policy. Chapter 9 will set that boundary carefully.

The model qualification matters again. The documented classifier-refusal form described here is associated with a current model and policy path. Project Desk records the model and checks the actual response rather than inventing one universal refusal shape from memory.

Consider three Project Desk events.

In the first, Claude returns a complete support reply with a natural end-of-turn reason. Project Desk runs its normal review.

In the second, Claude returns half a reply and reports that the output ceiling was reached. Project Desk continues or retries under its truncation policy.

In the third, the API returns a rate-limit error. Project Desk slows or schedules the request according to its HTTP retry policy.

The visible business task is the same in all three cases: draft a support reply. The control paths differ because the operational events differ.

Add a fourth event. Claude returns a refusal response. Project Desk reads the refusal details and applies its refusal-specific policy. It does not route that event through ordinary rate-limit handling, and it does not claim the requested draft was completed.

This is evidence-driven branching. The application chooses its next action from structured evidence rather than from a guess about the prose.

The code can remain conceptually simple even when the production details grow. First, separate successful responses from request errors. Second, within a successful response, branch on the stop reason. Third, validate the content for the product.

Transport outcome, generation outcome, product outcome.

Those are three different questions.

Did the request produce a successful response?

Why did generation stop?

Is the returned content suitable for this use?

Project Desk becomes more reliable when it refuses to collapse them into one boolean called success.

The refusal branch now deserves its own inspection. Anthropic documents fallback mechanisms for qualifying refusals, including a dated fallback-credit feature. Those mechanisms are narrow. They do not replace ordinary retry logic, and they do not apply to every model or every refusal.

The next chapter compares one refusal with one rate limit, then chooses different handling for each.

---

## Chapter 9 — The Alternate Route With One Job

Project Desk sends a legitimate support-classification request to Claude Fable 5. The request is valid. The service processes it. Instead of a classification, the response carries a refusal stop reason.

The application has reached a particular kind of blockage. Another permitted Claude model may be able to serve the request, so Project Desk can choose an alternate route.

That route is fallback. Fallback means retrying a qualifying refused request on another model that is allowed to receive it.

The qualification does most of the work in that definition.

Fallback is not a second attempt at every failed call. It is not the response to a rate limit, an overloaded service, a server error, or malformed input. Current server-side fallback runs when the requested model's safety classifier declines. Those other failures return to the application unchanged.

Compare two events.

In the first, Claude Fable 5 returns a successful response envelope with the refusal stop reason. Project Desk can inspect the refusal and decide whether an eligible fallback model should receive the same request.

In the second, the service returns an HTTP rate-limit error. No successful assistant response exists. Project Desk follows its rate-limit policy: control the request pace, respect retry guidance, and try later when appropriate.

The alternate model does not create more capacity on the rate-limited route. Refusal fallback solves the first event, not the second.

The same boundary applies to safety policy. Fallback is a documented way to handle classifier differences between permitted models. It is not permission to rewrite a harmful request until some model accepts it. Project Desk still applies the product's safety policy and the platform's usage rules. If the request itself should not be served, another route does not make it suitable.

Current Claude Platform documentation offers managed and manual arrangements. The API or SDK can manage the alternate route, or Project Desk can write the refusal retry when the product needs custom control. In each case, Fable refuses, a permitted alternate model is tried, and the returned-model field says which model served the result.

All three arrangements begin with the same decision: a qualifying refusal occurred, and another permitted model should be tried. They differ only in who owns the retry machinery. The final response's returned-model field identifies which model actually produced the message.

One billing note is enough for now. For a manual retry of a cached prompt, the current beta fallback credit can avoid duplicate cache-creation cost; managed API and SDK paths apply it automatically. It changes billing, not eligibility, and does not make fallback processing free.

None of these arrangements changes eligibility. The retry target must be permitted, the request must work on that target, and the trigger must be the qualifying refusal path.

Suppose Project Desk configures a chain of two fallback models. The first model refuses. The next model also refuses. A final model returns an answer.

Project Desk receives the final response and records the model that actually served it. It also records that fallback occurred. If every permitted model declines, the final result remains a refusal. A chain is not a guarantee that some answer will emerge.

This is another place where the visible prose cannot tell the whole story. A successful fallback answer may look ordinary. The response metadata reveals that the requested model declined and another model served the turn. That fact matters for evaluation, cost tracking, consistency, and later model decisions.

The application also needs an explicit no-fallback outcome. If a refusal has no permitted target or no product-approved alternate model, Project Desk returns or handles the refusal. Missing fallback credit changes the billing path for a manual retry; it does not make an otherwise eligible fallback impossible.

Now return to the rate-limit comparison.

One response says refusal. Project Desk may choose a permitted alternate model.

One HTTP error says too many requests. Project Desk manages request timing.

The business task may be identical. The evidence selects different machinery.

That is the useful boundary around fallback: one alternate route, designed for one class of blockage.

Choosing the alternate model raises the next question. Project Desk now has a primary model, perhaps one or more fallback models, and behavior that can differ by model version. Those names are production dependencies, not decorative labels.

Chapter 10 builds the selection from real support prompts and records the exact model ID that earned the route.

---

## Chapter 10 — The Model That Earned the Route

Project Desk needs a primary model for support work and perhaps another model for eligible fallback. A model comparison page can narrow the candidates. It cannot tell Project Desk which one handles Project Desk's work best.

The application has its own mix of jobs. Some customer messages are short and routine. Others contain contradictory dates, indirect requests, or several problems tangled together. Some require a fast draft while an employee waits. Others can take longer if the answer is more dependable.

Model selection begins with those requirements.

Anthropic's current guidance frames the choice around capability, speed, cost, and effort. Project Desk turns those broad criteria into observable questions.

Does the model identify the actual customer request?

Does it preserve dates, order numbers, and policy boundaries?

Does it follow the required reply style?

How quickly does it return a usable draft?

What does the workload consume at production volume?

The answers come from testing the application, not from choosing the most impressive product description.

An evaluation set is a repeatable collection of real or representative inputs, expected qualities, and edge cases used to compare model behavior for one workload.

Project Desk might include ordinary damaged-parcel reports, vague follow-ups whose meaning depends on history, a complaint containing two separate orders, an internal note that must never enter the reply, and an escalation that forbids a refund promise. The set should include the cases where a plausible-looking answer can still be operationally wrong.

The same prompts run against candidate models. Project Desk records response quality, accuracy, instruction following, latency, usage, and the frequency of unacceptable failures. Human review remains necessary for qualities that a simple automated score cannot judge.

This does not require a giant research program before the first prototype. A small, representative set is more useful than a large pile of easy examples. The set can grow whenever production reveals a new failure mode.

The evaluation set gives model migration a stable question. Has another model improved Project Desk's actual workload enough to justify a change?

Without that set, migration can become a reaction to a launch announcement or one striking demonstration. With it, Project Desk can compare the new candidate against the same support cases and the same acceptance boundaries.

Once a model earns the route, the request records its model ID.

A model ID is the API name for a specific pinned model version. Anthropic's current versioning contract says each model ID identifies a fixed model version for the lifetime of that ID.

The spelling changed at the Claude 4.6 generation, so Project Desk keeps a compact worked record.

For an earlier line, the application might request the short Sonnet 4.5 name. That name is a convenience alias, so Project Desk also stores the dated model value returned with the response.

For the current line, the application can request the Sonnet 4.6 dateless model ID. Under the current contract, that name already identifies one pinned release, so the returned value names the same release.

The stable rule is smaller than the naming history: store what the application requested and the model value the response returned. That pair gives Project Desk evidence for investigating a later behavior change without assuming that every returned value has been normalized into a different spelling.

Pinned does not mean permanent availability. Each model ID has its own deprecation and retirement schedule. Project Desk needs both reproducibility and a migration path: know what was tested, and know what evidence would justify moving.

The evaluation record can stay compact.

It names the model ID.

It names the evaluation-set version.

It records the test date and relevant settings.

It summarizes the criteria and unacceptable failures.

It records why this model was selected for the primary route or fallback route.

The prose of a particular answer remains in the detailed test record. The decision note explains why the dependency entered production.

When a new model arrives, Project Desk does not replace the ID immediately. It runs the evaluation set, compares the results, checks new failures, and decides whether the gain is worth migration. If the new model wins, the application changes the request field deliberately and records a new decision.

The same discipline applies to fallback. The alternate model should not be chosen merely because it is different from the primary model. It needs to be a permitted target, support the request features Project Desk uses, and perform acceptably on the workload it may inherit.

One tested support prompt, one edge case, and the identifier that produced each result: that is the smallest useful reset.

The ordinary prompt shows whether the model handles the common route. The edge case shows whether it respects a boundary under pressure. The model ID connects the behavior to a versioned dependency.

Project Desk can now explain its model choice without reciting the current product lineup. It selected a model because that model met the workload's capability, speed, cost, and effort requirements on a named evaluation set. It stored the canonical ID that produced the result. It defined the failure or improvement that would trigger another comparison.

The next measurement happens before and after every call. Project Desk can estimate how many input tokens a structured request may use, constrain possible output with max tokens, and read final usage from the response. Those three numbers answer different questions, especially when the selected model changes.

---

## Chapter 11 — Three Token Numbers, Three Questions

Project Desk is preparing a support request with several earlier messages and a long customer attachment. The application wants to know whether the input is a sensible size before sending it. It also wants to limit the possible reply. After the call, it needs a record of what the operation actually used.

One token number cannot answer all three questions.

Before the call, Project Desk can use the Token Counting API. It sends the same structured inputs it plans to use for message creation and names the intended model. The counting response estimates the number of input tokens.

A token estimate is a preflight approximation of input size for a particular structured request and model. It helps Project Desk reason about capacity, rate limits, cost planning, and routing before committing the generation call.

The word estimate matters. Anthropic documents that the preflight count may differ slightly from the actual input usage reported when the message is created. The count is useful evidence before departure, not a promise about the final record.

The estimate is also model-specific. Different models can use different tokenizers. A tokenizer is the mechanism that divides input into the token units the model processes. The same words and content blocks can therefore produce different counts when Project Desk changes the model named in the counting request.

This is why a model migration requires a recount. Project Desk should not take the count measured for yesterday's model and relabel it for today's model. It sends the same structured request to the counting endpoint with the new model ID and measures again.

The second number belongs to the actual message request. Max tokens sets the output ceiling we met in Chapter 3. It limits the number of tokens Claude may generate for the response.

The ceiling does not estimate input. It does not predict output. It does not report cost already incurred. It is a control chosen by Project Desk before generation.

The third number arrives in the response usage record. Final usage reports what the completed call actually processed and generated. It is the after-the-event evidence Project Desk uses for accounting and monitoring.

Estimate before sending. Ceiling in the request. Usage after completion.

Work through one small Project Desk call. The token counter estimates five thousand input tokens. Project Desk permits up to one thousand output tokens. Claude finishes with four hundred twenty output tokens reported in final usage.

Three values are enough.

Five thousand answers, approximately, how large is this planned input for the selected model?

One thousand answers, what is the most output this request permits?

Four hundred twenty answers, how much output did the completed call report?

The unused space between one thousand and four hundred twenty is not missing work. The ceiling was permission, not a target.

The final input usage may also differ slightly from the five-thousand-token estimate. Project Desk stores the final response usage as the completed event record rather than rewriting history to make the preflight estimate look exact.

Think of a delivery route estimate and the end-of-day mileage log. The estimate helps dispatch decide whether the route fits the day. A maximum permitted detour constrains what the driver may add. The final mileage records what happened.

The comparison stops at the mechanism. Tokens are not kilometres, and token use depends on the structured model request. Keep the relationship: planning evidence, a chosen bound, and final evidence serve different decisions.

This separation prevents several production mistakes.

If Project Desk treats the token estimate as final billing, small differences appear to be accounting defects when they are ordinary estimate variance.

If it treats max tokens as expected output, concise answers appear incomplete merely because they did not fill the allowance.

If it uses final output usage to judge whether the next input will fit, it asks an after-the-event output number to solve a preflight input problem.

Each mistake comes from moving a number into the wrong question.

The Token Counting API accepts the same broad structured input shape as message creation, including system guidance, messages, tools, images, and PDF documents when those features are used. Project Desk therefore counts the request it plans to send, not only the visible customer sentence.

That distinction matters for a long conversation. The newest user message might contain twelve words, while the selected history, system instruction, PDF document, and tool definitions make the complete request much larger. Counting only the latest sentence would measure the wrong object.

The request envelope is the unit of preflight.

Project Desk can use the estimate to decide whether to send the selected history as-is, remove irrelevant turns, summarize material under a deliberate policy, route to a suitable model, or reject an oversized operation. Those are application decisions made before generation.

It then sets the output ceiling according to the job. A short classification needs less possible output than a detailed support draft. The application leaves enough room for a complete answer without treating capacity as a quota.

After the response returns, Project Desk records final usage beside the message identifier, returned model, and stop reason. If the stop reason says the output ceiling was reached, the application has both the ending evidence and the usage record needed to understand the truncation.

Now imagine Project Desk changes its selected model after the evaluation in Chapter 10. The conversation text remains identical. The correct workflow still repeats the count against the new model, chooses an appropriate output ceiling for that model and task, sends the request, and records the new response usage.

The estimate belongs to the model named at preflight. The final usage belongs to the model that served the completed call. In a fallback path, those identities may differ, which is another reason to retain the returned-model evidence.

The three token numbers now sit in their proper places.

The preflight estimate supports a before-call decision.

Max tokens constrains possible generated output.

Final usage records the completed operation.

Project Desk no longer asks one number to stand for capacity, output control, and accounting at once.

The final chapter moves this mechanism into a different product. A PDF-review assistant will build selected history, count and send a versioned request, inspect the complete response, and branch on evidence. The names remain familiar, but Project Desk will no longer be there to carry the explanation.

---

## Chapter 12 — A New Desk, the Same Route

Project Desk steps out of the story. In its place is Review Room, an internal application that helps a team examine policy PDFs.

A user uploads a proposed remote-work policy and asks for three things: the decisions the policy makes, the questions it leaves unanswered, and any dates or responsibilities that appear inconsistent.

Review Room will use the direct Messages API. The product is new, but the application responsibilities are already familiar.

Before anything crosses the API boundary, Review Room owns the PDF, the user request, the review policy, the selected model, and any earlier conversation it may choose to include. Claude cannot inspect the application's file store or recover omitted history on its own.

Classify the opening input before Review Room builds it. Do the policy PDF and the instruction form one user turn or two? Do they require separate messages? Where should the standing review rule go?

They form one user turn: one stretch contributed from the user side. Review Room supplies one user-role message for that turn. Inside the message, the policy PDF is one typed content block and the review instruction is a text block after it. The role names the side, the turn groups the contribution, the message carries it, and the blocks carry its ordered pieces.

The standing rule belongs outside that conversational contribution. The assistant should quote policy language only when needed, distinguish explicit statements from inferences, and never invent a missing decision. Because that guidance applies from the first turn, Review Room places it in the top-level system field.

Now ask the three request questions from Chapter 3.

What model?

How much possible output?

What conversation?

Review Room names the canonical model ID that passed its document-review evaluation set. It chooses an output ceiling large enough for the requested analysis. It supplies the user message with the document and instruction, plus the system guidance that governs the call.

Before sending, the application counts the full structured input against that selected model. The document, instruction, and system guidance all contribute to the estimate. Counting only the sentence “Review this policy” would measure the wrong request.

The estimate supports the preflight decision. The max-tokens value constrains possible output. Neither one predicts final usage.

Review Room calls messages dot create. The request crosses.

Claude returns an assistant Message object: the complete response envelope. The application reads it before deciding that the review succeeded.

The content blocks contain the generated analysis. The message identifier distinguishes this result. The returned model records which model served it. The stop reason explains why generation ended. Usage records the completed operation.

Review Room then separates three outcomes that a weak integration might collapse into one word.

The request produced a successful response.

Generation ended for a recorded reason.

The content either passes or fails the product's review checks.

A natural end of turn clears only the middle question. Review Room still checks that the response identifies decisions, open questions, and inconsistencies without turning speculation into policy fact.

Suppose the review passes. The application stores the assistant contribution with the document case. It also stores the operational evidence needed to explain the event. A person sees the useful analysis. The software keeps the arrival record.

The user now asks a follow-up: “Which of those open questions should legal review first?”

Sent alone, the phrase “those open questions” has no supplied referent. The API is stateless. Review Room must carry the relevant case file into the new call.

The application selects the original user contribution, the approved assistant analysis, and the new follow-up. It sends those messages in order. The system guidance remains application policy rather than a conversational quotation.

Claude can now answer from the history Review Room provided. The apparent memory belongs to the application's stored and resent conversation.

That completes the ordinary loop.

Store selected history.

Construct a versioned request.

Count the planned input and set the output ceiling.

Send the request.

Inspect the complete response.

Branch on the stop reason and product evidence.

Store the accepted assistant contribution for a possible next turn.

The sequence is useful because each step has an owner. It is not a framework Claude performs invisibly for Review Room.

Three failure tests show whether the product really owns the route.

The first test removes necessary history. Review Room sends “Which of those open questions should legal review first?” without the earlier analysis. What is missing, and which side must repair it?

The referent for “those open questions” is missing. Review Room must catch the dangling reference or supply the relevant earlier analysis. The test proves that conversation continuity comes from selected resend, not hidden service memory.

The second test makes the output ceiling too low for the three-part policy review. Claude returns polished text and a max-tokens stop reason. Should Review Room accept the punctuation as proof of completion?

No. The stop reason places the response in the truncated action family. The test proves that visible prose does not override completion metadata.

The third test produces an HTTP rate-limit error. Does Review Room look for a stop reason, enter refusal fallback, or use request-error handling?

No successful assistant response exists, so Review Room uses its HTTP request-error policy. The test proves that transport failure and generation outcome are different control surfaces.

Those three tests cover omission, truncation, and misclassification. They exercise the application's responsibilities without requiring one exact generated answer.

Review Room can add another test when it uses a fallback model. A qualifying refusal may route the request to a permitted alternate model. The returned response must identify the model that actually served the analysis, and the application's event record must preserve that fact. A rate limit still follows the ordinary error path.

Model migration gets its own test lane. When a new candidate appears, Review Room runs the same policy documents, ordinary questions, and edge cases from its evaluation set. It does not switch because the new model has a newer name. It switches when the workload evidence supports the change.

If the model changes, Review Room recounts its representative requests against the new model. The old token estimate belonged to the old model. The application then chooses its output ceilings, observes final usage, and updates capacity planning from the new evidence.

The new product now gives us a retrieval without Project Desk. In Review Room's opening input, name the role, turn, message, and blocks before reading on.

The role is user. The document and instruction form one user turn. Review Room supplies one message for that turn. The message contains two ordered blocks: document first, instruction second.

The standing review policy belongs in the top-level system field, outside the user's conversational contribution.

Earlier user and assistant contributions return only when Review Room selects and resends them.

The model ID records the versioned dependency chosen through evaluation.

The token estimate informs the call before departure. Max tokens bounds possible output. Final usage describes the completed call.

The response content carries the analysis. The surrounding envelope carries identity, model, stop, and usage evidence.

The stop reason selects a successful-response branch. An HTTP error selects request-error handling. Product checks decide whether the analysis is fit for use.

These are not independent facts to memorize. They are one conversation core: the smallest application loop that keeps ownership visible from input selection through the next action.

The word core sets a boundary. A production assistant may add streaming, tools, prompt caching, batches, files, citations, structured outputs, observability, retries, permissions, and user-interface state. Those features deepen or extend the route. They do not remove the need to explain what the application sent, what returned, and why it acted next.

That explanation is also a debugging method.

When Claude appears to forget, inspect the selected history.

When an answer looks cut off, inspect the stop reason and output ceiling.

When usage surprises the team, compare the model-specific estimate with final usage rather than treating them as identical.

When behavior changes after migration, inspect the model IDs and rerun the evaluation set.

When a retry behaves strangely, identify whether the event was a refusal, an HTTP error, or another stop outcome before choosing the mechanism.

The questions lead back to structured evidence instead of guesswork about the prose.

Review Room stores its accepted first analysis and waits for the next user contribution. If one arrives, the application will select the history again and construct another stateless request. The service will generate another assistant message. The application will inspect the result and decide what happens next.

One trip at a time, the product creates a conversation.

Volume 1 has stayed close to that loop because later Claude Platform volumes will take it into tools, streaming, prompt caching, structured outputs, and managed agents.

Each feature changes part of the machinery. The boundary questions remain available.

What did the application send?

What did the service return?

What evidence determined the next action?

Review Room can answer all three. That is enough to begin building directly with Claude without mistaking a fluent answer for the complete application contract.

---
