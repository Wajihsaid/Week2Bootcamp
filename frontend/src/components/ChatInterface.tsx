import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, Send, Loader2, Mic, MicOff } from "lucide-react";
import ChatMessage from "./ChatMessage";
import type { HistoricalCharacter } from "@/data/characters";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatInterfaceProps {
  character: HistoricalCharacter;
  onBack: () => void;
}

const CHAT_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/historical-chat`;

const ChatInterface = ({ character, onBack }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: character.greeting },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [inputMode, setInputMode] = useState<"text" | "voice">("text");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;
    const userMsg: Message = { role: "user", content: text.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    let assistantSoFar = "";
    const allMessages = [...messages, userMsg];

    try {
      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
        },
        body: JSON.stringify({
          messages: allMessages.map((m) => ({ role: m.role, content: m.content })),
          characterId: character.id,
        }),
      });

      if (!resp.ok || !resp.body) {
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData.error || "Failed to get response");
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let textBuffer = "";
      let streamDone = false;

      const upsert = (chunk: string) => {
        assistantSoFar += chunk;
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && prev.length > 1 && prev[prev.length - 2]?.role === "user") {
            return prev.map((m, i) => (i === prev.length - 1 ? { ...m, content: assistantSoFar } : m));
          }
          return [...prev, { role: "assistant", content: assistantSoFar }];
        });
      };

      while (!streamDone) {
        const { done, value } = await reader.read();
        if (done) break;
        textBuffer += decoder.decode(value, { stream: true });

        let newlineIndex: number;
        while ((newlineIndex = textBuffer.indexOf("\n")) !== -1) {
          let line = textBuffer.slice(0, newlineIndex);
          textBuffer = textBuffer.slice(newlineIndex + 1);
          if (line.endsWith("\r")) line = line.slice(0, -1);
          if (line.startsWith(":") || line.trim() === "") continue;
          if (!line.startsWith("data: ")) continue;
          const jsonStr = line.slice(6).trim();
          if (jsonStr === "[DONE]") { streamDone = true; break; }
          try {
            const parsed = JSON.parse(jsonStr);
            const content = parsed.choices?.[0]?.delta?.content as string | undefined;
            if (content) upsert(content);
          } catch {
            textBuffer = line + "\n" + textBuffer;
            break;
          }
        }
      }
    } catch (e: any) {
      console.error(e);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "I cannot reach the spirits of the past right now. Please try again." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("Could not access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    // Placeholder for speech-to-text integration
    setInput("(Voice message transcription would appear here)");
    console.log("Audio blob ready for transcription:", audioBlob);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="absolute inset-0 flex bg-gradient-dark"
      style={{ width: '100vw', height: '100vh' }}
    >
      {/* Left Side - Character Avatar & Info */}
      <div className="w-2/5 min-w-[300px] border-r border-border bg-card/30 backdrop-blur-sm flex flex-col">
        {/* Back Button */}
        <div className="p-4 border-b border-border flex-shrink-0">
          <button
            onClick={onBack}
            className="flex items-center gap-2 p-2 rounded-lg hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft size={20} />
            <span className="text-sm font-medium">Back to Characters</span>
          </button>
        </div>

        {/* Character Avatar - Large Display */}
        <div className="flex-1 flex flex-col items-center justify-center p-8 overflow-y-auto">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="relative"
          >
            <div className="w-64 h-64 rounded-full overflow-hidden border-4 border-primary/40 shadow-2xl shadow-primary/20">
              <img
                src={character.image}
                alt={character.name}
                className="w-full h-full object-cover"
              />
            </div>
            {/* Decorative glow effect */}
            <div className="absolute inset-0 rounded-full bg-primary/10 blur-2xl -z-10" />
          </motion.div>

          {/* Character Info */}
          <div className="mt-8 text-center space-y-2">
            <h1 className="font-display font-bold text-3xl text-foreground">
              {character.name}
            </h1>
            <p className="text-primary font-medium">{character.title}</p>
            <p className="text-muted-foreground text-sm">{character.era}</p>
            <div className="pt-4 max-w-sm">
              <p className="text-xs text-muted-foreground/80 leading-relaxed">
                Speak with the legendary {character.name}. Ask about their life,
                conquests, and the wisdom they've gained through the ages.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Chat Interface */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card/50 backdrop-blur-sm flex-shrink-0">
          <div>
            <h2 className="font-display font-bold text-foreground text-xl">
              Conversation
            </h2>
            <p className="text-xs text-muted-foreground">
              Ask anything about history, strategy, or philosophy
            </p>
          </div>

          {/* Input Mode Toggle */}
          <div className="flex gap-2 bg-secondary rounded-lg p-1">
            <button
              onClick={() => setInputMode("text")}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${inputMode === "text"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
                }`}
            >
              Text
            </button>
            <button
              onClick={() => setInputMode("voice")}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${inputMode === "voice"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
                }`}
            >
              Voice
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
          <AnimatePresence>
            {messages.map((msg, i) => (
              <ChatMessage
                key={i}
                role={msg.role}
                content={msg.content}
                character={msg.role === "assistant" ? character : undefined}
              />
            ))}
          </AnimatePresence>
          {isLoading && messages[messages.length - 1]?.role === "user" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3 mb-4"
            >
              <div className="flex-shrink-0 w-9 h-9 rounded-full overflow-hidden border border-primary/30 mt-1">
                <img
                  src={character.image}
                  alt={character.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="rounded-lg bg-gradient-card border border-border px-4 py-3">
                <Loader2 size={18} className="animate-spin text-primary" />
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested questions */}
        {messages.length === 1 && (
          <div className="px-6 pb-3 flex-shrink-0">
            <p className="text-xs text-muted-foreground mb-2 font-medium">
              Suggested questions:
            </p>
            <div className="flex flex-wrap gap-2">
              {character.suggestedQuestions.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-xs px-3 py-2 rounded-full border border-primary/30 text-primary hover:bg-primary/10 transition-colors font-sans"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-6 border-t border-border bg-card/50 backdrop-blur-sm flex-shrink-0">
          {inputMode === "text" ? (
            <div className="flex gap-3 items-end">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={`Ask ${character.name} a question...`}
                rows={1}
                className="flex-1 resize-none bg-secondary border border-border rounded-lg px-4 py-3 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm font-body max-h-32"
              />
              <button
                onClick={() => sendMessage(input)}
                disabled={!input.trim() || isLoading}
                className="p-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
              >
                <Send size={20} />
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`p-8 rounded-full transition-all duration-300 ${isRecording
                      ? "bg-red-500 hover:bg-red-600 animate-pulse"
                      : "bg-primary hover:bg-primary/90"
                    } text-primary-foreground shadow-lg`}
                >
                  {isRecording ? <MicOff size={32} /> : <Mic size={32} />}
                </button>
                {isRecording && (
                  <motion.div
                    className="absolute inset-0 rounded-full border-4 border-red-500"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  />
                )}
              </div>
              <p className="text-sm text-muted-foreground">
                {isRecording
                  ? "Recording... Click to stop"
                  : "Click to start recording"}
              </p>
              {input && (
                <div className="w-full flex gap-3 items-end">
                  <div className="flex-1 bg-secondary border border-border rounded-lg px-4 py-3 text-foreground text-sm">
                    {input}
                  </div>
                  <button
                    onClick={() => sendMessage(input)}
                    disabled={isLoading}
                    className="p-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
                  >
                    <Send size={20} />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ChatInterface;