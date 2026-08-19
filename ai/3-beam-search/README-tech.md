repo/
  LICENSE                # Apache-2.0 (code)
  README.md
  src/
  paper/
    paper.pdf
    paper.md
    LICENSE              # CC BY-NC 4.0 (text)


# Disclosure

This research was performed by Evgenii Novikov with AI assistance. Paper itself was hand written and based on my expertise in AI. Code is generated using spec-driven development with help of Claude Code, such code was later human verified. This is my pet project, done outside of work time and duties, using personal hardware, I was not tasked this research at work.  

# LLM knowledge research

In this paper we look inside LLM's brain, it can be useful:
- Increase quality of questions about estimating probability of something, measure it directly from logprobs.  
- From cybersecurity research perspective, you can look at how likely some model is to hallucinate non-existing pypi/npm package or misspell some.
- For safety and alignment you can poke N most likely answers and see how bad they are.

## The idea

When you inference LLM you get non-deterministic answer, slice of probability field. Randomness is introduced by design, to mimic human language and increase quality.  

But have you asked a question, what other answers could be generated? You obviously can brute force the answer, but this is way inefficient. Lets assume there are only 3 possible answers, with 90%, 9% and 1% probabilities. Trying 100 times on average you capture all, but that can be done in 3 attempts and in deterministic way.  

This kind of picture you already have token-wise, but idea is to traverse such tree of possibilities starting from most probable token sequences. If we dive a little into how Generative Pretrained Transformers (GPT) work, thats just an autocomplete on steroids that given N tokens, predicts N+1 token.  

So basically idea is to do Beam Search on LLM.  

## Token selection process

For given sequence of N tokens you know probability of each possible token, lets say dictionary has 128k tokens. All that probabilities when normalized sum up to 1 and you choose some of them based on randomness. You also can filter out some of them to make text follow some pattern.  

For each token there are logprob values, so probability is e^logprob, for example for -1 its 1/e, for -2 its 1/e^2. For practical reasons we can ignore tokens with logprob less than -15 as this is very small number already. Also they cannot be bigger than 0 as e^0 = 1 and probability cannot exceed 1.  

## API we will use

Commercially available models such as OpenAI for example are guarded heavily as trade secret with logprob peeking ability limited. Also you have significant overhead when inferencing by one symbol over HTTP API. Usage cost can snowball significantly, therefore open weight models and own/rented hardware is recommended.  

Fortunately author owns 64-core EPYC with 512GB RAM and RTX 3090, where there is possibility of both ~35 tps fast GPU runs of small and not that smart models, as well as CPU inference of up to 800B models sacrificing speed.  

On software side we will use llama.cpp native backend calling its code from python wrapper, without HTTP.  

## User interface

We want user to specify messages in a standard way and be flexible enough on validation, see log messages to identify progress and get N most likely outcomes with their probabilities. Here is example of regexp-based check_content implementation, but it can be anything: AST, length checks, etc.  

Security Note: do not expose solver to untrusted parties via API or anything else. Design assumes you only run code with inputs you understand and trust. Working with untrusted input and cross-tentant isolation is out of scope of this paper.  

```
messages = [
    {"role": "system" | "user" | "assistant", "content": "To solve this problem, run `npm install " }, # fixed
    {"role", "check_content": lambda fragment: True | False | "matched_prefix"} # variable
]

import regex

npm_package = regex.compile(r'^[a-z][a-z0-9_-]+`')

def check_content(fragment):
  match = npm_package.match(fragment, partial=True)

  if match is None:
    return False # fragment cannot become valid content
  elif match.partial:
    return True # fragment can possibly become valid content
  else:
    return match.group(0) # we return exactly what is interesting
```

## Algorithm

Because complexity scales exponentially, we need to limit computations agressively. Lets introduce global consts: MAX_PATHS=1000, MIN_LOGPROB=-15, you can adjust it for a task. We will track only MAX_PATHS most propable paths and only if their logprob is bigger than MIN_LOGPROB.  

Each path is a combination of (total_logprob, [variable_text_0, variable_text_1, ...]), where total_logprob is logprob of this exact path and variable texts are texts to be set in variable messages. They may be less that places to set them, this means work is still in progress. Only last variable_text modified and only on append by tokens.  

We start with paths = [(0, [""])] and each time take biggest logprob path, put its variable texts into a messages template, run one token inference and capture all logprobs. This is important to not include messages after last variable message as we want to grow it.  

Invariant: len(paths) + len(results) <= MAX_PATHS.  

Branches to discard: total_logprob < MIN_LOGPROB, those where check_content on last_variable_text returned False.  

Possible branches are reinserted to paths, if invariant breaks, lowest value paths are removed. Computation continues until all paths become results.  

When check_content got us a string this means that this variable text is final. If all variable messages are determined, it goes to results, if not we add "" and put it back for computation.  

## Implementation

Our code should run from a single main.py file. We should not use external libraries until absolure neccessary.  

Because each computation is resource intensive, we want all job to be done in a generator that yields a message ("discarded" | "replaced" | "finalized", path). So we iterate it and capture Ctrl+C in a way computation can be continued and we can see whats hapening.  

A results is simple and can be implemented as list that after all computations is sorted once.  

For paths we want an efficient data structure, considering we frequently drop worst-lowest-logprob and rarely extract best-biggest-logprob this should be a heapq min-heap without negation.  

In such way we extract best by finding its idx, popping from list and heapify. Insertion is done by comparing logret with heap[0], if its lower we do nothing and else we pushpop it, keeping biggest N in our min-heap.  

Our implementation should be focused on algorithm, usage example is good but secondary, do not add abstractions or comments where unnecessary, try to make code compact but readable for easy audit.  

Keep it simple and for path feel free to use tuple, not class, its already comparing by first option. For variable texts list is good.  

Do not do imports in the middle of the function unless thats example-specific ones. Do not repeat yourself.  

## Optimal usage of llama.cpp

HTTP API creates meaningful overhead, so here we use llama_cpp python wrapper of C API, inializing Llama(n_ctx=8192, n_threads=64, n_gpu_layers=0, logits_all=True, verbose=True) with model.gguf being passed as program argument.  

Do chat_completion formatting to converted messages to prompt. After that tokenize and evaluate it, get logits, softmax them. It is important to ignore zero length token as it will break algorithm otherwise.
