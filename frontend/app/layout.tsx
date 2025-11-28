// frontend/app/layout.tsx

import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import './globals.css'; //Even tho using Material UI, still needed for layout.tsx

// 1. Define the MUI Theme
const daxterTheme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Blue
    },
    secondary: {
      main: '#dc004e', // Red
    },
  },
});

// Define metadata (required by Next.js)
export const metadata = {
  title: 'Daxter - Accountant Data Aggregator',
  description: 'Financial and tax compliance dashboard',
};

// 2. Wrap the content in the ThemeProvider
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider theme={daxterTheme}>
          {/* CssBaseline is MUI's version of a CSS reset/normalize */}
          <CssBaseline />
          {children} 
        </ThemeProvider>
      </body>
    </html>
  );
}