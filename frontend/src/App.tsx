import React from 'react';
import { Layout } from './components/Layout';
import { ChatProvider } from './contexts/ChatContext';
import { Toaster } from 'react-hot-toast';
import './styles/globals.css';

function App() {
  return (
    <ChatProvider>
      <Layout />
      <Toaster 
        position="top-center"
        toastOptions={{
          style: {
            background: '#2A2B2D',
            color: '#ECECF1',
            border: '1px solid #353740',
          },
        }}
      />
    </ChatProvider>
  );
}

export default App;
