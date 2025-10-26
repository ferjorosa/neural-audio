import { useRef, useCallback, useState, useEffect } from 'react';

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: any;
}

export interface VADEvent {
  type: 'vad_event' | 'vad_confidence' | 'reset_complete';
  event?: 'speech_start' | 'speech_end';
  confidence?: number;
  is_speaking?: boolean;
  message?: string;
  timestamp?: number;
}

export const useWebSocket = (
  url: string,
  onMessage?: (message: VADEvent) => void
) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const maxReconnectAttempts = 5;
  
  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    lastMessage: null
  });
  
  // Debug WebSocket state changes
  useEffect(() => {
    console.log(`📡 Frontend: WebSocket state changed - connected: ${state.isConnected}, connecting: ${state.isConnecting}`);
  }, [state.isConnected, state.isConnecting]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    setState(prev => ({ 
      ...prev, 
      isConnecting: true, 
      error: null 
    }));

    try {
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('📡 Frontend: WebSocket connected');
        setState(prev => ({ 
          ...prev, 
          isConnected: true, 
          isConnecting: false,
          error: null 
        }));
        setReconnectAttempts(0);
        
        // Send a test message to verify connection
        console.log('📡 Frontend: Sending test message...');
        ws.send(JSON.stringify({ type: 'test', message: 'Frontend connected' }));
      };

      ws.onmessage = (event) => {
        try {
          const message: VADEvent = JSON.parse(event.data);
          console.log('📨 Frontend: Received message from backend:', message);
          setState(prev => ({ 
            ...prev, 
            lastMessage: message 
          }));
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('📡 Frontend: WebSocket closed:', event.code, event.reason);
        setState(prev => ({ 
          ...prev, 
          isConnected: false, 
          isConnecting: false 
        }));
        
        // Attempt to reconnect if not manually closed
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
          console.log(`Attempting to reconnect in ${delay}ms...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, delay);
        }
      };

      ws.onerror = (error) => {
        console.error('📡 Frontend: WebSocket error:', error);
        setState(prev => ({ 
          ...prev, 
          error: 'WebSocket connection error',
          isConnecting: false 
        }));
      };

      wsRef.current = ws;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: 'Failed to create WebSocket connection',
        isConnecting: false 
      }));
    }
  }, [url, onMessage, reconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }
    
    setState({
      isConnected: false,
      isConnecting: false,
      error: null,
      lastMessage: null
    });
    setReconnectAttempts(0);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      console.log(`📤 Frontend: Successfully sent message: ${JSON.stringify(message).substring(0, 50)}...`);
    } else {
      console.warn(`⚠️ Frontend: WebSocket is not connected. Cannot send message. State: ${wsRef.current?.readyState}`);
    }
  }, []);

  const sendAudioChunk = useCallback((audioData: Uint8Array) => {
    // Convert Uint8Array to base64
    // Check if this is a valid Opus frame
    console.log(`📡 Frontend: Preparing audio chunk - ${audioData.length} bytes`);
    console.log(`📡 Frontend: First few bytes:`, Array.from(audioData.slice(0, 10)));
    
    // Only send if audioData has content
    if (audioData.length === 0) {
      console.warn('⚠️ Frontend: Skipping empty audio chunk');
      return;
    }
    
    // Properly convert Uint8Array to base64 (handles large arrays correctly)
    let binary = '';
    const len = audioData.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(audioData[i]);
    }
    const base64Data = btoa(binary);
    
    console.log(`📡 Frontend: Sending audio chunk - ${audioData.length} bytes (base64: ${base64Data.length} chars)`);
    
    sendMessage({
      type: 'audio_chunk',
      data: base64Data
    });
  }, [sendMessage]);

  const resetVAD = useCallback(() => {
    sendMessage({
      type: 'reset'
    });
  }, [sendMessage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    state,
    connect,
    disconnect,
    sendMessage,
    sendAudioChunk,
    resetVAD
  };
};
