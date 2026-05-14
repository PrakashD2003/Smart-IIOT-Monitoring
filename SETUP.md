# Setup Guide - Smart IIoT Monitoring System

## Prerequisites Checklist

Before running `make install-all`, ensure you have:

- [ ] **Conda** installed (Miniconda or Anaconda)
  - Verify: `conda --version`
  - Download: https://docs.conda.io/en/latest/miniconda.html

- [ ] **Node.js v18+** installed
  - Verify: `node --version` (should be v18.0.0 or higher)
  - Verify: `npm --version`
  - Download: https://nodejs.org/

- [ ] **Make** utility (optional but recommended)
  - Windows: Install via Chocolatey (`choco install make`) or use Git Bash
  - Mac/Linux: Usually pre-installed
  - Alternative: Run commands manually (see below)

## Quick Setup (One Command)

```bash
make install-all
```

This will:
1. Create/update the conda environment (`smart-iiot`)
2. Install pre-commit hooks
3. Install Node.js dependencies for the dashboard

## Manual Setup (If Make is not available)

### Step 1: Create Conda Environment
```bash
conda env create -f environment.yaml
# or update existing:
conda env update -f environment.yaml --prune
```

### Step 2: Setup Python Tools
```bash
conda activate smart-iiot
pre-commit install
```

### Step 3: Setup Dashboard Dependencies
```bash
cd dashboard
npm install
cd ..
```

## Running the Application

### Option 1: Using Make (Recommended)

**Terminal 1 - Backend:**
```bash
make run-api
```

**Terminal 2 - Dashboard:**
```bash
make run-dashboard
```

**Or run both together:**
```bash
make run-all
```

### Option 2: Manual Commands

**Terminal 1 - Backend:**
```bash
conda activate smart-iiot
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Dashboard:**
```bash
cd dashboard
npm run dev
```

## Access Points

- **API Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Dashboard**: http://localhost:5173

## Troubleshooting

### "Node.js not found" Error
1. Install Node.js from https://nodejs.org/
2. Restart your terminal
3. Verify: `node --version` and `npm --version`
4. Run `make setup-dashboard` again

### "Conda command not found"
1. Ensure Conda is installed and initialized
2. On Windows: Add Conda to PATH or use Anaconda Prompt
3. Verify: `conda --version`

### Port Already in Use
- **Port 8000 (API)**: Change in `Makefile` or stop the process using it
- **Port 5173 (Dashboard)**: Change in `dashboard/vite.config.js` or use `npm run dev -- --port 3000`

### Dashboard Styles Not Loading
1. Clear Vite cache:
   ```bash
   # Windows PowerShell
   Remove-Item -Recurse -Force dashboard\node_modules\.vite
   
   # Mac/Linux
   rm -rf dashboard/node_modules/.vite
   ```
2. Restart dashboard: `make run-dashboard`
3. Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

## Development Workflow

1. **Activate environment**: `conda activate smart-iiot`
2. **Make changes** to code
3. **Run linting**: `make lint`
4. **Run tests**: `make test`
5. **Start services**: `make run-api` and `make run-dashboard`

## Cleanup

- **Clean Python cache**: `make clean`
- **Clean everything** (including node_modules): `make clean-all`

## Next Steps

After setup:
1. Review the main [README.md](README.md) for project structure
2. Check `api/main.py` for API endpoints
3. Explore `dashboard/src/App.jsx` for dashboard components
4. See `notebooks/` for data analysis and preprocessing

