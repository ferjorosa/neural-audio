'use client';

import { useState, useCallback, useEffect } from 'react';
import { useAudioCapture } from '../useAudioCapture';
import { useWebSocket, VADEvent } from '../useWebSocket';

interface VADStatus {
  isSpeaking: boolean;
  confidence: number;
  lastEvent: string | null;
  eventTimestamp: number | null;
}

export default function Home() {
  const [vadStatus, setVADStatus] = useState<VADStatus>({
    isSpeaking: false,
    confidence: 0,
    lastEvent: null,
    eventTimestamp: null
  });
  
  const [isActive, setIsActive] = useState(false);

  // WebSocket connection
  const handleVADMessage = useCallback((message: VADEvent) => {
    console.log('Received VAD message:', message);
    
    if (message.type === 'vad_event') {
      setVADStatus(prev => ({
        ...prev,
        isSpeaking: message.event === 'speech_start',
        lastEvent: message.event || null,
        eventTimestamp: message.timestamp || Date.now(),
        confidence: message.confidence || prev.confidence
      }));
    } else if (message.type === 'vad_confidence') {
      setVADStatus(prev => ({
        ...prev,
        confidence: message.confidence || 0,
        isSpeaking: message.is_speaking || false
      }));
    }
  }, []);

  const { 
    state: wsState, 
    connect: connectWS, 
    disconnect: disconnectWS, 
    sendAudioChunk,
    resetVAD 
  } = useWebSocket('ws://localhost:8000/ws', handleVADMessage);

  // Audio capture
  const handleAudioChunk = useCallback((chunk: Uint8Array) => {
    // Always try to send - the sendAudioChunk function will check connection internally
    console.log(`🎤 Frontend: handleAudioChunk called`);
    sendAudioChunk(chunk);
  }, [sendAudioChunk]);

  const { 
    state: audioState, 
    startRecording, 
    stopRecording, 
    cleanup: cleanupAudio 
  } = useAudioCapture(handleAudioChunk);

  // Main control function
  const toggleVAD = useCallback(async () => {
    if (!isActive) {
      // Start VAD session
      try {
        connectWS();
        await startRecording();
        setIsActive(true);
      } catch (error) {
        console.error('Failed to start VAD:', error);
      }
    } else {
      // Stop VAD session
      stopRecording();
      disconnectWS();
      cleanupAudio();
      setIsActive(false);
      setVADStatus({
        isSpeaking: false,
        confidence: 0,
        lastEvent: null,
        eventTimestamp: null
      });
    }
  }, [isActive, connectWS, startRecording, stopRecording, disconnectWS, cleanupAudio]);

  const handleReset = useCallback(() => {
    resetVAD();
    setVADStatus(prev => ({
      ...prev,
      isSpeaking: false,
      lastEvent: 'reset',
      eventTimestamp: Date.now()
    }));
  }, [resetVAD]);

  // Format timestamp for display
  const formatTimestamp = (timestamp: number | null) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div style={{ 
      maxWidth: '800px', 
      margin: '0 auto', 
      padding: '2rem',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1 style={{ textAlign: 'center', marginBottom: '2rem' }}>
        Simple VAD Demo
      </h1>
      
      <div style={{ 
        textAlign: 'center', 
        marginBottom: '2rem',
        fontSize: '0.9rem',
        color: '#666'
      }}>
        Real-time Voice Activity Detection using Silero VAD
      </div>

      {/* Main Control Button */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <button
          onClick={toggleVAD}
          disabled={audioState.error !== null || wsState.error !== null}
          style={{
            padding: '1rem 2rem',
            fontSize: '1.2rem',
            backgroundColor: isActive ? '#dc3545' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: audioState.error || wsState.error ? 'not-allowed' : 'pointer',
            opacity: audioState.error || wsState.error ? 0.6 : 1
          }}
        >
          {isActive ? 'Stop VAD' : 'Start VAD'}
        </button>
        
        {isActive && (
          <button
            onClick={handleReset}
            style={{
              marginLeft: '1rem',
              padding: '0.5rem 1rem',
              fontSize: '1rem',
              backgroundColor: '#ffc107',
              color: '#000',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Reset VAD
          </button>
        )}
      </div>

      {/* Status Display */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        {/* VAD Status */}
        <div style={{
          padding: '1.5rem',
          border: '2px solid #ddd',
          borderRadius: '8px',
          backgroundColor: vadStatus.isSpeaking ? '#d4edda' : '#f8f9fa'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>
            Voice Activity
          </h3>
          <div style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold',
            color: vadStatus.isSpeaking ? '#155724' : '#6c757d',
            marginBottom: '0.5rem'
          }}>
            {vadStatus.isSpeaking ? '🎤 SPEAKING' : '🔇 SILENT'}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#666' }}>
            Confidence: {(vadStatus.confidence * 100).toFixed(1)}%
          </div>
        </div>

        {/* Connection Status */}
        <div style={{
          padding: '1.5rem',
          border: '2px solid #ddd',
          borderRadius: '8px',
          backgroundColor: wsState.isConnected && audioState.isRecording ? '#d4edda' : '#f8f9fa'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>
            Connection Status
          </h3>
          <div style={{ marginBottom: '0.5rem' }}>
            WebSocket: {
              wsState.isConnecting ? '🟡 Connecting...' :
              wsState.isConnected ? '🟢 Connected' : '🔴 Disconnected'
            }
          </div>
          <div>
            Audio: {
              audioState.isRecording ? '🟢 Recording' :
              audioState.isInitialized ? '🟡 Ready' : '🔴 Not Ready'
            }
          </div>
        </div>
      </div>

      {/* Event Log */}
      <div style={{
        padding: '1.5rem',
        border: '2px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#f8f9fa'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>
          Last Event
        </h3>
        <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
          {vadStatus.lastEvent ? (
            <span style={{ 
              color: vadStatus.lastEvent === 'speech_start' ? '#28a745' : 
                    vadStatus.lastEvent === 'speech_end' ? '#dc3545' : '#6c757d'
            }}>
              {vadStatus.lastEvent.replace('_', ' ').toUpperCase()}
            </span>
          ) : (
            <span style={{ color: '#6c757d' }}>No events yet</span>
          )}
        </div>
        <div style={{ fontSize: '0.9rem', color: '#666' }}>
          Time: {formatTimestamp(vadStatus.eventTimestamp)}
        </div>
      </div>

      {/* Error Display */}
      {(audioState.error || wsState.error) && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '6px'
        }}>
          <strong>Error:</strong> {audioState.error || wsState.error}
        </div>
      )}

      {/* Instructions */}
      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        backgroundColor: '#e7f3ff',
        border: '1px solid #b3d7ff',
        borderRadius: '6px',
        fontSize: '0.9rem'
      }}>
        <h4 style={{ margin: '0 0 0.5rem 0' }}>Instructions:</h4>
        <ol style={{ margin: 0, paddingLeft: '1.5rem' }}>
          <li>Click "Start VAD" to begin voice activity detection</li>
          <li>Grant microphone permissions when prompted</li>
          <li>Speak normally - the system will detect when you start and stop talking</li>
          <li>Watch the "Voice Activity" panel for real-time feedback</li>
          <li>Use "Reset VAD" to clear the detection state if needed</li>
          <li>Click "Stop VAD" to end the session</li>
        </ol>
      </div>
    </div>
  );
}
