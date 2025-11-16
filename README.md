The CubePython project intends to provide a recommender engine for Magic: the Gathering cube lists. These recommendations are based on existing cube lists from CubeCobra, as well as learning about the contents of a card so it is able to recommend newly released cards. This documentation covers the setup of the project.

# Data

The main data is coming from two sources:
- CubeCobra for the cube lists (this needs scraping)
- Scryfall for the card content (this has an API)

As the amount of data involved is not small we want to make sure we cache the data locally so we are not overloading these external systems.

The backend should interact with the data through SQLModel (which is Pydantic based). The data should be stored in SQLite.

# UI
We will start with a simple UI that helps us develop. Think of this as a set of visual tools. We should be able to inspect the data as well as recommendations.

Let's use React with Typescript for the UI.

# Backend
The Backend is written in Python using FastAPI and is providing the content for the UI.

# Setup

## Frontend Setup
The frontend is built with Create React App and TypeScript.

```bash
cd frontend
npm install
npm start
```

Available scripts:
- `npm start` - Starts the development server on http://localhost:3000
- `npm run build` - Creates an optimized production build
- `npm test` - Runs the test suite
- `npm run eject` - Ejects from Create React App (one-way operation)
