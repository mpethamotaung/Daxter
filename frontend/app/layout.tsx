// frontend/app/layout.tsx
export const metadata = {
  title: 'Daxter - Accountant Data Aggregator',
  description: 'Financial and tax compliance dashboard',
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      {/* Note: Browser extensions like Grammarly may add data attributes to <body>, causing hydration warnings. This is external and can be ignored during development. */}
      <body>{children}</body>
    </html>
  );
}