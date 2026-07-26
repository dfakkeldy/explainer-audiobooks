# Tools Claude Can Operate

_Managed Tools, Sandboxes, and Delegated Execution_

by Dan Fakkeldy

Roughly 35,069 words.

---

## Chapter 1: Client Tools and Server Tools

The support lead has a question that sounds easy. A customer is waiting on an order from a supplier called Kestrel Components, and the delivery date has moved twice. "Have they said anything publicly?" she asks. "A notice, a status page, anything. I need to know before I call this customer back."

Project Desk cannot answer her.

That failure is a different shape from the one you spent Volume 3 solving. In that volume, Project Desk could not act. It could describe an escalation beautifully and change nothing, and the fix was a controlled loop: define a tool, read Claude's request, validate it, authorize it, run your own Python function, return the result. By the end of it Project Desk could look up a project, change a status, and write an audit entry, all under policy you wrote.

None of that helps here. Project Desk can act. What it cannot do is know. There is no local function that returns the contents of a web page that Project Desk has never seen, because the information simply is not inside the building. You could write a tool that fetches a URL, of course. You would then own an HTTP client, a redirect policy, a timeout policy, a content-type policy, a decision about what to do with JavaScript-rendered pages, and a running argument about which domains that client is allowed to reach. You would have built a small, permanent piece of infrastructure to answer one question about Kestrel Components.

Some capabilities are like that. They are not hard to imagine and they are tedious to own. And this is where a second category of tool arrives.

Anthropic provides a set of tools of its own. They appear in your request the same way your tools do, in the same list, alongside the functions you wrote yourself. But they divide into two kinds, and the division is not cosmetic. It is the fact that determines almost everything else about how a tool behaves, what it costs, how it fails, and who is answerable when it does something unfortunate.

The first kind is a **server tool**. Anthropic runs it. You put it in your request, and the work happens on Anthropic's infrastructure during that request. Web search is a server tool. So are web fetch, code execution, the tool that lets one model consult another, and the tool that searches your own tool catalogue. You do not implement them, you do not host them, and you do not return their results.

The second kind is a **client tool with a schema Anthropic wrote**. This one surprises people. Anthropic defines the shape of the tool — its name, its commands, what Claude may ask it to do — but your application still performs the work. The memory tool is like this. So are the Bash tool, the text editor tool, and the computer use tool. Claude asks; your code does it; you return the result exactly as you did in Volume 3.

So a tool can be Anthropic's in the sense that Anthropic wrote its specification, while being entirely yours in the sense that your machine runs it and your credentials are at risk. Those are different senses of "Anthropic's tool," and conflating them is the single most expensive misunderstanding you can carry into this volume.

The practical version of the distinction is a single sentence about debt. When work happens on Anthropic's side, Anthropic owes you the answer. When work happens on your side, you owe Claude the answer. Everything else — the security burden, the credential exposure, the question of what happens when the tool hangs — follows that one line.

That raises an obvious question. You are handed a response with a pile of content blocks in it. How do you tell which is which?

The answer is pleasingly small. Every tool call in a response carries an identifier. When your application is expected to run the tool, that identifier looks the way it did in Volume 3. When Anthropic ran the tool, the identifier begins with a distinct prefix. Spoken aloud it is "server tool you" — a squeezed abbreviation of server tool use, written without vowels the way engineers write things they type often. If you see that prefix, the work already happened somewhere else.

The block itself has a matching name. A call your application must handle is a tool use block, the same one you have been reading since Volume 3. A call Anthropic handled is a server tool use block. That is the name to remember: server tool use.

And the rule attached to it is absolute. You never return a result for a server tool use block. There is no tool result to send, because there is nothing you were asked to do. If you write a handler that dutifully answers every tool call it sees, it will send a result for a search Anthropic already performed, and the API will reject the request. This is one of the first errors people hit, and it comes from good instincts applied one category too broadly.

Instead, the result arrives on its own. A server tool's result block follows its call in the same assistant turn — a web search call is followed by a web search tool result, a web fetch call by a web fetch tool result, and so on. You read them. You do not produce them.

One detail about how those two blocks find each other will matter enormously in about ten chapters. The call and its result are matched by a shared identifier, instead of by their position in the list. The field is called tool use id, and it appears on the result pointing back at the call. Most of the time the two blocks sit next to each other and the distinction seems academic. Later in this book you will meet a response where the call arrives in one message and its result arrives in the next one, with other content in between, and at that point the identifier is the only thing holding the pair together. Position will lie to you. The identifier will not.

So Project Desk gains a way to answer the support lead's question. You add web search to the request, Claude decides it needs current information, Anthropic runs the search, and a result comes back with the Kestrel Components notice and a citation pointing at the page it came from. Project Desk did not write an HTTP client. It did not decide how to handle a redirect. It delegated all of that, and in exchange it gave up some control over exactly what happened, which is a trade this book will keep examining from different angles.

That is the shape of the volume. Volume 3 was about keeping control. This volume is about giving pieces of it away on purpose, and being able to say precisely which pieces went where.

The route through it runs roughly in order of how much you are handing over.

The next two chapters are about reading: searching the web, and then reading a specific document from it. Chapter 4 moves from reading to computing, in a sandbox that can run code but cannot reach anything. Chapter 5 buys judgment rather than information, by letting one model consult a stronger one mid-task. Chapter 6 deals with a problem you create by succeeding — having so many tools that Claude cannot choose among them.

Then the volume crosses back to your side of the line. Chapter 7 is memory, which will not be what you expect. Chapters 8 and 9 give Claude a shell and a file editor on your own machines. Chapter 10 goes as far as this gets: a desktop Claude can see and operate, for systems with no other way in.

The last five chapters are about what happens once you have all of it. Combining tools in a single turn turns out to have a tricky protocol, which is Chapter 11. Chapter 12 adds up what all of this costs in context instead of in fees. Chapter 13 attacks the round trip itself. Chapter 14 handles a small trade between speed and certainty. And Chapter 15 runs one real request through every boundary and writes down who owns what.

By the end, the useful thing you will have is not the list of tools. It is the ability to look at a capability you have never seen and say, within a minute or two, where its work happens, what it will cost you in context, which of its settings are real boundaries, and which decisions it should never be allowed to make alone.

One caution about the roster itself. As this book is recorded, in late July 2026, the server-executed tools are web search, web fetch, code execution, the advisor tool, tool search, and the connector for outside tool servers. The client-executed ones with Anthropic's schema are memory, Bash, text editing, and computer use. That list is a photograph, not a law. Tools get added, tools move between categories as they mature, and a tool that runs on Anthropic's side today could reasonably ship a local variant tomorrow. What will not change is the question you ask about each one, which is where the work happens and who answers for it. Learn the question rather than the list, and check the list when you actually build something.

Before you can do any of that, though, there is a smaller thing to fix in how you read a tool definition, because it will otherwise mislead you in every chapter that follows.

When you add one of these tools to a request, you name it with a type string, and most of those strings end in a date. Web search comes in a version stamped March 2025, another stamped February 2026, and another stamped March 2026. Code execution has versions stamped August 2025, January 2026, and May 2026. The dates are not decoration. They mark the moment a tool's behaviour, schema, or model support changed, and the older versions keep working so that systems built against them keep working too.

Everything about that arrangement is sensible. The problem is what your instincts do with it. A string ending in a bigger number looks like a version number, and version numbers train you to take the largest one and move on. That instinct is wrong here often enough to be dangerous, because a dated tool version is closer to an edition of a contract than to a software release. You are not upgrading a library. You are choosing which set of terms you want to operate under.

Anthropic's own documentation sorts the relationships into a handful of shapes, and knowing them saves you a lot of guessing.

Sometimes two versions are both current, and the newer one simply adds a capability. The February 2026 web search and web fetch tools added the ability to filter results with code before they reach the conversation; a March 2026 version added control over what appears in the response. All of these are live. Which one you want depends entirely on whether you need what the newer one does. Neither is the successor of the other in any meaningful sense.

Sometimes two versions are keyed to models instead of to features. The text editor tool has a version for Claude 4 and later models and an earlier one for the models before them. The version you use follows the model you are pointing at, and taking the newer one because it is newer will simply not work if your model is older.

Sometimes two versions are not versions at all. The tool search tool ships in two flavours released on the same day, one that searches with regular expressions and one that searches with natural language. They are siblings. Neither replaced the other, and picking between them is a choice about how you want searching to behave, not a choice about how modern you want to be.

And sometimes a version really is legacy. The original code execution tool ran Python and nothing else. The later ones added shell commands and file operations, and the old one is genuinely superseded.

There is one more case, and it is my favourite, because it shows how literally these strings describe a contract. Two of the code execution versions — the one stamped January 2026 and the one stamped May 2026 — run exactly the same runtime. Identical behaviour, identical sandbox. The only difference is that the newer one's description tells Claude about a ninety-second limit on each cell of code it runs, so that Claude can budget its own work accordingly. The change was not to the machine. The change was to what Claude is told about the machine, and that was considered a large enough difference to justify a new dated version.

Which is a reasonable position, once you accept that a tool definition is primarily a message to a model.

The last thing to know before you start adding these tools is that every one of them, including the ones you wrote yourself, accepts a handful of optional properties that stack. You can mark a tool as a caching boundary. You can require strict validation of its inputs. You can keep it out of the initial prompt and load it only when it is needed. You can restrict who is allowed to call it. You can give it example inputs, or turn on a faster kind of streaming for its arguments. Not all of them apply to every tool — you cannot give example inputs to a server tool, and the faster streaming is for tools you defined yourself — but they compose freely, and this book will pick them up one at a time as the chapter that needs them arrives.

One practical way to use the boundary is to run it as a question against a tool you have never seen, before you read a word of its documentation. Ask where the work happens. Then ask what that implies.

Try it on a tool this book covers much later, without knowing anything about it yet. Suppose somebody tells you Claude has a memory tool that stores information across conversations. Where does the work happen?

If Anthropic runs it, then Anthropic is storing your users' information, which means there is a data-retention conversation to have, an outage on Anthropic's side would lose your memory, and you have almost nothing to build.

If your application runs it, then the storage is yours to choose and yours to secure, nothing leaves your systems, and you have a file-handling implementation to write with all the validation that implies.

Those are wildly different projects. One is a configuration decision and one is a sprint. And you can tell which you are facing from a single fact about execution location, before you know one command name.

The same question does useful work in the other direction, on a system that has nothing to do with Claude. A payment processor that redirects your customer to its own hosted page and a payment library you install and run both let you take a card. But one of them means the card number never touches your servers, and the other means it does, along with every obligation that follows. Same capability, different execution location, entirely different compliance posture. Engineers who work with payments learn to ask that question first, and it is the same question.

That is why this chapter spends its length on one distinction rather than introducing four tools. The tools are a list you can look up. The question is what makes the list readable.

So: Project Desk can now look up Kestrel Components. It has one new reading instrument, which is the server tool prefix on an identifier, and one new reflex, which is to check whether a version string is an upgrade or a different contract entirely.

The support lead is still waiting. The next chapter actually answers her.

---

## Chapter 2: Web Search

Adding web search to Project Desk takes one entry in the tools list. You give it a type string — the March 2025 version is the plain one, and there are two newer editions this chapter will come back to — and a name, which is simply "web search." That is the whole configuration. There is no schema to write, because Anthropic wrote it, and no function to implement, because Anthropic runs it.

Then you send the support lead's question about Kestrel Components, and something happens that is easy to describe carelessly.

You did not tell Claude to search. You told Claude that searching was available.

Claude decides. It looks at the request and judges whether the answer depends on information that is current, changing, or outside what it was trained on. A question about a supplier's published delivery notice is squarely in that category, so it searches. A question about how a hash table works is not, so it answers directly. Anthropic's documentation is fairly specific about the split: recent events, current prices and scores and statistics, facts about particular organizations or people or products that might have moved, and any explicit request to look something up all trigger a search. Established facts, creative writing, brainstorming, analysis of material already sitting in the conversation, and ordinary conversational turns do not.

Most of the time that judgment is the one you want, and it is convenient not to have to make it. What you have delegated, though, goes one step further than it first appears. In Volume 3 you delegated the *proposal* of an action and kept the decision. Here you have delegated the decision to act as well. Anthropic's servers will perform searches, possibly several of them in a single turn, without asking you first.

You have two ways to influence that, and they are not equivalent.

The first is your system prompt. You can encourage Claude to search more readily, or to prefer answering from what it already knows. Anthropic describes the triggering as steerable, and it is. What it is not, is a guarantee. A system prompt is a request to a model, and a model that is fairly convinced it needs current information will sometimes go and get it.

The second is a parameter called max uses, which caps how many searches a single request may perform. That one is a real ceiling. If Claude tries to search more often than you allowed, the next result comes back as an error saying the maximum was exceeded, and the turn continues without it.

This distinction between a steer and a ceiling recurs in almost every chapter of this book, and the plain version is short: prompting changes what Claude tends to do, and a parameter changes what the system permits. When you need a number you can defend to somebody, use the parameter. Anthropic notes that simple factual questions typically take one to three searches, while comparative research across several organizations can take ten or more, which gives you a rough sense of where to set it.

So Anthropic searches, and results come back. What arrives is more interesting than a block of text.

Each search result carries the source's URL, its title, an indication of how old the page is, and one more field that will cause you trouble if you ignore it. That field holds the result's content in encrypted form. You cannot read it. It is not meant for you.

It is meant for the next turn.

When the conversation continues — the support lead asks a follow-up, and Project Desk sends the history back — the API needs the search results restored into Claude's context. It does that by decrypting the content you hand back. Which means you must hand it back, exactly as you received it, unaltered. Send the assistant's content blocks through untouched. If that encrypted field is missing, or if something in your pipeline has helpfully normalized it, the request fails with a validation error.

This is the sort of rule that gets broken by good code. An application that parses responses into its own tidy internal objects, stores what it considers the useful parts, and reconstructs the history later will drop the encrypted content without noticing, because nothing about it looks useful. Then multi-turn conversations break while single-turn conversations work perfectly, which is a miserable thing to debug. The fix is a habit, not a technique: for any assistant turn that contains server tool results, keep the original blocks and replay them verbatim. Store your tidy version alongside it if you like, but the thing you send back is the thing you got.

Citations come with the same turn, and they work differently from anything you have configured so far, because you cannot turn them off. Web search citations are always enabled. Every claim Claude draws from a search result carries a reference back to the source: the URL, the title, a short quotation of up to about a hundred and fifty characters, and an index that, like the encrypted content, must be passed back on later turns.

Anthropic is explicit about why that matters beyond mechanics. When you show these outputs to end users, the citations are expected to go with them. If you are reprocessing or recombining the output with your own material, the guidance is to work out the right citation behaviour with your own legal advice rather than assume. For Project Desk this is straightforward and rather welcome: the support lead gets an answer with the Kestrel Components notice linked, so she can look at the page herself before she picks up the phone.

There is a small piece of good news in the accounting. The citation's quoted text, title, and URL do not count toward your input or output tokens. The underlying search results absolutely do, but the citation apparatus itself is free.

There are two ways this goes wrong, and the first one is a genuine trap.

When a search fails — a rate limit, a query that was too long, a malformed parameter, an internal problem on Anthropic's side — the API does not return an error status. It returns a perfectly ordinary successful response, with the failure described inside the body, in the place where the search results would have been.

Two hundred does not mean it worked.

This is the correct design, once you think about it from Claude's side. A failed search is not a failed request. Claude asked for something, did not get it, and can still carry on and answer as best it can, or try a different query. Failing the whole request would throw away a turn's worth of useful work over one unavailable service. But it does mean that an application which checks only the HTTP status will believe every search succeeded, forever.

So Project Desk reads inside the result. The error codes it might find are worth knowing by name, because they tell you different things to do. A too-many-requests error means you hit a rate limit and should back off. A max-uses-exceeded error means your own ceiling stopped it, which is not a fault at all. A query-too-long error and an invalid-tool-input error point at the query Claude constructed. A request-too-large error usually means something else entirely: a very long list of domain restrictions has made the search request itself too big. And an unavailable error means Anthropic had an internal problem.

One more distinction, because it catches people. A search that runs correctly and simply finds nothing is not an error. It returns an empty list of results. If your handler treats "no results" as a failure, Project Desk will report a supplier outage every time a supplier has genuinely published nothing.

The second cost is money, and web search is one of the tools that charges for itself on top of tokens.

As of this recording, in late July 2026, web search on the Claude API costs ten US dollars per thousand searches. That is separate from, and in addition to, the ordinary token cost of everything the search brings back — and the search results do count as input tokens, both during the turn where they arrive and on every later turn where they are still in the conversation.

Two details make that number more useful than it looks. Each search counts as one use no matter how many results it returns, so a search that finds twelve relevant pages costs the same as one that finds two. And a search that errors is not billed, which means the rate limits and outages that produce those in-body errors are at least free.

Price is exactly the sort of fact that will be wrong before this recording is old, so treat the number as a dated example and the shape as the durable part. The shape is this: web search has a per-use fee, so the cost of a search-heavy request grows with how many times Claude decides to look, which is a decision you influence with a prompt and bound with a parameter. That relationship will hold long after ten dollars per thousand stops being the figure.

There is one more capability in the newer versions, and this chapter will deliberately only sketch it, because it belongs to a tool you have not met yet.

With the plain March 2025 web search, every result Anthropic finds is loaded into Claude's context window. All of it. If Claude runs eight searches to compare suppliers, the conversation carries eight searches' worth of web pages, most of which turned out to be irrelevant. You pay tokens for the irrelevant parts, and they crowd the space Claude needs for reasoning.

The February 2026 version changed that. With it, Claude can write and run code that filters the search results before they reach the context window, keeping what is relevant and discarding the rest. Anthropic calls this dynamic filtering, and the point of it is straightforwardly economic: fewer tokens for the same answer on search-heavy work.

The reason this chapter will not explain how it works is that it works by running code in a sandbox, which is the subject of Chapter 4. What matters here is that a version of web search exists whose behaviour depends on another tool entirely, that Anthropic provisions that other tool for you automatically so you do not add it yourself, and that this arrangement has consequences — for data retention, for which models can use it, and for which clouds it runs on — that Chapter 12 will collect and settle.

The March 2026 version adds one more control, over whether the raw search content is echoed back to you in the response at all, which matters when an agent is working in a loop and nobody needs to see the pages. Also Chapter 12.

Two smaller parameters exist, and one of them matters more than its size suggests.

You can localize results by supplying an approximate location — some combination of city, region, a two-letter country code, and a timezone identifier. It changes what the search returns, which for anything involving availability, pricing, regulation, or shipping is not a cosmetic difference. A search about component availability run from an unspecified location and the same search run from Nova Scotia can surface different suppliers, and neither result is wrong.

That is a small illustration of a general problem with delegated retrieval. The search happened somewhere, on somebody's infrastructure, with defaults you did not set. If where it happened affects the answer, and you did not say where, then you have accepted a default you never chose. That is worth a moment's thought for any application whose users are not all in one place.

The other parameter is a set of domain filters, which web search shares with web fetch. The next chapter handles them properly, because that is the chapter where they matter most.

Batches deserve one sentence, because there is a constraint on them specific to this tool. Web search works in a batch, and calls through the batch interface are priced the same as ordinary ones — but to protect shared capacity, Anthropic throttles web search requests per organization, so a large batch with many searches can take longer to complete than the arithmetic suggests. Your organization's limit is visible in the Console. A nightly job that searches for two thousand suppliers is not two thousand searches' worth of time.

For now, Project Desk answers the support lead. Kestrel Components published a notice on its own site four days ago acknowledging a component shortage and naming a revised shipping window. Project Desk found it, quoted the relevant sentence, and linked the page. She reads the quotation, clicks through to check it herself, and calls the customer back with something she can defend.

The next question she asks is harder, and it is the one that breaks this tool. She wants to know what the notice actually commits them to — not the summary, the terms.

---

## Chapter 3: Web Fetch

The support lead's follow-up is the reasonable next question, and web search cannot answer it. She does not want to know that Kestrel Components published a notice. She wants to know what the notice actually says — the full text, the conditions, whatever it commits them to about the revised shipping window. A hundred and fifty characters of quoted snippet is not a contract term.

What she is asking for is the document.

Web fetch is the tool that reads one. You give Project Desk the tool, Claude identifies the page, and Anthropic retrieves the full text and puts it into the conversation. It handles ordinary web pages and PDF documents, which covers most of what a support team ever needs to read. For a PDF it returns the content the same way a directly attached PDF would arrive, so Claude reads it as a document instead of as scraped text.

There is one category it does not handle, and it is worth knowing before you build on it: pages that assemble themselves in the browser with JavaScript. If the content only exists after a script runs, web fetch will not see it. Plenty of modern sites are built exactly that way, so this is a real limitation rather than a footnote. A supplier's static notice page will be fine. A supplier's single-page application dashboard will not.

Web fetch is a server tool, so the mechanics you learned in Chapter 1 apply unchanged. Anthropic performs the retrieval during your request, the result arrives in the same turn as a web fetch tool result block, and Project Desk returns nothing. There is one exception involving your own tools appearing in the same turn, and Chapter 11 is entirely about it.

What makes this tool different from every other one in the volume is a rule about where it is allowed to go.

Web fetch can only retrieve a URL that has already appeared in the conversation.

Not any URL. Not a URL Claude constructs. A URL that was already there — in a message you sent, in the result of one of your own client tools, or in the results of an earlier web search or web fetch. Anything else is refused, with an error saying the URL was not in the prior context.

The first time you meet that restriction it can feel arbitrary, even obstructive. You have a tool that reads web pages and it will not read the web page you just thought of. The reasoning becomes clear the moment you invert the question and ask what a URL is, from a security standpoint.

A URL is not only a destination. It is also a message. Everything after the question mark in a web address is data you are handing to whoever owns that server. So a tool that can fetch a URL Claude invented is a tool that can send information out of your system, encoded in an address, to a destination Claude chose. If Project Desk is holding a customer's account details in one part of the conversation and reading an untrusted web page in another, that is a channel.

Anthropic states this risk directly instead of burying it, and the wording is notably unsoftened: enabling web fetch in environments where Claude processes untrusted input alongside sensitive data poses data exfiltration risks. The prior-context rule is named as the mitigation — Claude is not allowed to dynamically construct URLs — and then, importantly, the documentation says the residual risk should still be carefully considered. It does not claim the problem is solved.

That is the right posture, and it is a good habit to copy when you write your own tools. A control that reduces a risk is not the same as a control that removes it, and saying so plainly is more useful than reassurance.

So what do you actually do about it? Three levers, and they work at different places.

The first is simply not enabling the tool where it does not belong. Anthropic lists that first, and it deserves to be. Project Desk probably wants web fetch in the workflow where a support agent researches a supplier, and probably does not want it in the workflow that processes payment disputes.

The second is a cap on how many fetches a request may perform, the same max uses parameter you met with search. There is currently no default limit at all, which means an unbounded number until you say otherwise. Failed fetches count against the cap too, so a site that keeps timing out will consume your allowance without returning anything.

The third is domain filtering, and this is the substantial one, because it lets you say where Project Desk is permitted to look.

You provide either a list of allowed domains or a list of blocked domains. Not both. A request carrying both lists is rejected outright. Entries are bare domains without the protocol on the front — "kestrelcomponents.com," not the version with the slashes — and subdomains come along automatically, so allowing the bare domain also allows the documentation subdomain and the status subdomain underneath it. Naming a specific subdomain narrows things instead: allow the status subdomain alone and results come only from there, not from the parent domain or its siblings.

There is an asymmetry between the two web tools here that will bite somebody eventually. Web search lets you include a path, so you can allow a domain's blog section and match everything beneath it. Web fetch matches on the domain only, which means an entry that includes a path will simply never match a fetch URL. The same list, written once and used for both tools, behaves differently in each.

Wildcards follow one rule: they are allowed in the path and never in the domain itself. You can write a domain followed by a wildcard path. You cannot write a wildcard in front of a domain to mean "any subdomain," which is precisely the thing most people try first, because that is how such patterns work almost everywhere else. Invalid formats are rejected when you send the request rather than failing quietly later, which is the kindest possible version of that mistake.

Now for the attack, because there is one, and it is the sort of thing that sounds theoretical until you see it written down.

Domain names can be written with characters from alphabets other than Latin. A Cyrillic letter can be shaped identically to a Latin one. So a domain that renders on screen as "amazon.com" can be a completely different domain from amazon.com, differing only in one character that looks the same to a human reader. Anthropic names this — a homograph attack — and gives the mitigation: keep allow and block lists to ASCII characters only, and audit any existing list for non-ASCII entries that may already be in it.

The general lesson underneath that is larger than one tool's parameter. Your allowed-domain list is a security control you verify by reading it. If two entries can look identical and behave differently, reading is not verification, and the control needs a check that does not depend on your eyes.

There is one more layer above all of this, and it is easy to forget because it lives somewhere else entirely. Your organization can configure domain restrictions in the Claude Console, and those interact with what you send per request in an asymmetric way worth remembering. A request-level allowed list must be a subset of the organization-level list; if you allow a domain your organization has not allowed, you get a validation error and know about it immediately. But a domain your organization has explicitly blocked is silently removed from your request-level allowed list. No error. It is simply not there.

So the same misconfiguration produces a loud failure in one direction and a quiet one in the other. If Project Desk seems to be ignoring a domain you are certain you allowed, that quiet removal is the first thing to check, and nothing in your own code will tell you.

Two smaller controls, and then the part about money.

Citations, which were mandatory for web search, are optional here and switched off by default. If you want Claude to cite passages from a fetched document, you enable them. The same guidance about showing citations to end users applies when you do.

And results are cached. The content that comes back may not be the newest version at that address, because the caching is managed automatically and Anthropic notes it may change over time to suit different content types. A parameter added in the March 2026 version lets you bypass the cache and force a fresh retrieval, and the advice about it is admirably specific: only do that when the user explicitly asked for fresh content or when the source changes fast, because skipping the cache costs latency.

For Project Desk this is a real decision rather than a default to accept. A supplier's terms page from an hour ago is fine. A supplier's live inventory count from an hour ago is a lie that Project Desk will state confidently.

Now, the cost, and this is where web fetch teaches something the price list cannot.

Web fetch has no fee. Nothing per use, nothing per document. It is free.

It is also, quite easily, the most expensive tool in this volume.

Because you pay tokens for everything it brings back, and documents are large. Anthropic's own figures make the shape clear: an average web page of about ten kilobytes comes to roughly two and a half thousand tokens. A large documentation page of a hundred kilobytes comes to about twenty-five thousand. A research paper PDF of five hundred kilobytes comes to about a hundred and twenty-five thousand tokens.

Set that beside the previous chapter. Web search charges ten dollars per thousand searches, which sounds like the expensive one. But a single fetched research paper can consume more of your context window — and more tokens, on this turn and every subsequent turn where it stays in the conversation — than a great many searches would. The tool with a price tag is not the tool with the cost.

The lever for this is a parameter that caps how much fetched content enters the context, and two things about it are worth precision. The limit is approximate, so actual token use can vary a little around it. And it applies to text content only, not to binary content like PDFs — which is unfortunate, because PDFs are exactly where the frightening numbers live.

So "free" stops meaning "cheap," and that reframing is the durable lesson of this chapter. Every tool in this book has two prices: what it charges, and what it puts into your context window. They are not correlated, and the second one is usually larger. Chapter 12 collects all of these into a single budget you can reason about, which is a more useful thing to own than a memorized fee table.

The error codes for this tool are worth a pass, because unlike most error lists they map almost one-to-one onto decisions.

Two of them tell you the tool refused instead of failed. A not-in-prior-context error means the URL was never in the conversation, which is the rule from earlier in this chapter working as designed. A not-allowed error means the URL was blocked — by your domain rules, by your organization's, or by Anthropic's own restrictions on private network addresses and on sites whose robots file declines automated access. Neither is a fault. Both mean a policy applied.

Two tell you the request was malformed. A too-long error means the URL exceeded two hundred and fifty characters. An invalid-input error means it was malformed or used a scheme other than web addresses.

And two tell you the fetch genuinely did not work. A not-accessible error means the site returned an HTTP error. An unsupported-content-type error means the page was something other than text, HTML, or PDF — a video, an archive, a spreadsheet.

That last one produces a specific and avoidable disappointment. A supplier who publishes their terms as a Word document rather than a PDF cannot be read by this tool at all, and the failure looks like a content type instead of like a missing capability.

A second use case, away from Project Desk entirely, shows what this tool is really for. A compliance team tracking regulatory guidance needs to know what a published standard actually says, not what a summary of it says, and needs to know when the wording changes. Search finds the page; fetch reads the clause; the citation records which version was read on which date. The token cost of reading a long standard is real, and it is dramatically less than the cost of acting on a paraphrase of it.

That pairing — search to locate, fetch to read, citation to record — is a durable shape, and it is the shape the rest of this section describes.

One last capability, because it is the first genuine composition in the book and it happens without you asking.

When Project Desk has both web search and web fetch enabled, and the support lead names a document without giving a URL — read Kestrel's returns policy, look at their published terms — Claude does something sensible. It searches to find the page, then fetches the page it found. The search result supplies the URL, which satisfies the prior-context rule, and the fetch reads the document.

Two tools, one request, no orchestration from you. Claude searched, chose the most promising result, retrieved the full content, and answered from the document rather than from the snippet.

Project Desk now reads the actual terms. The revised shipping window turns out to be conditional on a component arriving from Kestrel's own supplier, which is a fact the support lead needs and the search snippet never contained.

It also means the conversation is now carrying a full terms document, which is about eleven thousand tokens of legal text that Project Desk will pay for on every remaining turn. The next chapter is about doing something smarter with a large document than putting all of it in front of the model.

---

## Chapter 4: Code Execution

A different request arrives, and it is the kind that makes the previous two chapters look cheap.

Operations has a spreadsheet of delivery exceptions — every order in the last quarter that shipped late, short, or damaged. It is about four thousand rows. They want to know which suppliers are responsible for the pattern, and whether Kestrel Components is unusually bad or merely the one everybody happens to be annoyed about this week.

Project Desk could put the spreadsheet in front of Claude. Four thousand rows of order data is perhaps a hundred and fifty thousand tokens, which may not even fit, and if it fits it will crowd out everything else and cost real money on every turn afterwards. Claude would then have to do arithmetic across four thousand rows by reading them, which is exactly the sort of work a language model does adequately and a pocket calculator does perfectly.

The answer is not to show Claude the data. The answer is to give Claude somewhere to compute.

Code execution is a server tool that provides a sandboxed container where Claude can run shell commands and create, view, and edit files. You add one entry to your tools list — a type string and the name "code execution" — and no other configuration. Both fields are fixed. There is nothing to tune.

Providing that one tool quietly gives Claude two sub-tools, not one. There is a Bash sub-tool for running shell commands, and a text editor sub-tool for viewing, creating, and editing files. Claude uses them in combination: it writes a Python script with the editor, then runs it with the shell. Their results come back as separate block types, so a response reads as an interleaving of the commands Claude ran and what each one produced, followed by Claude's own explanation.

For the delivery exceptions, that means Project Desk uploads the spreadsheet, Claude writes a dozen lines of pandas, runs it, gets a summary table of exceptions per supplier with rates and severities, and reasons about *that*. Perhaps forty lines of output rather than four thousand rows. The data never enters the conversation. Only the conclusion does.

That is a good moment to close a loop opened two chapters ago.

The dynamic filtering that the February 2026 web search and web fetch tools offer — the thing that filters results before they reach the context window — is this tool doing the work. Claude writes code that filters the search results inside the container, and only what survives comes back. You did not add code execution to those requests, and you do not need to: when dynamic filtering runs, Anthropic provisions the code execution it requires for that request automatically, and both web tools share a single container. There is no extra charge for code execution used that way beyond the ordinary token cost.

So the feature you met as a line item in Chapter 2 was this chapter's tool wearing a different name. That is a pattern worth expecting on this platform: capabilities compose underneath the surface, and a tool you never enabled can still be running on your behalf.

Now, the container itself, which is defined at least as much by its refusals as by its capabilities.

It runs Python 3.11 on Linux, on an x86 architecture, with five gibibytes of memory, five gibibytes of disk for the workspace, and one CPU. Those numbers are generous for data work and modest for anything else, and they are the numbers as of this recording.

The refusal that matters most is this: the container has no internet access at all. Not restricted access. None. No outbound network requests are permitted.

That single fact explains almost everything else about how the tool behaves. It is why the container ships with a substantial library set preinstalled — pandas, numpy, scipy, scikit-learn, statsmodels for analysis; matplotlib and seaborn for charts; a long list of file-processing libraries for Excel, PDFs, images, and Word documents; and command-line tools including ripgrep, fd, sqlite, and the usual archive utilities. It is also why that list is the whole world. Claude cannot install a package it needs, because nothing can be downloaded. If your analysis requires a library that is not on the shelf, the analysis does not happen in this container.

That is a constraint you can plan around once you know it, and a baffling failure if you do not. Claude will sometimes try, discover it cannot, and work around the gap with what is available — which is usually the right behaviour and occasionally produces a solution more roundabout than you would have written.

The isolation goes further than the network. The sandbox is fully isolated from the host and from other containers, file access is limited to the workspace directory, and containers are scoped to the workspace of the API key that created them. It is a sealed room, and the seal is the security property.

Containers also have a lifetime, and the arithmetic here is worth getting right because two different numbers are in play.

Every request gets a new container unless you say otherwise. If you want to keep the files Claude created — and for multi-step analysis you usually do — you take the container's identifier from the response and pass it back on the next request. Files persist. With the January 2026 version or later, the Python interpreter's own state persists too, so variables Claude bound in one request are still bound in the next.

The two numbers are these. A container is checkpointed after roughly five minutes of inactivity, and a request that names it inside a thirty-day window restores it. Thirty days is the outer bound: no container can be reused more than thirty days after it was created. There is also a timestamp in the response telling you when the container expires, and it is a shorter rolling value that does not report the thirty-day limit, so do not read it as the whole story.

An expired container cannot be brought back. A request that references one gets an error, not a fresh container, and the fix is to send the request again without naming a container at all, which gets you a new one.

Two notes on the surrounding documentation, because they disagree slightly in emphasis and it is better to know that than to memorize either phrasing. One page describes containers as checkpointed after about five minutes and restorable within thirty days. Another describes idle containers as reclaimed after about five minutes. Those are consistent in substance — short idle window, thirty-day outer bound — but the second sounds more final than the first. Treat the durable shape as the fact and neither exact sentence as a guarantee.

Now the bill, which has an unusual shape and one genuinely surprising clause.

Code execution is free when it accompanies the current web search or web fetch tools. If your request includes the February 2026 or later version of either, there is no charge for code execution in that request beyond ordinary tokens, and that covers both the filtering that happens automatically and any code Claude runs directly. So the research workflow from the last two chapters gets a sandbox thrown in.

Used on its own, code execution is billed by execution time rather than by tokens. There is a five-minute minimum per invocation. Each organization gets one thousand five hundred and fifty free hours a month, and beyond that it is five cents per hour per container. For most applications, that free allowance is the entire story and the meter never becomes relevant.

The surprising clause is this: if files are included in the request, execution time is billed even when the tool is never called. The reason is mechanical — files are preloaded onto the container, so the container exists whether or not Claude decides to use it.

That produces a specific piece of advice. If Project Desk attaches a spreadsheet to a request on the chance that Claude might want it, Project Desk is paying for a container regardless. Attaching files speculatively is not free, and the five-minute minimum means a request that touches nothing still costs five minutes.

The last thing in this chapter is a failure mode, not a feature, and it is the one that generates the most confusing bug reports.

Suppose Project Desk offers Claude both this sandbox and a shell tool of its own — the client-side Bash tool that Chapter 8 covers, running on Project Desk's own machine. Claude now has two execution environments. One is Anthropic's sealed container. The other is a real machine that Project Desk controls, with Project Desk's files and Project Desk's network access.

They share nothing. Not the filesystem, not the environment variables, not the working directory, not the Python state. A file Claude wrote in the sandbox is not on your machine, and a file on your machine is not in the sandbox.

Anthropic's documentation says plainly that Claude can sometimes confuse these environments, attempting to use the wrong tool or assuming state is shared. And when it does, the symptom is bewildering: Claude writes a file, then cannot find it; runs a script that worked a moment ago against data that has vanished; reports that a directory is empty when you can see the files in it yourself.

The recommended fix is not a parameter. It is a sentence or two in your system prompt that tells Claude the two environments exist, which is which, and that state does not travel between them. That is unusually low-tech for a platform problem, and it works because the confusion is a modelling problem rather than a plumbing one — Claude cannot distinguish them from the tool definitions alone, so you say it out loud.

There is a trap folded inside this, and it is the reason this failure is more common than it sounds. Web search and web fetch enable code execution automatically. So an application that offers a client-side shell tool and also does web research has two execution environments whether or not anybody decided to have two. Nobody added code execution. It arrived with the search tool, and now Claude has a sandbox it was not told about sitting alongside the shell it was.

For Project Desk, the practical shape is a short paragraph in the system prompt naming both environments, written once, kept there permanently. It costs a few dozen tokens and prevents an afternoon of debugging.

Getting your own data in, and Claude's output back, works through a separate service for files, and this chapter will name the shape without teaching it, because that service belongs to Volume 5.

The pattern is: upload a file, reference it in your message, include the code execution tool, and the container can read it. The environment handles the formats you would expect — spreadsheets in both common formats, delimited text, structured data files, images, and plain text. Coming back the other way, when Claude creates a file during execution, the file's identifier appears in the tool result and you download it afterwards.

Which is how the exceptions chart reaches a human. Claude drew it inside the container, the result named it, and Project Desk fetched it and attached it to the operations email. The chart was never in the conversation either. Only its identifier was.

There is a retention fact attached that belongs with the money instead of with the mechanics. Container data — execution artifacts, uploaded files, outputs — is retained for up to thirty days, and files created through the file service persist until something explicitly deletes them. So a container that expires is not the same as data that is gone, and an application that generates a chart per request is accumulating charts somewhere until it decides not to.

A second use case, well away from supplier data, shows the shape of what this tool is for. A research team receives quarterly submissions as a few hundred spreadsheets in inconsistent formats. The work is to normalize them, find the outliers, and produce one summary. Doing that by putting spreadsheets in front of a model is expensive and error-prone; doing it by writing a normalizer by hand takes a week and breaks when the format shifts again. Doing it in a sandbox, where Claude writes the normalizer, runs it, reads the errors, and adjusts, is a different kind of task altogether — and the several hundred spreadsheets never enter the conversation.

The common thread with the delivery exceptions is that the data is large, the answer is small, and the transformation between them is code. When those three things are true, the sandbox is almost always the right instrument.

Operations gets its answer. Kestrel Components accounts for a bit under a fifth of the exceptions on about a twelfth of the order volume, which is disproportionate, and the exceptions cluster in a single component category rather than spreading evenly — which is the detail that makes the earlier terms document suddenly relevant. The pattern and the published notice describe the same shortage.

None of the four thousand rows entered the conversation. What entered was a summary Claude computed, and a chart Claude drew, which came back as a file Project Desk can download and put in front of a human.

That is three tools now, and Claude has been choosing among them competently without much help. The next chapter is about a request where competent tool selection is not the problem, because the work is not hard — it is just long, and somebody needs a plan.

---

## Chapter 5: The Advisor Tool

Project Desk has a job that will take a while.

The exceptions analysis was convincing enough that operations wants the supplier records restructured — component categories normalized, exception codes mapped to a new scheme, historical orders backfilled so the quarterly comparison actually compares like with like. It is perhaps two hundred small edits across a dozen files, and none of them is difficult. There is no clever algorithm here. There is a lot of careful, repetitive work, and one decision at the beginning about what order to do it in that determines whether the whole thing goes smoothly or turns into four hours of untangling.

That shape — mostly mechanical, with the quality concentrated in a plan made early — is extremely common in agentic work, and it creates an awkward economic problem.

Run all of it on a fast, cheap model and you get two hundred competent edits executed in a poor order, and you pay for the untangling. If you run it on your strongest model, you get an excellent plan and then pay premium rates for two hundred edits that a cheaper model would have done identically. Neither choice is obviously right, and the reason is that you are being asked to buy one thing — intelligence — when what you actually want is intelligence in one place and throughput everywhere else.

The advisor tool splits those apart.

You run your task on a fast model, called the executor. You give it a tool whose only function is to consult a stronger model, called the advisor, in the middle of generating. The advisor reads everything that has happened so far, produces a plan or a course correction, and hands it back. The executor keeps going, now better informed, still generating at its own cheaper rate.

Anthropic frames the fit narrowly, which is useful. It suits long-horizon agentic workloads — coding agents, computer use, multistep research — where most turns are mechanical but having a good plan matters a great deal. It fits poorly for single-turn question answering, because there is nothing to plan; for pass-through model pickers where your users already chose their own cost and quality tradeoff; and for work where every turn needs the larger model's full capability.

The tool is in beta as of this recording, which means requests that use it carry a beta header — a string naming the advisor tool and the date March the first, 2026. Two versions of the configuration guidance exist for different executor models, and this chapter will get to why that matters.

Adding it takes three fields, not two. A type string, the name "advisor," and — this one is new — the model you want the advisor to be. That model is billed at its own rates for its own work, which is a sentence to remember for later in this chapter.

Now, how the consultation actually happens, because there is a detail here that is genuinely striking once you see it.

When the executor decides to consult, it emits a server tool use block with the name "advisor" and an input that is completely empty.

Empty. No question. No summary of the difficulty. Nothing.

The executor signals *timing* and nothing else. The server supplies the context. Anthropic then runs a separate inference pass on the advisor model, and the advisor receives the executor's full transcript as quoted context — your system prompt, the tool definitions, the prior turns and their tool results, and the text the executor has produced so far in this turn. All of it.

So the executor is not asking a question. It is raising its hand and saying "look at this." Whatever it might have wanted to put in the input would not have reached the advisor anyway.

That design choice is worth understanding rather than just memorizing, because it determines what the tool is good at. A model summarizing its own difficulty is a model deciding in advance what the problem is, and a stuck model is frequently stuck precisely because its framing of the problem is wrong. Handing over the raw transcript lets the advisor form its own view. The cost is that the advisor's input is large, which is a cost this chapter will return to twice.

The advisor runs without tools and without context management. It cannot search, cannot execute code, cannot consult anything. It reads and it advises. Its thinking blocks are discarded before the result comes back, so only the advice itself reaches the executor.

All of this happens inside one request to the Messages API. There are no extra round trips on your side, unless the turn pauses mid-consultation, which Chapter 11 handles along with every other kind of pause.

The result arrives as an advisor tool result block, and its content comes in one of two shapes depending on which model you chose as the advisor.

Some advisor models return the advice as plain text you can read. Others return it encrypted — an opaque value your client cannot open. As of this recording, the Opus 5, Fable 5, and Mythos 5 advisors return the encrypted form; several earlier models return plain text, which makes them useful for development when you want to see what the advisor actually said.

In both cases the rule is identical: round-trip the content verbatim on later turns. The executor's prompt always contains the plaintext advice regardless of which form your client received, because the server decrypts it on the way in. So caching and behaviour are the same either way. What differs is only whether you can read it.

If you switch advisor models mid-conversation, you will get both shapes in one history, so code that handles this should branch on the content's type instead of assuming.

There is a compliance-flavoured consequence here. With an encrypted advisor, your application is carrying, storing, and replaying a message it cannot inspect, which influenced work it is accountable for. That is a perfectly reasonable arrangement, and it is also the sort of thing worth knowing before someone asks you to produce an audit trail of why the system did what it did. The advice is in your logs. It is just not legible.

Failures here behave gently, and the design is considerate.

If the advisor call fails, the executor sees the error and carries on without further advice. The request does not fail. The error codes cover the situations you would expect: your own per-request cap was reached, the advisor sub-inference was rate-limited, it hit capacity limits, the transcript exceeded the advisor model's context window, it timed out, or something else went wrong.

One asymmetry in that is worth holding onto. Advisor rate limits draw from the same per-model bucket as direct calls to that model. A rate limit on the *advisor* appears as an error inside the tool result, and the turn continues. A rate limit on the *executor* fails the whole request with an HTTP 429. Same underlying condition, two completely different consequences, depending on which model ran out of room.

That means a Project Desk that is already hammering a model directly can find that its advisor consultations quietly stop working, while every request still appears to succeed. The work degrades to executor-only quality with no signal except a code buried in a result block.

Now the money, and this is the part where an obvious implementation gets it wrong.

The advisor's tokens are billed at the advisor model's rates, not the executor's. That is the point of the arrangement. But they are also reported in a different place. Usage comes back with an iterations array, one entry per inference pass, and the advisor's entries are marked as advisor messages while the executor's are marked as ordinary ones. Top-level usage reflects executor tokens only.

Advisor tokens are not rolled into the top-level totals, because they are billed at a different rate and summing them would produce a number that means nothing.

So cost-tracking code that reads top-level usage — which is to say, almost all cost-tracking code, because that is where usage has always been — will undercount every request that consulted an advisor. It will not error. It will simply be wrong, quietly, in the direction of "cheaper than reality."

The aggregation rules inside that array have their own quirk. Top-level output tokens is the sum of all executor iterations. Top-level input tokens and cached read tokens reflect the *first* executor iteration only, because later iterations' inputs include earlier outputs and re-summing them would double-count. If you are building real cost tracking, read the iterations array and do your own arithmetic.

Then there is the size of what the advisor produces, and here the default is expensive.

The top-level max tokens on your request bounds executor output. It does not bound the advisor at all. To cap the advisor you set a max tokens on the tool definition, with a minimum of one thousand and twenty-four.

Anthropic's recommended starting point is two thousand and forty-eight, and the reported effect is large: on a hard reasoning benchmark, that cap cut mean advisor output by roughly a factor of seven, with close to no truncation and no detectable quality loss. The minimum of one thousand and twenty-four cut output by about a factor of ten but truncated around one call in ten.

Two caveats belong with those numbers, and they come from Anthropic's own documentation rather than from caution on my part. The sample was forty runs per configuration, and the accuracy differences across configurations were within noise at that size. And hard reasoning tasks produce much longer advisor output than lighter work, so those figures size the *savings ratio* instead of establishing a baseline. Anthropic says to validate on your own workload, which is the correct advice and also the advice everybody skips.

The cap is not a blunt truncation either. The server passes the advisor its remaining token budget, so the advisor shapes its response to fit. When it does hit the cap, the result block carries a stop reason saying so, and a note naming your cap is appended to the advice text so the executor can see that the guidance it received was cut short.

There is a second caching layer specific to this tool, and one sentence explains when to bother. The advisor's prompt on each call is the previous call's prompt with one more segment appended, so the prefix is stable and cacheable. You enable it with a caching object on the tool definition, which — unlike the cache breakpoints you may have met elsewhere — is an on-off switch rather than a marker; the server decides where the boundaries go. Anthropic's guidance is that the cache write costs more than the reads save at two or fewer advisor calls per conversation, breaks even around three, and improves from there. Long agent loops want it on. Short tasks want it off. Set it once and leave it, because toggling it mid-conversation causes misses.

Finally, a behavioural finding that is unusual to see published, and which should change what you do.

Executors under-call the advisor in some domains, particularly coding. Anthropic tested adding a short reminder as an extra user message early in the conversation if the executor has not consulted yet. On Haiku executors this raised task pass rates by roughly seven percentage points. On Sonnet executors it had no measurable effect. On Opus executors it slightly *lowered* pass rates, and the guidance is explicit: do not apply it to Opus.

The same intervention, three different signs depending on the model underneath.

There is a subtler warning attached. The reminder is highly salient — in Anthropic's testing, between roughly three-quarters and nearly all of nudged Haiku and Sonnet attempts consulted the advisor immediately. If that lands before the executor has read the problem or gathered any context, the resulting consultation is low-context and may displace a better-timed one later. On workloads where the executor's natural first call came around turn seven, a turn-two nudge correlated with a three to four point performance *drop*.

The instruction that follows from all of that is not "add the nudge." It is "measure when your executor naturally consults, then decide." Which is a less satisfying takeaway than a configuration snippet, and a considerably more useful one.

Two more pieces of published guidance are specific enough to act on, and both are about output length instead of timing.

The first is a prompting technique with an unusual justification. The advisor sees your system prompt and your user messages as quoted context describing the executor's task — which means an instruction addressed *to the advisor*, in the second person, is followed far more reliably than a third-person description of what the advisor should do. Anthropic found the most effective placement to be a line in the user message, prefixed programmatically by an agent framework before the request goes out. Ask for roughly eighty percent of your true ceiling, because the limit is a soft constraint the advisor occasionally exceeds.

There is a counterintuitive side effect. In Anthropic's testing that same line also increased how often the executor consulted the advisor — more consultations, each shorter — and the net effect was still lower total cost.

The second is that the advisor composes with everything else. It goes in the same tools array as your own tools, as web search, as code execution. The executor can search, consult, and call your tools in one turn, and the advisor's plan can inform which tool the executor reaches for next. Anthropic notes one refinement for agents that expose planner-like tools of their own — a task list, say: prompt the model to consult the advisor *before* those tools, so the plan funnels into them rather than competing with them.

A use case outside Project Desk shows the fit more clearly than a restructuring job does. A support-triage agent handles a few thousand tickets a day. Almost all of that work is mechanical classification a cheap model does perfectly. A small number of tickets are ambiguous — a customer describing two problems as one, or a complaint whose real subject is a policy, not a product. Running every ticket on a strong model to catch that minority is expensive; running none of them on a strong model means the minority gets misrouted. An advisor consulted only on the ambiguous ones is exactly the shape of that problem.

That is the general test for this tool, and it is narrower than "make the model smarter." The advisor earns its cost when the *distribution* of difficulty is uneven and the model can tell which end of the distribution it is looking at. Uniformly hard work should just use the better model. Uniformly easy work does not need advice.

Project Desk's restructuring job runs on a fast executor with a strong advisor, capped at two thousand tokens, caching on because the loop is long. The advisor is consulted twice: once near the beginning, after the executor has read a few files and can describe the actual shape of the data, and once near the end when a backfill produces a result that does not reconcile. The first consultation produces the ordering. The second catches a mapping error that would have propagated through the historical comparison.

Two hundred edits at executor rates. Two consultations at advisor rates. And an invoice that Project Desk's cost dashboard reports correctly, because somebody read the iterations array.

The next problem is not about any single tool. It is that Project Desk now has rather a lot of them.

---

## Chapter 6: Tool Search

Project Desk has been growing, and nobody planned for the way it would fail.

It started with three tools: look up a project, update a status, write an audit entry. Then the supplier work added tools for orders, shipments, and exception codes. Then the restructuring added tools for the component taxonomy. Then someone connected the ticketing system, and someone else connected the warehouse, and now Project Desk offers Claude something like forty tools.

Nothing is broken. That is what makes the problem hard to spot. Requests still succeed, answers still come back, and the support lead has not complained. But two things have quietly gone wrong, and they are separate problems that happen to have the same cause.

The first is that Project Desk is now paying a substantial bill before any work begins.

Every tool definition travels in the request, and every definition Claude can see occupies space in the context window. Names, descriptions, argument names, argument descriptions — all of it. Anthropic gives a concrete figure for a fairly ordinary situation: a setup drawing tools from five services, something like a code host, a chat system, an error tracker, a metrics system, and a log search, can consume roughly fifty-five thousand tokens in tool definitions alone. Fifty-five thousand tokens spent before Claude has read the user's question.

The second problem has nothing to do with cost. Claude's ability to pick the right tool degrades as the toolset grows. Anthropic puts the threshold at somewhere around thirty to fifty tools, past which selection accuracy starts to suffer.

That second one is more insidious than the first, because a budget overrun shows up on a dashboard and a slightly wrong tool choice shows up as a strange answer three weeks later. Project Desk at forty tools has probably already made this mistake. Somebody asked about a shipment and got a query against orders, which returned something plausible, and nobody checked.

Both problems come from the same fact: everything is loaded, all the time, regardless of whether this request needs it.

Tool search changes that. Claude searches your catalogue and loads only the tools it needs for the request in front of it. Anthropic reports the context reduction as typically over eighty-five percent, with three to five tools loaded instead of forty, and the selection accuracy staying high even across thousands of tools because Claude is only ever choosing among a focused set.

The mechanism has one detail that people consistently get wrong, and getting it wrong produces a confidently broken implementation, so this chapter will handle it before anything else.

You still send every tool definition on every request.

All of them. The full definitions, the complete argument schemas, every one of your forty tools, in the tools array, every single time. Tool search does not reduce what you transmit.

What it changes is what enters the context window.

You mark the tools that should not load up front with a field called defer loading, set to true. The API keeps their definitions server-side, where it needs them in order to search across them and to expand them when Claude finds one. It simply does not put them in front of Claude until Claude asks.

Once that distinction is clear, most of the tool's behaviour follows from it. The search runs against names, descriptions, argument names, and argument descriptions — which is why the definitions must be present server-side. When Claude's search matches something, the API returns tool reference blocks pointing at the matches, up to five by default, and then expands those references into full definitions before Claude sees them. You never expand anything yourself. You never return a result for the search call, because it is a server tool and its identifier carries that prefix from Chapter 1.

A few rules bound the arrangement, and they are the kind that produce immediate, legible errors instead of subtle ones.

At least one tool has to stay non-deferred. Defer everything, including the search tool itself, and the request fails with a four hundred, which is a mistake almost everybody makes once. Never defer the search tool — it is the thing Claude needs in order to find anything else.

Beyond that minimum, Anthropic's advice is to keep your three to five most frequently used tools loaded normally. If Project Desk looks up a project on nearly every request, making Claude search for the project lookup tool first is pure overhead. Deferral pays off for the long tail, not for the tools you always need.

There is an elegant consequence for prompt caching. Deferred tools are stripped out of the rendered tools section *before* the cache key is computed, so they do not appear in the cached prefix at all. Which means you can add deferred tools to a request without invalidating an existing cache entry, and the cache survives both the turn where a tool is discovered and the turn where it is called, because the discovered definition is expanded inline in the conversation body rather than in the prefix.

So deferral is not a tradeoff against caching. It protects caching. The one restriction is that a deferred tool cannot itself carry a cache breakpoint — that combination returns a four hundred — so put your breakpoints on the tools that stay loaded.

The tool ships in two variants, and this is where the lesson from Chapter 1 about version strings earns its keep, because these two are a textbook case of the shape that misleads people.

One variant has Claude construct regular expressions to search with. The other has Claude write natural-language queries, using a classical text-ranking algorithm. Both carry the same date, November the nineteenth, 2025. Neither replaced the other. They are siblings, released together, and choosing between them is a decision about how you want searching to behave, not a decision about how current you want to be.

If you had applied the ordinary instinct — take the newest — you would have found two identically dated strings and no guidance at all. The version relationships from Chapter 1 are what tell you to stop looking for a winner.

Practically, the two behave differently in ways you can predict. The regular expression variant means Claude writes patterns, matched case-insensitively, up to two hundred characters. It rewards consistent naming: if every tool touching your code host starts with the same prefix, one pattern finds the whole family. The natural-language variant takes queries up to five hundred characters and rewards descriptive prose in your tool descriptions.

That suggests something you can do regardless of variant. The searchable surface is names, descriptions, argument names, and argument descriptions, so those fields have a second job now. They are no longer only instructions to Claude about how to use a tool. They are also the index by which the tool gets found at all. A tool with a terse description was always slightly worse; a tool with a terse description in a deferred catalogue may simply never surface.

Anthropic's optimization advice follows from that directly: write clear descriptive names, use consistent prefixes per service or resource, put the keywords your users actually say into the descriptions, and add a short system prompt section describing what categories of tools exist so Claude knows what is worth searching for. Then watch which tools Claude discovers, and refine the descriptions that never get found.

The failure modes are mercifully clear. A search that matches nothing returns an empty list of references rather than an error, so Claude simply finds nothing and proceeds. A reference pointing at a tool whose definition is missing from your request produces a four hundred, because the API cannot expand what you did not send. A malformed regular expression, or one over the length limit, produces an error inside a successful response — the same envelope you met in Chapter 2, where two hundred does not mean it worked.

When a regular expression pattern finds nothing you expected it to find, the debugging path is short. Claude searched names, descriptions, argument names, and argument descriptions, so check all four instead of only the name. Matching is case-insensitive, so casing is never the answer. And Claude tends toward broad patterns rather than exact matches, which means the problem is usually a description that does not contain the word anybody would search for.

The limits are generous enough to be uninteresting for most applications: up to ten thousand deferred tools per request, five results per search by default, and the pattern and query length caps already mentioned.

The decision about whether to use this at all has published thresholds, which is convenient. Anthropic suggests tool search when you have ten or more tools, when definitions exceed roughly ten thousand tokens, when selection accuracy is degrading as the toolset grows, when you are aggregating several outside tool servers, or when the library is expected to keep growing. Standard tool calling is the better fit below ten tools, when every tool is used on every request, or when the definitions are genuinely tiny.

Project Desk at forty tools is comfortably past all of those.

One thing this tool does not do is cost money directly. Tool search is not metered as a separate server tool — there is no per-search fee the way web search has one. The definitions it loads into context count as ordinary input tokens, exactly like any other tool definition. Which means the entire economic case for it is the tokens it *avoids*, and the tokens it avoids are real.

There is a variation worth knowing exists, because it changes what the feature is. You can implement tool search yourself. If you have a semantic search index, or embeddings over your tool catalogue, you can write your own tool that returns tool reference blocks in an ordinary tool result, and the API will expand them the same way it expands its own. Every referenced tool still needs a definition in the request, normally deferred.

So the built-in variants are two implementations of a pattern, not the pattern itself. If regular expressions and text ranking both suit your catalogue poorly, the extension point is there.

The mechanics of that are worth a sentence because they are simpler than they sound. When Claude calls your custom search tool, you return an ordinary tool result whose content contains tool reference blocks, and the API expands them exactly as it expands its own. Every referenced tool still needs a definition in the request, normally deferred. So a semantic index sitting in front of your catalogue is a client tool that happens to return references instead of data.

One format caution, because the two paths look similar and are not interchangeable. The result shape shown for the built-in search is Anthropic's own internal format. A custom implementation uses the standard tool result format with reference blocks in its content — not a copy of the server-side shape.

Which brings the chapter to its one operational suggestion, and it applies whichever variant you use. Monitor which tools Claude actually discovers. A deferred catalogue creates a failure mode that a loaded catalogue does not have: a tool can become effectively invisible, because nothing ever matches it. It is still defined, it still transmits, it still works if called — and it is never found.

That failure is silent by construction. Nobody gets an error when a tool goes undiscovered; Claude simply uses something else, or says it cannot help. Which means the discovery log is the only place the problem is visible, and the repair is almost always a description rewritten to include the words a person would actually use.

One misconception survives even after the "you still send everything" lesson lands.

Deferring a tool does not make Claude worse at using it. The full definition is expanded inline before Claude sees it, so a discovered tool arrives complete — schema, descriptions, and any example inputs you provided. Anthropic notes specifically that tool-use examples work with tool search: when a deferred tool is discovered, its examples expand along with its definition.

The same is true of strict schema validation. The grammar that constrains tool calls to match your schemas is built from the full toolset, so deferral and strict mode compose without the grammar having to be rebuilt. A deferred tool is not a second-class tool. It is the same tool, arriving later.

And discovery persists. The API expands references throughout the conversation history, so a tool Claude found on turn two is available on turn nine without searching again. The cost of discovery is paid once per conversation, not once per call — which matters, because a naive mental model of this feature imagines Claude searching repeatedly for the same tool and paying for it each time.

For tools that arrive from a connected outside tool server rather than from your own definitions, the configuration lives in a different place: you set deferral once for the whole server, or per tool in its configuration, instead of on individual definitions. Those servers belong to Volume 5, so the detail worth carrying is only that the mechanism exists and the field moves.

A second use case, well away from Project Desk, is where this feature was really aimed. An internal developer assistant with connectors to a code host, a chat system, an incident tracker, a metrics platform, and a deployment tool can easily reach two or three hundred tools. Nobody wrote two hundred tools; five integrations each brought forty. At that scale the selection-accuracy problem dominates the cost problem, because a wrong tool choice in a deployment tool is considerably worse than an expensive request.

Project Desk defers thirty-five tools, keeps five loaded — project lookup, status update, audit entry, shipment lookup, and the search tool — and adds two sentences to its system prompt saying that tools exist for orders, shipments, exceptions, components, tickets, and the warehouse.

The definitions bill drops by most of itself. The shipment question that used to query orders now gets answered by a tool Claude found by searching for the word "shipment," which is a better outcome arrived at almost incidentally.

And Project Desk still forgets everything the moment the conversation ends.

---

## Chapter 7: Memory

The restructuring job from Chapter 5 did not finish in one sitting. Real work rarely does. It ran for an afternoon, got through most of the component taxonomy, and stopped when the person supervising it went home.

The next morning, Project Desk began again from nothing.

Not from a checkpoint. From nothing. It had no idea which files it had already normalized, which mapping decisions it had made and why, or that it had discovered halfway through that two exception codes in the old scheme meant the same thing. All of that had been worked out, at real cost, and then discarded when the conversation ended.

So it re-explored. It read files it had already read, rediscovered the duplicate exception codes, and made a slightly different decision about them the second time, because nothing recorded the first one. By mid-morning the taxonomy contained both decisions.

This is the most expensive kind of failure in agentic work, and it is not a bug in anything. The Messages API is stateless. It was stateless in Volume 1 and it is stateless now. Conversation history persists because *you* send it, and when a conversation ends, whatever was learned inside it ends with it.

The memory tool addresses this, and it does so in a way that will be either obvious or infuriating depending on what its name led you to expect.

The shape of it is this. Claude can store and retrieve information in a directory of files that persist between conversations. It checks that directory before starting a task, writes what it learns as it works, and reads it back in later sessions to continue. The path is a memory directory — spoken as "slash memories" — and Claude creates, reads, updates, renames, and deletes files underneath it.

Now the part that surprises people.

The memory tool is a client tool. Claude does not store anything. Claude requests file operations, and your application performs every one of them, against storage you own, and returns the result.

There is no memory unless you wrote the memory.

That path — slash memories — is a prefix, not a location. It is a name Claude uses in its requests, and your handler maps it onto whatever real storage you have: a per-user directory on disk, rows in a database, objects in cloud storage, encrypted files, anything. A later conversation continues from the same memory because it sends the same tool entry and your handler serves the same store. Nothing about that continuity lives on Anthropic's side.

That is the clean confirmation of the boundary from Chapter 1, arriving in the form most likely to catch you out. The tool with the most managed-sounding name in this volume — a *memory*, provided by the platform — is the one where Anthropic supplies a specification and you supply everything else. Web search runs on Anthropic's machines and needs nothing from you but a tool entry. Memory needs a storage backend, a validation layer, an expiry policy, and someone on call when it breaks.

The tool entry itself is almost nothing: a type string stamped August 2025 and the name "memory." No input schema, because it is an Anthropic-schema tool and the schema is built into the model. It is generally available on the Messages API, with no beta header required, on all Claude 4 and later models.

Then you implement six commands.

View shows a directory listing or a file's contents, optionally a range of lines. Create makes a new file. There is a string-replacement command that swaps one exact piece of text for another. Insert adds text after a given line number. Delete removes a file or directory. Rename moves one.

If those sound familiar, they should — they are close cousins of the text editor tool's commands, which Chapter 9 covers. The error-handling conventions are deliberately similar too.

The specifications are quite precise about what to return, and precise in a way that tells you something about how Claude uses them. A directory listing shows files and directories with human-readable sizes, up to two levels deep, excluding hidden files and dependency folders. A file view returns contents with line numbers prepended, right-aligned in a six-character field, one-indexed. A file with more than about a million lines should return an error, not a listing.

Anthropic describes these as recommended behaviours rather than a rigid contract, and says so explicitly: Claude reads whatever text your tool result contains, so you can return different strings if your application needs to. The reason to follow them anyway is that Claude's built-in tool description already tells it what to expect, and matching that description means Claude's assumptions and your handler's behaviour agree.

Two details in the specification quietly tell you what Claude will actually do. Claude's tool description says the view command displays image files and truncates the text view of files longer than about sixteen thousand characters. So expect view calls on image paths, and expect follow-up ranged views when a file is long — Claude will read a slice, then ask for another. And the description says the create command creates *or overwrites* a file, so expect create calls on paths that already exist. Returning an error in that case is the reference behaviour; overwriting instead is a valid implementation choice. Either way, decide deliberately instead of discovering it in production.

Two commands come with a restriction that comes from Claude's side rather than yours. Claude's tool description tells it that it cannot delete or rename the memory root itself. So your handler should reject a delete or rename whose target is the root. Claude will rarely try, but the guarantee belongs in your code, not in a description you do not control.

The part of this chapter that actually matters is not the command list.

Your application executes every file operation Claude requests. Which means the security of that operation is entirely, unavoidably yours.

Anthropic's warning is specific about the attack. A path can contain parent-directory segments — the two dots that mean "up one level" — and a path built out of enough of those can climb out of the memory directory and reach anything your process can read. A path that appears to live under slash memories can resolve to a credentials file three directories up.

The mitigations are the ordinary ones, and each item on the list catches a different attempt. Validate that every path starts with the memory prefix. Resolve paths to their canonical form and verify the result is still inside the memory directory, because checking the string before resolving it proves nothing. Reject paths containing traversal sequences in either slash direction. Watch for URL-encoded versions of those sequences, where the dots and slashes arrive percent-escaped and slip past a naive string check. And use your language's own path-security utilities instead of writing the comparison yourself.

The general principle underneath is one to carry into every client tool in this volume. A path arriving from outside your application is an instruction until something checks it. Claude is not attacking you. But Claude is reading files whose contents someone else may have written, in a conversation someone else may be steering, and a path that reaches your handler has travelled through all of that.

Anthropic names two more obligations that are less dramatic and equally yours. Claude usually refuses to write sensitive information into memory files, and for stronger guarantees you add validation that strips it before writing. Memory files grow, so track their sizes, cap how large one may get, and consider capping how much the view command returns so Claude pages through a long file rather than loading all of it. And memory that is never read is just cost, so periodically delete files that have not been touched in a long time.

There is one thing you do not have to do. When the memory tool is present in your request, the API adds a memory instruction to the system prompt automatically. You do not send it. Claude's own tool description also already tells it to keep the directory organized, so repeating that instruction is unnecessary — though if Claude still produces clutter, reinforcing it is available. You can also constrain what gets written at all: telling Claude to record only information relevant to a particular topic works, and is a reasonable way to keep a memory store focused.

Now, the pattern, because a tool this open-ended is easy to use badly.

Writing memory files ad hoc as work progresses produces a directory nobody understands and a recovery story that does not work. Anthropic documents a deliberate alternative for software projects spanning multiple sessions, and its shape is simple enough to describe in three moves.

An initializer session sets up the memory files *before* any substantive work begins. It creates a progress log recording what has been done and what comes next, a feature checklist defining the scope, and a reference to whatever startup or initialization script the project needs.

Each subsequent session opens by reading those files. That restores the project state without re-exploring the codebase or retracing earlier decisions — which is precisely the cost Project Desk paid on that second morning.

And before a session ends, it updates the progress log with what was completed and what remains, so the next session starts from something accurate.

The key principle attached to this is sharper than the pattern itself, and it is the kind of rule that only comes from having watched it fail. Work on one feature at a time, and mark a feature complete only after end-to-end verification confirms it works — not when the code is written.

The reason is that a progress log which says "done" about something that was merely written is worse than no progress log. The next session trusts it, builds on it, and discovers the problem several steps later with the false record still in place. An inaccurate memory does more damage than an empty one, because an empty one prompts exploration and an inaccurate one prevents it.

You do not have to write the plumbing from scratch, and it is worth knowing what the SDKs provide before you do. Several of them ship a helper that handles the tool interface and the loop, leaving you to implement only the storage: an abstract class to subclass in some languages, a handler interface to implement in others, a function that wraps a closure in another. Two of them also ship a ready-made implementation backed by the local filesystem, which is useful for development and is not what you want in production for anything multi-tenant.

One naming detail will confuse you if it goes unmentioned. Those helper surfaces live in each SDK's beta namespace even though the memory tool itself is generally available. The beta label is on the helper, not on the tool.

The languages without a helper run the ordinary tool-use loop themselves, which is the loop from Volume 3 and nothing more exotic. Every one of the documented examples uses an in-memory store you are expected to replace, and none of them includes the path validation this chapter just spent four paragraphs on. That is a reasonable choice for an example and a dangerous one to copy.

That is a small, general caution about starting from any vendor's example. The example demonstrates the interface. The parts it omits are usually the parts that are your responsibility, which is precisely why they were omitted, and precisely why their absence is easy to miss.

A second use case shows the tool doing something other than resuming engineering work. A support assistant that talks to the same customer across months can keep a memory file per customer: their configuration, the things they have already been told, the workaround they agreed to last time. Which produces an assistant that does not ask a customer to re-describe their setup every time — and produces, at the same moment, an obligation. That file is customer data, subject to whatever retention and deletion promises your organization has made, and the memory tool gives you no policy for it. Anthropic's advice to periodically delete files that have not been accessed is a starting point, not a compliance posture.

That obligation is the same one this chapter opened with, arriving from the other direction. The storage is yours, which means the storage's rules are yours too.

There is one boundary to mark before leaving this chapter, because two related capabilities exist and this volume does not own them.

Memory carries information *between* conversations. It does not manage the space *inside* one. Two other mechanisms do that: context editing, which clears specific tool results on the client side, and compaction, which summarizes a whole conversation server-side as it approaches the context window limit. Anthropic's guidance for long-running agents is to use memory alongside them — compaction keeps the active context small without client bookkeeping, while memory preserves the information that must survive being summarized away.

Both belong to Volume 5. What matters here is knowing that memory is not the answer to a conversation that has grown too long, and reaching for it as though it were will produce a system that has an excellent filing cabinet and still runs out of desk.

Project Desk's restructuring gets an initializer session, a progress log, and a checklist. The duplicate exception codes get recorded once, with the reasoning, the first time they are found. The next morning it opens the log, sees where it stopped, and continues — and the taxonomy ends up with one decision in it rather than two.

The memory lives in Project Desk's own database, behind a handler that validates every path, because Anthropic never had it.

---

## Chapter 8: Bash

The exceptions analysis lives in a sandbox that cannot reach anything.

That was fine while the work was arithmetic. Four thousand rows went in, a summary came out, and the sealed room was exactly right for the job. But the restructuring that followed touches Project Desk's actual data — the supplier records in the company's own database, on the company's own machines, behind the company's own network. Anthropic's container cannot see any of it, and never will, because it has no network access at all.

Some work has to happen where the data is.

The Bash tool is how Claude asks for that. And the pattern will feel familiar immediately, because it is the loop from Volume 3 wearing Anthropic's schema. Claude returns a tool use block naming a command. Your application runs that command, in a shell it owns, and returns the output in a tool result. Claude either asks for another command or answers in text.

Its current version is stamped January 2025, requires no beta header, and every model from Claude Sonnet 3.7 onward accepts it. There is an older version from October 2024 that belongs to the original computer use beta and works with exactly one retired model; new work should ignore it.

The tool definition has two required fields and no input schema. Type and name, and the name must be "bash." Like the memory tool, it is schema-less because the schema is built into the model and cannot be modified. Claude sets two input fields: a command to run, and a restart flag.

The interesting property is not any field. It is that your application keeps one shell process alive across tool calls.

That single decision produces most of what makes the tool useful. Because the process persists, state persists with it. The working directory Claude changed in one command is still the working directory in the next. Environment variables it exported are still set. Files it created are still there. Claude can change into a directory, run a build, read the output, and run a test against what the build produced, across four separate tool calls, and the fourth command sees everything the first three did.

That raises the question of who is responsible for that continuity, and the answer is entirely you.

The API is stateless. Nothing about your shell session travels between requests — not the process, not its environment, not the fact that it exists. Your application decides when the session starts, how long it lives, and when to throw it away. From the API's side there is no session at all; there are only commands arriving in tool use blocks and output arriving in tool results.

This is the same statelessness you met in Volume 1 and again in the previous chapter, showing up in a third costume. The pattern by now should be predictable: anything that persists in a Claude application persists because your application persisted it.

The restart flag is the acknowledgment that sessions go wrong. When Claude sets it, your handler kills the shell process, starts a fresh one, and returns a result confirming the restart. What Claude gets back is a clean session — and clean means empty. The working directory is gone, the environment variables are gone, and any process the old session started is gone with it.

So a restart is destructive by design, and Claude will sometimes ask for one after a command has left the session in a state it cannot reason about. That is usually the right instinct. It is also worth knowing that a restart discards work, so a handler that restarts eagerly on every error will lose context Claude was depending on.

Now the part of this chapter that matters more than anything mechanical, and it is the part where Anthropic's documentation is unusually blunt about the limits of its own advice.

Your application runs whatever command Claude requests.

The obvious response is validation, and validation is genuinely recommended. The guidance is to use an allowlist, not a blocklist, and the reasoning is the familiar one: a blocklist misses whatever it did not anticipate, and you cannot anticipate a shell. So you enumerate the commands your application permits and reject everything else.

Then the documentation does something admirable. It shows an example of exactly that check, and immediately explains how the example fails.

The check rejects shell operators that appear as separate words — the chaining operator, pipes, redirection — by looking at the command split into tokens. Which catches a command written with spaces around its operators. It does not catch an operator glued to a word, because a tokenizer that splits on whitespace keeps a filename and a pipe and a following command inside a single token when nobody typed a space between them.

And the conclusion Anthropic draws is the one to carry out of this chapter. That check is a tripwire for obvious mistakes, not an enforcement boundary.

The real control is isolation.

Run the whole session inside a container or a virtual machine, as the least-privileged user that can do the work, and treat every command as untrusted input. That is the sentence that actually protects you. Everything else — the allowlist, the operator check, the careful enumeration of permitted commands — reduces the frequency of accidents inside a boundary that is doing the real containment.

This distinction is the one this book will keep returning to, and it now has a name. An allowlist is a sign. A container is a lock. Signs are useful, and worth posting, and they change where almost everyone goes. They do not decide where anyone can go. When you find yourself relying on a sign for a guarantee, the guarantee is not there.

Beyond isolation, three more controls are recommended, and each addresses a different failure. Set resource limits on the shell process — CPU, memory, disk — so a runaway command cannot take the machine with it. Log every command and its output so that what ran is auditable afterwards. And redact credentials and secrets from output *before* returning it to Claude, because output travels into the conversation and the conversation travels into your logs, your storage, and possibly your memory files.

That last one deserves a moment, because it is easy to miss. A command that prints an environment variable puts a secret into the conversation history. Nothing malicious has happened. But the secret is now in the transcript, and the transcript is now wherever transcripts go.

Then there are the limits, and they shape a real implementation more than the features do.

The session cannot run interactive commands. Anything that waits for input on standard input — a text editor, a pager, a password prompt — will simply hang, because there is nobody to type. There are no graphical applications; it is a command line and nothing else. Session state is client-side, which by now you expect. The API does not truncate tool results, so an oversized request is rejected rather than trimmed, which means your application must truncate large output itself before sending it. And there is no streaming: output reaches Claude only when your application returns the tool result on the next request, so a long-running command produces silence and then everything at once.

The hang deserves the most attention, because it is the failure people hit first, and the mechanism behind it is worth understanding.

A pipe to a live process never reports end of file. So an implementation cannot simply read until the output stops — the output never formally stops, because the shell is still alive. The usual technique is to have the session print a unique marker line after each command, and read until that marker appears. Which works beautifully, and fails completely when a command never finishes, because the marker never arrives and the read waits forever.

The consequence is a rule with no exceptions: every command gets a deadline. When the deadline passes, stop the shell and everything the command started, restart the session, and return an error result telling Claude the command timed out. Killing the shell alone is not enough, because a hung command has usually started something else that is also hung.

A command with no deadline is a session with no end.

Errors follow the convention Volume 3 established: return the message as the tool result's content and mark the result as an error, so Claude knows the call failed instead of believing an error message was the command's normal output. A command that does not exist, a permission problem, a timeout — each gets a plain description of what happened. Claude handles these well when told, and handles them badly when an error is silently formatted as success.

Two patterns from the documentation show what this tool is actually for. Development work — running tests, building projects, staging and committing changes — is the obvious one, and it is where the persistent session matters most, because those commands assume a working directory and an environment that survived the previous step. File and data work is the other: counting lines across files, searching a tree for a pattern, archiving a directory.

A third category is worth separating out, because it is where the truncation obligation stops being theoretical. System inspection — checking disk space, listing processes, examining what is running — produces output whose size you do not control. A process listing on a busy machine is thousands of lines. A search across a large tree can return more matches than anybody wants.

Since the API does not truncate results and an oversized request is rejected outright, a command whose output is unbounded will eventually fail the whole request rather than returning a lot of text. Which is a worse failure than truncation, because it takes the turn with it.

The practical shape is to truncate in your handler with a limit you chose, and to say in the result that truncation happened. Claude handles "the first two hundred lines of output, truncated" perfectly well and will narrow the command if it needs more. What it handles badly is a request that failed for reasons nobody explained.

There is a related habit that costs nothing. When Claude writes a command whose output is likely to be large, it will often bound the output itself if the tool description mentions that results are truncated. A sentence in the description does work that a parameter cannot, because the tool is schema-less and there is no parameter to add.

Both are things Project Desk needs on the machine that holds the data, and neither is possible in the sealed container from Chapter 4.

Which brings back the trap from that chapter, now from the other side. If Project Desk offers both this tool and code execution, Claude has two execution environments and they share nothing. And Project Desk does not have to enable code execution deliberately for that to happen, because the current web search and web fetch tools bring it along automatically. An application that does supplier research and runs local commands has two shells whether or not anybody chose to have two.

The mitigation is still a couple of sentences in the system prompt naming both environments and stating that state does not travel between them. It is a small amount of prose standing in for a distinction the tool definitions cannot express.

One more pairing, because it is the subject of the next chapter. The Bash tool goes naturally with the text editor tool: Claude edits a file with one and requests the command that runs it with the other. Which sounds like a division of labour for convenience, and turns out to be a division of labour for safety.

The audit obligation deserves its own paragraph, because the recommended shape is more specific than "log things" and the specificity is the useful part.

Route every command through one wrapper that records the command before it runs and the output after it finishes. Two records per command, not one. The reason for two is the failure case: a command that hangs, or that breaks the session badly enough that nothing comes back, still leaves the first record behind. A single record written after completion writes nothing at all for exactly the commands you most want to know about.

Include whatever ties a record to a request in your own system — the end user, the identifier on the tool call — because a shell log without that linkage tells you a command ran and nothing about who caused it. The records go to standard error by default, which is fine for development and means nothing is being retained; point them at a file or your logging pipeline if you want to keep them.

A second use case, and it is where this tool earns its reputation. A coding agent needs to run tests, read failures, edit code, and run the tests again. That loop is the reason the Bash tool exists, and the persistent session is what makes it work — the test command assumes a virtual environment activated three calls ago and a working directory set before that. Anthropic points at using version control as a checkpoint-and-recovery mechanism for exactly this kind of long-running work, which is a sensible pairing: a session that can be restarted destructively is much less frightening when the work is committed.

There is a corollary worth stating for the same reason the memory chapter stated its version. An agent whose shell session can be restarted at any moment should treat uncommitted work as work that might vanish. The restart flag is not a hostile act, but it is a discontinuity, and an agent that has been building state in a directory for twenty minutes without recording it anywhere will lose all of it to a single hung command.

Project Desk's restructuring now runs where the data is. One shell process, started when the session starts, restarted when a command hangs, with a deadline on every command and a wrapper that logs each one before it runs and its output after it finishes. The whole thing lives in a container as a user that can read the supplier records and cannot read anything else.

The verification suite runs. One test fails, in the historical backfill, and the failure names a single field in a single configuration file.

Claude could fix it with a shell command. The next chapter is about why it should not.

---

## Chapter 9: Text Editing

The failing test names one field in one configuration file. The exception-code mapping has the wrong target for a single legacy code, and the historical backfill inherits the error.

Claude has a shell. It could fix this with a stream editor and a substitution expression, in one command, in about four seconds.

Consider what that command would actually do. It would find every occurrence of a pattern in that file and replace it. If the pattern appears once, the fix is correct. If it appears twice — because the same legacy code is referenced in a comment, or because a similar code shares the same prefix — the command changes both and reports success either way. The output of a successful substitution is nothing at all. Claude would see an empty result, conclude the edit worked, and move on.

The failure mode of a shell edit is a silent wrong answer, and a silent wrong answer in a data migration is the expensive kind, because the next step builds on it.

The text editor tool exists for this. It is narrower than a shell in a way that is deliberately, usefully awkward.

Its name is longer than its purpose suggests, and you will see it in your own code: it is called the string-replace-based edit tool. The name describes its architecture, not its job, which is a small window into how it wants to be used. Its current type string is stamped July 2025, for Claude 4 and later models. Like the memory and Bash tools, it is schema-less; you provide no input schema because the schema is built into the model.

It supports four commands, and they are almost the memory tool's commands from two chapters ago, which is not a coincidence — Anthropic reuses the shape.

View reads a file's contents or lists a directory. String replace swaps one exact piece of text for another. Create writes a new file with given content. Insert adds text after a specific line.

The whole safety argument lives in one requirement on one of those commands.

For a string replacement, the text being replaced must match exactly. Every character, including whitespace and indentation. And your application should ensure there is exactly one match, or return an error saying so.

That is the difference from the shell command. A substitution expression is happy to match many things and reports nothing about how many it matched. This tool insists on knowing precisely which text you meant, and the standard behaviour when it cannot tell is refusal.

Refusal is the feature.

An edit that cannot find its target should fail rather than guess, and an edit that finds three plausible targets should stop and say which three. The errors your handler returns encode that: a file that does not exist, text that appears in multiple places along with the line numbers where it appears, text that does not appear at all. Each of those is a message Claude can act on, and each of them is information a shell substitution would have thrown away.

The other commands have their own precision, and the details are the kind that matter only when you implement them. The view range is one-indexed, and a second value of negative one means "read to the end of the file." Insert takes a line number to insert *after*, and zero means the beginning of the file. Create takes the whole file's content as text.

One detail about view is easy to skip and turns out to be load-bearing. When your handler returns file contents, prepending line numbers to each line is not required. But without them, the view range and insert parameters become guesswork — Claude has to count lines in a block of text in order to ask for a range or an insertion point. The line numbers are what make the precise commands usable.

There is one optional parameter, added in the July 2025 version, that caps how many characters a view returns so a large file can be truncated instead of loaded whole. It is not compatible with earlier versions of the tool.

Which brings this chapter to its second job, because the text editor's version history is the clearest worked example in the book of the idea from Chapter 1 that a dated version is a contract rather than an upgrade.

Four versions exist. The original, from October 2024, shipped with the first computer use release and offered five commands: view, create, string replace, insert, and undo edit. A March 2025 version was documented as a standalone tool, optimized for a newer model, with identical capabilities. An April 2025 version arrived for Claude 4 — and it *removed* the undo edit command. The July 2025 version added the character cap and is otherwise identical to April's.

Undo was there, and then it was not.

Read that as a version number and it makes no sense: how is a later release with fewer commands an upgrade? Read it as a contract keyed to a model, which is what Chapter 1 called the model-keyed relationship, and it becomes ordinary. The April 2025 version is the contract for Claude 4 and later models. The January 2025 version is the contract for the models before them. Which one you use follows the model you are pointing at, and taking the newer string because it is newer will fail outright against an older model.

The lesson generalizes past this tool. When a version's command list shrinks, the temptation is to read it as a regression. Usually it means the version is keyed to something other than time — a model, a runtime, a capability tier — and the shrinkage is a consequence of that keying, not a loss.

It also means that if your application depended on undo edit, the migration was not optional and not automatic. Something in your code has to notice. Which is the practical argument for reading version strings as contracts: a contract is something you check when it changes, and a version number is something you increment.

Worth knowing before you go looking for it: the documentation publishes a token cost for the April 2025 version of this tool and does not publish one for the July 2025 version that supersedes it. So there is a number available for the older contract and no number available for the current one. The durable fact is the shape rather than the figure — a schema-less tool adds a fixed cost to every request that includes it, on top of the general tool-use overhead that applies whenever any tool is present — and if you need the current figure you count tokens instead of trusting a table that does not list it.

That gap is a small, real example of why this book dates its numbers. A published figure for a superseded version is worse than no figure, because it looks authoritative and describes something you are not using.

A second use case, and it is the one that made this tool famous. A debugging assistant reads a file, identifies the fault, and fixes it. The reason the editor suits that better than a shell is the same reason it suited Project Desk's mapping error: the assistant does not know in advance how many places the faulty pattern appears, and finding out is part of the job. A tool that refuses ambiguous edits turns "I do not know how many matches there are" from a silent risk into an explicit message.

The same shape appears in documentation work — adding a docstring to one function among forty that look similar — and in generating tests, where a file is created rather than modified and the create command does the whole job.

What connects those cases is that the edit is small and the file is important. When either of those stops being true, the calculus changes. Rewriting most of a file is a create, not a sequence of replacements. And a file nobody depends on can perfectly well be edited with a shell command, because the cost of getting it wrong is an afternoon, not a migration.

That is the honest boundary on this chapter's argument. Precision is not free — it takes a view, then a replacement, then usually a verification, where a shell substitution took one call. Paying that cost on a throwaway file is ceremony. Paying it on a configuration file that a data migration depends on is the reason the tool exists.

The implementation obligations are the ones you would expect, and Anthropic states them as warnings rather than suggestions. The tool has access to your filesystem, so validate paths to prevent traversal outside where edits belong — exactly the obligation from Chapter 7, arriving again because the shape is the same. Create backups before allowing edits to important files, so a wrong edit is recoverable. Validate inputs. And make sure a replacement matches exactly one location.

The backup advice is more interesting than it sounds, given what this chapter has already established. The undo command was removed. So the tool no longer offers any way to reverse an edit, which means the recovery story is entirely your application's. A copy of the file before the edit is the whole mechanism. If you skipped that because the tool once had undo, the removal quietly took your safety net.

There is a verification obligation too, and it belongs to the pairing from the last chapter. After Claude edits a file, something should confirm the change did what it was supposed to. That is what the Bash tool is for: edit with the editor, then run the test with the shell. The division of labour is not about convenience. The editor makes changes that are precise and auditable, and the shell provides the evidence that the precise change was also the correct one.

The errors your handler returns are worth designing instead of defaulting, because each one tells Claude something different about what to do next.

A file that does not exist means Claude looked in the wrong place, and it will usually respond by listing a directory to find the right one. Text that appears in multiple places is the interesting one: returning the line numbers where it appears lets Claude construct a longer, more specific replacement string that includes surrounding context, which is precisely the repair you want. Text that appears nowhere means Claude's model of the file is stale — it may have been working from a view taken before an earlier edit — and the productive response is a fresh view. And a permission problem is not Claude's to solve at all; it needs saying plainly so Claude stops trying.

So an error message here is not a complaint. It is the input to Claude's next decision, and a vague one produces a worse next decision. "Edit failed" tells Claude nothing. "That text appears on lines forty-one and sixty-eight" tells Claude exactly how to succeed.

Which is a general principle for every client tool in this volume, and it is the reason Volume 3 spent time on the error flag rather than treating it as a formality. A tool result marked as an error is a message in a conversation with a reader who will act on it.

There is a prompting consequence too, and the documentation is specific about it in a way that is easy to dismiss as obvious. Being vague about which file to examine produces worse results than naming it. "Fix my code" gives Claude no starting point, so it explores; "there is a syntax error in this particular file that stops it running" gives Claude a target. The same holds for scope: asking about a named file's performance is a different request from asking somebody to review your helpers.

That is not a statement about politeness. A tool that can view any file needs to be pointed somewhere, and an unpointed request spends its first several calls discovering what you already knew.

One structural note about combining this with anything else. Because each of the Anthropic-schema tools adds its own fixed token cost to the request, and because versions are keyed to models, a request carrying the editor and the shell and computer use is carrying three fixed costs and three version decisions. Match every version to the model you are actually using, and account for all three when you budget the request. Chapter 12 collects that arithmetic.

Project Desk fixes the mapping. Claude views the configuration file, finds the wrong target, and requests a replacement of one exact string. Project Desk's handler confirms the string appears exactly once, writes a copy of the file to its backup directory, makes the edit, and returns a result describing what changed.

Then Claude asks the shell to run the verification suite again, and it passes.

One field changed. The rest of the file is byte-for-byte what it was, which is something Project Desk can demonstrate, because it kept the copy.

Every tool so far has needed a system with an interface Project Desk could reach — an API, a filesystem, a shell. Kestrel Components has none of those. It has a login page and a form, and a human who has been filling it in by hand.

---

## Chapter 10: Computer Use

Kestrel Components has a supplier portal, and there is no way in except the front door.

Project Desk needs to file a damage claim there — one claim, with an order number, a description, and two photographs. Kestrel has no API. It has no bulk upload. It has a web form, behind a login, that a human fills in. The support lead has been doing it by hand, eleven minutes at a time, several times a week.

Every tool in this book so far has needed an interface Project Desk could reach. Web fetch needs a URL that returns content. The Bash tool needs a shell. The text editor needs a filesystem. A web form behind a session cookie offers none of those in any form Project Desk can use.

What is left is to do what the human does: look at the screen, move the pointer, type.

The computer use tool provides that. It gives Claude screenshot capture, mouse control, and keyboard input against a desktop environment, and with those three things Claude can operate any application that runs on that desktop. Not a category of application. Any of them, because the interface is the screen itself.

It is in beta as of this recording, and it requires a beta header. Two headers exist, keyed to two tool versions and two sets of models: a November 2025 header and tool version for the current models including Opus 5 and Sonnet 5, and a January 2025 pair for the earlier set. This is another model-keyed relationship, in the sense Chapter 1 established and Chapter 9 worked through: the version follows the model, not the calendar.

Unlike everything else in this volume, this tool needs you to build a place for it to work.

The tool definition is four fields — a type, the name "computer," and the display's width and height in pixels — plus two optional ones. But the definition describes a screen that has to exist. Anthropic's reference implementation shows what that means in practice: a virtual X11 display server rendering a desktop that nobody is looking at, a lightweight window manager and panel, a set of preinstalled Linux applications such as a browser and an office suite, the code that translates Claude's abstract requests into actual mouse and keyboard events, and an agent loop carrying messages between Claude and the environment. All of it inside a Docker container.

Claude never connects to that environment. Your application does. Claude asks for a screenshot; your code captures one and returns it. Claude asks for a click at a coordinate; your code performs it and returns whatever the screen looks like afterwards. The documentation states the obligation plainly: your application must run the tool, because Claude cannot.

That places this squarely with memory, Bash, and the text editor. Anthropic wrote the schema. You built the machine, you run the machine, and you answer for what the machine does.

The action set has grown across versions, and the growth is a good illustration of the capability-keyed relationship. Every version offers the basics: capture a screenshot, click the left button at a coordinate, type a string, press a key or combination, and move the pointer. The January 2025 version added the actions that make real interfaces workable — scrolling with an amount, click-and-drag between two points, right and middle clicks, double and triple clicks, separate mouse-down and mouse-up for fine control, holding a key for a duration, and an explicit wait. The November 2025 version added one more: zoom, which views a region of the screen at full resolution, and which has to be switched on with an optional field in the tool definition before Claude can use it.

Modifier keys work through a text field on the click and scroll actions rather than through a separate action, which is a small distinction with a practical consequence: holding shift while clicking to select a range is a click action with a modifier named on it, while holding a key for a duration without clicking anything is the separate hold action. Two similar-sounding capabilities, two different shapes.

Now the part of this chapter that matters more than the action list, and it is a security problem unlike any other in this book.

Claude is looking at a screen. Whatever is on that screen becomes input.

And Anthropic's documentation says something about that which deserves to be quoted in substance instead of paraphrased away: in some circumstances Claude will follow commands found in content even when they conflict with your instructions. Instructions on a webpage, or contained in an image, might override your instructions or cause Claude to make mistakes.

So a page Claude is reading can contain text addressed to Claude. Not to the user. To the model. And the model may act on it.

This is the same shape as the path-traversal problem from Chapter 7 and the command-validation problem from Chapter 8, escalated. Data arriving from outside your system can behave like an instruction. In Chapter 7 the data was a file path and the defence was validation. Here the data is a rendered screenshot of an arbitrary web page, and there is no equivalent of canonicalizing a path.

Anthropic has done real work on this rather than only warning about it. The model is trained to resist these injections. And there is a second layer: when you use the computer use tools, classifiers automatically run on your prompts to flag potential prompt injections, and when they identify one in a screenshot they steer the model to ask for user confirmation before it takes the next action.

Two things about that defence deserve stating precisely, because both come from the documentation and both are easy to lose in summary. Anthropic notes the protection will not be ideal for every use case — specifically naming use cases without a human in the loop — and offers a way to turn it off by contacting support. And the documentation says the other precautions remain important even with the classifier in place.

A defence that asks a human to confirm is not a defence in a system with no human. That is not a criticism of the classifier; it is a statement about where it applies.

The recommended precautions are four, and they map onto controls this book has already built in other chapters. Use a dedicated virtual machine or container with minimal privileges, which is the isolation argument from Chapter 8 arriving again. Avoid giving the model access to sensitive data such as login credentials, to limit what a successful injection can steal. Limit internet access to an allowlist of domains, which is the reachability policy from Chapter 3 applied to a whole machine instead of to one tool. And ask a human to confirm decisions that might have meaningful real-world consequences, along with anything requiring affirmative consent.

That last one comes with examples, and the examples are specific enough to act on: accepting cookies, completing financial transactions, and agreeing to terms of service.

That is a useful list, because it names a category rather than a rule. The common thread is that each of those actions creates an obligation on somebody's behalf. A click that agrees to terms is a click that binds a company to something. Some actions are not recoverable by apology, and those are the ones that stop for a human regardless of how well the automation is working.

Anthropic also asks something of you toward your own users: inform end users of the relevant risks and obtain their consent before enabling computer use in your products. Which for Project Desk means the support team knows this is happening and agreed to it, instead of discovering it when a claim gets filed strangely.

The credential question deserves one more sentence, because Project Desk's portal has a login. Anthropic's guidance is that if you need the model to log in, you provide the username and password in the prompt inside tags — and immediately notes that using computer use in applications requiring login *increases* the risk of bad outcomes from prompt injection, and points at its own jailbreak-mitigation guidance before you do it.

That is a documented path with a documented warning attached. The reasonable reading is that a login is possible and is a decision to make deliberately, with the injection risk priced in, rather than a detail to configure and forget.

Now, making it actually work, because the published operating guidance is specific and most of it is counterintuitive.

The first and most valuable practice is to make Claude verify its own actions. The documentation gives close to the exact wording: after each step, take a screenshot and carefully evaluate whether the right outcome was achieved, show that evaluation explicitly, try again if it was wrong, and only move on once a step is confirmed correct.

The reason is a failure mode named directly: Claude sometimes assumes the outcome of its actions without checking. Which in a desktop context is quietly disastrous, because a click that missed produces a screen that looks almost right, and the next five actions build on a state that never existed.

The second practice is to prefer keyboard shortcuts for controls that are awkward to manipulate with a pointer. Dropdowns and scrollbars are named specifically. A dropdown operated by clicking requires hitting a small target twice in sequence; the same dropdown operated by typing is one keystroke.

The third is the most surprising, and it is about the order of things inside a single message. When you build a user turn containing both instruction text and a screenshot, put the text *before* the image. Providing the target description before the image is processed improves click accuracy.

That is a real, actionable detail that nobody would guess, and it costs nothing to apply.

There is a fourth for the newer version's zoom action. Claude zooms when asked about small text or elements that are not legible at the screenshot's default resolution — file names in a sidebar, tab titles, status-bar text, line numbers, button labels. If it is not zooming when you expect it to, the fix is to ask about a specific region or element instead of about the screen as a whole.

Two structural notes, and then what this actually costs to operate.

Anthropic generates a computer-use-specific system prompt when one of these tools is requested, similar to the ordinary tool-use prompt but opening with a statement that Claude has access to a sandboxed computing environment. Your own system prompt is still respected and still used in constructing the combined one, so anything you say about the environment sits alongside rather than instead of that framing.

The loop itself is the loop from Volume 3, run without a human in the middle: Claude requests an action, your application performs it and returns the result, and the cycle repeats until Claude answers without requesting anything. Anthropic's reference implementation includes a maximum iteration count, and the reason given is worth taking seriously — it prevents a loop that would otherwise run up unexpected API costs. A desktop agent that has misread a screen can retry forever, and each retry is a full request with a screenshot attached.

Which is the operational shape of this tool that the action list does not convey. Every step costs a screenshot. A screenshot is an image, images are expensive in tokens, and a task that takes forty steps sends forty of them. The verify-after-each-step practice that makes the tool reliable is also what makes it expensive, and those are the same decision, not two competing ones.

Two more use cases show where the tradeoff lands well. Legacy enterprise software — an inventory system from 2004 with no API and no prospect of one — is the canonical case, because the alternative is a human doing the same clicks. Testing a web application end to end is another, where the point is precisely to interact the way a person would rather than through a programmatic interface.

And one case where it lands badly, because the boundary matters as much as the capability. If a system has an API, use the API. Driving a web interface to do something an endpoint would do is slower, more expensive, dramatically more fragile, and it exposes the model to a rendered page it did not need to see. Computer use is the last resort, and Project Desk's supplier portal qualifies only because there genuinely is no other door.

Project Desk files the claim. A container comes up with a browser, Claude logs in with credentials scoped to a portal account that can file claims and read nothing else, navigates to the claim form, and fills it in — taking a screenshot after each field and confirming the value landed where it was supposed to. The domain allowlist contains Kestrel's portal and nothing else, so an injected instruction pointing somewhere else has nowhere to go.

The final submit does not happen. Claude fills the form, captures the completed state, and stops. The support lead looks at the screenshot and clicks submit herself, because submitting a damage claim asserts something to a supplier on the company's behalf, and that belongs on the list of things a human confirms.

Eleven minutes becomes about forty seconds of review.

Ten chapters in, Project Desk can read the web, compute in a sandbox, buy a plan from a stronger model, search its own catalogue, remember across sessions, run commands, edit files, and drive a desktop. Every one of those arrived on its own, in its own turn, politely.

They will not stay that polite.

---

## Chapter 11: Combining Tools

The question that breaks Project Desk is an ordinary one.

"Has Kestrel updated their terms since we filed the claim, and what does our contract say about damage windows?"

Two halves. The first needs the current published terms, which means web fetch. The second needs Project Desk's own contract record, which means a local tool that queries the contracts table. Both are enabled. Both are relevant. Claude asks for both, in the same response, in the same group of parallel calls.

And the request that comes back is a shape Project Desk has never handled.

The response contains a server tool use block for the fetch. It contains a tool use block for the contract lookup. It does *not* contain a result for the fetch. And its stop reason is "tool use" — not "pause turn," which is what you might expect from a server tool that has not finished.

What happened is this. When Claude calls a server tool and one of your client tools in the same group of parallel calls, the API does not run the server tool. It returns immediately, so that you can run yours first. The fetch is queued, not executed.

And there is no marker announcing that. Nothing in the response says "a server tool is pending." The way you detect it is the thing Chapter 1 planted: look for a server tool use block whose identifier has no matching result block in the response.

That is the entire diagnostic. A server tool call with a result is finished and needs nothing from you. A server tool call without one is waiting, and it is waiting behind your client tool.

The same behaviour applies to a call from a connected outside tool server, which produces its own block type and behaves identically. And Project Desk should read this state from block structure instead of from stop reason, because stop reason alone cannot distinguish it.

Continuing the turn is straightforward once you know the rule, and unforgiving about one detail.

You run your client tools and send back a user message whose content is *only* tool result blocks — one for each client tool use block in that response. Then the API attaches your results to the still-open assistant turn, runs the deferred server tool, and lets Claude continue.

The detail is that word "only."

The follow-up message must contain nothing except tool results. A block added after the results — a line of text, a helpful note, anything — tells the API that the assistant turn is over. Which leaves the turn with an unresolved server tool call, and the request fails with a four hundred.

This trips people because adding context feels helpful. The support lead mentions something while the loop is running, and the natural move is to append it to the message carrying the tool results. Do not. Send it as a separate user message after the turn completes.

There is a second version of the same mistake, and it fails earlier and more legibly. A follow-up that puts content *before* the results, or answers only some of the client tool identifiers, or contains no results at all, fails with the client tool error from Volume 3 rather than with the server tool error.

And a third, which is easy to make while refactoring: the continuation request must still define the waiting server tool. Drop web fetch from the tools array on the resume request — because the code path that builds the resume seemed like it only needed the client tools — and the API returns a four hundred whose message ends with the observation that no web fetch tool was provided.

That error message is worth recognizing by shape, because it is quite specific and tells you exactly what happened.

When the continuation succeeds, the next response begins with the result block that answers the *previous* response's server tool call. That is where the detail about pairing from Chapter 1 stops being academic. The server tool use block is not repeated in the second response. Its result arrives alone, carrying the identifier of a call that lives in a different message.

Position cannot help you there. The two blocks are in separate responses with a user message between them. The identifier is the only thing connecting them, exactly as promised.

For your message history, accumulate the whole exchange in order: the first response as an assistant message, the tool result user message, then the next response as another assistant message. The same way you have accumulated every tool exchange since Volume 3. Nothing exotic.

Now the other way a turn can be unfinished, because there are exactly two and confusing them is the expensive mistake.

When Claude uses server tools without any of yours involved, the API runs them in a server-side agentic loop. It searches, reads results, searches again, and keeps going until the work is done. On a long-running turn, it may pause that loop and return a stop reason of "pause turn."

A paused turn is continued by sending the assistant content back unchanged. Not tool results — there are none to send. You take the response you received and pass it back as-is, in a new request, with the same tools defined. The API picks up where it stopped.

Three things about that. Preserve tool state by including the same tools: a paused turn can end with a server tool call that has not run yet, and a continuation missing that tool returns a validation error. Expect it to pause again, because a continued turn can pause too, so check the stop reason on every response. And cap the number of continuations the way you would cap any retry loop, because nothing else will.

So now the rule, and it is short enough to keep in your head while driving.

A paused turn never leaves one of your tools waiting. A turn that leaves one of your tools waiting is never a paused turn.

That gives you a two-question decision. Is one of my tools waiting for a result? If yes, send the results — only the results — and the API will run any pending server tool at the start of the next request. If no, and the turn is unfinished, send the response back unchanged.

Both paths end the same way: the API runs the pending server tool at the beginning of the next request. What differs is what you put in that request.

There is a variant of this shape that means something different, and it belongs to Chapter 13, so this chapter will name it and move on. With programmatic tool calling — where Claude writes code that calls your tools — you get a response that looks identical: a client tool use block waiting on you, in a turn that is not finished. But the call came from code running inside the sandbox instead of from Claude directly, its caller field says so, and that code has already started and is paused waiting for your result. Sending the result resumes the running script rather than starting a deferred tool. The follow-up message is the same shape; there is one extra thing to include, which Chapter 13 covers.

Streaming changes none of the logic and is worth a paragraph because the event shapes differ.

Server tool events arrive through the ordinary event flow you met in Volume 2. A server tool call that Claude makes directly streams like a client tool call: a content block start event, then a series of events carrying fragments of its input. The result block does not stream. It arrives complete, in a single content block start event, with no deltas at all.

That makes sense — the input is generated token by token by a model, and the result is a finished thing produced by a service.

The advisor tool from Chapter 5 is the exception that proves the shape. Its sub-inference does not stream at all. The executor's stream simply goes quiet while the advisor works, with nothing but the protocol's keepalive pings roughly every thirty seconds, and then the whole result arrives at once. If you are building a progress indicator, that silence is a state you should design for instead of treat as a stall.

Batches behave the same way with one number changed. Every server tool works in a batch, the agentic loop runs as it does synchronously, and the per-turn iteration limit is higher. If the loop reaches that higher limit, the response ends with a paused turn, which you continue by submitting a follow-up request with the returned content — the same move as the synchronous case.

The workloads that suit this are the ones where the pattern repeats: enriching a dataset with information from the web, checking many documents against current sources, running analysis code over a pile of files. Which is a fair description of half of what Project Desk does at night.

The higher iteration limit in batches is a small detail with a real consequence for how you write the loop. A synchronous turn pauses relatively early, so an application handling live traffic sees paused turns often and continues them often. The same work submitted as a batch runs further before pausing, which means fewer continuations per item — but it also means an item that does pause has already done a great deal of work, and abandoning it because your continuation cap was tuned for synchronous traffic throws away more than it would have synchronously.

So the cap on continuations is worth setting per workload rather than once globally. A live request that has paused three times is probably in trouble. A batch item that has paused twice may be perfectly healthy and most of the way through a long research task.

There is a related note about the paused-turn shape that catches people converting synchronous code to batches. The continuation move is identical — submit a follow-up request carrying the returned content — but in a batch you are submitting a new item instead of continuing a stream, so the bookkeeping that tracks which item is a continuation of which original is yours to build. Nothing in the response tells you it is the third continuation of a particular piece of work.

So one contract, expressed three ways. Synchronously you check a stop reason. Streaming you watch events arrive in a particular order. In a batch you check a stop reason on each item. The shape does not change; the pace does.

Before leaving this chapter, one clarification about what the mixed-turn rule does *not* apply to, because over-applying it produces its own bug.

A turn containing only server tool calls needs nothing from you. Its result blocks are normally already present, the work is done, and reaching for a continuation is wrong. A turn containing only your client tools takes the same continuation path as always — the Volume 3 path — because there is no server tool queued behind anything.

So the handler you write for the mixed case is correct for all three cases, which is a pleasant property and the reason it is worth writing once, properly. Check for client tool calls; if there are any, run them and return only their results. Check for a server tool call with no result and no client call waiting; if you find one, re-send the response unchanged. Otherwise the turn is finished.

That single piece of logic covers a plain client turn, a paused server turn, a mixed turn, and — with the container detail from Chapter 13 — a paused script. Four situations, one branch structure.

A worked failure is the fastest way to make the rule stick. Suppose a request enables web search and a local inventory tool, and it works perfectly for weeks. Then somebody asks a question that makes Claude want both at once, and the request starts failing with a four hundred that says the turn already ended.

The cause is almost always that the application appends a status line to the message carrying its tool results — a timestamp, a note about which tool ran, something added for logging. Harmless for a plain client turn, because the turn was over anyway. Fatal for a mixed turn, because it closes an assistant turn that still has a queued search inside it.

Which is why this failure is characteristically intermittent and characteristically blamed on the model. The code did not change. What changed is that a user asked a question requiring two kinds of tool, and a line that had been harmless for a thousand requests became a protocol violation.

The fix is one line removed and sent as a separate message afterwards.

Project Desk handles the combined question. Claude asks for the fetch and the contract lookup together. Project Desk notices the fetch has no result, runs the contract lookup, and sends back a message containing exactly one tool result and nothing else — no commentary, no context, no helpful additions. The API attaches that result, runs the queued fetch, and Claude answers using both.

The answer is that Kestrel's terms changed nine days ago, the damage window shortened from thirty days to fourteen, and Project Desk's contract record still reflects the old window. Which is a useful finding, and it required two tools in one turn to produce.

It also means the conversation is now carrying a terms document, a contract record, a search history, and forty tool definitions. The next chapter adds all of that up.

---

## Chapter 12: Managing Tool Context

Project Desk's morning briefing request has stopped working, and the way it stopped is instructive.

It has not started failing. It succeeds every time. It is simply costing four times what it cost a month ago, taking noticeably longer, and producing answers that feel slightly less sharp than they used to. Nobody changed the prompt. What changed is that the request accumulated capabilities, one reasonable decision at a time, and each one brought luggage.

Add up what that request now spends before Claude writes a single word of the briefing.

Forty tool definitions, of which five are loaded and thirty-five deferred, so the loaded ones occupy the prompt. The supplier terms document from Chapter 3, which is roughly eleven thousand tokens of legal text. A contract record. Two search results from a follow-up question, each carrying page content. A memory file that Claude read at the start to recover where yesterday's work stopped.

None of that is waste. Every piece is there because something needed it. But all of it occupies the same working space, and it was all paid for before the briefing began.

That is the reframing this chapter exists to deliver. Every tool in this book has two prices. There is what it charges — a fee per search, a rate per container hour, or nothing at all. And there is what it puts into your context window, which you pay for in tokens on this turn and on every subsequent turn where it remains in the conversation.

The two are not correlated, and the second is usually larger.

Chapter 3 established the anchor figures, and they carry the argument on their own. A ten-kilobyte web page is roughly two and a half thousand tokens. A large documentation page is around twenty-five thousand. A five-hundred-kilobyte research paper is about a hundred and twenty-five thousand tokens. And web fetch charges nothing.

Set that against web search, which charges ten dollars per thousand searches as of this recording and is therefore the tool that looks expensive. A briefing that runs six searches has spent six cents on fees. A briefing that fetches one research paper has spent a hundred and twenty-five thousand tokens, on that turn, and again on the next turn, and again after that.

So the tool with a price tag is not the tool with the cost. Of the tools in this volume, web search and code execution add usage-based charges on top of tokens. Web fetch and tool search add nothing beyond tokens. And the ones that add nothing are perfectly capable of being the most expensive things in your request.

That relationship is the durable part, and it will outlast every figure quoted here.

Now the levers, and the useful thing about them is that you already know all five. They have appeared one at a time across seven chapters as parameters belonging to individual tools. Collected, they are a coherent toolkit, and they act at different points.

The first bounds how many times a tool may run. The use cap on web search and web fetch is the crudest instrument and sometimes the right one, because a request that searches four times instead of twelve has a quarter of the results in it. Two details from earlier chapters matter when you set it: failed fetches count against the cap, and web fetch has no default limit at all, so unbounded means unbounded until you say otherwise.

The second bounds how much any single result may contribute. The content cap on web fetch truncates a document instead of refusing it, which is the difference between reading the first section of a specification and not reading the specification. Its two limitations are the ones from Chapter 3: the cap is approximate, and it applies to text rather than to binary content — so the PDFs that produce the frightening numbers are exactly what it does not constrain.

The third controls whether results are echoed back to you at all. The March 2026 versions of web search and web fetch accept a response-inclusion setting. When a result was consumed by a completed code execution call in the same turn — filtered inside the sandbox, its useful part extracted — setting inclusion to excluded drops those nested call-and-result pairs from the response entirely. That cuts output token costs for agentic workflows where nobody needs the raw page content echoed back to the client.

There is a sensible safety property attached. Results from direct calls, and results from code execution calls that paused before completing, are always returned in full, because you might need to send them back on the next turn. The setting only removes what has already been consumed.

That third lever repays a second look, because it is the only one that acts on the *response* instead of on the request, and the distinction is where its value lives.

Consider what a filtered fetch actually produces. Claude fetches a page, code in the sandbox extracts the three relevant clauses, and Claude reasons over the clauses. But the full page content also travels back to you in the response, nested inside the call-and-result pair that the sandbox consumed. For an agent running unattended in a loop, that is a large payload delivered to a client that will discard it, on every iteration.

Excluding it removes that. And the reason the exclusion is safe is the safety property from a moment ago: only results that were *already consumed by a completed* sandbox call get dropped. Anything you might need to send back on the next turn — direct calls, and calls that paused before finishing — comes back in full regardless of the setting.

So the setting is not a general "send me less." It is specifically "do not echo what has already been used," which is a narrower and much safer thing to switch on.

The fourth is deferred loading from Chapter 6, and its effect is the largest of any lever here for a large catalogue. Thirty-five tool definitions that used to occupy the prompt on every request now occupy it on none. The property that makes it strictly better than it sounds is that deferred tools are stripped before the cache key is computed, so the prefix is untouched and the prompt cache survives.

The fifth is the one that does the most work per unit of effort, because Anthropic does it for you. Dynamic filtering, in the February 2026 and later web tools, has Claude write code that filters results inside the sandbox before they reach the context window. Only what survives arrives. You do not add the code execution tool for this; the API provisions it, and there is no additional charge for that provisioning beyond ordinary tokens.

That reframes the whole set. Four of these levers decide how much goes *out* — how many calls, how large a result, how many definitions. One decides what comes *back*. And the one that decides what comes back is where the leverage is, because the outbound side of a tool request was never the expensive part.

Choosing what returns is the skill this chapter is actually teaching.

Now the trade, because there is one, and it is not paid in money.

The dynamic-filtering versions of web search and web fetch are not eligible for Zero Data Retention by default. The basic versions — the March 2025 web search and the September 2025 web fetch — are. The newer ones are not, and the reason is mechanical: dynamic filtering relies on code execution internally, which changes what the request does with your data.

There is a way to have the newer tool version under a retention constraint. Setting the allowed callers on the tool to direct-only disables dynamic filtering and restores eligibility, restricting the tool to direct invocation and bypassing the internal code execution step.

Read what that means as a decision rather than as a configuration note. If your organization operates under Zero Data Retention, the cheapest context path is unavailable to you, and the tool that would have filtered results before they arrived will instead deliver all of them. Sometimes the cheaper request is the one you are not allowed to make, and a token budget built without knowing your retention posture is a budget built on the wrong tool version.

There is a related note for web fetch that is worth stating even when the configuration is eligible: website publishers might retain any parameters passed to a URL that Claude fetches from their site. Retention eligibility on Anthropic's side is not the same as data not travelling.

Two compatibility details, and then this chapter's boundary.

Context editing — the client-side mechanism that clears specific tool results out of a conversation — is documented as not fully compatible with advisor tool blocks. And the thinking-clearing variant, when configured to keep anything other than all turns, shifts the advisor's quoted transcript on each turn and causes advisor-side cache misses. Anthropic is careful about the severity there: it is a cost degradation only, and advice quality is unaffected.

Which is a genuinely useful shape of warning. Two features that both work, that both save money, and that partially cancel each other. Nothing fails. The savings just quietly do not appear.

And now the boundary, stated plainly so you know exactly where this volume stops.

Everything in this chapter is about what tools *put into* a conversation and how to put in less. What to do about a conversation that has already grown too long is a different subject, and it belongs to Volume 5.

Chapter 7 drew this boundary from memory's side and named the two mechanisms that live on the other side of it. What that chapter could not do, because it had not happened yet, is say where those mechanisms sit relative to the levers in front of you now.

They act at a different moment. Every lever in this chapter operates *before* content arrives: fewer calls, smaller results, filtered results, definitions kept out of the prompt. The next volume's mechanisms operate *after* content has arrived and the conversation has grown around it.

That means they are not alternatives, and reaching for the wrong one produces a characteristic frustration. If a request is expensive on its first turn, no amount of summarizing later will fix it — the cost was incurred on arrival, and the fix is in this chapter. If a conversation is fine on turn one and unmanageable by turn forty, no parameter in this chapter will help, because nothing here has any opinion about what happens to content already in the conversation.

The diagnostic is simply which turn the problem starts on. First-turn cost is a tool-configuration problem. Accumulating cost is a context-architecture problem, and it belongs to Volume 5.

One instrument this chapter has not mentioned is the one that tells you whether any of this worked, and it deserves naming even though its home is the next volume.

You can count the tokens of a request before sending it. Which turns every estimate in this chapter into a measurement, and turns the question "is this request too expensive" from a judgment into a number you can put in a test.

There is a limitation specific to the advisor tool. Token counting returns the executor's first-iteration input tokens only. For a rough advisor estimate you count separately, with the advisor model named and the same messages supplied — which follows from the point in Chapter 5 that a request with an advisor has two invoices, and counting only one of them counts one of them.

The habit worth forming from all of this is smaller than a budget process. When you add a tool to a request that already works, count the tokens before and after. The difference is what that tool costs you before it does anything, and it is usually larger than the guess.

A second application, outside Project Desk, shows why this matters more as systems get more capable instead of less. A customer-facing assistant with retrieval over a documentation set, a handful of account tools, and web search enabled for current pricing has three separate sources feeding the same working space. Each one was added by somebody solving a real problem. None of them was wrong. And the request that results can spend most of its budget on material irrelevant to the question actually asked.

The failure that produces is not an error. It is an assistant that gets gradually vaguer as it gets more capable, because the space it has to reason in keeps shrinking while the material it must reason over keeps growing. Which is a difficult thing to diagnose from the outside, and an obvious one to diagnose from a token count.

Project Desk's briefing gets trimmed with two levers rather than five, which is usually how this goes.

The thirty-five deferred definitions were already deferred, so that saving was banked. The change that mattered was moving to the dynamic-filtering version of web fetch, which meant the supplier terms document stopped arriving whole and started arriving as the three clauses anybody had ever asked about. And a content cap went on the fetch as a backstop for the day somebody points it at a specification.

The eleven thousand tokens of legal text became a few hundred. The briefing got faster, cheaper, and — because Claude was reasoning over three relevant clauses instead of hunting through eleven thousand tokens for them — noticeably sharper.

One cost survived all of it. Every tool call still requires a round trip: Claude asks, you answer, Claude continues. Forty records checked one at a time is forty round trips, and no parameter in this chapter touches that.

---

## Chapter 13: Programmatic Tool Calling

Somebody in finance wants to know which supplier accounts exceeded their agreed spending limit last quarter.

There are sixty accounts. Project Desk has a tool that returns one account's transactions. So the obvious implementation is the one Volume 3 taught: Claude asks for account one, Project Desk answers, Claude asks for account two, Project Desk answers, sixty times, and then Claude compares each account's total against its limit and reports the ones over.

That works. It is also close to the worst possible way to do it.

Sixty round trips, each one a full request with the entire conversation history attached. Sixty tool results landing in the context window, each carrying every transaction line for an account — thousands of lines of ledger data, almost all of it irrelevant, because what finance asked for is a list of names and the amounts they went over by. Perhaps a dozen lines of actual answer, arrived at by pulling several hundred kilobytes through the model.

The previous chapter's levers do not help here. A use cap would just truncate the work. A content cap would truncate the transactions. Deferred loading saves definitions, not results. Dynamic filtering applies to web results, not to your tools. Every one of those instruments assumes the expensive thing is what a tool returns, and here the expensive thing is the *conversation* — the sixty separate occasions on which a model had to be sampled in order to ask the next question.

Programmatic tool calling attacks that directly.

Instead of Claude calling your tool sixty times through the model, Claude writes a script that calls your tool sixty times, runs it in the code execution sandbox from Chapter 4, and gets back only what the script decided to return. The script loops, compares, filters, and produces the dozen lines. The individual transaction results never enter Claude's context window at all.

Anthropic's own example is close to this one: checking budget compliance across twenty employees, where the traditional approach requires twenty round trips and pulls thousands of expense line items into context along the way, and the programmatic approach runs a single script that does all twenty lookups, filters, and returns only the people who exceeded their limits — shrinking what Claude reasons over from hundreds of kilobytes to a handful of lines.

The reported effect on real benchmarks is worth stating with its attribution intact. On two agentic search benchmarks that test multistep web research and complex information retrieval, Anthropic reports that adding programmatic tool calling on top of basic search tools improved performance by an average of eleven percent while using twenty-four percent fewer input tokens.

Better *and* cheaper is an unusual combination, and the mechanism explains why it is possible here. Removing irrelevant data from the context window does not only save tokens. It also removes the material a model can get distracted by.

The requirement is the January 2026 code execution version or later, which means this feature and the sandbox are inseparable — it is the same container, with the same lifetime rules, the same absence of network access, and the same billing behaviour.

The flow has a shape that will feel familiar from Chapter 11 and means something slightly different.

Claude writes Python that invokes your tool as a function, possibly many times, possibly with logic around it. The code runs in the sandbox. When it calls one of your tool functions, execution *pauses* and the API returns a tool use block. You provide the result, and the code continues from exactly where it stopped, with the intermediate results staying inside the sandbox. Once all the code finishes, Claude receives the final output and carries on with the task.

Your tools are exposed to that code as asynchronous Python functions. Each takes a single dictionary of arguments and returns a string — the text of the tool result you send back. Because they are asynchronous, Claude can run many of them concurrently instead of in sequence, which is where the latency saving comes from on top of the token saving.

That return type has a consequence you can act on. The function returns a string, so if you want Claude's code to treat the result as structured data, it has to parse it — and it will do that far more reliably if your tool description says what the output format is. Anthropic's guidance is explicit: describe the output format in detail, and if you specify that the tool returns structured data, Claude will attempt to deserialize and process it in code. A vague description produces a script that does string manipulation on something that was meant to be parsed.

Two fields make this work, and one of them carries a warning that matters more than the feature.

The first is a field naming which callers may invoke a tool. It takes three useful values: direct, meaning Claude calls the tool itself in the ordinary way; a code execution version, meaning Claude calls it from inside the sandbox; or both. Anthropic's advice is to pick one rather than enabling both, because a single clear answer gives Claude better guidance than a choice.

The second is a field on every tool use block recording how the call was made. For a direct call it says so. For a programmatic call it names the code execution version and carries the identifier of the sandbox call that made it — so you can match each programmatic tool call to the script run that produced it.

Now the warning, and it is the sharpest instance in this book of a distinction that has been building since Chapter 8.

The field that restricts callers is not a security boundary.

Anthropic states it directly: it controls how the tool is presented to Claude, and it is validated against forced tool choice, but it is not a hard API-level block on direct invocation. Claude is strongly guided to respect it. Your client should still be prepared to handle a direct call for any tool it defines. And then, in as many words: do not rely on it as a security boundary.

That is exactly the shape of the allowlist from Chapter 8. An allowlist is a sign; a container is a lock. This field is a sign. It changes where Claude almost always goes. It does not decide where Claude can go.

The practical consequence is a specific piece of code you should write. If a tool is restricted to sandbox callers because calling it directly would be inappropriate — because it is expensive, or because its results should never reach the context window, or because it should only run inside a loop that validates something — then your handler still needs to cope with a direct call. Reject it if rejecting is right. But handle it, because the platform will not do that for you.

The continuation contract has one addition to the rule from Chapter 11, and one deadline.

The addition is the container. While a programmatic tool call is waiting for your result, the container identifier is *required* on the continuation request instead of optional. The API rejects a continuation that has pending programmatic calls and no container identifier, because the paused script lives in that container and there is no way to resume it without naming it. You also send the same tools array, including code execution, because the paused code needs it in order to run at all.

The deadline is four minutes. If your result does not arrive in roughly that time, the pending call raises a timeout error inside Claude's running code. Claude sees the error in the script's output and typically retries the call, which is graceful behaviour and not a reason to be casual about latency. Return each result well before the container's stated expiry, monitor that expiry, put timeouts on your own tool execution, and break long operations into smaller pieces.

That four-minute window is a real constraint on what tools belong in a programmatic loop. A tool that queries a database in fifty milliseconds is perfect. A tool that kicks off a report generation taking six minutes is not, and no amount of retrying will make it so.

The honest list of what this mode cannot do is short and worth having before you adopt it.

Tools with strict schema validation are not supported. You cannot force programmatic calling of a specific tool through tool choice — and if you name a tool in tool choice whose allowed callers do not include direct, you get a four hundred. Disabling parallel tool use is not supported. Tools provided by a connected outside tool server cannot be called programmatically at all.

And there is one schema restriction with a memorable error message. A tool whose input schema contains a recursive reference — a schema that refers to itself, directly or through a cycle — cannot be enabled for programmatic calling. Including a code execution caller for such a tool fails the request with a message about a circular reference being detected. The same schema is accepted perfectly well for direct calling.

The workarounds are the ones you would design yourself. Keep that tool direct-only, which does not prevent other tools in the same request from being programmatic. Or remove the cycle: unroll the recursion to a fixed depth and describe any deeper nesting in the description of the innermost level, or replace the recursive property with a plain object whose description explains the expected shape.

That second option is a reminder of something this volume keeps demonstrating. A tool description is not documentation attached to a schema. It is part of the interface, and it can carry meaning the schema cannot express.

There is a decision this chapter should make explicit, because it is easy to adopt programmatic calling as a default and it is not one.

The mode pays when the number of tool calls is large, the individual results are large, or the logic between calls is mechanical. Sixty lookups with arithmetic between them is the ideal case. Two lookups where Claude needs to think carefully about the first before choosing the second is the opposite case — there, the round trip *is* the work, and the model's judgment between calls is what you are paying for.

So the test is whether the reasoning between calls is something a script can do. If the between-step is comparison, filtering, aggregation, or a loop, put it in code. If the between-step is judgment, leave it in the conversation.

Getting that wrong in the ambitious direction produces something specific: a script that makes decisions Claude should have made, using logic Claude wrote in advance without having seen the data. Which is exactly the failure mode of writing the program before understanding the problem, expressed at machine speed.

A second application shows the mode at its best, and it is the one Anthropic's benchmark numbers come from. Multistep web research — where an agent searches, reads, follows a lead, searches again, and most of the intermediate material is irrelevant to the final answer — is almost pathologically suited to this. The research is a loop, the results are large, the filtering is mechanical, and the conclusion is small. That is the same profile as the sixty accounts, which is why one benchmark result generalizes to a completely different-looking task.

And a boundary that matters for anyone building on top of this: it does not compose with everything. The context levers from Chapter 12, deferred loading from Chapter 6, and container reuse from Chapter 4 all work alongside it. Strict schemas, forced tool choice, and connected outside tool servers do not. If your architecture depends on any of those three, the decision is made for you, and it is made before you write any code.

Project Desk answers finance with one script. Claude writes a loop over sixty account identifiers, calls the transactions tool for each concurrently, sums each account against its limit inside the sandbox, and returns four account names with the amounts they exceeded by.

Four names. Sixty tool calls, one round trip, and a context window that never contained a single transaction line.

The pattern generalizes past aggregation, and the variations are worth naming individually because each solves a different problem.

Early termination is the script stopping as soon as its criteria are met. Searching sixty accounts for the first three that breach a threshold does not require reading all sixty, and a loop that breaks is trivial to write in code and impossible to express as a sequence of model round trips — because the model would have to decide, after each result, whether to continue, which is another round trip.

Conditional selection is the script choosing which tool to call based on what a previous call returned. If an account is flagged, look up its dispute history; otherwise skip it. Done through the model, that branch costs a sampling step per account. Done in code, it costs an if statement.

Plain filtering is the case from the sixty accounts: a large result set reduced before anything reaches the model.

What those three share is that the decision between steps is mechanical. And the reason they matter more than they first appear is that a conversation cannot express them cheaply at all. Every branch, every loop iteration, every early exit in a conversational tool loop is a full request with the whole history attached. In code they are ordinary control flow.

So the saving is not really about tokens, although the tokens are real. It is that control flow belongs in a program, and a tool-calling conversation is an expensive place to put a for loop.

All of which are things a competent engineer would write by hand, expressed as a capability the model can reach for.

That is the last of the large optimizations. The remaining one is small, sharply defined, and about how quickly a tool's input arrives rather than what it contains.

---

## Chapter 14: Fine-Grained Tool Streaming

Something else about Project Desk feels slow, and not for any of the reasons the last two chapters addressed.

The support lead asks for a written summary of the Kestrel situation — the timeline, the claim, the terms change, what the contract says — as a document she can attach to the customer file. Project Desk has a tool that writes a file, and Claude calls it with the whole document as one argument.

She waits. Nothing appears. Then, several seconds later, the entire document arrives at once.

The document was being written the whole time. Claude generated it token by token, the way it generates everything. What she experienced as silence was the API doing something helpful on her behalf: buffering that argument, and validating it, before streaming any of it back.

That is a reasonable default and exactly wrong for this case.

Standard tool streaming buffers and validates each parameter value before sending it to you. For a small argument — an account number, a date range — the buffering is imperceptible and the validation is free insurance. For an argument that is three thousand words of prose, the buffering means you receive nothing until Claude has finished writing all of it.

Fine-grained tool streaming removes the buffering. The tool's input arrives as Claude generates it, without server-side buffering and without JSON validation, so the first fragment of a large parameter reaches you almost immediately. The fragments come through the same streaming events as standard tool use — nothing new to learn about the event flow itself.

You turn it on per tool, with a field on the tool definition set to true, and streaming enabled on the request. It applies to tools you defined yourself; it is not available on Anthropic's server tools.

The field is optional, and its behaviour with the older mechanism is worth knowing if you have existing code. There used to be a beta header that turned fine-grained streaming on for the whole request. That header still works, and it still enables the behaviour for tools that leave the field unset — but the per-tool field replaces it, and an explicit false on a tool keeps buffered streaming for that tool even when the request still carries the header. So the field wins, in both directions, which is the sane migration story.

Now the price, and it is stated in the documentation as bluntly as it deserves.

Because the API does not buffer or validate a tool's input before streaming it, you might receive partial or invalid JSON.

That is the whole trade. You get the input sooner; you get it unchecked.

There is a second way it can arrive broken, and it has nothing to do with the streaming. A response that stops because it hit the output token limit can cut a parameter off midway. That happens with or without fine-grained streaming — but with buffering, the server would have noticed the value was not valid; without it, you are the first thing in the chain that could notice.

So the obligation transfers to you: accumulate the fragments, and guard the parse.

The truncation case deserves separating from the invalid case, because they look identical at the point of failure and call for different responses. An input that is invalid because the model produced malformed structure is a modelling problem, and reporting it back lets Claude try again. An input that is invalid because the response ran out of output tokens partway through a three-thousand-word document is a budget problem, and reporting it back invites Claude to regenerate a document that will be truncated at exactly the same place.

The stop reason is what distinguishes them, and checking it is the difference between a retry that can succeed and a loop that cannot. If the response stopped at the token limit, the useful moves are to raise the limit and try again, or to keep the partial content and ask for the remainder — not to report a parse failure and hope.

That is a small illustration of something worth generalizing. Two failures that present the same way at the point of detection can have entirely different remedies, and the signal that separates them is often somewhere other than the failure itself. The parse error is in the accumulated string; the reason for it is in the stop reason on the message.

The accumulation contract is the same one standard tool streaming uses, which is convenient, because it means this section applies whether or not you turn the feature on. What changes is not how you assemble the input. What changes is whether the assembled result is guaranteed to be valid.

The contract has three steps. When a tool use content block starts, initialize an empty string. For each event carrying a fragment of the input, append that fragment to the string. When the block closes, parse the accumulated string.

There is one detail in that flow which looks like a bug and is deliberate. The event that starts the block carries an input field containing an empty object. Not the input — an empty object. It is a placeholder marking the slot in the content array. The actual value arrives afterwards as a series of string fragments.

So the block-start event says the input is an object, and the fragments that build the real input are strings. Anthropic notes that the type mismatch is by design: the empty object marks the position, and the delta strings build the value.

Several SDKs provide an accumulator that handles all of this. The manual pattern is for languages whose SDK does not, or for when you want control over how the input is assembled.

Anthropic makes a distinction there that is easy to miss and clarifies a genuine confusion: reacting to fragments and assembling them are separate concerns. You can print each fragment the moment it arrives — or write it to a file, or push it to a browser — while still letting the SDK's accumulator build the final value for you. The two are not alternatives. Watching the stream does not mean you have to own the assembly.

Which resolves a design question that comes up immediately. If the SDK is accumulating, how do you show progress? The answer is that you do both: react to the fragments for the user's benefit, and let the accumulator produce the value your tool actually runs on. Reach for the manual pattern only when there is no accumulator, or when you want to control assembly for some other reason.

One availability note, unusual in this volume because it is uncomplicated. Every model supports fine-grained tool streaming, on the Claude API and on all the major cloud providers. After fourteen chapters of platform matrices with holes in them, this one has none. It is the plainest feature in the book, and it is worth saying so instead of leaving you to assume there is a catch.

Two smaller behaviours round out what changes when the flag is on. The fragments tend to be longer, with fewer breaks in the middle of a word, because nothing is chopping them at validation boundaries. And without the flag, a large parameter produces nothing at all until Claude has finished generating it — so the difference is not "faster" so much as "something rather than nothing." And reacting to fragments and assembling them are separate concerns — you can print or forward each fragment as it arrives while still letting an accumulator build the final value.

That is exactly what makes the feature useful for Project Desk's document. Each fragment can go straight into the file, or straight to the support lead's screen, as it arrives. She watches the summary appear line by line instead of waiting for silence to end.

Then the parse, and this is where the feature demands something back.

When the accumulated input is not valid JSON, you cannot run the tool. There is nothing to run it with. And the correct response is not to repair it.

Report the failure back to Claude.

The recommended shape is specific and slightly more thoughtful than it first appears. Wrap the raw invalid string in a JSON object under a single key, serialize that, and return it as the content of a tool result with the error flag set — the same error-signalling convention from Volume 3.

Two reasons for the wrapper. It makes it unambiguous to Claude that what it produced was invalid JSON, instead of leaving Claude to infer that from a fragment of malformed text. And it preserves the original input for debugging, so the thing that went wrong is still in your logs in the form it arrived.

Anthropic adds one implementation note that is easy to skip and will eventually matter: build that wrapper with your JSON library rather than by concatenating strings, so quotes and other special characters in the invalid input get escaped correctly. Concatenating a broken string into a JSON envelope by hand produces a second broken string, which is an annoying bug to find.

There is also a decision to make when the input was truncated by the output limit instead of merely malformed. Check the stop reason. If the response stopped at the token limit, the input is not wrong so much as unfinished, and the useful responses are to retry with a higher limit or to repair the partial input deliberately. Those are different situations from a model producing genuinely invalid structure, and the stop reason is what distinguishes them.

A question this raises, and the answer is narrower than you might expect: when should you not turn this on?

Most of the time. The feature exists for one situation — a tool parameter large enough that waiting for it is noticeable — and outside that situation it trades a real guarantee for an imperceptible gain. A tool whose arguments are an account number and a date range gains nothing from unbuffered streaming, because the buffering of a twenty-character value takes no time worth measuring. What it loses is server-side validation, which was free.

So the decision is per tool, which is exactly why the field is per tool rather than per request. Turn it on for the tool that writes a document, the tool that generates code, the tool that takes a long block of prose. Leave it off for everything else, and the everything else keeps its validation.

That is a better arrangement than the beta header it replaced. A request-level switch turned the trade on for every tool at once, including the dozens for which it bought nothing, and that is a straightforward loss of safety for no benefit.

A second use case, away from Project Desk's document, is the one that makes the latency argument concrete. A coding assistant that writes a file through a tool call has the same shape: the argument is the whole file, the file is long, and a developer watching an empty editor for eight seconds experiences that as the assistant being slow instead of as the assistant being careful. Streaming the content as it is written turns a wait into progress, and progress is what people actually judge responsiveness by.

The same reasoning applies to any tool whose argument is the deliverable. When the parameter *is* the output — a document, a file, a long message — the user is waiting for the parameter, and buffering it means buffering the thing they asked for.

When the parameter is merely how you address the output, buffer it and keep the validation.

Which is the last instance in this volume of a pattern that has appeared in nearly every chapter. A capability arrives with a guarantee removed, and the guarantee lands on your application. Server tools removed the obligation to execute anything and added the obligation to round-trip results you cannot read. The memory tool removed the need to design a persistence interface and added the obligation to validate every path. Programmatic tool calling removed fifty-nine round trips and added a four-minute deadline. This feature removes a wait and adds a parse you have to guard.

None of those trades is bad. All of them are trades, and the pattern is worth recognizing on a tool you meet after this book, because the question generalizes: what did this convenience stop doing for me, and where did that job go?

For Project Desk it goes into about fifteen lines of handler code. Fragments accumulate into a string, the parse sits inside a guard, an invalid result comes back wrapped and flagged, and a truncated one checks the stop reason before deciding whether to retry.

The support lead watches the Kestrel summary write itself. First line to last, a few words at a time, the way a person would type it. The document lands in the customer file, and nobody waits for silence to end.

The tools are all in place now, and so are the mechanisms that hold them together. What has not been written down anywhere is who owns which piece of it — and on a Tuesday morning, a customer is about to ask a question that touches all of them at once.

---

## Chapter 15: Project Desk Becomes an Operator

A customer emails on a Tuesday morning. Their order is three weeks late, they have been told two different revised dates, and they want to know whether to keep waiting or cancel and buy elsewhere.

That question crosses every boundary this volume built. Following it once, end to end, is a better summary than any list of tools.

Project Desk starts local. It looks up the order in its own database with one of its own tools, the kind Volume 3 taught: a schema Project Desk wrote, running Python Project Desk owns, under validation and approval policy Project Desk enforces. The order is real, it is late, and its supplier is Kestrel Components. Nothing has left the building yet.

Then it needs something it does not have. Has Kestrel published anything since the last time anybody checked? That is web search, and the moment it runs, the work moves to Anthropic's infrastructure. Project Desk sends a tool entry and receives a result. It does not run an HTTP client, does not implement a redirect policy, and does not return a tool result — because the identifier on that call carries the server prefix, and a call with that prefix has already been answered.

The search finds a notice. Reading the notice properly means web fetch, still on Anthropic's side, and still constrained: it can retrieve that page only because the search result put the URL into the conversation first. Project Desk never handed Claude a destination, and Claude could not invent one.

The notice is long, and the version of web fetch Project Desk uses filters it inside a sandbox before any of it arrives — so what lands in the conversation is the two paragraphs about revised shipping windows instead of nine thousand tokens of notice. That filtering ran in a container on Anthropic's side that Project Desk did not configure and does not manage.

Then the question turns quantitative. Is this order unusual, or is every Kestrel order late by about this much? That is a query across the exceptions data, and it happens with a script Claude writes and runs in the code execution sandbox. Four thousand rows go into a container; a rate and a percentile come out. The rows never enter the conversation.

Then the contract. What does Project Desk's agreement with this customer actually promise about delay? That is a local tool again, back inside the building, reading a contracts table with credentials that belong to Project Desk and to nobody else.

And when Claude asks for the contract lookup and a second fetch in the same breath, the response comes back with a client tool waiting and a server tool queued behind it. Project Desk runs its lookup, sends a message containing nothing but that result, and the API runs the queued fetch and continues the turn.

Finally, Project Desk writes what it learned to a memory file, so that the next person asking about Kestrel starts from this morning's findings rather than rediscovering them. Which is a client tool — Project Desk's own storage, Project Desk's own handler, Project Desk's own path validation.

Six hops. Three of them ran on Anthropic's infrastructure, two ran on Project Desk's machines, and one ran in a container that Anthropic provisioned without being asked. At every hop, the question that identified the owner was the same one from Chapter 1: where does the work happen, and who owes the result?

The customer gets an answer with a citation, a delay figure in context, and a plain statement of what the contract entitles them to. It takes about forty seconds.

Now the part that a tool-by-tool tour cannot give you, which is what all of this adds up to as a set of decisions somebody has to own.

Fifteen individual settings do not add up to a policy. Across this volume, a consistent pattern has appeared: the platform provides controls that shape behaviour, and the guarantees live somewhere else. Naming that pattern once, properly, is more useful than remembering every parameter.

Start with credentials, because they are the least reversible thing in the list. Project Desk's local tools use credentials Project Desk holds. The Bash tool from Chapter 8 runs as a user with exactly the access the work requires, and the browser in Chapter 10 logs into the supplier portal with an account that can file claims and read nothing else. None of that came from a tool setting. It came from deciding, per capability, what the smallest sufficient access is.

Then reachability. The domain lists from Chapter 3 decide where the web tools may go, with the rules that trip people: one list or the other and never both, no scheme on the entries, subdomains included automatically, wildcards in the path and never in the domain. The precaution list from Chapter 10 applies the same idea to a whole desktop.

Two properties of that control deserve to be carried out of this book. Domain entries can be written in characters that render identically and resolve differently, so a list you verified by reading is a list you have not verified. And your organization-level configuration interacts asymmetrically with your request-level one: allowing a domain your organization has not allowed produces a validation error you will see, while a domain your organization has blocked is silently removed from your allowed list. One direction shouts and the other whispers, so when a domain you are certain you allowed is being ignored, that silent removal is the first thing to check.

Then enforcement, and this is the item most likely to be got wrong by a competent team, because the mistake is made out of diligence instead of carelessness.

Three of the controls in this volume are documented as guidance rather than as boundaries. The command allowlist from Chapter 8 is described by Anthropic itself as a tripwire for obvious mistakes, not an enforcement boundary, with isolation named as the real control. The caller restriction from Chapter 13 is documented as shaping how a tool is presented to Claude, with an explicit instruction not to rely on it as a security boundary. And the prompt-injection classifier from Chapter 10 is described as steering the model toward asking for confirmation, with an explicit note that it will not suit use cases without a human in the loop.

Every one of those is worth using. None of them is worth trusting as a guarantee. The things that actually enforce are the container, the least-privileged user, the validated path, the single-match requirement on an edit, and the human who clicks submit.

That leaves the confirmation points. The list in Chapter 10 is the sharpest guidance in the volume because it names a category rather than a rule. Accepting terms of service, completing a financial transaction, granting consent — what those share is that they create an obligation on somebody's behalf. A useful test is whether an apology would fix it. If it would not, that action stops for a person, regardless of how well the automation has been working.

For Project Desk, that is why the damage claim gets filled in automatically and submitted by hand.

Two more items belong on that sheet, and both are about money instead of safety.

The first is that the cost of a capability is not on its price page. Chapter 12 established the shape and it is worth restating as a line item: the tools that charge fees are web search and code execution, and the tools most likely to dominate your bill are web fetch and a large tool catalogue, neither of which charges anything. A governance sheet that lists per-use fees and omits context consumption describes about a third of the cost.

The second is that a request can have more than one invoice. The advisor from Chapter 5 is billed at a second model's rates and reported in a separate array, and cost-tracking code that reads top-level usage undercounts it silently. Anywhere a capability involves a second model or a second environment, check whether the accounting is in the place you are already looking.

There is one more decision that belongs to whoever operates this rather than to whoever builds it, and it is the one most likely to be discovered too late.

Data retention interacts with tool choice. The example in Chapter 12 is the concrete one: the dynamic-filtering versions of the web tools are not eligible for Zero Data Retention by default, because the filtering runs code internally, and the way to have them under that constraint is to disable the filtering — which is to say, to give up the thing you wanted them for. So an organization's retention posture silently determines which tool versions are available to it, and therefore how expensive its context is.

That is an awkward coupling, and it is not the kind of thing that shows up in a design review, because retention lives with one team and tool versions live with another. Naming it on the sheet is how it stops being a surprise.

The last thing to say about this volume is about its shelf life, and saying it plainly is more useful than pretending otherwise.

Almost every specific fact in these fifteen chapters is dated. The roster of which tools run where is a photograph taken in late July 2026. The prices — ten dollars per thousand searches, five cents per container hour, one thousand five hundred and fifty free hours a month — are current as of that recording and nothing more. The beta headers for the advisor tool and computer use will graduate or change. The version strings will accumulate new dates.

Platform availability is the most volatile of all, and worth one concrete example of how uneven it is. As of the snapshot, web search is unavailable on one major cloud; web fetch, code execution, and programmatic tool calling are unavailable on two; one cloud offers only the basic web search without dynamic filtering; and one requires a particular deployment type for several of these tools. Server-side tool search on one provider is available only through an older interface, not the newer one. None of that is a stable fact about the world. All of it is a snapshot of a rollout in progress.

There is a small piece of evidence for how fast this moves, drawn from making this series. When Volume 3 was recorded a week before this one, the same documentation pages showed a different model in their examples than they show now. One week, one changed name, in prose that was describing something else entirely.

So the durable material is not the roster. It is the questions.

Where does this work happen, and who owes the result? What did this convenience stop doing for me, and where did that job go? Is this setting a sign or a lock? What does this tool put into my context window, as distinct from what it charges me? Is this version string an upgrade, or a different contract keyed to something I should check? Which of these actions would an apology not fix?

Those questions will still work when the roster has turned over twice. They are what lets you read a tool you have never met — one that ships next year, with a name nobody has thought of — and know within a few minutes where its risks live.

One of those questions deserves converting into a habit instead of left as a principle, because it is the one you will use most often and the one that is easiest to get wrong under pressure.

When a response comes back and something is unfinished, ask whether one of your own tools is waiting for a result. If it is, send the results and nothing else — no timestamps, no notes, no text of any kind — and the API will run whatever server-side work was queued behind them. If nothing of yours is waiting and the turn is still unfinished, send the response back exactly as it arrived.

Two questions, and they cover a plain client turn, a paused server turn, a mixed turn, and a paused script. The only addition is the container identifier when a sandboxed script is what is waiting.

That is the piece of Chapter 11 worth carrying out of the book, because it is the one that produces a bug rather than an inefficiency when you get it wrong. Everything else in this volume, done badly, costs money or clarity. This one, done badly, returns a four hundred that names neither mistake.

The version of this habit that scales is to write the branch once, in one place, and route every response through it — instead of handling tool continuation wherever each feature happened to be added. The three-line logic is the same for every tool in this volume, which is a design gift and easy to squander by discovering it four times.

Project Desk is now something different from what it was at the start of Volume 3. Then it was an application that could call its own tools carefully. Now it operates capabilities across three different kinds of boundary, and it can produce, on demand, a sheet naming what runs where, under whose credentials, reaching which destinations, with which decisions reserved for a person.

That sheet is the deliverable. Not the tool list.

What Project Desk still cannot do well is decide what to keep. It carries a terms document it may not need again, a search history nobody will read, a memory directory growing without a policy, and a conversation that will eventually run out of room no matter how carefully each tool is configured. Managing that space — caching it, counting it, editing it, compacting it, and deciding what a long-running application should retain at all — is the subject of the next volume.

---

## Sources and Drift Notes

This appendix is written to be read, not narrated. It is deliberately excluded from the audiobook spine and from the narrated word count.

Source snapshot

Every claim in this volume was taken from the official Claude Platform documentation as it stood on **2026-07-25**. Eighteen pages were captured and hashed; the manifest lives with the production run. Volumes 1 through 3 of this series were built against earlier snapshots, and at least one difference is already visible: the server tools examples showed a different model name one week earlier than they do here.

How to read the dated material

Of the 100 recorded claims, 56 describe durable mechanisms, 42 are dated facts true at the snapshot, and 2 describe capabilities that were in beta. Prices, quotas, model names, tool version strings, beta headers, and platform availability are all in the dated category. Check the live page before relying on any of them.

Pages consulted

- <.../code-execution-tool> — 1 claims - <.../programmatic-tool-calling> — 1 claims - <.../web-fetch-tool> — 1 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool> — 11 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool> — 6 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool> — 7 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool> — 6 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming> — 4 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool> — 7 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview> — 1 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling> — 8 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools> — 15 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool> — 3 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference> — 5 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool> — 10 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool> — 9 claims - <https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool> — 8 claims

Recorded uncertainty

**UC-001 — What is the additional input-token cost of the current text editor tool version?**

The tool reference publishes a figure for the superseded text_editor_20250429 and none for the current text_editor_20250728.

Disposition: `unresolved-do-not-assert` (claims CP4-072, CP4-074)

**UC-002 — Which per-model additional-token figure should the narration quote for the Bash tool?**

The page gives 325 tokens for one model set and 244 for another; both are dated per-model values.

Disposition: `resolved-narrate-one-dated-example` (claims CP4-067)

**UC-003 — How long does an idle code execution container survive?**

The code execution page describes checkpointing after about five minutes with restoration inside thirty days; the programmatic tool calling page describes idle containers as reclaimed after about five minutes.

Disposition: `resolved-narrate-durable-shape` (claims CP4-038, CP4-088)

**UC-004 — Do the published advisor performance figures generalize beyond Anthropic's own tests?**

Every advisor figure comes from Anthropic internal testing at small sample sizes, and the page instructs readers to validate on their own workload.

Disposition: `resolved-attribute-never-generalize` (claims CP4-048, CP4-050, CP4-084)

**UC-005 — Which model appears in the server tools examples?**

The 2026-07-18 snapshot used for Volume 3 shows claude-opus-4-8 where the 2026-07-25 snapshot shows claude-opus-5.

Disposition: `resolved-usable-as-dated-illustration` (claims CP4-005, CP4-099)

What this volume deliberately does not cover

Context windows, token counting, prompt caching, cache diagnostics, compaction, context editing, mid-conversation system messages, the Files API, Skills, the MCP connector, and cloud platform differences belong to Volume 5. Prompt engineering and evaluation belong to Volume 6. Errors, rate limits, retries, and cost optimization as disciplines belong to Volume 7. Managed Agents belong to Volume 9. Where a tool in this volume genuinely depends on one of those subjects, the narration names it and declines to teach it.

Attribution

Anthropic's documentation and API reference are the primary sources. All explanatory prose, analogies, worked examples, and the Project Desk case study are original to this book. Performance figures attributed to Anthropic's own testing are reported as such, with the sample caveats the source states.
