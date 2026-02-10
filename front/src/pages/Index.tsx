import { useState, useCallback } from "react";
import ModeToggle from "@/components/ModeToggle";
import ChatPanel from "@/components/ChatPanel";
import VoicePanel from "@/components/VoicePanel";
import MosaicDivider from "@/components/MosaicDivider";
import heroBg from "@/assets/hero-bg.jpg";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  character?: string;
}

const DEMO_RESPONSES: Record<string, { character: string; response: string }> = {
  default: {
    character: "hannibal",
    response: "I am Hannibal Barca, the great general of Carthage! Ask me about our mighty civilization that once rivaled Rome itself.",
  },
  carthage: {
    character: "dido",
    response: "I am Queen Dido, founder of Carthage. Our city rose from the shores of North Africa to become the jewel of the Mediterranean. What would you know of our legacy?",
  },
  modern: {
    character: "bourguiba",
    response: "I am Habib Bourguiba, father of modern Tunisia. I led our nation to independence in 1956 and worked to build a progressive, educated society.",
  },
  history: {
    character: "ibn-khaldun",
    response: "I am Ibn Khaldun, born in Tunis in 1332. I am considered the father of historiography and sociology. History, my friend, is far more than a chronicle of events.",
  },
  war: {
    character: "kahena",
    response: "I am Al-Kahina, the warrior queen who resisted the Umayyad conquest. I fought for our people's freedom with every breath. What do you wish to know?",
  },
};

const Index = () => {
  const [mode, setMode] = useState<"text" | "voice">("text");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const getResponse = useCallback((userMessage: string) => {
    const lower = userMessage.toLowerCase();
    if (lower.includes("carthage") || lower.includes("dido") || lower.includes("punic")) {
      return DEMO_RESPONSES.carthage;
    }
    if (lower.includes("modern") || lower.includes("independence") || lower.includes("bourguiba")) {
      return DEMO_RESPONSES.modern;
    }
    if (lower.includes("history") || lower.includes("khaldun") || lower.includes("scholar")) {
      return DEMO_RESPONSES.history;
    }
    if (lower.includes("war") || lower.includes("kahena") || lower.includes("resist") || lower.includes("fight")) {
      return DEMO_RESPONSES.war;
    }
    return DEMO_RESPONSES.default;
  }, []);

  const handleSendMessage = useCallback(
    (content: string) => {
      const userMsg: Message = {
        id: Date.now().toString(),
        role: "user",
        content,
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      setTimeout(() => {
        const { character, response } = getResponse(content);

        const assistantMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: response,
          character,
        };
        setMessages((prev) => [...prev, assistantMsg]);
        setIsLoading(false);
      }, 1500);
    },
    [getResponse]
  );

  const handleToggleListening = useCallback(() => {
    setIsListening((prev) => !prev);
    if (!isListening) {
      // Simulate voice input after 3 seconds
      setTimeout(() => {
        setIsListening(false);
        handleSendMessage("Tell me about the history of Carthage");
      }, 3000);
    }
  }, [isListening, handleSendMessage]);

  return (
    <div className="min-h-screen bg-background mosaic-pattern flex flex-col">
      {/* Header - BIGGER HERO IMAGE */}
      <header className="relative overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-70"
          style={{ backgroundImage: `url(${heroBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/5 via-background/20 to-background/90" />
        <div className="relative z-10 px-6 pt-12 pb-10 text-center">
          <h1 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold text-foreground tracking-tight mb-3">
            Voices of Tunisia
          </h1>
          <p className="mt-2 text-muted-foreground font-body text-xs md:text-sm max-w-lg mx-auto leading-relaxed">
            Journey through centuries of Tunisian history — guided by the voices of those who shaped it
          </p>
          <div className="mt-6">
            <ModeToggle mode={mode} onModeChange={setMode} />
          </div>
        </div>
        <MosaicDivider />
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center max-w-4xl mx-auto w-full px-4 pb-6 mt-6">
        {/* Chat / Voice Area - CENTERED & SMALLER */}
        <div className="w-full max-w-2xl bg-sand-light/50 backdrop-blur-sm border border-border rounded-2xl overflow-hidden min-h-[400px] max-h-[600px] flex flex-col shadow-xl">
          {mode === "text" ? (
            <ChatPanel
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          ) : (
            <VoicePanel
              isListening={isListening}
              onToggleListening={handleToggleListening}
            />
          )}
        </div>
      </main>

      {/* Footer - SMALLER TEXT */}
      <footer className="text-center py-4 text-[10px] text-muted-foreground/70 font-body">
        Explore 3,000 years of Tunisian heritage
      </footer>
    </div>
  );
};

export default Index;