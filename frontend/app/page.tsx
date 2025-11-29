// frontend/app/page.tsx

"use client"; // Mark as Client Component

import Dashboard from './Dashboard';
import ThemeWrapper from './ThemeWrapper'; // Direct import, no dynamic needed

export default function Home() {
  return (
    <ThemeWrapper>
      <main className="min-h-screen bg-gray-100 p-8">
        <Dashboard />
      </main>
    </ThemeWrapper>
  );
}