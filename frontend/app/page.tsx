import Dashboard from './Dashboard';
import ClientProvider from './ClientProvider';

export default function Page() {
  return (
    <ClientProvider>
      <Dashboard />
    </ClientProvider>
  );
}