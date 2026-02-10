import { useState } from "react";
import { Mic, MicOff } from "lucide-react";

interface VoicePanelProps {
  isListening: boolean;
  onToggleListening: () => void;
}

const VoicePanel = ({ isListening, onToggleListening }: VoicePanelProps) => {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-8 p-6">
      <p className="text-muted-foreground font-body text-sm text-center max-w-xs">
        {isListening
          ? "Listening... Speak about Tunisian history"
          : "Tap the microphone to start speaking"}
      </p>

      {/* Mic button */}
      <button
        onClick={onToggleListening}
        className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 ${
          isListening
            ? "bg-secondary text-secondary-foreground speaking-glow scale-110"
            : "bg-primary text-primary-foreground hover:scale-105"
        }`}
      >
        {isListening ? (
          <MicOff className="w-8 h-8" />
        ) : (
          <Mic className="w-8 h-8" />
        )}

        {/* Ripple rings */}
        {isListening && (
          <>
            <span className="absolute inset-0 rounded-full border-2 border-secondary animate-ping opacity-20" />
            <span
              className="absolute inset-0 rounded-full border-2 border-secondary animate-ping opacity-10"
              style={{ animationDelay: "0.5s" }}
            />
          </>
        )}
      </button>

      {/* Voice wave visualization */}
      {isListening && (
        <div className="flex items-end gap-1 h-12">
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="w-1.5 bg-ceramic rounded-full voice-wave-bar"
              style={{
                height: `${Math.random() * 32 + 16}px`,
                animationDelay: `${i * 0.1}s`,
                animationDuration: `${0.8 + Math.random() * 0.6}s`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default VoicePanel;
