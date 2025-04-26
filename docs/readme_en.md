# Service Idea Generation System

## Overview
This system is a tool that uses LM Studio to automatically generate, evaluate, and select innovative service ideas by combining multiple elements. It reads elements from a CSV file, randomly combines them, and performs visionary service design using AI.

## Features
- Creative idea generation by combining multiple elements
- Idea construction from the perspective of a visionary service designer
- Efficient idea generation through parallel processing
- Idea evaluation and automatic selection of promising ideas
- Saving all generated data in JSON format

## Prerequisites

### Required Environment
- Python 3.8 or higher
- LM Studio (local LLM server)
- Required Python packages:
  ```bash
  pip install openai asyncio
  ```

### LM Studio Configuration
1. Install and launch LM Studio
2. Download the desired model (default: `gemma-3-12b-it`)
3. Load the model and click the "Start" button to launch the API server

## Configuration Parameters

| Variable Name | Default Value | Description |
|:--|:--|:--|
| LMSTUDIO_BASE_URL | "http://localhost:1234/v1" | LM Studio API endpoint URL. This is the URL displayed after clicking the "Start" button in LM Studio, with `/v1` appended. |
| API_KEY | "lm-studio" | LM Studio API authentication key. Not actually used for authentication. |
| MODEL_NAME | "gemma-3-12b-it" | Name of the LLM model to use. |
| CSV_FILENAME | "q.csv" | Name of the CSV file containing the list of elements. |
| GOOD_SERVICE_FILENAME | "good-service.json" | JSON file to save selected promising ideas. |
| ALL_IDEAS_FILENAME_PREFIX | "all_ideas_" | Prefix for the files saving all ideas (a timestamp will be appended). |
| IDEAS_PER_CYCLE | 5 | Number of ideas to generate per cycle. |
| NUM_ELEMENTS_TO_COMBINE | 3 | Number of elements to combine when generating ideas. |

## Usage

### Preparation
1. Prepare the element list in the `q.csv` file
   - Write one element per row or cell
   - At least `NUM_ELEMENTS_TO_COMBINE` (default: 3) elements are required

### Execution
```bash
python service_idea_generator.py
```

### Operation
- The program automatically runs in cycles
- There is a 5-second wait time between cycles
- You can safely terminate with `Ctrl+C`

## Output Files
1. **all_ideas_[timestamp].json**
   - All ideas generated in each cycle
   - Filenames are distinguished by timestamps

2. **good-service.json**
   - Selected promising ideas from each cycle (up to 3)
   - Updated each cycle

## Output Data Format
The generated JSON files contain the following information:

```json
[
  {
    "elements": ["Element1", "Element2", "Element3"],
    "raw_text": "Full text of the generated idea",
    "service_name": "Extracted service name"
  },
  ...
]
```

## Customization
- Change `MODEL_NAME` to use a different LLM model
- Adjust `NUM_ELEMENTS_TO_COMBINE` to change the number of elements to combine
- Adjust `IDEAS_PER_CYCLE` to change the number of ideas generated per cycle
- Modify the system prompt to adjust the AI's output style or perspective

## Error Handling
- A connection error will be displayed if LM Studio is not running
- An error message will be displayed if the CSV file is not found or has insufficient elements
- Errors during idea generation are logged, and processing continues where possible

## License
This tool is provided as open source.

## Notes
- Be mindful of system resource usage (parallel processing may increase CPU/memory usage)
- The quality of generated ideas depends on the performance of the LLM model