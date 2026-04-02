# CESAR Rating UI – Instructions for Python-only developers

This folder contains a **small web interface** so you can try the valuation model from your browser (Chrome, Firefox, etc.) by entering surface, rooms, department, and property type, then seeing the estimated value. If you have only coded in Python so far, this README explains what is going on and how to run and tweak the UI.

---

## What you need to run the UI

- **Node.js** (and **npm**, which comes with it).  
  Think of Node.js as “Python for JavaScript”: it runs JavaScript outside the browser. We use it only to **install dependencies** and **start a small dev server** that serves our files. You are not expected to write Node.js code.

- **A running CESAR API** (the FastAPI app that runs the model).  
  The UI is just a client: it sends the form data to that API and displays the response. So start the API first (see the main project README).

**Check that Node is installed:**

```bash
node --version
npm --version
```

If you see version numbers, you’re good. If not, install Node.js from [nodejs.org](https://nodejs.org/) (LTS version).

---

## Install and run (quick version)

From the **project root** (the folder that contains `runtime/`):

```bash
cd runtime/rating_ui
npm install
npm run dev
```

Then open the URL shown in the terminal (usually **http://localhost:5173**) in your browser. You should see a form (surface, rooms, department, type) and a map. Fill the form and click **Estimate**; the estimated value appears below.

**Important:** The API must be running separately, e.g.:

```bash
# In another terminal, from project root:
export CESAR_MODEL_PATH=/path/to/model.joblib
export CESAR_CONTRACT_PATH=/path/to/contract.json
uvicorn runtime.prediction_api.app:app --reload --host 0.0.0.0 --port 8000
```

By default the UI talks to the API at `/api`. If your API runs on another URL (e.g. `http://localhost:8000`), open the browser’s **Developer Console** (F12 → “Console”), type:

```javascript
window.CESAR_API_BASE = 'http://localhost:8000'
```

then press Enter and click **Estimate** again. The UI will use that base URL.

---

## High-level: what is this stack?

You are used to **Python**: one language, one interpreter, files like `main.py` that you run with `python main.py`. In the browser things are split into a few layers. Here is a minimal map so you know what each piece is for.

| Concept | In Python terms | Here in the UI |
|--------|------------------|-----------------|
| **HTML** | Not really in Python; it’s the structure of a web page (headings, forms, buttons, divs). | `index.html`: the single page. It has a `<div id="app">` where our code will inject the form, map, and result area. |
| **JavaScript (JS)** | The language that runs **inside the browser**. The only language browsers execute. | All our logic (form, API call, display) is written in **TypeScript**, which compiles to JavaScript so the browser can run it. |
| **TypeScript (TS)** | Like “Python with type hints”: same idea of types for function arguments and return values. | Our source files are `.ts` in `src/`. They get compiled to `.js` and run in the browser. |
| **npm** | Like **pip**: it installs packages (libraries) and runs scripts. | `npm install` reads `package.json` and installs dependencies (e.g. Vite, TypeScript, Leaflet). |
| **Vite** | A **dev server** and **bundler**. Like a small “run and reload” tool. | `npm run dev` starts Vite: it serves `index.html` and our TS/JS, and when you edit a file it refreshes the page. No need to understand Vite in depth. |
| **Leaflet** | A library to show a map in the page. | We use it in `map_france.ts` to display a map of France. |

So in one sentence: **HTML is the page skeleton, TypeScript/JavaScript is the logic (like your Python scripts), and Vite + npm are the tools that let you run and edit this in the browser.**

---

## What each file does (so you can adapt the code)

Everything the UI does lives under `src/`. Think of each file as a **module** (like a Python file with functions).

| File | Role in plain English |
|------|------------------------|
| **`index.html`** | The only HTML page. It loads the Leaflet CSS and our main script. The “app” is a single empty `<div>`; our code fills it. |
| **`src/main.ts`** | Entry point (like `if __name__ == "__main__"`). Finds the `#app` div, creates three areas (form, map, result), and “mounts” the form, map, and result display into them. |
| **`src/form_property_params.ts`** | Builds the **form**: inputs for surface, rooms, department, and a dropdown for property type. On “Estimate” it reads the values and triggers a custom event with those params (so the display module can call the API). |
| **`src/api_client.ts`** | **Calls the API.** Defines the shape of the request (surface, rooms, department, type) and the response (estimated value, optional bounds). `fetchEstimate` does the HTTP POST (similar to `requests.post` in Python). `getApiBase()` returns the API base URL (default `/api`, or what you set in `window.CESAR_API_BASE`). |
| **`src/display_estimate.ts`** | Listens for the “user clicked Estimate” event, shows “Loading…”, calls the API via `api_client`, then shows the estimated value (or an error). |
| **`src/map_france.ts`** | Shows a Leaflet map of France. Right now it’s display-only; you could later add clicks on departments to set the department code. |

**Data flow (same idea as in Python):**

1. User fills form and clicks **Estimate** → `form_property_params.ts` sends the four values in an event.
2. `display_estimate.ts` receives the event → calls `api_client.fetchEstimate(baseUrl, params)` (like `requests.post(url, json=params)` in Python).
3. API returns `{ estimated_value_eur: ... }` → we display it (or show an error).

So: **form** → **event** → **API client** → **display**. No framework like React; just plain TypeScript and the DOM.

---

## Commands you will use

- **`npm install`**  
  Run once (or after someone adds a dependency to `package.json`). Installs the tools and libraries listed in `package.json`.

- **`npm run dev`**  
  Starts the Vite dev server. You get a URL (e.g. http://localhost:5173). Open it in the browser; edits to `src/*.ts` or `index.html` trigger a reload.

- **`npm run build`**  
  Compiles TypeScript and builds a production bundle in `dist/`. Use this if you want to serve the UI from a real web server later.

- **`npm run preview`**  
  Serves the contents of `dist/` locally so you can test the built version (e.g. after `npm run build`).

---

## Making small changes (for students)

- **Change labels or default values**  
  Edit `src/form_property_params.ts`: the strings in the form (e.g. “Rooms”, “Department”) and the `value="50"`, `value="3"`, `value="75"` for defaults.

- **Change how the result is shown**  
  Edit `src/display_estimate.ts`: the strings “Estimated value:”, “Range:”, “Error:”, “Loading…” and the way we build the HTML for the result.

- **Change the API base URL by default**  
  Edit `src/api_client.ts`: the line `const DEFAULT_BASE = "/api"`. Change it to e.g. `"http://localhost:8000"` if your API always runs there during development.

- **Add a new field in the form**  
  You’d add the input in `form_property_params.ts`, add the field to the `EstimateParams` type in `api_client.ts`, and ensure the API contract (request schema) on the Python side includes that field.

After any change, save the file; if `npm run dev` is running, the page should reload and show your changes.

---

## If something doesn’t work

- **“Cannot GET /” or blank page**  
  Make sure you opened the URL given by `npm run dev` (e.g. http://localhost:5173), not a file path.

- **“Failed to fetch” or network error when clicking Estimate**  
  The UI cannot reach the API. Check: (1) Is the API running? (2) Is it on the same origin (same host/port) as the page? If not, set `window.CESAR_API_BASE` in the console to the API URL (e.g. `http://localhost:8000`).

- **`npm: command not found`**  
  Node.js is not installed or not on your PATH. Install Node.js from nodejs.org and try again.

- **Port 5173 already in use**  
  Another process is using that port. Stop it or run the dev server with a different port (see Vite docs); for a first run you can just close the other app.

---

## Summary

- **Install:** `cd runtime/rating_ui && npm install`  
- **Run:** `npm run dev` → open the URL in the browser.  
- **API:** Start the CESAR API (e.g. uvicorn) and, if needed, set `window.CESAR_API_BASE` in the browser console.  
- **Understand:** HTML = page structure, TypeScript/JS = logic, Vite = dev server, npm = install/run.  
- **Edit:** Form and defaults in `form_property_params.ts`, result text in `display_estimate.ts`, API base in `api_client.ts`.

This should be enough to run the UI, understand at a high level what each technology does, and make small adaptations to the code.
