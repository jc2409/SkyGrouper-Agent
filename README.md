# SkyGrouper Trip Planner

![SkyGrouper](./images/SkyGrouper.png)

**SkyGrouper** is a MCP-based AI-Agent service that suggests optimal travel destinations and flight itineraries for a group of travelers departing from different airports. It combines user interests with budget constraints and leverages an Agent for detailed planning.

![SkyGrouper Demo Video](./images/demo.mkv)

## Features

* SkyScanner MCP Server
* Shortlisting of candidate cities based on group interests
* Concurrent LLM-powered destination overview and flight plan generation
* Multi-origin support with individual budgets
* MongoDB integration for storing and retrieving trip requests

## Prerequisites

* Python 3.8+
* MongoDB (local or hosted)
* OpenAI API credentials (configured via `agent_helpers`)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jc2409/SkyGrouper.git
   cd SkyGrouper
   ```
2. Create a virtual environment and install dependencies:

   ```bash
   uv init
   source .venv/bin/activate
   ```

## Configuration

1. Copy the sample environment file and set your variables:

   ```bash
   cp .env.example .env
   ```
2. In `.env`, configure:

   ```ini
    SKYSCANNER_API_KEY=""
    OPENAI_API_KEY=""
    MONGO_URI=""
   ```

## Database Seeding

Insert a sample trip document for testing:

```js
db.groupTrips.insertOne({
  createdAt: new Date(),
  users: [
    { from: "LHR", dates: { start: "2025-06-01", end: "2025-06-10" }, budget: { max: 1500 }, interests: ["culture","mountain"] },
    { from: "KOR", dates: { start: "2025-06-01", end: "2025-06-10" }, budget: { max: 1500 }, interests: ["beach","party"] }
  ]
});
```

## Running the MCP Server

```bash
cd agent/mcp
uv run server.py
```

## Running the Flask Server

```bash
cd ~
cd agent && uv run app.py
```

## API Endpoint

### `POST /plan-trip`

Fetches the latest trip request from MongoDB, generates a shortlist, and returns detailed plans.

#### Example

```bash
curl -X POST http://127.0.0.1:7000/plan-trip \
     -H "Content-Type: application/json"
```

##### Response

```json
{
  "plans": [ /* array of { destination, flights, totals } */ ],
  "shortlist": [ /* array of candidate cities */ ]
}
```

## Testing

* For manual testing, use the provided `curl` example after seeding Mongo.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Developed during the HackUPC Hackthon in Barcelona*
