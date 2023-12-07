# 🚀 CodeLearn Agent

CodeLearn Agent is a Python project designed to facilitate the learning of code. It includes several modules that each serve a specific purpose in the learning process.

## 📚 Modules

- 🔀 Splitter: This module provides an abstract base class for splitting text into chunks. It defines a `ChunkInfo` data class and a `Splitter` abstract base class with a `split` method that takes a `FileTree` and returns a list of `ChunkInfo`.

- 💾 Storage: This module provides classes for storing and retrieving project information. The `ProjectStorage` class has methods for storing a project and retrieving a project by its ID, repository URL, or local directory. The `ProjectCache` class provides a cache for projects, and the `ProjectStorageManager` class manages the storage and cache.

- 🧠 LLM: This module provides a function for asking questions using the CodeLearn Agent. It uses the OpenAI API to translate the question into multiple languages and infer hypothetical code. It then retrieves similar documents and codes and asks the question again.

- 📖 Example: This module provides an example of how to use the CodeLearn Agent in a web UI using the Gradio library. It also includes examples of how to use the CodeLearn Agent to ask a question, create a project, and retrieve code from a GitHub repository. There is also a custom agent demo that uses the OpenAI API and the CodeLearn Agent to answer questions.

- 🛠 Tools: This module provides a tool for automating the exploration of project directory structures. The `DirectoryStructViewTool` class provides a structured view of specified directories within the project.

- 🔍 Retrieval: This module provides an abstract base class for retrieving documents. The `Retriever` class has an abstract `retrieve` method that takes a query and returns a list of documents.

- 📑 Index: This module provides an abstract base class for indexing projects. The `Indexer` class has an abstract `index` method that takes a project, a splitter, an embedding, and a vector database.

- ⛓ Chains: This module provides a chain for retrieving code from a vector database. The `CodeRetrivalChain` class retrieves code based on a question and ranks the results.

- 📂 Project: This module provides a `Project` class that represents a project. It includes the project ID, local directory, source content, repository URL, and last updated time.

- 🤖 Agents: This module provides a custom output parser for the CodeLearn Agent. The `CustomOutputParser` class parses the output of the language model and determines whether the agent should finish or take an action.

- 📦 Loader: This module provides abstract base classes for source providers and project loaders. The `SourceProvider` class has an abstract `fetch_contents` method that returns a `FileTree`. The `ProjectLoader` class has an abstract `load_project` method that takes project information and returns a `Project`.

- 🔧 Utils: This module provides a utility function for processing file paths. The `process_file_paths` function takes a string of file paths and returns a list of processed paths.

## 📖 Usage

Here are some examples of how to use the CodeLearn Agent:

1. GPT Action API: This is a FastAPI application that provides endpoints for interacting with the CodeLearn Agent. It includes endpoints for getting the project structure, getting the files in a sub-directory, and getting the contents of a file. It uses the `ProjectManager` class to create a project, get the project structure, and get the contents of a file. It also includes a middleware example and a main entry point with settings dependency.

2. Ask Code Web UI: This is a Gradio application that provides a chat interface for interacting with the CodeLearn Agent. It uses the `AskCodeWithMemory` class to ask a question and get a response. The `AskCodeWithMemory` class uses the OpenAI API to translate the question into multiple languages and infer hypothetical code. It then retrieves similar documents and codes and asks the question again.

3. Ask Code Chain: This is a script that uses the `ask_by_chain` function to ask a question using the CodeLearn Agent. The `ask_by_chain` function uses the OpenAI API to translate the question into multiple languages and infer hypothetical code. It then retrieves similar documents and codes and asks the question again. The script also includes code for creating a project, getting a project, and retrieving code.

4. Ask Code Agent: This is a script that uses the `AskCodeWithMemory` class to ask a question and get a response. The `AskCodeWithMemory` class uses the OpenAI API to translate the question into multiple languages and infer hypothetical code. It then retrieves similar documents and codes and asks the question again.

Each of these examples demonstrates a different way to use the CodeLearn Agent. The GPT Action API provides a web API for interacting with the CodeLearn Agent, the Ask Code Web UI provides a web UI for interacting with the CodeLearn Agent, the Ask Code Chain demonstrates how to use the CodeLearn Agent in a script, and the Ask Code Agent demonstrates how to use the CodeLearn Agent in a chatbot.
