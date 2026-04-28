import { Activity, Database, Search } from "lucide-react";

import { RunsPage } from "./pages/RunsPage";

export default function App() {
  return (
    <div className="app-shell">
      <nav className="side-nav" aria-label="Glassbox">
        <div className="brand">
          <Database aria-hidden="true" size={22} />
          <span>Glassbox</span>
        </div>
        <a className="nav-item active" href="#runs">
          <Activity aria-hidden="true" size={18} />
          Runs
        </a>
        <a className="nav-item" href="#inspect">
          <Search aria-hidden="true" size={18} />
          Inspect
        </a>
      </nav>
      <RunsPage />
    </div>
  );
}
