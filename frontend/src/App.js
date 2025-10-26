import { useMicVAD } from "@ricky0123/vad-react"

export default function App() {
  const vad = useMicVAD({
    onSpeechEnd: (audio) => {
      console.log("User stopped talking")
    },
    onSpeechStart: () => {
      console.log("User started talking")
    },
    onVADMisfire: () => {
      console.log("VAD misfire")
    },
    onError: (error) => {
      console.error("VAD Error:", error)
    },
    // Explicitly use CDN URLs to avoid local asset loading issues
    workletURL: "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.28/dist/vad.worklet.bundle.min.js",
    modelURL: "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.28/dist/silero_vad_legacy.onnx",
    ortConfig: {
      wasmPaths: "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.17.1/dist/"
    },
    startOnLoad: true,
  })

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Voice Activity Detection Demo</h1>
      <div style={{ 
        padding: '20px', 
        border: '2px solid #ccc', 
        borderRadius: '10px',
        backgroundColor: vad.userSpeaking ? '#e8f5e8' : '#f5f5f5',
        transition: 'background-color 0.3s ease'
      }}>
        {vad.loading && <p>Loading VAD...</p>}
        {vad.errored && <p style={{color: 'red'}}>Error loading VAD</p>}
        {!vad.loading && !vad.errored && (
          <p style={{ fontSize: '18px', margin: 0 }}>
            {vad.userSpeaking ? "🎤 User is speaking" : "🔇 Listening..."}
          </p>
        )}
      </div>
      <p style={{ marginTop: '20px', color: '#666' }}>
        Grant microphone permissions and start speaking to test the voice activity detection.
      </p>
    </div>
  )
}
