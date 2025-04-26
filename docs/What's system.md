# Service Idea Generation System Using LM Studio: Specifications

## Overview
This system utilizes LM Studio's Large Language Model (LLM) to automatically generate innovative service ideas by combining multiple elements and selecting the best ones. It performs AI-driven visionary service design by combining elements read from a CSV file.

## System Requirements
- Python 3.8 or higher
- LM Studio (Local LLM server)
- Required Python packages:
  - openai (AsyncOpenAI)
  - asyncio
  - Other standard libraries (csv, random, json, time, os, datetime, signal, sys)

## Configuration Parameters

| Variable Name | Default Value | Description |
|:--|:--|:--|
| LMSTUDIO_BASE_URL | "http://localhost:1234/v1" | The API endpoint URL for LM Studio. Add `/v1` to the URL displayed after starting LM Studio and pressing the "Start" button. |
| API_KEY | "lm-studio" | The key used for LM Studio API authentication. Required for OpenAI compatibility, but actual authentication is not performed. |
| MODEL_NAME | "gemma-3-12b-it" | The name of the LLM model to use. Others like "deepseek-r1-distill-qwen-32b" or "qwen2.5-bakeneko-32b-instruct" can also be used. |
| CSV_FILENAME | "q.csv" | The name of the CSV file containing the list of elements used for idea generation. |
| GOOD_SERVICE_FILENAME | "good-service.json" | The name of the JSON file to save the selected excellent service ideas. |
| ALL_IDEAS_FILENAME_PREFIX | "all_ideas_" | The prefix for the filename where all generated ideas are saved. A timestamp will be added to the actual filename. |
| IDEAS_PER_CYCLE | 5 | The number of ideas to generate per cycle. |
| NUM_ELEMENTS_TO_COMBINE | 3 | The number of elements to combine when generating ideas. Combines three elements in the format "Element1 × Element2 × Element3". |

## System Prompts
Two types of prompts are configured in the system:

1.  **Visionary Designer Prompt (VISIONARY_DESIGNER_SYS_PROMPT)**:
    *   Detailed system prompt used during idea generation.
    *   Provides the role of a visionary service designer and guidelines for idea generation.
    *   Includes perspectives such as the core concept, experience design, and roadmap for social implementation.

2.  **Selection Prompt (SELECTION_SYS_PROMPT)**:
    *   Prompt used when selecting superior ideas from the generated ones.
    *   Sets the evaluation perspective as a business analyst.

## Main Features

### 1. Initialization and Connection Test
- Initialize the AsyncOpenAI client.
- Test the connection to the LM Studio API.

### 2. Loading Elements from CSV
- Load the list of elements from the specified CSV file.
- Verify if there are enough elements.

### 3. Service Idea Generation
- Generate service ideas based on combinations of randomly selected elements using AI.
- Generate IDEAS_PER_CYCLE ideas in parallel using asynchronous processing.
- Extract the following information from the generated ideas:
  - The combination of elements used.
  - Service name (extracted from the AI's response).
  - Detailed text of the idea (raw_text).

### 4. Best Idea Selection
- Select up to three superior ideas from the generated ones.
- Output the results including the idea number, service name, and selection reason.

### 5. Data Saving
- Save all generated ideas to a JSON file with a timestamp.
- Save the selected excellent ideas to the specified JSON file.

### 6. Control Flow
- Processing occurs in cycles.
- Signal handling (safe shutdown with Ctrl+C).
- Efficient execution through asynchronous processing.

## Execution Flow
1. Initialize the OpenAI client.
2. Test the API connection.
3. Load elements from the CSV file.
4. Execute the following in each cycle:
   - Create idea generation tasks with random element combinations.
   - Generate ideas using parallel processing.
   - Save all generated ideas to a JSON file.
   - Select the best ideas and save them to a separate JSON file.
   - Wait before the next cycle (5 seconds).
5. Terminate safely upon receiving a signal or encountering an error.

## Error Handling
- Client initialization errors
- API connection errors
- File reading errors
- Insufficient number of elements error
- Errors during idea generation
- Errors during best idea selection
- File saving errors

## Constraints
- LM Studio must be running and the model loaded.
- The CSV file must contain a sufficient number of elements (at least NUM_ELEMENTS_TO_COMBINE).
- Requires sufficient system resources due to heavy parallel processing.

## Output Files
1.  **all_ideas_[timestamp].json**: All ideas generated in each cycle.
2.  **good-service.json**: Excellent ideas selected in each cycle (up to 3).