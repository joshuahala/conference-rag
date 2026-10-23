# Conference RAG — Written Reflection

**Custom feature (deliverable 4):** Shared semantic answer cache — after embedding a question, we compare it to past questions with cosine similarity. If it is close enough (threshold 0.88), we reuse the stored GPT answer instead of calling `generate-answer` again.

---

## 1. Security Architecture

Draw or describe a diagram showing what protects each sensitive asset in this application. Your answer should address:

- Why is the anon key safe to expose in `config.public.json`?
- What would happen if someone got the service role key?
- How do Edge Functions protect the OpenAI API key?
- What role does Row Level Security play?

## **Answer:**

The database is protected by the service role key and by RLS. The anon key is used by browser applications to access the DB in only ways that it is authorized. RLS sets policies on what kind of operations are allowed by who in the actual tables. Our anon key in the app can write to page_views and with the jwt can select from embeddings, call embed-question and generate-answer. It only has access to act in ways the app is meant to act. The service role key is the admin key for the database and skips RLS. It can do whatever it wants. If someone got their hands on it, they could wreck our project. Edge functions also protect our AI key, because instead of having the client browser call OpenAI, it calls the edge function. Users can inspect code on the client browser, but they can't on the edge function. The edge function then uses a secret variable to call OpenAI and return the response.

## 2. Edge Functions & the "Secure Middle"

Why can't we call OpenAI directly from the browser? Explain the flow: browser → Edge Function → OpenAI. What role does JWT verification play in this chain? How does this pattern apply to other production applications?

## **Answer:**

Calling OpenAI directly from the browser would expose our secret and our code to the users. Having the edge function in the middle is secure because it is not transparent to users. A logged in user sends a request to the edge function along with the jwt token which validates them as a registered user. The edge function accepts the jwt token and then uses our OpenAI secret we have stored on the server to make the AI request. This is the same pattern that is used for lots of different services, not just OpenAI.

## 3. From SQL to Semantics

Compare keyword search (SQL `ILIKE`) vs semantic search (vector cosine similarity):

- When would each be better?
- Give a specific query example where one succeeds and the other fails
- What makes semantic search "understand" meaning?

## **Answer:**

SQL 'LIKE' searches for matching strings and only returns results that have an exact match, or match a regex expression. If you don't know the exact words you are looking for, it will be difficult to find what you want. Semantic search using cosine similarity uses the embeddings. It measures the angle between two vectors, to see how similar they are in direction. If two embeddings are similar in direction, it means they have similar meaning or are related to each other. We can use this to find how similar two sentences, podcasts, etc are.

## 4. RAG vs Fine-Tuning

We used RAG instead of fine-tuning a model on conference talks. Research what fine-tuning is, then explain:

- What are the trade-offs between RAG and fine-tuning?
- Why did we choose RAG for this application?
- When might fine-tuning be the better choice?

**Answer:**
Fine-tuning a model involves training it on data, essentially creating a new type of model. It changes its neural network weights so that it learns the content it digests. If we train it on the conference talks, it will start to sound like the authors of the talks, and be able to dispense their ideas from memory. Our RAG is still the same GPT model underneath, it just now has access to new data. If we want to add new data, no problem. However, with a fine-tuned model, we would have to train it on the new data. RAGs are more flexible and cheaper up front. fine-tuned models take a while to train but can be very good at what they do, and after all the training is done, they can be cheaper to run.

---

## 5. AI-Assisted Development

Briefly describe how your AI coding assistant helped you during this assignment:

- What did it do well?
- Where did you need to guide it?
- What did you learn about working with AI tools?

**Answer:**
I think it did a good job of keeping me on track. It was able to follow the instructions of the project and help me through each step. It was helpful for answering questions in context of the project. It was helpful to give it access to my tools so that it can do setup and crud operations faster than I could. I have been working with AI tools for a little while now, so it is not so new to me, but there is still a lot more to learn about optimization. And also the different ways you can use it. Sometimes you want to move fast and other times you want to take your time and learn as you go. Having specific rules, boundaries, and prompts for different projects can really make a difference in how you interact with the AI.
