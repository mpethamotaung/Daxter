// frontend/app/page.tsx 

import Dashboard from './Dashboard';

// The function exported here MUST be a valid React Component.
export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 p-8">
      {/* Renders the client component */}
      <Dashboard />
    </main>
  );
}
