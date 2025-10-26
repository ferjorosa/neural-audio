import { useRef, useCallback, useState } from 'react';
import OpusRecorder from 'opus-recorder';

export interface AudioCaptureState {
  isRecording: boolean;
  isInitialized: boolean;
  error: string | null;
}

export const useAudioCapture = (onAudioChunk: (chunk: Uint8Array) => void) => {
  const opusRecorderRef = useRef<OpusRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  
  const [state, setState] = useState<AudioCaptureState>({
    isRecording: false,
    isInitialized: false,
    error: null
  });

  const initializeAudio = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, error: null }));
      
      // Request microphone access
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: false,
          autoGainControl: true,
          channelCount: 1,
        }
      });
      
      mediaStreamRef.current = mediaStream;
      
      // Configure Opus recorder (matching the main project settings)
      const recorderOptions = {
        mediaTrackConstraints: {
          audio: {
            echoCancellation: true,
            noiseSuppression: false,
            autoGainControl: true,
            channelCount: 1,
          },
          video: false,
        },
        encoderPath: '/encoderWorker.min.js',
        bufferLength: 960, // 40ms at 24kHz
        encoderFrameSize: 20,
        encoderSampleRate: 24000,
        maxFramesPerPage: 2,
        numberOfChannels: 1,
        recordingGain: 1,
        resampleQuality: 3,
        encoderComplexity: 0,
        encoderApplication: 2049, // OPUS_APPLICATION_VOIP
        streamPages: true, // Output Ogg pages (backend will handle with sphn)
      };
      
      const opusRecorder = new OpusRecorder(recorderOptions);
      
      // Set up data handler
      opusRecorder.ondataavailable = (data: Uint8Array) => {
        console.log(`🎤 Frontend: Audio chunk captured - ${data.length} bytes`);
        onAudioChunk(data);
      };
      
      opusRecorderRef.current = opusRecorder;
      
      setState(prev => ({ 
        ...prev, 
        isInitialized: true,
        error: null 
      }));
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to initialize audio';
      setState(prev => ({ 
        ...prev, 
        error: errorMessage,
        isInitialized: false 
      }));
      console.error('Audio initialization error:', error);
    }
  }, [onAudioChunk]);

  const startRecording = useCallback(async () => {
    console.log('🎤 Frontend: Starting recording...');
    if (!opusRecorderRef.current) {
      console.log('🎤 Frontend: Initializing audio first...');
      await initializeAudio();
    }
    
    if (opusRecorderRef.current && !state.isRecording) {
      try {
        opusRecorderRef.current.start();
        console.log('🎤 Frontend: OpusRecorder started successfully');
        setState(prev => ({ 
          ...prev, 
          isRecording: true,
          error: null 
        }));
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to start recording';
        console.error('🎤 Frontend: Failed to start recording:', error);
        setState(prev => ({ 
          ...prev, 
          error: errorMessage 
        }));
      }
    }
  }, [initializeAudio, state.isRecording]);

  const stopRecording = useCallback(() => {
    if (opusRecorderRef.current && state.isRecording) {
      try {
        opusRecorderRef.current.stop();
        setState(prev => ({ 
          ...prev, 
          isRecording: false 
        }));
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to stop recording';
        setState(prev => ({ 
          ...prev, 
          error: errorMessage 
        }));
      }
    }
  }, [state.isRecording]);

  const cleanup = useCallback(() => {
    if (opusRecorderRef.current) {
      try {
        opusRecorderRef.current.stop();
      } catch (e) {
        // Ignore errors during cleanup
      }
      opusRecorderRef.current = null;
    }
    
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
    
    setState({
      isRecording: false,
      isInitialized: false,
      error: null
    });
  }, []);

  return {
    state,
    startRecording,
    stopRecording,
    cleanup,
    initializeAudio
  };
};
