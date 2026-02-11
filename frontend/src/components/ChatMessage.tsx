import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import type { HistoricalCharacter } from "@/data/characters";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  character?: HistoricalCharacter;
}

const ChatMessage = ({ role, content, character }: ChatMessageProps) => {
  if (role === "user") {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="flex justify-end mb-6"
      >
        <div className="max-w-[75%] rounded-2xl rounded-tr-sm bg-primary/15 border border-primary/20 px-5 py-3 shadow-sm">
          <p className="text-foreground text-sm leading-relaxed">{content}</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="flex gap-3 mb-6"
    >
      {character && (
        <div className="flex-shrink-0 w-10 h-10 rounded-full overflow-hidden border-2 border-primary/30 mt-1 shadow-md">
          <img
            src={character.image}
            alt={character.name}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      <div className="max-w-[80%] rounded-2xl rounded-tl-sm bg-gradient-card border border-border px-5 py-3 shadow-sm">
        <div className="prose prose-sm prose-invert max-w-none text-foreground/90 leading-relaxed [&_p]:mb-2 [&_p:last-child]:mb-0 [&_strong]:text-primary [&_strong]:font-semibold [&_em]:text-gold-light [&_em]:italic [&_code]:text-primary [&_code]:bg-primary/10 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded [&_ul]:my-2 [&_ol]:my-2 [&_li]:my-1">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatMessage;