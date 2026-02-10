import { Mic, MessageSquare } from "lucide-react";

interface ModeToggleProps {
  mode: "text" | "voice";
  onModeChange: (mode: "text" | "voice") => void;
}

const ModeToggle = ({ mode, onModeChange }: ModeToggleProps) => {
  return (
    <div className="inline-flex items-center rounded-full bg-card border border-border p-1 gap-1">
      <button
        onClick={() => onModeChange("text")}
        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-body font-medium transition-all duration-300 ${
          mode === "text"
            ? "bg-primary text-primary-foreground shadow-md"
            : "text-muted-foreground hover:text-foreground"
        }`}
      >
        <MessageSquare className="w-4 h-4" />
        Text
      </button>
      <button
        onClick={() => onModeChange("voice")}
        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-body font-medium transition-all duration-300 ${
          mode === "voice"
            ? "bg-secondary text-secondary-foreground shadow-md"
            : "text-muted-foreground hover:text-foreground"
        }`}
      >
        <Mic className="w-4 h-4" />
        Voice
      </button>
    </div>
  );
};

export default ModeToggle;
