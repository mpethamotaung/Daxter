// frontend/app/ThemeWrapper.tsx

"use client";

import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

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

export default function ThemeWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ThemeProvider theme={daxterTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}